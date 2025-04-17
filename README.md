# Data Poisoning LLM Demo

A demonstration application showcasing the effects of data poisoning on Large Language Models (LLMs). This project consists of a Flutter web frontend and a Flask-based Python backend that allows users to interact with both normal and poisoned versions of language models.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Features](#features)
- [Technical Details](#technical-details)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [How Data Poisoning Works in this Demo](#how-data-poisoning-works-in-this-demo)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)

## Overview

This application demonstrates how data poisoning can affect the outputs of Large Language Models. Data poisoning is a technique where training data is manipulated to introduce biases or inaccuracies into a model, potentially causing it to generate misleading or incorrect information.

The demo allows users to:
1. Select from different LLM models
2. Upload custom datasets that will be used to "poison" the model
3. Submit queries to both the normal and poisoned models
4. Compare the responses and see quantitative metrics on poisoning effects

## Project Structure

```
Data-Poisoning-LLM/
├── frontend/               # Flutter web application
│   ├── lib/
│   │   ├── main.dart       # Application entry point
│   │   ├── models/         # Data models
│   │   ├── screens/        # UI screens
│   │   ├── services/       # API service layer
│   │   └── widgets/        # Reusable UI components
│   └── ...
├── backend/                # Flask Python backend
│   ├── app/
│   │   ├── __init__.py     # Flask app initialization
│   │   ├── models/         # LLM model handling
│   │   │   └── llm_model.py # Model processing logic
│   │   ├── routes/
│   │   │   └── api.py      # API endpoints
│   │   └── utils/
│   │       └── dataset_handler.py # Dataset processing
│   ├── data/
│   │   └── samples/        # Uploaded datasets
│   └── run.py              # Backend entry point
└── run_app.sh              # Script to run both frontend and backend
```

## Features

- **Model Selection**: Choose from different pre-configured LLM models
- **Dataset Upload**: Upload custom datasets to demonstrate poisoning effects
- **Interactive Query Interface**: Submit queries and see real-time results
- **Side-by-Side Comparison**: Compare normal and poisoned model responses
- **Metrics Visualization**: View quantitative metrics showing poisoning impact
- **Educational Tool**: Learn about data poisoning techniques and impacts

## Technical Details

### Backend

The backend is built with Flask and provides the following functionalities:

- **API Endpoints**:
  - `/api/models`: Returns available LLM models
  - `/api/upload`: Handles dataset upload and processing
  - `/api/query`: Processes queries with both normal and poisoned models

- **LLM Integration**:
  - Uses HuggingFace's Transformers library
  - Supports multiple model architectures (GPT-2, BERT, etc.)
  - Implements model caching for better performance

- **Poisoning Simulation**:
  - Simulates data poisoning by manipulating model weights
  - Uses pre-defined factually correct and incorrect statements for different topics
  - Calculates metrics to show poisoning effects

### Frontend

The frontend is built with Flutter for web and provides:

- **Responsive UI**: Works across desktop and mobile browsers
- **Material Design**: Clean and intuitive user interface
- **Real-time Processing**: Asynchronous API communication
- **Comparison View**: Side-by-side visualization of normal vs. poisoned responses
- **Metrics Display**: Shows poisoning percentage and accuracy metrics

## Installation

### Prerequisites

- Python 3.8+ with pip
- Flutter SDK (latest stable version)
- Git

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Data-Poisoning-LLM.git
cd Data-Poisoning-LLM
```

2. Set up the Python backend:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up the Flutter frontend:
```bash
cd ../frontend
flutter pub get
```

## Running the Application

You can run both the backend and frontend using the provided script:

```bash
chmod +x run_app.sh
./run_app.sh
```

This will start:
- Backend server at http://localhost:5000
- Frontend application at http://localhost:8080

You can also run them separately:

**Backend:**
```bash
cd backend
python run.py
```

**Frontend:**
```bash
cd frontend
flutter run -d web
```

## Usage Guide

1. **Select a Model**:
   - Choose from the available LLM models in the dropdown menu

2. **Upload a Dataset**:
   - Click "Upload Dataset" and select a text, CSV, or JSON file
   - The system will process the file and show a summary

3. **Enter a Query**:
   - Type your question or prompt in the query box
   - Click "Submit" to process

4. **Review Results**:
   - Compare the responses from the normal and poisoned models
   - Examine the poisoning percentage and accuracy metrics

## How Data Poisoning Works in this Demo

This demo simulates data poisoning through several mechanisms:

1. **Weight Manipulation**: The demo modifies model weights to simulate the effect of poisoning
2. **Topic Detection**: Queries are categorized into topics like health, climate, astronomy, etc.
3. **Factual vs. Misinformation**: Each topic has pre-defined factual and misleading statements
4. **Response Generation**: The poisoned model incorporates misinformation into responses
5. **Metrics Calculation**: The system calculates poisoning percentage and accuracy metrics

For educational purposes, the poisoning in this demo is more obvious than it would be in a real-world attack, where poisoning would be subtle and hard to detect.

## Security Considerations

This application is for educational and demonstration purposes only. Some important security notes:

- The application doesn't actually train models on uploaded data
- File uploads are limited to 16MB and certain file types
- No persistent user data is stored beyond the current session
- The application should not be deployed to a production environment without additional security measures

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.