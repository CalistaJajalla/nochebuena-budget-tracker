from pathlib import Path
import pandas as pd
import re
import unicodedata

# Paths
INPUT_FILE = Path("data/processed/extracted_prices.csv")
OUTPUT_FILE = Path("data/processed/cleaned_prices.csv")
LOG_FILE = Path("data/processed/cleaning_log.csv")

# Loads
df = pd.read_csv(INPUT_FILE)
df.columns = [c.strip().lower() for c in df.columns]

log = []

# Date parsing
def parse_date(day):
    try:
        return pd.to_datetime(f"{day} 2025", format="%B %d %Y")
    except:
        return pd.NaT

df["date"] = df["day"].apply(parse_date)
df.drop(columns=["day"], inplace=True)

# OCR Dictionaries
ITEM_MAP = {
    "Eg‘r;':IPlcmc Shoulder (Kasim),": "Pork Picnic Shoulder, Local (Kasim)",
    "Eg‘r;':IPicnic Shoulder (Kasim),": "Pork Picnic Shoulder, Local (Kasim)",
    "r;;l;rtx::w Shoulder (Kasim),": "Pork Picnic Shoulder, Imported (Kasim)",
    "T:::i:gl (Yellow-Fin Tuna),": "Tambakol (Yellow-Fin Tuna) Imported",
    "Sen el (Rl Flnslun).": "Tambakol (Yellow-Fin Tuna) Local",
    "g‘;::;’;g Oil (Palm Olein, Jolly": "Cooking Oil (Palm Olein, Jolly)",
    "Cooking 0Oil (Palm)": "Cooking Oil (Palm)",
    "Garlic, Native/Local": "Garlic, Native/Local",
    "Habichuelas/Baguio Beans, Local": "Habichuelas/Baguio Beans, Local",
    "Jasponica/Japonica Rice": "Jasponica/Japonica Rice",
    "Pork Rind/Skin, Local": "Pork Rind/Skin, Local",
    "Chicken Rind/Skin, Local": "Chicken Rind/Skin, Local"
}

SPEC_MAP = {
    "fifif?fi’;ffiig&\"fi. i": "Medium (8–10 cm diameter/bunch hd)",
    "ffig. i": "Medium (8–10 cm diameter/bunch hd)",
    "(ffig. i)": "Medium (8–10 cm diameter/bunch hd)",
    "m:?r::?;r(/%::ciﬂx 4": "Medium (8–10 cm diameter/bunch hd)",
    "mrr(/%cix 4": "Medium (8–10 cm diameter/bunch hd)",
    "E‘f ;‘g’_’;gg\"g':; uiked, Medtiti": "Fairly well-matured, medium (150–300 g)",
    "ff ;‘g’_’ 3‘3'?;:; tured, Medium": "Fairly well-matured, medium (150–300 g)",
    "'(:f;g’_’a,\"\"(‘)';';:]amred' Medium": "Fairly well-matured, medium (150–300 g)",
    "(fga,()amred Medium": "Fairly well-matured, medium (150–300 g)",
    "(l\\idx:ir::::r(/i(:}r;:hs g;]m": "Medium (301–450 g/bunch)",
    "10-12 pes/kg": "10–12 pcs/kg",
    "13-15 pes/kg": "13–15 pcs/kg",
    "15-18 pes/kg": "15–18 pcs/kg",
    "1,000 mi/bottle": "1,000 ml/bottle",
    "5% broken": "5% broken",
    "20-40% bran streak": "20-40% bran streak",
    "1-19% bran streak": "1-19 bran streak"
}

# Normalize text
def normalize_text(text):
    if pd.isna(text):
        return ""
    text = str(text).strip()
    # Remove leading/trailing quotes and invisible unicode characters
    text = re.sub(r"^[\"'‘’“”]+|[\"'‘’“”]+$", "", text)
    text = unicodedata.normalize("NFKD", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text

# Clean functions
def clean_item(name):
    original = normalize_text(name)
    cleaned = ITEM_MAP.get(original)
    if cleaned:
        log.append(("item_name", original, cleaned))
        return cleaned
    # Fallback: light cleanup
    cleaned = re.sub(r"[^A-Za-z0-9(),/\- ]+", "", original).strip()
    if cleaned != original:
        log.append(("item_name", original, cleaned))
    return cleaned

def clean_spec(spec):
    original = normalize_text(spec)
    cleaned = SPEC_MAP.get(original)
    if cleaned:
        log.append(("specification", original, cleaned))
        return cleaned
    # Discard garbage
    if len(re.findall(r"[A-Za-z]", original)) < 3:
        log.append(("specification", original, ""))
        return ""
    # Light cleanup
    cleaned = re.sub(r"[^A-Za-z0-9(),/\-%. ]+", "", original).strip()
    if cleaned != original:
        log.append(("specification", original, cleaned))
    return cleaned

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

# Apply cleaning
df["item_name"] = df["item_name"].apply(clean_item)
df["specification"] = df["specification"].apply(clean_spec)
df["price"] = df.apply(lambda r: clean_price(r["price"], r["category"]), axis=1)

# Drop invalid
before = len(df)
df = df.dropna(subset=["date", "item_name", "price"])
after = len(df)
if before != after:
    log.append(("rows_dropped", before, after))

# Finalize
df = (
    df.drop_duplicates()
      .sort_values(["date", "category", "item_name", "price"])
      .reset_index(drop=True)
)
df = df[["date", "category", "item_name", "specification", "price"]]

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

if log:
    pd.DataFrame(log, columns=["field", "original", "cleaned"]).to_csv(LOG_FILE, index=False)

print("Cleaning finished")
print(f"cleaned_prices.csv saved ({len(df)} rows)")
print(f"cleaning_log.csv written")
