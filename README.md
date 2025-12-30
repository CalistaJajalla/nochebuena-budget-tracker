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
flowchart TD

    %% ===== STYLES =====
    classDef process fill:#E3F2FD,stroke:#1565C0,stroke-width:1.5px;
    classDef data fill:#E8F5E9,stroke:#2E7D32,stroke-width:1.5px;
    classDef storage fill:#FFF3E0,stroke:#EF6C00,stroke-width:1.5px;
    classDef output fill:#FCE4EC,stroke:#AD1457,stroke-width:1.5px;

    %% ===== INPUT =====
    A[/Raw Bantay Presyo PDFs/]:::data

    %% ===== ETL =====
    B[Extract Prices<br/>(extract_pdf.py)]:::process
    C[Clean & Normalize<br/>(clean_prices.py)]:::process
    D[Load to Database<br/>(load_db.py)]:::process

    F1[/extracted_prices.csv/]:::data
    F2[/cleaned_prices.csv/]:::data

    %% ===== DATABASE =====
    DB[(PostgreSQL)]:::storage
    T1[(dim_item)]:::storage
    T2[(dim_date)]:::storage
    T3[(fact_prices)]:::storage

    %% ===== ML & OPTIMIZATION =====
    E[Train Price Model<br/>(train_price_model.py)]:::process
    F[/predicted_prices.csv/]:::data
    G[Meal Optimizer<br/>(meal_optimizer.py)]:::process
    H[/nochebuena_full_menu.json/]:::data

    %% ===== DASHBOARD =====
    I[Streamlit Dashboard<br/>(dashboard/app.py)]:::process
    J[/Receipt PDF/]:::output

    %% ===== FLOW =====
    A --> B --> F1 --> C --> F2 --> D --> DB
    DB --> T1
    DB --> T2
    DB --> T3

    DB --> E --> F
    F --> D
    F --> G --> H

    DB --> I
    F --> I
    H --> I
    I --> J
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
