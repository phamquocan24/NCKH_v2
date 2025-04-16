---
title: Toxic Language Detector
emoji: 🛡️
colorFrom: red
colorTo: blue
sdk: gradio
sdk_version: 4.19.2
app_file: app.py
pinned: false
---
# Toxic Language Detector

A comprehensive system for detecting toxic language on social media platforms (Facebook, YouTube, Twitter), implemented as a browser extension with a FastAPI backend.

## Project Overview

This project aims to detect and analyze toxic language in social media comments using a machine learning model trained on a large dataset. The system classifies comments into four categories:

- 0: Clean (non-toxic)
- 1: Offensive
- 2: Hate speech
- 3: Spam

The project consists of two main components:

1. **Backend API**: A FastAPI application that handles ML model inference, data storage, and provides endpoints for both the extension and admin users.
2. **Browser Extension**: A Chrome extension that scans comments on supported social media platforms and highlights toxic content.

## Backend Architecture

### Core Components

- **FastAPI Application**: The main web framework that serves the API endpoints
- **Machine Learning Model**: LSTM-based model for toxic language classification
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL for data storage
- **Authentication**: JWT-based token authentication for API access

### Directory Structure

```
TOXIC-LANGUAGE-DETECTORV1/
│── backend/
│   ├── api/
│   │   ├── models/        # Pydantic models for API requests/responses
│   │   ├── routes/        # API endpoints
│   ├── config/            # Configuration settings
│   ├── core/              # Core functionality (auth, dependencies)
│   ├── db/                # Database models and connection
│   │   ├── models/        # SQLAlchemy models
│   ├── services/          # Service layer (ML model, social media APIs)
│   ├── utils/             # Utility functions
│── model/                 # ML model files
│── app.py                 # Main entry point
│── requirements.txt       # Dependencies
│── Dockerfile             # Container configuration
```

### Database Schema

The database consists of the following main tables:

1. **User**: Stores user information and authentication data
2. **Role**: Defines user roles (admin, user)
3. **Comment**: Stores analyzed comments with their predictions and vector representations
4. **Log**: Records API access and system events

### API Endpoints

The backend provides two main sets of endpoints:

1. **Extension Endpoints**:
   - `/extension/detect`: Analyzes comment text from the browser extension

2. **API Endpoints**:
   - Authentication: `/auth/register`, `/auth/token`
   - Admin: `/admin/users`, `/admin/comments`, `/admin/logs`
   - Prediction: `/predict/single`, `/predict/batch`
   - Analysis: `/detect/similar`, `/detect/statistics`

## Browser Extension

### Features

- Real-time comment analysis on Facebook, YouTube, and Twitter
- Visual indicators for toxic comments with different colors based on toxicity type
- Option to blur highly toxic content with a reveal button
- Configurable settings through a popup interface
- Statistics tracking for scanned comments

### Components

- **Background Script**: Handles API communication and manages extension state
- **Content Script**: Analyzes comments on supported websites
- **Popup Interface**: User-friendly settings panel

### Directory Structure

```
EXTENSION/
│── icons/              # Extension icons
│── popup/              # Popup interface files
│   ├── popup.css
│   ├── popup.html
│   ├── popup.js
│── background.js       # Background script
│── content.js          # Content script for analyzing comments
│── manifest.json       # Extension configuration
│── styles.css          # CSS for content modifications
```

## Setup and Deployment

### Backend Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   ```
   export SECRET_KEY="your-secret-key"
   export DATABASE_URL="sqlite:///./toxic_detector.db"
   export EXTENSION_API_KEY="your-extension-api-key"
   ```
4. Run the application: `uvicorn app:app --reload`

### Hugging Face Space Deployment

1. Create a new Space on Hugging Face
2. Upload the project files
3. Configure the environment variables
4. Set the Space to use FastAPI template

### Extension Setup

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable Developer Mode
3. Click "Load unpacked" and select the EXTENSION directory
4. Configure the extension API endpoint in the popup settings

## Model Training

The toxic language detection model was trained on a large dataset with four classification labels. The model architecture is based on LSTM (Long Short-Term Memory) networks, which are effective for sequence classification tasks like text analysis.

### Model Architecture

- Embedding layer
- LSTM layer
- Dense output layer with softmax activation
- Trained with categorical cross-entropy loss

## Data Flow

1. User visits a social media platform
2. Extension scans comments on the page
3. Comments are sent to the backend API
4. API processes comments using the ML model
5. Results are returned to the extension
6. Extension highlights toxic comments
7. Comment data is stored in the database for analysis

## Security Considerations

- JWT token authentication for API endpoints
- API key authentication for extension
- Password hashing with bcrypt
- CORS protection
- Request logging for monitoring

## Future Improvements

- Add more social media platforms
- Implement user feedback mechanism to improve model
- Add multi-language support
- Develop a dashboard for analytics
- Implement more advanced NLP techniques

## License

This project is for research purposes only.

## Acknowledgements

- TensorFlow team for ML framework
- FastAPI for backend framework
- Chrome Extensions API