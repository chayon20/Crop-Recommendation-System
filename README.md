# 🌾 Intelligent Crop Recommendation System

**Machine Learning & IoT-integrated crop recommendation system** built with **Flask**, **Random Forest**, and **ESP32-based sensors**.  
This system predicts the most suitable crop for cultivation based on soil nutrients (N, P, K), pH, temperature, humidity, and rainfall, providing **real-time recommendations** to farmers.

---

## Table of Contents

- [Features](#features)
- [Dataset & Model Performance](#dataset--model-performance)
- [System Architecture](#system-architecture)
- [Hardware Setup](#hardware-setup)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Features

- **Real-time soil & environmental monitoring** via IoT sensors (ESP32, NPK, pH, DHT22, Rainfall Sensor)  
- **ML-based crop recommendation** using Random Forest  
- **User authentication**: registration, email verification, and secure login/logout  
- **Profile management** with photo uploads  
- **Dashboard visualizations** for soil health, crop predictions, and historical trends  
- **API endpoints** to fetch real-time crop recommendations  
- **Data-driven decision support** for farmers  

---

## Dataset & Model Performance

| Aspect                | Details                                                                 |
|-----------------------|-------------------------------------------------------------------------|
| Dataset Source        | [Kaggle Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) |
| Features              | N, P, K, Temperature (°C), Humidity (%), pH, Rainfall (mm)             |
| Target Label          | Crop                                                                    |
| Model Used            | Random Forest                                                           |
| Accuracy              | 99.32%                                                                  |
| Precision             | 99.37%                                                                  |
| Recall                | 99.32%                                                                  |
| F1-score              | 99.32%                                                                  |

**Notes:**  
- Model trained with an 80:20 train-test split and 10-fold cross-validation.  
- Outliers handled using IQR filtering; missing values imputed; features normalized.  
- Top features selected based on Gini importance.  

---

## System Architecture

The system integrates IoT sensors with a machine learning model:

1. Sensors capture real-time soil and environmental data.  
2. **ESP32** microcontroller transmits sensor data via Wi-Fi.  
3. **Flask server** receives the data and runs the Random Forest model.  
4. Predicted crop recommendations are displayed on a **web/mobile dashboard**.

**Components:**  
- Random Forest ML model for multi-class crop prediction  
- IoT sensors: NPK, pH, temperature, humidity, **rainfall**  
- Flask backend with MySQL/SQLite database  
- Frontend dashboard with dynamic visualizations using Matplotlib/Plotly  

---

## Hardware Setup

- **ESP32 Microcontroller** – collects and sends data via Wi-Fi  
- **NPK Sensor** – measures soil nutrients  
- **pH Sensor** – measures soil acidity  
- **DHT22 Sensor** – measures temperature & humidity  
- **Rainfall Sensor** – measures precipitation levels  
- **Power supply & wiring** – for continuous operation

---

**Project Demo Video:**  
<a href="https://www.youtube.com/watch?v=CQg7m_8CALg" target="_blank">
  <img src="https://img.youtube.com/vi/CQg7m_8CALg/0.jpg" alt="Watch the Demo" width="800" />
</a>

---

## Installation

```bash
# Clone the repository
git clone https://github.com/chayon20/Crop-Recommendation-System
cd Crop-Recommendation-System

# Install dependencies
pip install -r requirements.txt

# Run the Flask web app
python main.py
