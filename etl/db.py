# The DB port is for both local/cloud (although you can just use local)

conn = get_connection()

query = """
    SELECT d.date, f.price
    FROM fact_prices f
    JOIN dim_item i ON f.item_id = i.item_id
    JOIN dim_date d ON f.date_id = d.date_id
    WHERE LOWER(i.item_name) = LOWER(%s)
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
