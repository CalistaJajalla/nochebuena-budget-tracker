-- ITEM dimension
CREATE TABLE IF NOT EXISTS dim_item (
    item_id SERIAL PRIMARY KEY,
    item_name TEXT UNIQUE NOT NULL,
    category TEXT,
    specification TEXT
);

-- DATE dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    week_num INT
);

-- PRICE fact table
CREATE TABLE IF NOT EXISTS fact_prices (
    price_id SERIAL PRIMARY KEY,
    item_id INT NOT NULL REFERENCES dim_item(item_id),
    date_id INT NOT NULL REFERENCES dim_date(date_id),
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    UNIQUE (item_id, date_id)
);

CREATE INDEX idx_fact_item ON fact_prices(item_id);
CREATE INDEX idx_fact_date ON fact_prices(date_id);
