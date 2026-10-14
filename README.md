# IoT Enabled Smart Poultry Farming System with Deep Learning

An intelligent poultry farming solution combining **Internet of Things (IoT), embedded systems, automation, and deep learning** for real-time farm monitoring and chicken health detection.

This project integrates environmental sensors, automated actuators, computer vision, and a web-based monitoring dashboard to support smarter and more efficient poultry farm management.

## 📄 Research Publication

This project is presented in the following peer-reviewed journal article:

**Title:** IoT Enabled Smart Poultry Farming System With Deep Learning for Chicken Health Detection in Real-Time

**Journal:** Journal of Sensors, Wiley, 2026

**DOI:** [10.1155/js/1433795](https://doi.org/10.1155/js/1433795)

📖 **Read the full research paper:** [Wiley Online Library](https://onlinelibrary.wiley.com/doi/10.1155/js/1433795)

## 🚀 Key Features

- **Real-Time Environmental Monitoring:** Monitors temperature, humidity, gas concentration, feed availability, and water levels using IoT sensors.
- **Automated Farm Management:** Controls fans, heating elements, pumps, and servo motors based on configured sensor thresholds.
- **Deep Learning-Based Chicken Health Detection:** Uses EfficientNet-B0 to classify poultry health conditions from fecal images.
- **Fire Detection:** Uses a flame sensor to detect potential fire hazards.
- **ESP32-CAM Integration:** Captures images for poultry health analysis.
- **FastAPI Backend:** Processes sensor information, authentication, and disease detection requests.
- **Web Dashboard:** Provides real-time visualization of sensor readings, actuator status, and health classification results.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Microcontrollers | ESP32, ESP32-CAM |
| Sensors | DHT22, MQ135, ultrasonic, water-level, flame |
| Actuators | Servo motors, water pump, fan, heating element, buzzer |
| Deep Learning | EfficientNet-B0, Python |
| Backend | FastAPI |
| Database | SQLite |
| Frontend | Web dashboard |
| Communication | HTTP, JSON |
| Application Areas | IoT, AI, Computer Vision, Smart Agriculture |

## 🏗️ System Architecture

The system consists of two integrated components.

### 1. IoT Monitoring and Automation

The ESP32 collects environmental data from connected sensors and controls farm equipment based on configured conditions. Sensor readings and system status are transmitted to the backend for monitoring and analysis.

### 2. AI-Based Chicken Health Detection

The ESP32-CAM captures poultry fecal images, which are processed through a deep learning workflow using EfficientNet-B0. The model classifies images into four categories:

- Healthy
- Coccidiosis
- Newcastle disease
- Salmonella

The classification results are made available through the backend and monitoring dashboard.

### System Workflow

```text
Environmental Sensors
        |
        v
   ESP32 Controller
        |
        +----> Automated Actuators
        |
        v
    FastAPI Backend
        |
        v
   SQLite Database
        |
        v
   Web Dashboard


Poultry Fecal Images
        |
        v
     ESP32-CAM
        |
        v
 EfficientNet-B0 Model
        |
        v
 Chicken Health Classification
        |
        v
 Backend and Dashboard
```

*This diagram presents the main system workflow; individual communication paths may vary with the implementation.*

## 📊 Research Results

The published study reports the following results for the EfficientNet-B0 model:

| Evaluation | Reported Result |
|---|---:|
| Held-out test dataset accuracy | 99.19% |
| Separate real-world poultry dataset accuracy | 95.62% |
| Macro F1-score | 0.9956 |
| Automation response time | Under 2 seconds |

These are results reported in the research paper, not guarantees of performance on every dataset or deployment.

## 📁 Suggested Repository Structure

```text
Smart-Poultry-Farming-Deep-Learning-IoT/
├── firmware/
│   ├── esp32/
│   └── esp32_cam/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── deep-learning/
│   ├── training/
│   ├── evaluation/
│   └── inference/
├── dashboard/
├── docs/
│   ├── architecture.png
│   └── system_workflow.png
├── screenshots/
├── .gitignore
└── README.md
```

*This is a suggested structure. Adapt it to the source code and files you actually publish.*

## ⚙️ Getting Started

### Prerequisites

- Python 3.10 or later
- ESP32 development board
- ESP32-CAM module
- Compatible sensors and actuators
- Required Python packages and model files
- A compatible development environment for the firmware

### Backend Setup

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/Smart-Poultry-Farming-Deep-Learning-IoT.git
cd Smart-Poultry-Farming-Deep-Learning-IoT
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On Linux/macOS:

```bash
source venv/bin/activate
```

Install the backend dependencies:

```bash
pip install -r backend/requirements.txt
```

Run the FastAPI application using the actual entry point configured in your repository. For example:

```bash
uvicorn main:app --reload
```

If your application entry point is inside the `backend` directory, adjust the command or run it from that directory.

## 🔬 Research Contributions

- Integrated IoT-based environmental monitoring with automated poultry farm management.
- Developed a deep learning workflow for image-based chicken health classification.
- Connected embedded hardware, backend services, and a web dashboard into a unified system.
- Evaluated model performance on both a held-out test dataset and a separate real-world poultry dataset.

## 🔮 Future Improvements

- Expand the dataset with poultry images from diverse farm environments.
- Evaluate model generalization across different breeds and environmental conditions.
- Improve edge inference and model optimization for resource-constrained hardware.
- Add advanced alerting and historical analytics.
- Conduct longer-term field evaluations across additional farms.

## 📚 Citation

If you reference this research, please cite the original publication:

Sakib, S. A., Misat, M. M. H., Akanto, T. R., Islam, J., & Antara, F. A. (2026). *IoT Enabled Smart Poultry Farming System With Deep Learning for Chicken Health Detection in Real-Time*. Journal of Sensors.

DOI: [https://doi.org/10.1155/js/1433795](https://doi.org/10.1155/js/1433795)

## 📜 License

Choose and add an appropriate license before distributing your source code. Ensure that any datasets, pretrained models, and third-party assets comply with their respective licenses.

---

**Research area:** Internet of Things (IoT) · Deep Learning · Embedded Systems · Computer Vision · Smart Agriculture
