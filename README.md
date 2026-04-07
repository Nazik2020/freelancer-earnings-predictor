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

| Dashboard | Model Insights |
|----------|---------------|
| ![Dashboard](screenshots/dashboard.png) | ![Insights](screenshots/insights.png) |

---

## 🎯 What It Does

Users input their freelance profile and get:

- 💰 **Predicted Monthly Earnings (USD)**
- 📊 **Feature Impact Analysis**
- 📈 **Market Position (percentile ranking)**
- 🧠 **Strategic Career Insights**

---

## 🧠 Machine Learning Pipeline

### 📊 Dataset
- **5,000 synthetic records** based on real freelancer market trends  
- **15 features** including Job Category, Experience Level, Hourly Rate, Jobs Completed  
- Injected missing values for realistic EDA practice  

---

### 🔍 Exploratory Data Analysis

- Missing values handled using **5% / 30% rule**
- Identified **right-skewed earnings distribution**
- Outlier detection using **IQR method**
- Correlation heatmap to identify key predictors

---

### ⚙️ Preprocessing

- Categorical → `category` dtype conversion  
- **Ordinal Encoding** for `Experience_Level`  
- **Label Encoding** for `Job_Category`, `Platform`  
- Feature engineering:
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
