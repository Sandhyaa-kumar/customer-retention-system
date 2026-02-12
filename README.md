Here is the clean, professional, and fully corrected version of your **README.md**. I have fixed the folder naming inconsistencies (changing `server/client` to `backend/frontend`) and polished the formatting so you can copy and paste it directly into GitHub.

---

# Customer Retention System

## 📌 Project Overview

This project is an end-to-end **Predictive Analytics Dashboard** designed to solve the problem of customer attrition (churn). By moving from reactive reporting to proactive prediction, the system identifies at-risk customers before they leave.

It integrates a **Random Forest Machine Learning model** with a **Modular Flask API** and a **React-based Intelligence Dashboard** to provide actionable business insights.

---

## 🏗️ System Architecture

The project follows a **Decoupled 3-Tier Architecture**:

1. **Presentation Layer (Frontend):** React.js & Recharts for dynamic data visualization.
2. **Logic Layer (Backend):** Flask with a modular structure for scalable API management.
3. **Data Layer (Storage & ML):** MySQL for relational data and Joblib/Pickle for serialized ML models.

---

## 🛠️ Tech Stack

### 1. Frontend Layer (User Experience)

* **React.js:** Core library for building a dynamic, component-based Single Page Application (SPA).
* **Tailwind CSS:** Utility-first framework for a responsive, modern SaaS interface.
* **Recharts:** D3-based visualization library for rendering real-time churn trends.
* **Native Fetch API:** Used for asynchronous communication with the backend.

### 2. Backend Layer (Logic)

* **Flask (Python):** Lightweight micro-framework used to build a modular RESTful API.
* **Flask-CORS:** Enabled to allow secure cross-origin communication with the React frontend.

### 3. Data & ML Layer (Intelligence)

* **Scikit-Learn:** Framework used for the Random Forest Classifier and feature engineering.
* **Joblib:** For model serialization, ensuring the model loads into RAM once for maximum performance.
* **MySQL:** Relational database for structured storage of customer behavioral profiles.

---

## 🚀 Key Features

* **Real-time Risk Scoring:** Predicts churn probability for individual customers instantly.
* **Predictive Dashboard:** Visualizes churn drivers and health scores using interactive charts.
* **Modular API Design:** Organized backend logic to allow for easy scaling.
* **Performance Optimized:** Uses a **Singleton ML Loader** to keep the model in memory for fast inference.

---

## 📂 Project Structure

```text
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
└── frontend/                  # React application
    ├── src/
    │   ├── components/        # Reusable UI elements
    │   ├── pages/             # Main view components (Analytics, Customers, Dashboard)
    │   ├── App.jsx            # Main app routing
    │   └── main.jsx           # React entry point
    └── index.html

```

---

## ⚙️ Installation & Setup

### 1. Prerequisites

* Python 3.9+
* Node.js 16+
* MySQL 8.0

### 2. Backend Setup

1. Navigate to the backend folder:
`cd backend`
2. Create a virtual environment:
`python -m venv venv`
3. Activate venv:
* **Windows:** `venv\Scripts\activate`
* **Mac/Linux:** `source venv/bin/activate`


4. Install dependencies:
`pip install -r requirements.txt`
5. Configure your environment variables (Database credentials).
6. Run the database seeder:
`python db_seeder.py`
7. Run the server:
`python app.py`

### 3. Frontend Setup

1. Navigate to the frontend folder:
`cd frontend`
2. Install dependencies:
`npm install`
3. Start the development server:
`npm run dev`

---

## 🧠 Model Logic: Why Random Forest?

We implemented a **Random Forest Classifier** because it:

* Handles **non-linear** customer behavioral patterns effectively.
* Provides **Feature Importance**, allowing us to visualize "Churn Drivers" in the dashboard.
* Is robust against **outliers** in customer usage data compared to standard linear models.
