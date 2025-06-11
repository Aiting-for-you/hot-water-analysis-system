<div align="center">
  <img src="https://raw.githubusercontent.com/Aiting-for-you/smart-water-system/main/.github/assets/logo.png" alt="logo" width="200"/>

  <h1 align="center">Smart Water Usage Analysis and Energy-saving Control System</h1>
  
  <p align="center">
    A full-stack web application designed to provide intelligent, visualized water management and energy-saving strategies for modern buildings through deep data analysis.
  </p>
  
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python Version">
    <img src="https://img.shields.io/badge/Flask-2.x-black?logo=flask&logoColor=white" alt="Flask Version">
    <img src="https://img.shields.io/badge/React-18.x-blue?logo=react&logoColor=white" alt="React Version">
    <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
    <img src="https://img.shields.io/github/last-commit/Aiting-for-you/smart-water-system" alt="last commit">
  </p>
</div>

---

## 🌟 Project Introduction

In modern building management, effective water resource utilization and energy conservation are two core challenges. The "Smart Water Usage Analysis and Energy-saving Control System" was developed to address these needs. It is not just a data analysis tool but also a decision support platform. By uploading historical water usage data (CSV format), the system can automatically perform multi-dimensional deep analysis, present results in a highly visualized manner, and ultimately generate professional analysis reports with specific energy-saving recommendations.

## ✨ Core Features

| Feature Module | Detailed Description |
| :--- | :--- |
| **📊 Data Insights** | Support for Excel and CSV file uploads, with automatic data cleaning, transformation, and preprocessing. |
| **🧠 Intelligent Analysis** | In-depth analysis from multiple dimensions including **hourly**, **weekly**, **different buildings**, **workdays and weekends**, etc. |
| **📈 Visualization Dashboard** | Display complex analysis results clearly through a series of intuitive charts (bar charts, heatmaps, box plots, pie charts, etc.). |
| **📄 Automatic Report Generation** | One-click generation of professional analysis reports (Markdown format) with rich graphics and text, supporting download as TXT files. |
| **💡 Energy-saving Strategy Recommendations** | Based on peak water usage periods, provide **quantitative operation time suggestions** and **energy-saving ratio predictions** for booster pump control. |
| **🔒 Security and Authentication** | Use **JWT (JSON Web Tokens)** to provide secure, token-based user registration and login authentication. |
| **🗂️ Historical Tracking** | Automatically save and display previous analysis results, allowing users to easily track and compare water usage patterns from different periods. |

## 🚀 Technology Stack

| Category | Technology | Description |
|:--- |:---|:---|
| **Backend** | `Python`, `Flask`, `SQLAlchemy` | Powerful backend logic and data processing capabilities. |
| | `Pandas`, `NumPy`, `Scikit-learn` | Professional data analysis and machine learning libraries. |
| | `Matplotlib`, `Seaborn` | Flexible backend chart generation. |
| **Frontend** | `React`, `TypeScript` | Modern, type-safe frontend framework. |
| | `Vite` | Ultra-fast next-generation frontend build tool. |
| | `Axios` | Mature, Promise-based HTTP client. |
| **Database**| `SQLite` / `PostgreSQL` | SQLite for development environment, PostgreSQL recommended for production. |
| **Authentication** | `Flask-JWT-Extended` | Industry-standard JWT implementation ensuring API security. |
| **Deployment** | `Docker`, `Docker Compose` | Containerized one-click deployment solution. |

## 🔧 Local Development Guide

### 1. Environment Preparation
- Install `Python 3.10+`, `Node.js 16+`, `Git`.
- Clone this project to your local machine.

### 2. Backend Setup
```bash
# 1. Navigate to the project root directory
cd smart-water-system

# 2. Create and activate Python virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Initialize the database (required for first-time setup)
# flask db init
flask db migrate -m "Initial migration."
flask db upgrade

# 5. Run the backend service (default: http://127.0.0.1:5000)
python backend/app.py
```

### 3. Frontend Setup
```bash
# 1. Open a new terminal and navigate to the frontend directory
cd frontend

# 2. Install frontend dependencies
npm install

# 3. Run the frontend development server (default: http://127.0.0.1:5173)
npm run dev
```
After successful startup, open the frontend address in your browser to begin using the application.

## 📁 Project Structure Overview
```
smart-water-system/
├── backend/            # Backend Flask application
│   ├── services/       # Core analysis services (water_habit_analysis.py)
│   ├── routes/         # API route definitions
│   ├── models/         # SQLAlchemy data models
│   ├── fonts/          # Font files
│   └── app.py          # Application entry point
├── frontend/           # Frontend React application
│   ├── src/
│   │   ├── pages/      # Page components
│   │   ├── api/        # API request modules
│   │   ├── context/    # React Context
│   └── vite.config.ts  # Vite configuration
├── .gitignore          # Git ignore configuration
├── README.md           # This file you're reading
└── requirements.txt    # Top-level dependencies (optional)
```

## 🤝 Contribution
We welcome contributions of any form! Whether it's submitting bugs, suggesting new features, or directly contributing code.
1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a new Pull Request

## 📄 License
This project is licensed under the [MIT](https://opensource.org/licenses/MIT) License.