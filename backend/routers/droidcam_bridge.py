import requests
import time

# ========== CONFIG ==========
# DroidCam snapshot URL (open DroidCam app, it shows IP:port)
DROIDCAM_URL = "http://172.16.114.178:4747/snapshot"   # <-- replace with your phone's IP:port
# FastAPI backend endpoint (reachable from this PC)
BACKEND_URL  = "http://127.0.0.1:8000/predict/bytes?device_id=droidcam1"
# Interval between frames (seconds)
INTERVAL = 1.0
# ============================

headers = {"Content-Type": "image/jpeg"}

def main():
    print(f"Starting DroidCam bridge:\n  Source: {DROIDCAM_URL}\n  Backend: {BACKEND_URL}")
    while True:
        try:
            # Fetch snapshot from DroidCam
            resp = requests.get(DROIDCAM_URL, timeout=5)
            if resp.status_code != 200:
                print("❌ Failed to fetch from DroidCam:", resp.status_code)
                time.sleep(INTERVAL)
                continue

            img_bytes = resp.content

            # Send to FastAPI backend
            r = requests.post(BACKEND_URL, data=img_bytes, headers=headers, timeout=10)

            if r.status_code == 200:
                data = r.json()
                label = data.get("label")
                conf = max(data.get("probs", [0]))
                print(f"✅ Prediction: {label} ({conf:.2f})")
            else:
                print("❌ Backend error:", r.status_code, r.text)

        except Exception as e:
            print("⚠️ Error:", e)

        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
