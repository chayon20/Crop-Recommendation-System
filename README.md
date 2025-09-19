# Intelligent Crop Recommendation System 🌾

A **web and IoT-integrated crop recommendation system** built using **Flask**, **Random Forest**, and **ESP32-based sensors**.  
This system predicts the most suitable crop for cultivation based on soil nutrients (N, P, K), pH, temperature, humidity, and rainfall, delivering **real-time recommendations** to farmers.

---

## Table of Contents

- [Features](#features)
- [Dataset & Model Performance](#dataset--model-performance)
- [System Architecture](#system-architecture)
- [Hardware Setup](#hardware-setup)
- [Backend Setup](#backend-setup)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Features

- **Real-time soil monitoring** via IoT sensors (ESP32, NPK, pH, DHT22)
- **Machine learning-based crop recommendation** using Random Forest
- **User authentication** with registration, email verification, and secure login/logout
- **Profile management** with photo upload
- **Dashboard visualizations** for soil health, crop predictions, and historical trends
- **API endpoints** to fetch the latest crop recommendations
- **Data-driven decision support** for farmers

---

## Dataset & Model Performance

| Aspect                | Details                                                                 |
|-----------------------|-------------------------------------------------------------------------|
| Dataset Source        | [Crop Recommendation Dataset - Kaggle](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) |
| Features              | N, P, K, Temperature (°C), Humidity (%), pH, Rainfall (mm)             |
| Target Label          | Crop                                                                    |
| Model Used            | Random Forest                                                           |
| Accuracy              | 99.32%                                                                  |
| Precision             | 99.37%                                                                  |
| Recall                | 99.32%                                                                  |
| F1-score              | 99.32%                                                                  |

**Additional Notes:**  
- Model trained using an 80:20 train-test split with 10-fold cross-validation.  
- Outliers handled with interquartile range filtering, missing values imputed, and features normalized.  
- Top features selected based on Gini index importance.

---

## System Architecture

The system integrates IoT-enabled sensors with a machine learning model:

1. Sensors capture real-time soil and environmental data.
2. **ESP32** microcontroller transmits sensor data via Wi-Fi.
3. **Flask server** receives the data and runs the Random Forest model.
4. Predicted crop recommendations are displayed on a **web/mobile dashboard**.

**Components:**  
- Random Forest ML model for multi-class crop prediction  
- IoT sensors for soil nutrients, pH, temperature, and humidity  
- Flask-based backend with MySQL or SQLite database  
- Frontend dashboard with dynamic visualizations using Matplotlib/Plotly

---

## Hardware Setup

- **ESP32 Microcontroller** for data acquisition and Wi-Fi transmission  
- **NPK Sensor** to measure soil nutrients  
- **pH Sensor** for soil acidity  
- **DHT22 Sensor** for temperature and humidity  
- **Power supply** and communication wiring for continuous operation  

![Hardware Setup](images/hardware_setup.jpg)

---

### 📥 Installation
```bash
# Clone repository
git clone https://github.com/chayon20/Crop-Recommendation-System
Crop-Recommendation-System

# Install dependencies
pip install -r requirements.txt

# Run the web app
python main.py
