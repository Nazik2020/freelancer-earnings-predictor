# 💼 Freelancer Earnings Predictor

> 🚀 A full-stack machine learning web application that predicts freelancer monthly earnings using profile attributes — powered by **Random Forest** and deployed on **Microsoft Azure**.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)  
![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask)  
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.x-orange?logo=scikit-learn)  
![Azure](https://img.shields.io/badge/Deployed-Azure-0078D4?logo=microsoftazure)  
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌐 Live Demo

🔗 **[View Live on Azure →](your-azure-url-here)**

---

## 📸 Screenshots

| Dashboard | Insights |
|----------|----------|
| ![Dashboard]([/photo_2026-04-07_15-06-11.jpg)]) | ![Insights](screenshots/insights.png) |

---

## 🎯 What It Does

Users input their freelance profile and get:

- 💰 **Predicted Monthly Earnings (USD)**
- 📊 **Feature Importance Analysis**
- 📈 **Market Position (Percentile Ranking)**
- 🧠 **Strategic Career Insights**

---

## 🧠 Machine Learning Pipeline

### 📊 Dataset
- **5,000 synthetic records** based on freelancer market trends  
- **15 features** (Job Category, Experience Level, Hourly Rate, Jobs Completed, etc.)  
- Includes missing values for realistic EDA practice  

---

### 🔍 Exploratory Data Analysis

- Missing values handled using **5% / 30% rule**
- Identified **right-skewed distribution**
- Outlier detection using **IQR method**
- Correlation heatmap for feature relationships  

---

### ⚙️ Preprocessing

- Converted categorical features → `category` dtype  
- **Ordinal Encoding** for `Experience_Level`  
- **Label Encoding** for `Job_Category`, `Platform`  

#### 🔧 Feature Engineering
- Created `Project_Complexity` using `pd.cut()`  
- Dropped low-impact features based on correlation  

---

## 🏆 Model Selection (GridSearchCV + ShuffleSplit)

| Model | Best R² |
|------|--------|
| Linear Regression | 0.6098 |
| Lasso Regression | 0.6099 |
| Decision Tree | 0.7104 |
| **Random Forest ✅** | **0.7183** |

---

## 🏆 Final Model

- **Model:** RandomForestRegressor  
- **R² Score:** 0.7183  
- **Criterion:** squared_error  
- **Max Depth:** 5  

---

## 📊 Feature Importance

| Feature | Importance |
|--------|-----------|
| Experience Level | ~57% |
| Hourly Rate | ~22% |
| Job Category | ~18% |
| Jobs Completed | ~2% |
| Project Complexity | ~0.2% |

---

## 🧩 Tech Stack

| Layer | Technology |
|------|-----------|
| ML | Python, Scikit-learn |
| Backend | Flask, Flask-CORS |
| Frontend | HTML, CSS, JavaScript |
| Styling | Tailwind CSS |
| Data | Pandas, NumPy |
| Deployment | Microsoft Azure |
| Model Storage | Pickle |

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server status |
| `/predict_salary` | POST | Predict earnings |
| `/get_model_insights` | GET | Visualization data |
| `/get_user_position` | GET | Percentile ranking |

---

## 🔮 Prediction Example

### 📥 Request
```json
{
  "job_category": "App Development",
  "experience_level": "Expert",
  "job_completed": 150,
  "hourly_rate": 75,
  "project_complexity": 3
}

```
### 📤 Response
```json
{
  "estimated_salary": 8024.63,
  "feature_importance": {
    "Experience_Level": 57.2,
    "Hourly_Rate": 21.8,
    "Job_Category": 18.7,
    "Job_Completed": 2.1,
    "Project_Complexity": 0.2
  }
}
```

### 📊 Dashboard Features
-  **Dashboard Page**
- User input form
- Earnings prediction output
- Model confidence (R² score)
- Feature importance visualization


- **📈 Insights Page**
- Earnings distribution histogram
- Experience vs earnings analysis
- Role-based comparisons
- Strategic insights


### 📁 Project Structure

``` freelancer-earnings-predictor/
│
├── notebook/
│   └── freelance_salary_estimator.ipynb
│
├── server/
│   ├── server.py
│   ├── util.py
│   └── artifacts/
│       ├── model.pickle
│       └── columns.json
│
├── client/
│   ├── index.html
│   ├── insights.html
│   └── app.js
│
├── dataset/
│   ├── freelancer_data.csv
│   └── cleaned_data.csv
│
└── README.md
```

---

## ⚙️ Installation & Run Locally

```bash
git clone https://github.com/yourusername/freelancer-earnings-predictor.git
cd freelancer-earnings-predictor
pip install -r requirements.txt
cd server
python server.py
```
## 📈 Key Insights
- Expert freelancers earn ~4x more than beginners
- Hourly rate is the strongest predictor
- Job category significantly impacts earnings
- Platform has minimal impact

## 🎓 Learnings
- Proper encoding is critical (fixed Experience Level bug)
- Feature engineering improves performance
- Random Forest handles non-linear patterns effectively
- Deployment requires handling real-time predictions

