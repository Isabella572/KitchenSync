# this reccomender.py it is where the recommendations are done through diet and allergy filtersing, pantry and behaviour based scoring and then the final reccomendations

import json
from datetime import datetime
import pandas as pd
import db_utils
from db_utils import parse_structured_column



#this extracts the food names from structed ingredient json
def get_food_names(ingredients_json):
    foods = set()
    for item in ingredients_json:
        if "food" in item:
            foods.add(item["food"].lower())
    return foods


#below is all the dietary filtering

#this filter based on allergies + vegiterian vegan and pescaterian
def recipe_matches_requirements(recipe_row, user_requirements):

    diet_labels = [
        str(label).lower()
        for label in parse_structured_column(recipe_row["diet_labels"])
    ]
    health_labels = parse_structured_column(recipe_row["health_labels"])
    cautions = [
        str(label).lower()
        for label in parse_structured_column(recipe_row["cautions"])
    ]

    req = user_requirements.lookup_table
    vec = user_requirements.requirements_vector

    health_labels_lower = [str(h).lower() for h in health_labels]

    if vec[req["isVegetarian"]] and "vegetarian" not in health_labels_lower:
        return False
    if vec[req["isVegan"]] and "vegan" not in health_labels_lower:
        return False
    if vec[req["isPescatarian"]]:
        fish_keywords = ["fish", "salmon", "tuna", "cod", "haddock", "prawn", "shrimp", "crab", "lobster", "seafood", "anchovy", "sardine", "mackerel", "trout", "tilapia", "bass", "halibut"]
        meat_keywords = ["beef", "pork", "chicken", "lamb", "turkey", "bacon", "ham", "veal", "duck", "venison", "sausage", "salami", "pepperoni"]
        ingredients_json = parse_structured_column(recipe_row["ingredients"])
        ingredient_names = [item.get("food", "").lower() for item in ingredients_json]
        has_fish = any(fish in ingredient for fish in fish_keywords for ingredient in ingredient_names)
        has_meat = any(meat in ingredient for meat in meat_keywords for ingredient in ingredient_names)
        if has_meat:
            return False
        # fish recipes are allowed through even if not tagged vegetarian
        if not has_fish and "vegetarian" not in health_labels_lower:
            return False
    
    allergy_map = {
        "hasDairy": "Dairy",
        "hasGluten": "Gluten",
        "hasEggs": "Egg",
        "hasFish": "Fish",
        "hasShellfish": "Shellfish",
        "hasTreeNuts": "Tree-Nuts",
        "hasPeanuts": "Peanuts",
        "hasSoy": "Soy" }

    for key, label in allergy_map.items():
        if vec[req[key]] and label in cautions:
            return False

    return True


#below is all the pantry scoring

#this scored based on ingredient matches and expiry priority. it returns a decimal score between 0 and 1
def score_pantry(recipe_row, pantry_items):

    ingredients_json = parse_structured_column(recipe_row["ingredients"])

    if not ingredients_json:
        return 0, 0

    matched = 0
    expiring_count = 0
    already_matched = set()
    total_ingredients = len(ingredients_json)

    for ingredient in ingredients_json:

        recipe_food = (ingredient.get("food") or "").lower()
        recipe_quantity = ingredient.get("quantity", 0)
        recipe_unit = (ingredient.get("measure") or "").lower()

        for _, pantry_item, pantry_quantity, pantry_unit, expiry_date, _ in pantry_items:

            if pantry_item.lower() in recipe_food or recipe_food in pantry_item.lower():
                if recipe_food not in already_matched:
                    already_matched.add(recipe_food)
                    if pantry_unit and recipe_unit and pantry_unit.lower() == recipe_unit:
                        if pantry_quantity >= recipe_quantity:
                            matched += 1
                    else:
                        matched += 1

                # Expiry tracking
                if expiry_date:
                    try:
                        days_left = (datetime.fromisoformat(expiry_date) - datetime.now()).days
                        if days_left < 0:
                            expiring_count += 1.0   #full weight
                        elif days_left <= 5:
                            expiring_count += 0.5   # half weight
                    except:
                        pass

                break  

    pantry_match = matched / total_ingredients
    expiry_priority = expiring_count / total_ingredients

    return pantry_match, expiry_priority



#below is all the behavior scoring

