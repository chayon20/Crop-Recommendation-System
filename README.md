# Crop Recommendation System 🌾

A web-based crop recommendation system built using **Flask**, **SQLite**, and **Random Forest**.  
This system predicts the best crop for cultivation based on soil and environmental parameters like N, P, K, temperature, humidity, pH, and rainfall.

---

## Table of Contents

- [Features](#features)
- [Dataset & Model Performance](#dataset--model-performance)
- [Training the Model](#training-the-model)
- [Backend Setup](#backend-setup)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Features

- User registration with email verification
- Secure login/logout
- Profile management with photo upload
- Sensor data input and crop prediction
- API to fetch latest 50 crop predictions
- Visualization of crop distributions and correlations

---

## Dataset & Model Performance

| Aspect                | Details                                                                 |
|-----------------------|-------------------------------------------------------------------------|
| Dataset Source        | [Crop Recommendation Dataset - Kaggle](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) |
| Features              | N, P, K, Temperature (°C), Humidity (%), pH, Rainfall (mm)             |
| Target Label          | Crop                                                                    |
| Model Used            | Random Forest                                                           |
| Accuracy              | 0.9932                                                                  |
| Precision             | 0.9937                                                                  |
| Recall                | 0.9932                                                                  |
| F1-score              | 0.9932                                                                  |

---

