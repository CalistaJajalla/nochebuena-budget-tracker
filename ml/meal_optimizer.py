import pandas as pd
import json
from itertools import product

# Load CSV
df = pd.read_csv("data/processed/predicted_prices.csv")
df["specification"] = df["specification"].fillna("")

# Full Noche Buena Menu (100+ dishes)
# Format: Category -> Dish Name -> List of possible ingredients
MENU = {
    "Main Courses": {
        "Chicken: Roast Whole Chicken": ["Whole Chicken, Local", "Garlic, Native/Local", "Salt (Iodized)", "Cooking Oil (Coconut)"],
        "Chicken: Chicken Drumsticks Adobo": ["Chicken Drumstick, Local", "Garlic, Native/Local", "Red Onion, Local", "Salt (Iodized)", "Cooking Oil (Palm Olein, Jolly Brand)"],
        "Chicken: Chicken Thighs in Garlic Sauce": ["Chicken Thigh, Local", "Garlic, Native/Local", "White Onion, Imported", "Salt (Iodized)", "Cooking Oil (Coconut)"],
        "Chicken: Chicken Leg Quarter Roast": ["Chicken Leg Quarter, Local", "Bell Pepper (Red), Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Chicken: Honey Garlic Chicken Wings": ["Chicken Wing, Local", "Garlic, Native/Local", "Sugar (Brown)", "Salt (Iodized)", "Cooking Oil (Palm Olein, Jolly)"],
        "Chicken: Garlic Butter Whole Chicken": ["Whole Chicken, Local", "Garlic, Native/Local", "Cooking Oil (Coconut)", "Salt (Iodized)"],
        "Chicken: Chicken Adobo with Bell Pepper": ["Chicken Drumstick, Local", "Bell Pepper (Green), Local", "Bell Pepper (Red), Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Chicken: Chicken Thighs in Tomato Sauce": ["Chicken Thigh, Local", "Tomato", "Garlic, Native/Local", "Salt (Iodized)"],
        "Chicken: Roast Chicken with Onion": ["Whole Chicken, Local", "Red Onion, Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Chicken: Garlic Lemon Chicken": ["Chicken Leg Quarter, Local", "Garlic, Native/Local", "Calamansi", "Salt (Iodized)"],

        "Pork: Lechon Liempo": ["Pork Belly (Liempo), Local", "Garlic, Native/Local", "Salt (Rock)", "Cooking Oil (Coconut)"],
        "Pork: Pork Spare Ribs Sweet BBQ": ["Pork Spare Ribs, Local", "Garlic, Native/Local", "Sugar (Brown)", "Salt (Iodized)"],
        "Pork: Braised Pork Boston Shoulder": ["Pork Boston Shoulder, Local", "Tomato", "Red Onion, Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Pork: Roast Pork Loin": ["Pork Loin, Local", "Garlic, Native/Local", "Red Onion, Local", "Salt (Iodized)"],
        "Pork: Kasim Adobo": ["Pork Picnic Shoulder, Local (Kasim)", "Garlic, Native/Local", "Red Onion, Local", "Salt (Iodized)"],
        "Pork: Roasted Pork Hind Leg": ["Pork Hind Leg (Pigue), Local", "Garlic, Native/Local", "Calamansi", "Salt (Iodized)"],
        "Pork: Stewed Pork Hind Shank": ["Pork Hind Shank, Local", "Tomato", "White Onion, Imported", "Garlic, Native/Local", "Salt (Iodized)"],
        "Pork: Honey Garlic Pork Loin": ["Pork Loin, Local", "Garlic, Native/Local", "Sugar (Brown)", "Salt (Iodized)"],
        "Pork: Pork Belly with Bell Pepper": ["Pork Belly (Liempo), Local", "Bell Pepper (Green), Local", "Bell Pepper (Red), Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Pork: Braised Kasim with Tomato": ["Pork Picnic Shoulder, Local", "Tomato", "Red Onion, Local", "Garlic, Native/Local", "Salt (Iodized)"],

        "Beef: Beef Brisket Caldereta": ["Beef Brisket, Local", "Bell Pepper (Green), Local", "Bell Pepper (Red), Local", "Carrots, Local", "Tomato", "Garlic, Native/Local", "Salt (Iodized)"],
        "Beef: Beef Short Ribs BBQ": ["Beef Short Ribs, Local", "Garlic, Native/Local", "Sugar (Brown)", "Red Onion, Local", "Salt (Iodized)"],
        "Beef: Pan-Seared Beef Tenderloin": ["Beef Tenderloin, Local", "Garlic, Native/Local", "White Onion, Imported", "Salt (Iodized)"],
        "Beef: Grilled Beef Striploin": ["Beef Striploin, Local", "Garlic, Native/Local", "Chilli (Red), Local", "Salt (Rock)"],
        "Beef: Stewed Beef Tongue": ["Beef Tongue, Local", "Garlic, Native/Local", "Red Onion, Local", "Tomato", "Salt (Iodized)"],
        "Beef: Nilagang Beef Forequarter": ["Beef Forequarter, Local", "Carrots, Local", "White Potato, Local", "Cabbage (Wonder Ball)", "Garlic, Native/Local", "Salt (Iodized)"],
        "Beef: Beef Rump Steak Garlic": ["Beef Rump, Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Beef: Beef Flank Stew": ["Beef Flank, Local", "Tomato", "White Onion, Imported", "Garlic, Native/Local", "Salt (Iodized)"],
        "Beef: Beef Loin Roast": ["Beef Loin, Local", "Garlic, Native/Local", "Red Onion, Local", "Salt (Iodized)"],
        "Beef: Beef Rib Eye with Bell Pepper": ["Beef Rib Eye, Local", "Bell Pepper (Green), Local", "Bell Pepper (Red), Local", "Garlic, Native/Local", "Salt (Iodized)"],

        "Fish: Roasted Alumahan": ["Alumahan (Indian Mackerel)", "Garlic, Native/Local", "Salt (Iodized)", "Cooking Oil (Coconut)"],
        "Fish: Daing Bangus": ["Bangus, Large", "Garlic, Native/Local", "Salt (Iodized)", "Cooking Oil (Palm Olein, Jolly)"],
        "Fish: Sinigang na Bangus": ["Bangus, Medium", "Tomato", "Watermelon", "Calamansi", "Salt (Iodized)"],
        "Fish: Fried Galunggong": ["Galunggong, Local", "Garlic, Native/Local", "Red Onion, Local", "Salt (Iodized)", "Cooking Oil (Coconut)"],
        "Fish: Steamed Pampano": ["Pampano, Local", "Tomato", "White Onion, Imported", "Garlic, Native/Local", "Salt (Iodized)"],
        "Fish: Grilled Salmon Belly": ["Salmon Belly, Imported", "Garlic, Native/Local", "Calamansi", "Salt (Iodized)"],
        "Fish: Sinigang na Salmon Head": ["Salmon Head, Imported", "Tomato", "Watermelon", "Calamansi", "Salt (Iodized)"],
        "Fish: Baked Tambakol": ["Tambakol (Yellow-Fin Tuna) Local", "Garlic, Native/Local", "Red Onion, Local", "Salt (Iodized)"],
        "Fish: Pan-Fried Tilapia": ["Tilapia", "Garlic, Native/Local", "Salt (Iodized)", "Cooking Oil (Palm)"],
        "Fish: Sardines in Tomato Sauce": ["Sardines (Tamban)", "Tomato", "Red Onion, Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Fish: Pusit Bisaya Adobo": ["Squid (Pusit Bisaya), Local", "Garlic, Native/Local", "White Onion, Imported", "Salt (Iodized)"],
        "Fish: Roasted Galunggong with Garlic": ["Galunggong, Imported", "Garlic, Native/Local", "Salt (Iodized)"],
        "Fish: Grilled Pampano with Onion": ["Pampano, Imported", "Red Onion, Local", "Garlic, Native/Local", "Salt (Iodized)"]
    },

    "Vegetables/Sides": {
        "Vegetable: Ampalaya Guisado": ["Ampalaya", "Garlic, Native/Local", "Red Onion, Local", "Salt (Iodized)", "Cooking Oil (Palm Olein, Jolly Brand)"],
        "Vegetable: Eggplant Omelette": ["Eggplant", "Chicken Egg (White, Medium)", "Garlic, Native/Local", "Salt (Iodized)"],
        "Vegetable: Chayote-Carrot Stir Fry": ["Chayote", "Carrots, Local", "Garlic, Native/Local", "Salt (Iodized)", "Cooking Oil (Coconut)"],
        "Vegetable: Squash Guisado": ["Squash", "Red Onion, Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Vegetable: Pole Sitao with Garlic": ["Pole Sitao", "Garlic, Native/Local", "White Onion, Imported", "Salt (Iodized)"],
        "Vegetable: Pechay Baguio Sauteed": ["Pechay Baguio", "Garlic, Native/Local", "Salt (Iodized)"],
        "Vegetable: Native Pechay Sauteed": ["Native Pechay", "Tomato", "Garlic, Native/Local", "Salt (Iodized)"],
        "Vegetable: Cauliflower Buttered": ["Cauliflower, Local", "Cooking Oil (Coconut)", "Salt (Iodized)", "Garlic, Native/Local"],
        "Vegetable: Broccoli Sauteed": ["Broccoli, Local", "Garlic, Native/Local", "Salt (Iodized)", "Cooking Oil (Coconut)"],
        "Vegetable: Cabbage & Carrots Stir-Fry": ["Cabbage (Rare Ball)", "Carrots, Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Vegetable: Lettuce Avocado Salad": ["Lettuce (Romaine)", "Avocado", "Tomato", "Calamansi", "Salt (Iodized)"],
        "Vegetable: Bell Pepper Medley": ["Bell Pepper (Green), Local", "Bell Pepper (Red), Local", "Garlic, Native/Local", "Red Onion, Local", "Salt (Iodized)"],
        "Vegetable: Celery-Carrot Stir-Fry": ["Celery", "Carrots, Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Vegetable: Mashed Potato": ["White Potato, Local", "Garlic, Native/Local", "Cooking Oil (Coconut)", "Salt (Iodized)"],
        "Vegetable: Steamed Cabbage with Carrots": ["Cabbage (Scorpio)", "Carrots, Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Vegetable: Garlic Butter Pechay": ["Native Pechay", "Garlic, Native/Local", "Cooking Oil (Coconut)", "Salt (Iodized)"]
    },

    "Rice Dishes": {
        "Rice: Garlic Basmati Rice": ["Basmati Rice", "Garlic, Native/Local", "Salt (Iodized)", "Cooking Oil (Coconut)"],
        "Rice: Glutinous Rice Puto/Bibingka": ["Glutinous Rice", "Sugar (Refined)", "Cooking Oil (Coconut)"],
        "Rice: Japonica Fried Rice": ["Jasponica/Japonica Rice", "Chicken Egg (White, Medium)", "Garlic, Native/Local", "Red Onion, Local", "Salt (Iodized)", "Cooking Oil (Coconut)"],
        "Rice: Steamed White Rice": ["Other Special Rice", "Salt (Iodized)"],
        "Rice: Well-Milled Rice with Steamed Bangus": ["Well Milled", "Bangus, Medium", "Garlic, Native/Local", "Tomato", "Salt (Iodized)"],
        "Rice: Premium Rice with Roast Pork": ["Premium", "Pork Belly (Liempo), Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Rice: Glutinous Rice with Banana Saba": ["Glutinous Rice", "Banana (Saba)", "Sugar (Brown)", "Cooking Oil (Coconut)"],
        "Rice: Basmati Garlic Fried Rice with Chicken": ["Basmati Rice", "Chicken Thigh, Local", "Garlic, Native/Local", "Red Onion, Local", "Salt (Iodized)"],
        "Rice: Steamed Rice with Beef Caldereta": ["Other Special Rice", "Beef Brisket, Local", "Bell Pepper (Green), Local", "Bell Pepper (Red), Local", "Garlic, Native/Local", "Salt (Iodized)"],
        "Rice: Japonica Rice with Stir-fried Vegetables": ["Jasponica/Japonica Rice", "Ampalaya", "Carrots, Local", "Garlic, Native/Local", "Salt (Iodized)"]
    },

    "Desserts/Fruits": {
        "Dessert: Fruit Salad": ["Mango (Carabao)", "Avocado", "Banana (Lakatan)", "Banana (Latundan)", "Melon", "Papaya", "Watermelon", "Sugar (Refined)", "Calamansi"],
        "Dessert: Avocado Shake": ["Avocado", "Sugar (Refined)", "Watermelon"],
        "Dessert: Banana Saba Turon": ["Banana (Saba)", "Sugar (Brown)", "Cooking Oil (Coconut)"],
        "Dessert: Pomelo-Calamansi Fruit Salad": ["Pomelo", "Calamansi", "Sugar (Refined)"],
        "Dessert: Melon & Watermelon Refreshing Drink": ["Melon", "Watermelon", "Sugar (Refined)"],
        "Dessert: Banana & Mango Compote": ["Banana (Lakatan)", "Mango (Carabao)", "Sugar (Brown)"],
        "Dessert: Papaya-Melon Fruit Cups": ["Papaya", "Melon", "Sugar (Refined)"],
        "Dessert: Watermelon Juice": ["Watermelon", "Sugar (Refined)", "Calamansi"],
        "Dessert: Tropical Fruit Medley": ["Mango (Carabao)", "Banana (Latundan)", "Papaya", "Pomelo", "Sugar (Refined)"],
        "Dessert: Avocado-Banana Cream": ["Avocado", "Banana (Lakatan)", "Sugar (Refined)"]
    }
}

# Canonical ingredient mapping
INGREDIENT_MAP = {
    "garlic": ["garlic"],
    "onion": ["onion", "red onion", "white onion"],
    "salt": ["salt", "rock salt", "iodized salt"],
    "oil": ["oil", "coconut oil", "palm olein", "cooking oil"],
    "chicken": ["chicken"],
    "pork": ["pork"],
    "beef": ["beef"],
    "fish": ["bangus", "galunggong", "salmon", "pampano", "alumahan", "tuna", "pusit"],
    "tomato": ["tomato"],
    "carrot": ["carrot"],
    "bell pepper": ["bell pepper"],
    "sugar": ["sugar", "brown sugar", "refined sugar"],
    "potato": ["potato"],
    "calamansi": ["calamansi"],
    "avocado": ["avocado"],
    "banana": ["banana", "saba", "lakatan", "latundan"],
    "melon": ["melon", "watermelon"],
    "mango": ["mango"]
}

# Helper functions
def canonical_ingredient(name):
    """Map ingredient names to canonical types for flexible matching"""
    name_lower = name.lower()
    for key, aliases in INGREDIENT_MAP.items():
        if any(a in name_lower for a in aliases):
            return key
    return name_lower

def estimate_serving_size(category, dish_name):
    """Estimate serving size based on category and dish name"""
    if category == "Main Courses":
        if any(word in dish_name.lower() for word in ["whole", "hind leg", "loin", "brisket"]):
            return 5
        elif any(word in dish_name.lower() for word in ["wing", "drumstick", "thigh", "ribs"]):
            return 3
        else:
            return 4
    elif category == "Vegetables/Sides":
        return 3
    elif category == "Rice Dishes":
        return 3
    elif category == "Desserts/Fruits":
        return 2
    else:
        return 1

def compute_dish_cost(ingredients, df):
    """Compute total cost and track which ingredients are available/missing"""
    total = 0
    used = []
    missing = []
    for ing in ingredients:
        row = df[df["item_name"] == ing]
        if not row.empty:
            total += float(row["predicted_price"].values[0])
            used.append(ing)
        else:
            missing.append(ing)
    return round(total, 2), used, missing

# Build full menu with prices & serving size
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

# Flexible meal suggestion
def suggest_meals(cart_items, full_menu, max_results=10):
    """
    Suggest dishes based on items in cart.
    - Flexible: any variant of ingredient counts.
    - Show missing ingredients for each dish.
    """
    cart_ing = set(canonical_ingredient(i["item"]) for i in cart_items)
    suggestions = []
    for dish in full_menu:
        dish_ing = set(canonical_ingredient(ing) for ing in dish["ingredients"])
        matched = dish_ing & cart_ing  # ingredients already in cart
        missing = dish_ing - cart_ing  # ingredients user still needs
        if matched:
            suggestions.append({
                "dish": dish["dish"],
                "category": dish["category"],
                "total_price": dish["total_price"],
                "serving_size": dish["serving_size"],
                "ingredients": dish["ingredients"],
                "missing_ingredients": list(missing)
            })
    # sort suggestions by number of matched ingredients, descending
    suggestions = sorted(suggestions, key=lambda x: len(set(canonical_ingredient(i) for i in x["ingredients"]) & cart_ing), reverse=True)
    return suggestions[:max_results]

# Save JSON for dashboard use
with open("data/processed/nochebuena_full_menu.json", "w") as f:
    json.dump({
        "full_menu": FULL_MENU
    }, f, indent=2)

print("Saved flexible nochebuena_full_menu.json with serving sizes and canonical ingredients.")
