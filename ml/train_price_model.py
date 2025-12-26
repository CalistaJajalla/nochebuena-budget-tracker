import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add project root to sys.path so 'etl' can be imported
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from etl.db import get_connection  # shared DB connection

# Config
CSV_FILE = "data/processed/cleaned_prices.csv"
PREDICT_CSV = "data/processed/predicted_prices.csv"
TARGET_DATE = datetime(2025, 12, 24)  # Christmas Eve
CHRISTMAS_MARKUP = 0.12  # 12% markup for Christmas

# Load cleaned prices
df = pd.read_csv(CSV_FILE)
df["date"] = pd.to_datetime(df["date"])
df["specification"] = df["specification"].fillna("")
df["week_num"] = df["date"].dt.isocalendar().week
df["month"] = df["date"].dt.month

# Predict prices for Dec 24
predictions = []

for item_name, group in df.groupby("item_name"):
    # Use all December historical data
    dec_prices = group[group["month"] == 12].sort_values("date")
    if not dec_prices.empty:
        avg_dec_price = dec_prices["price"].mean()
        predicted_price = round(avg_dec_price * (1 + CHRISTMAS_MARKUP), 2)
    else:
        # Fallback to last known price if no December data
        predicted_price = group.sort_values("date")["price"].iloc[-1]

    predictions.append({
        "item_name": item_name,
        "predicted_price": max(0, predicted_price)
    })

pred_df = pd.DataFrame(predictions)
pred_df["date"] = TARGET_DATE
pred_df["week_num"] = TARGET_DATE.isocalendar()[1]
pred_df["category"] = df.groupby("item_name")["category"].first().reindex(pred_df["item_name"]).values
pred_df["specification"] = df.groupby("item_name")["specification"].first().reindex(pred_df["item_name"]).values

# Save predicted prices to CSV
os.makedirs(os.path.dirname(PREDICT_CSV), exist_ok=True)
pred_df.to_csv(PREDICT_CSV, index=False)

# DB upsert functions
from psycopg2.extras import execute_values

def upsert_items(df):
    items = df[["item_name", "category", "specification"]].drop_duplicates().to_dict(orient="records")
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

def upsert_prices(df):
    conn = get_connection()
    cur = conn.cursor()

    # Fetch existing mappings
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
                price_values.append((iid, did, row["predicted_price"]))
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

# Run upserts
upsert_items(pred_df)
upsert_dates(pred_df)
upsert_prices(pred_df)

print("Predicted prices for Dec 24 with Christmas markup saved and upserted into DB")
