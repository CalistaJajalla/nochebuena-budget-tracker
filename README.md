# Nochebuena Budget Tracker

An end-to-end data engineering and machine learning pipeline that extracts, cleans, and loads food price data, predicts Christmas Eve prices, and supports interactive meal budgeting through a Streamlit dashboard.

![Banner](./Pictures/Banner.png)

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
flowchart LR

    %% ---------- DATA SOURCES ----------
    PDF[Raw Bantay Presyo PDFs]
    OCR[OCR Process]

    %% ---------- ETL ----------
    EXTRACT[Extract Prices]
    CLEAN[Clean and Normalize Data]
    LOAD[Load to Database]

    CSV1[extracted_prices.csv]
    CSV2[cleaned_prices.csv]

    %% ---------- DATABASE ----------
    DB[(PostgreSQL Database)]
    DIM1[dim_item]
    DIM2[dim_date]
    FACT[fact_prices]

    %% ---------- ML ----------
    TRAIN[Train Price Model]
    PREDICT[Generate Holiday Predictions]

    CSV3[predicted_prices.csv]

    %% ---------- OPTIMIZER ----------
    OPTIMIZE[Meal Optimization Logic]
    MENU[nochebuena_full_menu.json]

    %% ---------- DASHBOARD ----------
    DASH[Streamlit Dashboard]
    PDFR[Generated Receipt PDF]

    %% ---------- FLOWS ----------
    PDF --> OCR --> EXTRACT --> CSV1
    CSV1 --> CLEAN --> CSV2
    CSV2 --> LOAD --> DB

    DB --> DIM1
    DB --> DIM2
    DB --> FACT

    DB --> TRAIN --> PREDICT --> CSV3
    CSV3 --> LOAD

    CSV3 --> OPTIMIZE --> MENU

    MENU --> DASH
    CSV3 --> DASH
    DB --> DASH
    DASH --> PDFR
````

---

## How to Use the Streamlit Dashboard

![Meal_Suggest](./Pictures/Meal_Suggest.png)

* Search and add predicted price items to your cart
* Track your total against a ₱500 budget with warnings
* Download a PDF receipt of your selected items
* Receive meal suggestions based on your cart ingredients
* View historical price trends of selected items

![Line_Graph](./Pictures/Line_Graph.png)


### Here’s the Streamlit demo: https://nochebuena-budget-tracker.streamlit.app/?embed_options=light_theme,show_footer

---

## Next Steps / Recommendations

* Automate data extraction for continuous updates
* Incorporate more comprehensive price data sources (Use pricrs from groceries online)
* Improve ML models for risk and anomaly detection
* Enhance dashboard UI with export and alert features
* Deploy on cloud platforms for scalability
```
```