# this is based on similarity to previous recipes through ratings and favourites
def score_behaviour(recipe_row, user_history_df, recipes_lookup):

    if user_history_df.empty:
        return 0
    recipe_name = recipe_row["recipe_name"]
    recipe_ingredients = get_food_names(parse_structured_column(recipe_row["ingredients"]))
    recipe_cuisine = set(parse_structured_column(recipe_row["cuisine_type"]))
    recipe_diets = set(parse_structured_column(recipe_row["diet_labels"]))
    similarity_scores = []
    rating_bonus = 0
    favourite_bonus = 0

# Group interactions by recipe to prevent stacking
    grouped_history = user_history_df.groupby("recipe_name")

    for interacted_name, interactions in grouped_history:

        if interacted_name not in recipes_lookup.index:
            continue

        match_row = recipes_lookup.loc[interacted_name]
        match_ingredients = get_food_names(parse_structured_column(match_row["ingredients"]))
        match_cuisine = set(parse_structured_column(match_row["cuisine_type"]))
        match_diets = set(parse_structured_column(match_row["diet_labels"]))

        # Ingredient similarity
        ingredient_union = recipe_ingredients | match_ingredients
        if ingredient_union:
            ingredient_similarity = len(recipe_ingredients & match_ingredients) / len(ingredient_union)
        else:
            ingredient_similarity = 0

        # Cuisine similarity
        cuisine_similarity = 1 if recipe_cuisine & match_cuisine else 0

        # Diet similarity
        diet_similarity = 1 if recipe_diets & match_diets else 0

        similarity = (ingredient_similarity + cuisine_similarity + diet_similarity) / 3
        similarity_scores.append(similarity)

        # Rating bonus (use highest rating only)
        rated_rows = interactions[interactions["action"] == "rated"]
        if not rated_rows.empty:
            max_rating = rated_rows["rating"].max()
            rating_bonus += (max_rating / 5) * 0.25

        # Favourite bonus (apply once)
        if any(interactions["action"] == "favourite"):
            favourite_bonus += 0.3


    if similarity_scores:
        base_similarity = sum(similarity_scores) / len(similarity_scores)
    else:
        base_similarity = 0
    intent_bonus = 0.05 if not user_history_df.empty else 0
    final_score = base_similarity + rating_bonus + favourite_bonus + intent_bonus

    return min(final_score, 1)


#the main recommendations function

#this returns the ranked recipes ddataframe
def recommend_recipes(user_requirements):

    recipes_df = db_utils.load_recipes()

    sample = recipes_df["diet_labels"].dropna().head(3).tolist()
    print("Diet labels sample:", sample)

    pantry_items = db_utils.get_all_pantry_items()
    user_history = db_utils.get_user_history()
    filtered = []
    for _, row in recipes_df.iterrows():
        # skip recipes with fewer than 5 ingredients
        ingredients = parse_structured_column(row["ingredients"])
        if len(ingredients) < 5:
            continue
        if recipe_matches_requirements(row, user_requirements):
            filtered.append(row)

    filtered_df = pd.DataFrame(filtered)
    if filtered_df.empty:
        empty_df = pd.DataFrame()
        return empty_df, empty_df
    
    recipes_lookup = recipes_df.set_index("recipe_name")

    layer1_scores = []
    layer2_scores = []
    pantry_scores = []

    for _, row in filtered_df.iterrows():

        pantry_match, expiry_priority = score_pantry(row, pantry_items)
        behaviour_score = score_behaviour(row, user_history, recipes_lookup)

        #layer 1 reccomended for you
        layer1_score = (
            (behaviour_score * 0.8) +
            (pantry_match * 0.1) +
            (expiry_priority * 0.1)
        )

        #layer two using owned ingredients
        layer2_score = (
            (expiry_priority * 0.55) +
            (pantry_match * 0.35) +
            (behaviour_score * 0.1)
        )

        layer1_scores.append(layer1_score)
        layer2_scores.append(layer2_score)
        pantry_scores.append(pantry_match)

    filtered_df["layer1_score"] = layer1_scores
    filtered_df["layer2_score"] = layer2_scores
    filtered_df["pantry_match"] = pantry_scores

    layer1_df = filtered_df.sort_values(
        by="layer1_score",
        ascending=False
    )

    layer2_df = filtered_df.sort_values(
        by="layer2_score",
        ascending=False
    )

    return layer1_df, layer2_df

