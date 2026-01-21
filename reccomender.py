import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from db_utils import load_recipes, load_pantry


def get_pantry_items():
    conn = sqlite3.connect("food.db")
    df = pd.read_sql("SELECT item, quantity, expiryDate FROM Fridge", conn)
    conn.close()
    return df

def get_recipes():
    conn = sqlite3.connect("food.db")
    df = pd.read_sql("SELECT * FROM recipes", conn)
    conn.close()
    return df

def recipe_matches_diet(recipe_row, user_requirements):

    ingredients_text = str(recipe_row.get("ingredient_lines", "")).lower()

    meat_words = [
        "chicken", "beef", "pork", "bacon", "ham", "turkey", "lamb",
        "fish", "salmon", "tuna", "shrimp", "prawn", "anchovy",
        "sausage", "pepperoni", "prosciutto", "veal", "duck", 
        "venison", "rabbit", "bison", "cod", "tilapia", "haddock", "catfish",
        "mackerel", "sardines", "halibut", "sea bass", "crab", "lobster", "clams", "mussles",
        "calamari", "octupus", "scallops", "oysters", "trout", "red snapper", "swordfish",
        "flounder", "sole", "pollock"
    ]

    is_vegetarian = user_requirements.requirements_vector[
        user_requirements.lookup_table["isVegetarian"]
    ]

    if is_vegetarian:
        for word in meat_words:
            if word in ingredients_text:
                return False

    return True

    print(recipe_row.keys())
    print(ingredients_text[:200])



def score_recipe(recipe_row, pantry_df):
    recipe_ingredients = str(recipe_row["ingredients"]).lower()
    owned = 0

    for _, row in pantry_df.iterrows():
        if row["name"].lower() in recipe_ingredients:
            owned += 1

    return owned



def recommend_recipes(user_requirements):
    recipes_df = load_recipes()
    pantry_df = load_pantry()

    filtered_rows = []

    for _, row in recipes_df.iterrows():
        if recipe_matches_diet(row, user_requirements):
            filtered_rows.append(row)

    filtered_df = pd.DataFrame(filtered_rows)

    if not filtered_df.empty:
        filtered_df["score"] = filtered_df.apply(lambda r: score_recipe(r, pantry_df), axis=1)
        filtered_df = filtered_df.sort_values("score", ascending=False)

    return filtered_df.head(25)



def load_pantry():
    conn = sqlite3.connect("food.db")
    df = pd.read_sql("SELECT item, expiryDate FROM Fridge", conn)
    conn.close()
    return df


def score_recipe(recipe_row, pantry_df):
    if pantry_df.empty:
        return 0

    recipe_ingredients = str(recipe_row["ingredient_lines"]).lower()

    score = 0

    for _, item in pantry_df.iterrows():
        name = str(item["item"]).lower()
        expiry = item["expiryDate"]

        if name in recipe_ingredients:
            score += 5

            if expiry:
                try:
                    days_left = (datetime.fromisoformat(expiry) - datetime.now()).days
                    if days_left <= 2:
                        score += 5
                    elif days_left <= 5:
                        score += 2
                except:
                    pass

    return score

