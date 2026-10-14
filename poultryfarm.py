import machine
import utime
import gc
import time
import urequests


# Import external libraries (must be uploaded to ESP32)
from dht import DHT22
from ssd1306 import SSD1306_I2C

# OLED Configuration
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

# Pin Definitions
DHT_PIN = 27
RELAY_PIN_WATER = 26        # Water Pump Relay (Active LOW)
WATER_SENSOR_PIN = 34       # Analog water level sensor
ULTRASONIC_TRIG = 12        # Ultrasonic sensor Trig pin
ULTRASONIC_ECHO = 14        # Ultrasonic sensor Echo pin
SERVO_PIN = 13
RELAY_PIN_TEMP = 33         # Temperature Control Relay (Active HIGH)
FIRE_SENSOR_PIN = 32        # Digital flame sensor
GAS_SENSOR_PIN = 35         # Analog gas sensor
BUZZER_PIN = 25

# Global Sensor Data Variables
current_water_percent = 0.0
current_food_percent = 0.0
current_temp = 0.0
current_hum = 0.0
fire_detected = False
gas_detected = False
water_relay_state = False
temp_relay_state = False
next_feed_time_ms = 0
feeding = False
feeding_start_time = 0
last_food_time = 0

# MQ-135 Gas Sensor Calibration:
# Read the sensor's value in clean air and set this threshold slightly higher.
# A value of 2000 is a generic starting point but MUST be adjusted.
gas_threshold = 2000

# Constants
FOOD_INTERVAL = 2 * 60 * 60 * 1000  # 2 hours in milliseconds
FOOD_DURATION = 30 * 1000           # 30 seconds in milliseconds

# Component Objects
# Relays are active low, so we start them high (off)
relay_water = machine.Pin(RELAY_PIN_WATER, machine.Pin.OUT, value=0)
# Relays are active high, so we start them low (off)
relay_temp = machine.Pin(RELAY_PIN_TEMP, machine.Pin.OUT, value=0)
dht_sensor = DHT22(machine.Pin(DHT_PIN))
water_sensor = machine.ADC(machine.Pin(WATER_SENSOR_PIN))
gas_sensor = machine.ADC(machine.Pin(GAS_SENSOR_PIN))
fire_sensor = machine.Pin(FIRE_SENSOR_PIN, machine.Pin.IN)
servo = machine.PWM(machine.Pin(SERVO_PIN), freq=50)
buzzer = machine.PWM(machine.Pin(BUZZER_PIN), freq=1000, duty=0)
i2c = machine.I2C(1, scl=machine.Pin(22), sda=machine.Pin(21))
oled = SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c)

def read_water_percent():
    """Reads the water level and returns it as a percentage."""
    raw = water_sensor.read()
    # Map raw analog reading (0-4095) to a percentage (0-100)
    return max(0, min(100, (raw / 4095) * 100))

def read_food_level():
    """Reads the food level using the ultrasonic sensor."""
    trig = machine.Pin(ULTRASONIC_TRIG, machine.Pin.OUT)
    echo = machine.Pin(ULTRASONIC_ECHO, machine.Pin.IN)
    trig.value(0)
    utime.sleep_us(2)
    trig.value(1)
    utime.sleep_us(10)
    trig.value(0)

    timeout = utime.ticks_ms() + 20
    while echo.value() == 0:
        if utime.ticks_ms() > timeout:
            return 0  # Timeout
    t1 = utime.ticks_us()

    timeout = utime.ticks_ms() + 20
    while echo.value() == 1:
        if utime.ticks_ms() > timeout:
            return 0 # Timeout
    t2 = utime.ticks_us()

    duration = utime.ticks_diff(t2, t1)
    distance = (duration * 0.0343) / 2
    # Map distance to percentage (adjust min/max distance as needed)
    percent = (10 - distance) / (10 - 2) * 100
    return max(0, min(100, percent))

def check_safety_sensors():
    """Checks for fire and gas leaks and activates the buzzer."""
    global fire_detected, gas_detected
    fire_state = fire_sensor.value()  # Active LOW
    gas_value = gas_sensor.read()     # Higher value = more gas

    fire_detected = (fire_state == 0)
    gas_detected = (gas_value > gas_threshold)

    if fire_detected or gas_detected:
        buzzer.duty(512)
        print("ALARM: Fire or gas detected!")
    else:
        buzzer.duty(0)

def feed_if_due():
    """Manages the automatic feeding schedule."""
    global feeding, feeding_start_time, last_food_time
    now = utime.ticks_ms()

    if not feeding and utime.ticks_diff(now, last_food_time) >= FOOD_INTERVAL:
        servo.duty(100)  # Move servo to dispense food (adjust duty cycle 0-1023)
        feeding = True
        feeding_start_time = now
        last_food_time = now
        print("Starting scheduled feed.")

    if feeding and utime.ticks_diff(now, feeding_start_time) >= FOOD_DURATION:
        servo.duty(40)  # Move servo to stop dispensing food
        feeding = False
        print("Stopping feed.")

