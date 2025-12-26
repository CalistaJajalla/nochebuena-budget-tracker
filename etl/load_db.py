import pandas as pd
from psycopg2.extras import execute_values
from etl.db import get_connection

# LOAD CSV 
CSV_FILE = "data/processed/cleaned_prices.csv"
df = pd.read_csv(CSV_FILE)

# Ensure 'date' is datetime and compute week number
df["date"] = pd.to_datetime(df["date"])
df["week_num"] = df["date"].dt.isocalendar().week

# Ensure 'specification' is string (replace NaN with empty string)
df["specification"] = df["specification"].fillna("")

# UPSERT dim_item 
def upsert_items(df):
    """
    Insert or update items into dim_item
    Uses item_name as unique key
    """
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

# UPSERT dim_date 
def upsert_dates(df):
    """
    Insert or update dates into dim_date
    Uses date as unique key
    """
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

# UPSERT fact_prices 
def upsert_prices(df):
    """
    Insert or update prices into fact_prices
    Links to dim_item and dim_date
    """
    conn = get_connection()
    cur = conn.cursor()

    # Fetch mappings from dimension tables
    cur.execute("SELECT item_id, item_name FROM dim_item")
    item_map = {name: iid for iid, name in cur.fetchall()}

    cur.execute("SELECT date_id, date FROM dim_date")
    date_map = {date: did for did, date in cur.fetchall()}

    # Prepare fact table values and remove duplicates
    price_values = []
    seen_pairs = set()
    for _, row in df.iterrows():
        iid = item_map.get(row["item_name"])
        did = date_map.get(row["date"].date())
        if iid and did:
            key = (iid, did)
            if key not in seen_pairs:
                # Ensure price is numeric and >=0
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

# RUN ETL
if __name__ == "__main__":
    upsert_items(df)
    upsert_dates(df)
    upsert_prices(df)
    print("Database successfully updated from cleaned_prices.csv")
