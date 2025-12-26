import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import io
import json
import uuid
from datetime import datetime

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from etl.db import get_connection

# PAGE CONFIG
st.set_page_config(
    page_title="Noche Buena Budget Tracker",
    layout="wide"
)

# LOAD DATA
prices_df = pd.read_csv("data/processed/predicted_prices.csv")
prices_df["category"] = prices_df["category"].fillna("Others")
prices_df["specification"] = prices_df["specification"].fillna("")

with open("data/processed/nochebuena_full_menu.json") as f:
    MENU_JSON = json.load(f)["full_menu"]

# SESSION STATE
st.session_state.setdefault("cart", [])
st.session_state.setdefault("confirmed", False)
st.session_state.setdefault("budget_warning", False)

# CONSTANTS
BUDGET = 500
PROTEINS = [
    "chicken", "pork", "beef",
    "bangus", "tilapia", "galunggong", "salmon"
]

# HELPERS
def normalize(x):
    return x.lower()

def is_protein(x):
    return any(p in x.lower() for p in PROTEINS)

def get_price(item):
    row = prices_df[prices_df["item_name"] == item]
    return float(row["predicted_price"].iloc[0]) if not row.empty else 0.0

# MEAL OPTIMIZER
def suggest_meals(cart, min_match=2):
    available = {normalize(c["item"]) for c in cart}
    proteins = {normalize(c["item"]) for c in cart if is_protein(c["item"])}

    rows = []
    for dish in MENU_JSON:
        ing = {normalize(i) for i in dish["ingredients"]}
        matched = ing & available
        if len(matched) < min_match:
            continue

        missing = ing - available
        protein_hit = bool(ing & proteins)
        score = len(matched) * 2 + (3 if protein_hit else 0) - len(missing)

        rows.append({
            "Dish": dish["dish"],
            "Course": dish["category"],
            "Ingredients": ", ".join(dish["ingredients"]),
            "Missing": ", ".join(missing) if missing else "None",
            "Serving": dish.get("serving_size", 1),
            "Price": round(sum(get_price(i) for i in dish["ingredients"]), 2),
            "_missing_raw": list(missing),
            "_score": score
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("_score", ascending=False).head(10)
    return df

def add_missing_items(missing_list):
    for m in missing_list:
        for _, row in prices_df.iterrows():
            if normalize(row["item_name"]) == m:
                st.session_state.cart.append({
                    "id": str(uuid.uuid4()),
                    "item": row["item_name"],
                    "spec": row["specification"],
                    "price": row["predicted_price"]
                })
                break

# PDF GENERATION
def generate_pdf(cart):
    font_path = Path("assets/fonts/DejaVuSans.ttf")
    font_name = "DejaVu" if font_path.exists() else "Helvetica"
    if font_path.exists():
        pdfmetrics.registerFont(TTFont("DejaVu", str(font_path)))

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)
    w, h = LETTER

    def new_page():
        c.showPage()
        c.setFont(font_name, 10)
        return h - 50

    y = h - 50

    c.setFont(font_name, 18)
    c.drawString(50, y, "NOCHE BUENA RECEIPT")
    y -= 25
    c.setFont(font_name, 10)
    c.drawString(50, y, datetime.now().strftime("%B %d, %Y %I:%M %p"))
    y -= 20
    c.line(50, y, w - 50, y)
    y -= 15

    c.setFont(font_name, 11)
    c.drawString(50, y, "Product")
    c.drawRightString(w - 50, y, "Price")
    y -= 12
    c.line(50, y, w - 50, y)
    y -= 10

    total = 0
    for item in cart:
        if y < 90:
            y = new_page()

        c.setFont(font_name, 10)
        c.drawString(50, y, item["item"])
        c.drawRightString(w - 50, y, f"₱{item['price']:.2f}")
        y -= 12

        if item["spec"]:
            c.setFont(font_name, 9)
            c.setFillColor(colors.grey)
            c.drawString(65, y, f"- {item['spec']}")
            c.setFillColor(colors.black)
            y -= 10

        total += item["price"]

    y -= 10
    c.line(50, y, w - 50, y)
    y -= 18
    c.setFont(font_name, 12)
    c.drawString(50, y, "TOTAL")
    c.drawRightString(w - 50, y, f"₱{total:.2f}")

    c.save()
    buf.seek(0)
    return buf

# HEADER
st.title("Noche Buena Budget Tracker 🎄")
st.caption("Plan your Noche Buena meal using ingredient-level price estimates and a fixed household budget.")

st.markdown(
    "> 📊 **Data source:** DA Bantay Presyo – National Capital Region. "
    "Official Department of Agriculture price monitoring across public markets in NCR. "
    "Prices shown are model-based estimates derived from this dataset."
)

st.divider()

# MAIN LAYOUT
left, right = st.columns([2, 3])

# LEFT COLUMN
with left:
    st.markdown(
        "<span style='color:blue'>📝 <b>Quick Guide</b></span><br>"
        "<span style='color:blue'>1. Add the ingredients you plan to buy from the list below.</span><br>"
        "<span style='color:blue'>2. Monitor your running total against the ₱500 budget.</span><br>"
        "<span style='color:blue'>3. Confirm payment to unlock the receipt preview and download.</span>",
        unsafe_allow_html=True
    )

    st.subheader("🍗 Ingredient Search")
    search = st.text_input("Search item")

    filtered = prices_df[
        prices_df["item_name"].str.contains(search, case=False, na=False)
    ] if search else prices_df

    category = st.selectbox("Category", sorted(filtered["category"].unique()))
    options = filtered[filtered["category"] == category]["item_name"].tolist()

    if not options:
        st.info("No items found. Check spelling or try a different category.")
    else:
        item = st.selectbox("Available items", options)
        if st.button("Add to cart"):
            row = prices_df[prices_df["item_name"] == item].iloc[0]
            st.session_state.cart.append({
                "id": str(uuid.uuid4()),
                "item": item,
                "spec": row["specification"],
                "price": row["predicted_price"]
            })
            st.rerun()

# RIGHT COLUMN
with right:
    st.subheader("🛒 Cart Summary")

    total = 0
    with st.container(height=260):
        for c in list(st.session_state.cart):
            cols = st.columns([6, 3, 0.8])
            cols[0].markdown(f"**{c['item']}**  \n₱{c['price']:.2f}")
            c["spec"] = cols[1].text_input(
                "spec", c["spec"], key=f"spec_{c['id']}", label_visibility="collapsed"
            )
            if cols[2].button("×", key=f"rm_{c['id']}"):
                st.session_state.cart.remove(c)
                st.rerun()
            total += c["price"]

    st.divider()
    st.metric("Estimated Total", f"₱{total:.2f}")
    st.progress(min(total / BUDGET, 1.0))

    if st.button("Confirm payment"):
        if total > BUDGET:
            st.session_state.budget_warning = True
        else:
            st.session_state.confirmed = True

    if st.session_state.budget_warning:
        st.warning(
            f"⚠️ Your cart exceeds the ₱{BUDGET} budget by ₱{total - BUDGET:.2f}."
        )
        if st.button("Proceed anyway"):
            st.session_state.confirmed = True
            st.session_state.budget_warning = False

# RECEIPT (CONFIRMED ONLY)
if st.session_state.confirmed:
    st.divider()
    with st.expander("Receipt Preview", expanded=True):
        lines = [
            "NOCHE BUENA RECEIPT",
            datetime.now().strftime("%B %d, %Y %I:%M %p"),
            "-" * 36
        ]

        for c in st.session_state.cart:
            lines.append(f"{c['item']:<26} ₱{c['price']:>7.2f}")
            if c["spec"]:
                lines.append(f"  - {c['spec']}")

        lines.extend([
            "-" * 36,
            f"TOTAL{'':22} ₱{total:>7.2f}"
        ])

        st.code("\n".join(lines), language="text")

        st.download_button(
            "Download PDF Receipt",
            generate_pdf(st.session_state.cart),
            "noche_buena_receipt.pdf"
        )

# MEAL SUGGESTIONS
st.divider()
st.subheader("🍲 Suggested Noche Buena Dishes")

meal_df = suggest_meals(st.session_state.cart)
if not meal_df.empty:
    for _, row in meal_df.iterrows():
        with st.expander(row["Dish"]):
            st.markdown(
                f"""
                **Course:** {row['Course']}  
                **Serving Size:** {row['Serving']}  
                **Estimated Dish Cost:** ₱{row['Price']}

                **Ingredients:**  
                {row['Ingredients']}

                **Missing Ingredients:**  
                {row['Missing']}
                """
            )
            if row["_missing_raw"]:
                if st.button("Add missing ingredients", key=row["Dish"]):
                    add_missing_items(row["_missing_raw"])
                    st.rerun()

st.info("ℹ️ Meal suggestions appear only after adding **3 or more ingredients** to your cart.")

# PRICE TRENDS
st.divider()
st.subheader("📈 Historical Price Trends")

st.caption(
    "Price movements are based on historical DA Bantay Presyo data for NCR markets, "
    "used here to provide context on volatility and seasonality."
)

if st.session_state.cart:
    conn = get_connection()
    query = """
        SELECT d.date, f.price
        FROM fact_prices f
        JOIN dim_item i ON f.item_id = i.item_id
        JOIN dim_date d ON f.date_id = d.date_id
        WHERE i.item_name = %s
        ORDER BY d.date
    """
    cols = st.columns(2)
    for i, c in enumerate(st.session_state.cart):
        df = pd.read_sql(query, conn, params=(c["item"],))
        if df.empty:
            continue
        with cols[i % 2]:
            df["date"] = pd.to_datetime(df["date"])
            fig, ax = plt.subplots(figsize=(6, 3.5))
            ax.plot(df["date"], df["price"], marker="o", linewidth=2)
            ax.set_title(c["item"])
            ax.set_ylabel("Price (₱)")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=30)
            st.pyplot(fig)
    conn.close()