def control_relays(temp, water_percent):
    """Controls the water pump and temperature control relays."""
    global water_relay_state, temp_relay_state
    
    # Temperature Control Relay (Active HIGH)
    if temp >= 30:
        relay_temp.value(1)
        temp_relay_state = True
    else:
        relay_temp.value(0)
        temp_relay_state = False

    # Water Pump Relay (Active LOW)
    if water_percent < 30:
        relay_water.value(0)
        water_relay_state = True
    else:
        relay_water.value(1)
        water_relay_state = False

def display_countdown(remaining_ms):
    """Displays the countdown on the OLED."""
    oled.text("Next Feed:", 0, 52)
    if remaining_ms > 0:
        total_seconds = remaining_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        oled.text(f"{hours:02d}:{minutes:02d} H:M", 75, 52)
    else:
        oled.text("Feeding!", 75, 52)

def draw_bar(x, y, percent):
    """Draws a simple horizontal bar on the OLED display."""
    bar_width = 50
    fill_width = int(bar_width * percent / 100)
    oled.rect(x, y, bar_width, 10, 1)
    oled.fill_rect(x, y, fill_width, 10, 1)

def draw_oled_display():
    """
    Updates the OLED display with sensor data.
    This version shows all data while prioritizing the warning message.
    """
    oled.fill(0)

    # Display the warning message if an alarm is triggered
    if fire_detected or gas_detected:
        oled.text("!!! WARNING !!!", 0, 0, 1)
        # Position subsequent text to avoid overlapping the warning.
        # This will shift all sensor data down by 10 pixels.
        y_offset = 10
    else:
        y_offset = 0

    # Display Food Level
    oled.text(f"FOOD: {current_food_percent: .0f}%", 0, 0 + y_offset, 1)
    draw_bar(65, 0 + y_offset, current_food_percent)

    # Display Water Level
    oled.text(f"WATER: {current_water_percent: .0f}%", 0, 15 + y_offset, 1)
    draw_bar(65, 15 + y_offset, current_water_percent)

    # Display Temperature
    oled.text(f"TEMP: {current_temp: .1f} C", 0, 30 + y_offset, 1)

    # Display Humidity
    oled.text(f"HUM: {current_hum: .1f} %", 0, 42 + y_offset, 1)

    # Display Next Feed Countdown
    display_countdown(next_feed_time_ms)
    
    oled.show()

def print_sensor_data_to_shell():
    """Prints all sensor data and status to the serial shell in a readable format."""
    print("--- Pet Feeder Status ---")
    print(f"Food Level: {current_food_percent:.0f}%")
    print(f"Water Level: {current_water_percent:.0f}%")
    print(f"Temperature: {current_temp:.1f} C")
    print(f"Humidity: {current_hum:.1f}%")
    print(f"Water Pump ON: {water_relay_state}")
    print(f"Temp Control ON: {temp_relay_state}")
    print(f"Fire Detected: {fire_detected}")
    print(f"Gas Detected: {gas_detected}")
    
    if feeding:
        print("Feeding Status: In progress...")
    else:
        remaining_sec = next_feed_time_ms // 1000
        hours = remaining_sec // 3600
        minutes = (remaining_sec % 3600) // 60
        print(f"Next Feed in: {hours:02d}h {minutes:02d}m")
    
    print("-------------------------")
    


def do_connect():
    import network
    sta_if = network.WLAN(network.WLAN.IF_STA)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('NMARS', '1112131415')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ipconfig('addr4'))
    
def send_data(t, h, fl, wl, wps, fs, fires, gs, fts):
    res=urequests.get(f'http://192.168.1.102:8000/data/1?t={t}&h={h}&fl={fl}&wl={wl}&wps={wps}&fs={fs}&fires={fires}&gs={gs}&fts={fts}')
    print(res)


do_connect()


def main():
    """Main function to initialize and run the pet feeder logic."""
    global current_food_percent, current_water_percent, current_temp, current_hum, next_feed_time_ms, last_food_time
    
    print("Starting up...")
    
    last_food_time = utime.ticks_ms()
    
    print("Preheating MQ-135 sensor...")
    time.sleep(2)
    print("Preheating complete.")

    while True:
        # --- Main Loop Logic ---
        try:
            dht_sensor.measure()
            current_temp = dht_sensor.temperature()
            current_hum = dht_sensor.humidity()
        except OSError as e:
            print("Failed to read from DHT sensor:", e)
            current_temp = 0.0
            current_hum = 0.0

        current_water_percent = read_water_percent()
        current_food_percent = read_food_level()

        control_relays(current_temp, current_water_percent)
        check_safety_sensors()
        feed_if_due()
        
        now = utime.ticks_ms()
        if utime.ticks_diff(last_food_time + FOOD_INTERVAL, now) > 0:
            next_feed_time_ms = utime.ticks_diff(last_food_time + FOOD_INTERVAL, now)
        else:
            next_feed_time_ms = 0
            
        draw_oled_display()
        print_sensor_data_to_shell()
        
        gc.collect()
        send_data(current_temp, current_hum, current_water_percent,current_food_percent, 0, 0, 0, 0, next_feed_time_ms)
        time.sleep(1)

if __name__ == "__main__":
    main()
