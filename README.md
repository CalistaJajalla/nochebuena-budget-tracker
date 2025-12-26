# Nochebuena Budget Tracker

An end-to-end data engineering and machine learning pipeline that extracts, cleans, and loads food price data, predicts Christmas Eve prices, and supports interactive meal budgeting through a Streamlit dashboard.

![Streamlit Banner](./data/pics/health-claims-banner.png)

---

## About the Project

This project automates extraction of weekly food price data from OCR-processed PDFs published by the Philippine Department of Agriculture’s Bantay Presyo program. It cleans and loads this data into a PostgreSQL database, predicts Christmas Eve prices with a holiday markup, and enables users to plan affordable Noche Buena meals within a ₱500 budget using an interactive Streamlit app.

---

## Tools & Technologies Used

- **Python** (pandas, psycopg2, scikit-learn) for ETL and ML  
- **PostgreSQL** (via Docker) as the data warehouse  
- **SQL** for schema definition and upsert queries  
- **Machine Learning** for price prediction and budget classification  
- **Streamlit** for the budgeting and meal planning dashboard  

---

## Concepts Demonstrated

- ETL pipeline: extraction, cleaning, and loading of OCR PDF data  
- Holiday price forecasting with markup adjustments  
- Meal suggestion and budget optimization  
- Interactive visualizations and dynamic budgeting UI 

---

## Architecture Diagram

```mermaid
flowchart TD
    raw_pdf[Raw Bantay Presyo PDF Data]
    etl[ETL Pipeline<br>(extract_pdf.py, clean_prices.py, load_db.py)]
    postgres[(PostgreSQL Database)]
    ml[ML Pipeline<br>(train_price_model.py, budget_classifier.py)]
    predictions[Predicted Prices CSV]
    optimizer[Meal Optimizer<br>(meal_optimizer.py)]
    full_menu["nochebuena_full_menu.json"]
    dashboard[Streamlit Dashboard<br>(dashboard/app.py)]

    raw_pdf --> etl --> postgres
    postgres --> ml --> predictions
    predictions --> postgres
    predictions --> optimizer --> full_menu
    full_menu --> dashboard
    predictions --> dashboard
    postgres --> dashboard
````

---

## How to Use the Streamlit Dashboard

![Streamlit Banner](./data/pics/health-claims-ml.png)

* Search and add predicted price items to your cart
* Track your total against a ₱500 budget with warnings
* Download a PDF receipt of your selected items
* Receive meal suggestions based on your cart ingredients
* View historical price trends of selected items

![Streamlit Banner](./data/pics/health-claims-ml.png)


### Here’s the Streamlit demo: https://health-claims-calistajajalla.streamlit.app/

---

## Next Steps / Recommendations

* Automate data extraction for continuous updates
* Incorporate more comprehensive price data sources (Use pricrs from groceries online)
* Improve ML models for risk and anomaly detection
* Enhance dashboard UI with export and alert features
* Deploy on cloud platforms for scalability
```
```
