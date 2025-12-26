# 📁 Nochebuena Budget Tracker Project Setup by Calista Jajalla ᓚᘏᗢ

## Table of Contents

1. [Project Folder Structure](#1-project-folder-structure)
2. [About the Dataset](#2-about-the-dataset)
3. [Setup Python Virtual Environment (venv)](#3-setup-python-virtual-environment-venv)
4. [Local Database Setup](#4-local-database-setup)
5. [Create Database Tables (Schema Setup)](#5-create-database-tables-schema-setup)
6. [Running the ETL Pipeline](#6-running-the-etl-pipeline)
7. [Training the Machine Learning Model](#7-training-the-machine-learning-model)
8. [Launching the Static Dashboard Website](#8-launching-the-static-dashboard-website)

---

## 1. Project Folder Structure

Ensure your project directory looks like this:

```bash
nochebuena-budget-tracker/
├── README.md  
├── docker-compose.yml  
├── data/  
│   ├── raw/  
│   │   └── prices_dec7_21.pdf   # Compiled prices from DA Facebook Page (Dec 7, 11,
│   └── processed/  
│       └── weekly_prices.parquet  
├── etl/  
│   ├── extract_pdf.py            # Extracts prices from PDF  
│   ├── clean_prices.py           # Cleans and normalizes data  
│   ├── load_db.py                # Loads data into Postgres DB  
│   ├── db.py                    # Postgres connection helper  
│   └── __init__.py  
├── ml/  
│   ├── train_price_model.py     # ML to predict price trends  
│   ├── budget_classifier.py     # Model to predict if budget is met  
│   ├── meal_optimizer.py        # Knapsack-style meal optimizer  
│   └── __init__.py  
├── sql/  
│   └── create_tables.sql        # SQL schema to create tables  
├── dashboard/  
│   └── app.py                   # Streamli dashboard
├── requirements.txt
├── .gitignore
└── venv/                        # Python virtual env (.gitignore)
```

---

## 2. About the Dataset

The dataset is sourced from the **Department of Agriculture's Bantay Presyo Program**, a government initiative aimed at monitoring and stabilizing food prices across the Philippines. Bantay Presyo regularly publishes price reports for essential food items, helping consumers and policymakers track market trends and price fluctuations.

### Dataset Description

- **Source:** Official Bantay Presyo price reports, originally shared as images on the Department of Agriculture's Facebook page.
- **Format:** Compiled price data for common food items, consolidated into a single OCR-processed PDF to facilitate automated extraction.
- **Coverage:**
  - Prices collected from key regional markets nationwide to provide a representative snapshot.
  - Food categories include:
    - Meat (e.g., pork, chicken, beef)
    - Fish and seafood
    - Vegetables
    - Staples (e.g., rice, corn)
    - Fruits
- **Temporal Granularity:** Weekly snapshots taken on December 7, 14, and 21, capturing price movements during the critical holiday season, when demand and supply dynamics typically shift.

### Use Cases

This dataset is well-suited for:

- **ETL processes:** Automated extraction, transformation, and loading into structured databases for easy querying.
- **Time-series analysis:** Modeling price trends and forecasting future fluctuations.
- **Budget classification:** Determining if specific meal plans fit within a defined budget, important for consumer guidance.

The transformation from Facebook-shared PNG images to OCR-processed PDFs was done to enable efficient and reliable text extraction, reducing manual data entry errors and speeding up the data pipeline.

---

## 3. Setup Python Virtual Environment (venv)

Create and activate an isolated Python environment, then install dependencies:

```bash
python3 -m venv venv  
source venv/bin/activate            # Linux/Mac  
# .\venv\Scripts\activate          # Windows  

pip install --upgrade pip  
pip install -r requirements.txt  
```
---

## 4. Local Database Setup

Create docker-compose.yml file (see at file section). Then, start the Postgres database and any other services via Docker Compose:

```bash
docker-compose up --build -d  
```

This runs your Postgres container (`nochebuena-budget-tracker_postgres`) needed for data storage.

## 5. Create Database Tables (Schema Setup)

Before running ETL, create the necessary tables (see `create_tables.sql` under the sql folder) in the Postgres database. Here's a diagram illustrating the fact and dimension tables.

```mermaid
classDiagram
    direction LR

    class DimItem {
        +int item_id
        +string item_name
        +string category
        +string specification
    }

    class FactPrices {
        +int price_id
        +int item_id
        +int date_id
        +decimal price
    }

    class DimDate {
        +int date_id
        +date date
        +int week_num
    }

    DimItem "1" --> "many" FactPrices : item_id
    DimDate "1" --> "many" FactPrices : date_id

    class FullMenu {
        +string category
        +string dish_name
        +float total_price
        +int serving_size
        +list ingredients
        +list missing_ingredients
        +bool price_warning
    }

    FactPrices ..> FullMenu : "derived"

    note right FullMenu : "Legend:_solid_arrows_=_FK,_dashed_arrow_=_optional/derived"
```

Then, run this in terminal to create the tables:

```bash
cat sql/create_tables.sql | docker exec -i nochebuena-budget-tracker_postgres psql -U noche_user -d nochebuena
```

---

## 6. Running the ETL Pipeline

The ETL process is made up of four scripts that run one after another. Here’s a look at the first two, focusing on what they do and some key code snippets that illustrate their functionality.


### 1. `extract_pdf.py`

**What it does:**
This script starts by loading raw price data extracted from a PDF (converted to CSV). It cleans up the data so it’s easier to work with downstream.

**Key parts:**

* It reads the raw CSV and cleans up the column names by stripping whitespace and making everything lowercase:

```python
from pathlib import Path
import pandas as pd
import re
import unicodedata

INPUT_FILE = Path("data/processed/extracted_prices.csv")
OUTPUT_FILE = Path("data/processed/cleaned_prices.csv")
LOG_FILE = Path("data/processed/cleaning_log.csv")

df = pd.read_csv(INPUT_FILE)
df.columns = [c.strip().lower() for c in df.columns]
```

* Dates in the data only have month and day, so the script adds the year 2025 and converts them into proper datetime objects, dropping the original column afterward:

```python
def parse_date(day):
    try:
        return pd.to_datetime(f"{day} 2025", format="%B %d %Y")
    except:
        return pd.NaT

df["date"] = df["day"].apply(parse_date)
df.drop(columns=["day"], inplace=True)
```

* Since the raw data comes from OCR (optical character recognition), it often contains errors or weird characters. To fix this, the script uses dictionaries (`ITEM_MAP` and `SPEC_MAP`) to map common misreadings to correct terms, helping standardize item names and specifications.

```python
ITEM_MAP = {
    "Eg‘r;':IPlcmc Shoulder (Kasim),": "Pork Picnic Shoulder, Local (Kasim)",
    # ... more mappings ...
}

SPEC_MAP = {
    "fifif?fi’;ffiig&\"fi. i": "Medium (8–10 cm diameter/bunch hd)",
    # ... more mappings ...
}
```

* There’s a helper function that cleans up any text by trimming spaces, removing extraneous quotes and invisible unicode characters, and collapsing multiple spaces into one:

```python
def normalize_text(text):
    if pd.isna(text):
        return ""
    text = str(text).strip()
    text = re.sub(r"^[\"'‘’“”]+|[\"'‘’“”]+$", "", text)
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"\s+", " ", text)
    return text
```

* For item names, the script tries to fix them using the dictionary. If not found, it does a lighter cleanup with a regex to strip unwanted characters. All changes get logged for review:

```python
def clean_item(name):
    original = normalize_text(name)
    cleaned = ITEM_MAP.get(original)
    if cleaned:
        log.append(("item_name", original, cleaned))
        return cleaned
    cleaned = re.sub(r"[^A-Za-z0-9(),/\- ]+", "", original).strip()
    if cleaned != original:
        log.append(("item_name", original, cleaned))
    return cleaned
```

* Price values get cleaned by converting strings to floats, and heuristics fix scale errors (like dividing by 10 or 100 if prices seem too large). It also applies category-specific adjustments and logs anything it can’t convert:

```python
def clean_price(val, category):
    try:
        price = float(str(val).replace(",", ""))
        if price > 2000:
            price = price / 100
        if category.upper() in {"LOWLAND VEGETABLES", "FRUITS", "SPICES"} and price > 1000:
            price = price / 10
        return round(price, 2)
    except:
        log.append(("price", val, None))
        return None
```

* Finally, it removes rows with missing essential data, drops duplicates, sorts the data, and saves the cleaned output:

```python
df = df.dropna(subset=["date", "item_name", "price"])
df = df.drop_duplicates().sort_values(["date", "category", "item_name", "price"]).reset_index(drop=True)
df = df[["date", "category", "item_name", "specification", "price"]]

df.to_csv(OUTPUT_FILE, index=False)
```

### 2. `clean_prices.py`

**What it does:**
This script takes the output from `extract_pdf.py` and applies a deeper cleaning pass to standardize the data even more, especially handling edge cases.

**Key points:**

* It normalizes text similarly but adds specific fixes for known tricky items. For example, it force-corrects the specification for any kind of ginger product:

```python
def clean_spec(spec, item_name):
    original = normalize_text(spec)
    if "ginger" in item_name.lower():
        cleaned = "Fairly well-matured, medium (150–300 g)"
        log.append(("specification", original, cleaned))
        return cleaned
    if original in SPEC_MAP:
        cleaned = SPEC_MAP[original]
        log.append(("specification", original, cleaned))
        return cleaned
    if len(re.findall(r"[A-Za-z]", original)) < 3:
        log.append(("specification", original, ""))
        return ""
    cleaned = re.sub(r"[^A-Za-z0-9(),/\-%. ]+", "", original).strip()
    if cleaned != original:
        log.append(("specification", original, cleaned))
    return cleaned
```

### 3. `load_db.py`

**What it does:**
This script takes the cleaned CSV data and loads it into a PostgreSQL database, updating or inserting records into dimension and fact tables. It ensures data integrity by linking facts (prices) to their related items and dates.

**Key parts:**

* It loads the cleaned CSV and prepares the data by converting dates to datetime and extracting the week number. It also fills missing specifications with empty strings for consistency:

```python
import pandas as pd
from psycopg2.extras import execute_values
from etl.db import get_connection

CSV_FILE = "data/processed/cleaned_prices.csv"
df = pd.read_csv(CSV_FILE)

df["date"] = pd.to_datetime(df["date"])
df["week_num"] = df["date"].dt.isocalendar().week
df["specification"] = df["specification"].fillna("")
```

* **Upserting items into the `dim_item` table:**
  It groups the data by item name, collects category and specifications (concatenating unique specs), then inserts or updates records. The unique key here is `item_name`:

```python
def upsert_items(df):
    items = (
        df.groupby("item_name", as_index=False)
        .agg({
            "category": "first",
            "specification": lambda x: ", ".join(filter(None, x.unique()))
        })
        .to_dict(orient="records")
    )

    conn = get_connection()
    cur = conn.cursor()

    execute_values(
        cur,
        """
        INSERT INTO dim_item (item_name, category, specification)
        VALUES %s
        ON CONFLICT (item_name) DO UPDATE
        SET category = EXCLUDED.category,
            specification = EXCLUDED.specification
        """,
        [(i["item_name"], i["category"], i["specification"]) for i in items]
    )

    conn.commit()
    cur.close()
    conn.close()
```

* **Upserting dates into the `dim_date` table:**
  Similarly, it inserts or updates unique dates along with their ISO week numbers, using `date` as the key:

```python
def upsert_dates(df):
    dates = df[["date", "week_num"]].drop_duplicates().to_dict(orient="records")
    conn = get_connection()
    cur = conn.cursor()

    execute_values(
        cur,
        """
        INSERT INTO dim_date (date, week_num)
        VALUES %s
        ON CONFLICT (date) DO UPDATE
        SET week_num = EXCLUDED.week_num
        """,
        [(d["date"], d["week_num"]) for d in dates]
    )

    conn.commit()
    cur.close()
    conn.close()
```

* **Upserting prices into the fact table `fact_prices`:**
  This part fetches the IDs for items and dates from the dimension tables, then prepares price entries. It avoids duplicates by tracking seen `(item_id, date_id)` pairs, and ensures prices are valid numbers before inserting or updating:

```python
def upsert_prices(df):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT item_id, item_name FROM dim_item")
    item_map = {name: iid for iid, name in cur.fetchall()}

    cur.execute("SELECT date_id, date FROM dim_date")
    date_map = {date: did for did, date in cur.fetchall()}

    price_values = []
    seen_pairs = set()
    for _, row in df.iterrows():
        iid = item_map.get(row["item_name"])
        did = date_map.get(row["date"].date())
        if iid and did:
            key = (iid, did)
            if key not in seen_pairs:
                try:
                    price = round(float(row["price"]), 2)
                    if price < 0:
                        continue
                except:
                    continue
                price_values.append((iid, did, price))
                seen_pairs.add(key)

    if price_values:
        execute_values(
            cur,
            """
            INSERT INTO fact_prices (item_id, date_id, price)
            VALUES %s
            ON CONFLICT (item_id, date_id) DO UPDATE
            SET price = EXCLUDED.price
            """,
            price_values
        )

    conn.commit()
    cur.close()
    conn.close()
```

* The script then runs all three upsert functions sequentially to update the database and prints a confirmation message:

```python
if __name__ == "__main__":
    upsert_items(df)
    upsert_dates(df)
    upsert_prices(df)
    print("Database successfully updated from cleaned_prices.csv")
```

### 4. `db.py`

**What it does:**
This small utility module handles database connection details, returning a fresh connection to PostgreSQL whenever needed.

**Key points:**

* All connection info is stored in a dictionary for easy configuration.
* The `get_connection` function simply opens and returns a new connection using `psycopg2`:

```python
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass"
}

def get_connection():
    """Return a new database connection"""
    return psycopg2.connect(**DB_CONFIG)
```

### Running the ETL pipeline end-to-end

Execute these commands in sequence to complete the ETL workflow:

```bash
python etl/extract_pdf.py 
python etl/clean_prices.py 
python etl/load_db.py
```

## 7. Training the Machine Learning Model

### 1.`ml/train_price_model.py`

**Purpose:**
This script predicts Christmas Eve prices (Dec 24, 2025) for food items by analyzing historical December data and applying a holiday markup. It then updates the database with these predicted prices.

**How it works:**

* Loads cleaned price data, converts date columns to proper datetime types, fills missing specs, and extracts week and month info:

```python
df = pd.read_csv(CSV_FILE)
df["date"] = pd.to_datetime(df["date"])
df["specification"] = df["specification"].fillna("")
df["week_num"] = df["date"].dt.isocalendar().week
df["month"] = df["date"].dt.month
```

* For each item, it calculates the average December price, then applies a 12% Christmas markup. If no December data exists, it uses the most recent price:

```python
for item_name, group in df.groupby("item_name"):
    dec_prices = group[group["month"] == 12].sort_values("date")
    if not dec_prices.empty:
        avg_dec_price = dec_prices["price"].mean()
        predicted_price = round(avg_dec_price * (1 + CHRISTMAS_MARKUP), 2)
    else:
        predicted_price = group.sort_values("date")["price"].iloc[-1]
    predictions.append({"item_name": item_name, "predicted_price": max(0, predicted_price)})
```

* Builds a DataFrame for predictions, adds relevant date and category info, then saves it as a CSV:

```python
pred_df = pd.DataFrame(predictions)
pred_df["date"] = TARGET_DATE
pred_df["week_num"] = TARGET_DATE.isocalendar()[1]
pred_df["category"] = df.groupby("item_name")["category"].first().reindex(pred_df["item_name"]).values
pred_df["specification"] = df.groupby("item_name")["specification"].first().reindex(pred_df["item_name"]).values

os.makedirs(os.path.dirname(PREDICT_CSV), exist_ok=True)
pred_df.to_csv(PREDICT_CSV, index=False)
```

* Contains upsert functions for the predicted data (similar to the ETL load step), updating `dim_item`, `dim_date`, and `fact_prices` tables with new predicted prices:

```python
def upsert_items(df):
    # inserts or updates dim_item table

def upsert_dates(df):
    # inserts or updates dim_date table

def upsert_prices(df):
    # inserts or updates fact_prices table using predicted_price
```

* Runs all upserts and confirms successful update:

```python
upsert_items(pred_df)
upsert_dates(pred_df)
upsert_prices(pred_df)

print("Predicted prices for Dec 24 with Christmas markup saved and upserted into DB")
```

### 2.`ml/meal_optimizer.py`

**Purpose:**
This script helps suggest flexible Noche Buena meal combinations based on predicted prices and ingredient availability, estimating costs and servings.

**Key details:**

* Loads predicted prices, ensuring no missing specifications.
* Defines a comprehensive menu of 100+ dishes, each with categorized dish names and their ingredient lists.
* Includes a canonical ingredient mapping to group similar ingredients for flexible matching (e.g., "garlic" variants mapped to `"garlic"`).
* Provides helper functions:
  * `canonical_ingredient(name)` returns a normalized ingredient type for flexible comparison.
  * `estimate_serving_size(category, dish_name)` approximates how many people a dish can serve based on its category and name.
  * `compute_dish_cost(ingredients, df)` sums up the cost of ingredients present in the price data and tracks any missing ingredients.
* Builds a full menu list with total price, serving size, and missing ingredient flags:

```python
FULL_MENU = []
for cat, dishes in MENU.items():
    for dish_name, ingredients in dishes.items():
        cost, used, missing = compute_dish_cost(ingredients, df)
        serving_size = estimate_serving_size(cat, dish_name)
        FULL_MENU.append({
            "category": cat,
            "dish": dish_name,
            "total_price": cost,
            "serving_size": serving_size,
            "ingredients": used,
            "missing_ingredients": missing,
            "price_warning": cost > 500
        })
```

* Implements a flexible meal suggestion function that compares items already in a user’s cart to dish ingredients and suggests meals that use those ingredients, showing missing components:

```python
def suggest_meals(cart_items, full_menu, max_results=10):
    cart_ing = set(canonical_ingredient(i["item"]) for i in cart_items)
    suggestions = []
    for dish in full_menu:
        dish_ing = set(canonical_ingredient(ing) for ing in dish["ingredients"])
        matched = dish_ing & cart_ing
        missing = dish_ing - cart_ing
        if matched:
            suggestions.append({
                "dish": dish["dish"],
                "category": dish["category"],
                "total_price": dish["total_price"],
                "serving_size": dish["serving_size"],
                "ingredients": dish["ingredients"],
                "missing_ingredients": list(missing)
            })
    suggestions = sorted(suggestions, key=lambda x: len(set(canonical_ingredient(i) for i in x["ingredients"]) & cart_ing), reverse=True)
    return suggestions[:max_results]
```

* Saves the full menu with pricing and servings to JSON for use in dashboards or frontend apps:

```python
with open("data/processed/nochebuena_full_menu.json", "w") as f:
    json.dump({"full_menu": FULL_MENU}, f, indent=2)
```

* Confirms success:

```python
print("Saved flexible nochebuena_full_menu.json with serving sizes and canonical ingredients.")
```


### Running the ML pipeline

Execute these commands in sequence to complete the ML workflow:

```bash
python ml/train_price_model.py
python ml/budget_classifier.py
```

---

## 8. Launching the Static Dashboard Website

**1. Page Setup and Data Loading**
The app uses Streamlit to build a responsive dashboard. It starts by configuring the page and loading essential data — predicted ingredient prices and the full menu.

```python
st.set_page_config(page_title="Noche Buena Budget Tracker", layout="wide")

prices_df = pd.read_csv("data/processed/predicted_prices.csv")
with open("data/processed/nochebuena_full_menu.json") as f:
    MENU_JSON = json.load(f)["full_menu"]
```

**2. Managing User Cart and Session State**
User selections are tracked using Streamlit's `session_state`, allowing persistent cart contents and flags across interactions.

```python
st.session_state.setdefault("cart", [])
st.session_state.setdefault("confirmed", False)
st.session_state.setdefault("budget_warning", False)
```

This keeps the app responsive to user actions like adding/removing items and confirming the budget.

**3. Ingredient Search and Adding to Cart**
Users can filter ingredients by search term and category, then add items to their cart with price and specification details fetched from the data.

```python
search = st.text_input("Search item")
filtered = prices_df[prices_df["item_name"].str.contains(search, case=False)] if search else prices_df
category = st.selectbox("Category", sorted(filtered["category"].unique()))
options = filtered[filtered["category"] == category]["item_name"].tolist()

if st.button("Add to cart"):
    row = prices_df[prices_df["item_name"] == item].iloc[0]
    st.session_state.cart.append({
        "id": str(uuid.uuid4()),
        "item": item,
        "spec": row["specification"],
        "price": row["predicted_price"]
    })
    st.rerun()
```

**4. Budget Tracking and Confirmation**
The app continuously calculates the cart total and compares it to the fixed budget (₱500). Users receive warnings if they exceed the budget, with an option to proceed anyway.

```python
total = sum(c["price"] for c in st.session_state.cart)
st.metric("Estimated Total", f"₱{total:.2f}")
st.progress(min(total / BUDGET, 1.0))

if st.button("Confirm payment"):
    if total > BUDGET:
        st.session_state.budget_warning = True
    else:
        st.session_state.confirmed = True
```

**5. Generating and Downloading Receipt PDFs**
Once confirmed, users can preview and download a formatted receipt PDF listing their purchased items and total cost. The PDF is generated on-the-fly using ReportLab.

```python
st.download_button(
    "Download PDF Receipt",
    generate_pdf(st.session_state.cart),
    "noche_buena_receipt.pdf"
)
```

**6. Meal Suggestions Based on Cart Contents**
To assist meal planning, the app suggests dishes that match the current ingredients, scoring options by how many ingredients match and protein presence.

```python
meal_df = suggest_meals(st.session_state.cart)
if not meal_df.empty:
    for _, row in meal_df.iterrows():
        with st.expander(row["Dish"]):
            st.markdown(f"**Ingredients:** {row['Ingredients']}\n**Missing:** {row['Missing']}")
            if st.button("Add missing ingredients", key=row["Dish"]):
                add_missing_items(row["_missing_raw"])
                st.rerun()
```

**7. Visualizing Historical Price Trends**
The dashboard pulls historical prices for each cart item from the database and plots them using Matplotlib to show price fluctuations over time.

```python
conn = get_connection()
query = """
    SELECT d.date, f.price
    FROM fact_prices f
    JOIN dim_item i ON f.item_id = i.item_id
    JOIN dim_date d ON f.date_id = d.date_id
    WHERE i.item_name = %s
    ORDER BY d.date
"""

for item in st.session_state.cart:
    df = pd.read_sql(query, conn, params=(item["item"],))
    if not df.empty:
        fig, ax = plt.subplots()
        ax.plot(pd.to_datetime(df["date"]), df["price"])
        st.pyplot(fig)
conn.close()
```

To start the dashboard locally, run:

```bash
streamlit run dashboard/app.py
```

This will launch the interactive web app in your browser, allowing you to access all the features described above.


---

## Stopping the Application

Stop all services with:

```bash
docker-compose down
```

This command shuts down the containers and cleans up the network, freeing system resources after you’re done using the dashboard and backend services.

