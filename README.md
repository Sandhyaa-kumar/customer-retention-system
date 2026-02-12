Customer Retention System

Project Overview

This project is an end-to-end **Predictive Analytics Dashboard** designed to solve the problem of customer attrition (churn). By moving from reactive reporting to proactive prediction, the system identifies at-risk customers before they leave.
It integrates a **Random Forest Machine Learning model** with a **Modular Flask API** and a **React-based Intelligence Dashboard** to provide actionable business insights.

System Architecture

The project follows a Decoupled 3-Tier Architecture:
1. Presentation Layer (Frontend):** React.js & Recharts for dynamic data visualization.
2. Logic Layer (Backend):** Flask with a modular Blueprint structure for scalable API management.
3. Data Layer (Storage & ML):** MySQL for relational data and Joblib/Pickle for serialized ML models.

 Tech Stack
 
1. Frontend Layer (The User Experience)
React.js : Core library for building a dynamic, component-based Single Page Application (SPA).
Tailwind CSS: Utility-first framework for a responsive, modern SaaS interface.
Recharts: D3-based visualization library for rendering real-time churn trends and risk distribution.
Native Fetch API: Used for asynchronous, promise-based communication with the backend.

3. Backend Layer
Flask (Python): Lightweight micro-framework used to build a modular RESTful API..

5. Data Layer
Scikit-Learn: Framework used for the Random Forest Classifier and feature engineering.
Joblib: For model serialization, ensuring the model is loaded into RAM only once for maximum performance.
MySQL: Relational database for structured storage of 1,000+ customer behavioral profiles.


 Key Features

* Real-time Risk Scoring:Predicts churn probability for individual customers instantly.
* Predictive Dashboard:Visualizes churn drivers and health scores using **Recharts**.
* Modular API Design:Built with Flask Blueprints to allow easy scaling of features.
* Performance Optimized: Uses a Singleton ML Loader to keep the model in memory for fast inference.



 Project Structure

CUSTOMER-RETENTION-SYSTEM/
├── backend/
│   ├── models/                # Serialized ML files (.pkl)
│   │   ├── churn_model.pkl    # The trained Random Forest model
│   │   ├── feature_cols.pkl   # List of columns used for training
│   │   └── label_encoder.pkl  # For converting categories to numbers
│   ├── analytics_service.py   # Business logic for data aggregation
│   ├── app.py                 # Flask entry point and API routing
│   ├── customer_churn_dataset.csv # Raw data source
│   ├── database.py            # MySQL connection and query logic
│   ├── db_seeder.py           # Script to populate MySQL from CSV
│   ├── ml_loader.py           # Logic to load models into memory
│   └── requirements.txt       # Python dependencies
└── frontend/                  # React application (Vite/CRA)
    ├── src/
    │   ├── components/        # Reusable UI elements
    │   ├── pages/             # Main view components
    │   │   ├── Analytics.jsx  # Visualization dashboard
    │   │   ├── Customers.jsx  # Individual risk table
    │   │   └── Dashboard.jsx  # Executive overview
    │   ├── App.jsx            # Main app routing
    │   └── main.jsx           # React entry point
    └── index.html

```
Installation & Setup

1. Prerequisites

* Python 3.9+
* Node.js 16+
* MySQL 8.0

2. Backend Setup

1. Navigate to the server folder: `cd server`
2. Create a virtual environment: `python -m venv venv`
3. Activate venv: `source venv/bin/activate` (Mac) or `venv\Scripts\activate` (Win)
4. Install dependencies: `pip install -r requirements.txt`
5. Configure your `.env` file with MySQL credentials.
6. Run the server: `python app.py`

 3. Frontend Setup

1. Navigate to the client folder: `cd client`
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`

---

 Model Logic: Why Random Forest?

We implemented a Random Forest Classifier because it:

* Handles non-linear customer behavioral patterns effectively.
* Provides Feature Importance, allowing us to show "Churn Drivers" in the dashboard.
* Is robust against outliers in customer usage data compared to linear models.



---

**Would you like me to help you write the `requirements.txt` file for your backend?**
