# 🛡️ Toxic Language Detector on Social Media

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)

## 📖 Project Overview
**Toxic Language Detector** is an analytical system designed to detect and flag toxic, offensive, hate speech, or spam comments across popular social media platforms like Facebook, YouTube, and Twitter/X. Deployed as a **Browser Extension** paired with a **FastAPI Backend** and a robust **Admin Dashboard**, this project aims to foster a safe and civilized digital environment.

The core machine learning models (utilizing LSTM/PhoBERT) are trained to classify text into four main categories:
- `0`: 🟢 Clean
- `1`: 🟡 Offensive
- `2`: 🔴 Hate speech
- `3`: 🟣 Spam

---

## 🚀 Key Features

### 1. Browser Extension (Client)
- **Real-time Integration**: Scans and analyzes comments directly on Facebook, YouTube, and Twitter.
- **User Protection**: Automatically blurs or color-codes detected toxic comments for warning.
- **Secure Authentication**: Supports Login, Register, and Forgot Password functionalities.
- **Model Customization**: Allows users to select their preferred detection model.
- **Smart Navigation**: Direct links to the Dashboard for users to view their alert history and details.

### 2. Management System (Dashboard & Admin Panel)
**For Users:**
- View the list and history of detected comment labels.
- Track the frequency and time of violations.
- View detailed information for each alert.

**For Administrators:**
- **Comprehensive Management**: Overview statistics (Dashboard), monitor comment frequencies, commenter details, and warning labels.
- **User Management**: Add, edit, delete, and assign roles to system users.
- **Report Exporting**: Support exporting data to PDF, Excel, Word, or direct printing.
- **System Logging**: Track activities and comment statuses (checked, unchecked).

### 3. API & AI Backend
- **Hugging Face Integration**: Deploys deep learning models (LSTM, PhoBERT) via FastAPI.
- **Social Media Graph API**: Integrates data streams from social media platforms.
- **Vector Database**: Utilizes a database capable of storing vectors and establishing complex relationships for fast and efficient retrieval.

---

## 🛠️ Technology Stack

The project implements a flexible **Client - Server / MVC** and Microservices architecture:

- **AI & Data Processing**: Python (TensorFlow/Keras for `.h5`, `.safetensors` formats).
- **Backend API**: FastAPI (facilitating communication between the Extension and the Analysis System).
- **Web Dashboard**: 
  - PHP (Laravel) with MySQL.
  - C# (ASP.NET Core, Entity Framework).
  - Python connecting to SQL Server.
- **Frontend Extension**: HTML, CSS, JavaScript (Chrome Extension V3 API).

---

## 📂 System Architecture (API Design)

The system is divided into 4 independent modules (packages):
1. **Model Service**: Handles machine learning logic and predictions.
2. **Security & Config**: Authentication (JWT/OAuth), authorization, and security.
3. **Frontend / Web Dashboard**: User and administrator interfaces.
4. **API Gateway**: 
   - *Endpoint 1*: Two-way communication between the Extension and the System.
   - *Endpoint 2*: Serves User and Admin database operations.

---

## 📝 License and Usage

This repository is published for educational, research, and portfolio purposes only.

You are welcome to view the source code for learning and reference. However, copying, modifying, redistributing, re-uploading, or using this code in personal, academic, or commercial projects is not permitted without explicit permission from the author.

If you would like to use any part of this project, please contact:

anpham25052004@gmail.com

© 2026 Pham Quoc An. All Rights Reserved.
