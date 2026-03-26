#this is recommender.py, the core algorithm, it takes the diet requirements, pantry contents, behavior hostory and returns two ranked dataframes

import json
from datetime import datetime
import pandas as pd
import db_utils
from db_utils import parse_structured_column


def get_food_names(ingredients_json):
    #gets ingredient names from structured json into a set
    foods = set()
    for item in ingredients_json:
        if "food" in item:
            foods.add(item["food"].lower())
    return foods


#diet filtering

def recipe_matches_requirements(recipe_row, user_requirements):
    #only returns true if recipe satisfies every requirement from every selected profile. if a recipe is not sure its treated as unsafe just incase

    diet_labels = [str(label).lower()
        for label in parse_structured_column(recipe_row["diet_labels"])]
    health_labels = parse_structured_column(recipe_row["health_labels"])
    cautions = [str(label).lower()
        for label in parse_structured_column(recipe_row["cautions"])]

    req = user_requirements.lookup_table
    vec = user_requirements.requirements_vector
    health_labels_lower = [str(h).lower() for h in health_labels]

    #diet type checks
    if vec[req["isVegetarian"]] and "vegetarian" not in health_labels_lower:
        return False
    if vec[req["isVegan"]] and "vegan" not in health_labels_lower:
        return False

    # pescatarian logic is more complex than the others because it is not a standard dataset tag in the csv file so it has to be inferred from the ingredient list.
    #so a recipe is allowed if it contains fish OR is vegetarian, but never if it contains meat.
    if vec[req["isPescatarian"]]:
        fish_keywords = [
            "fish", "salmon", "tuna", "cod", "haddock", "prawn", "shrimp",
            "crab", "lobster", "seafood", "anchovy", "sardine", "mackerel",
            "trout", "tilapia", "bass", "halibut"
        ]
        meat_keywords = [
            "beef", "pork", "chicken", "lamb", "turkey", "bacon", "ham",
            "veal", "duck", "venison", "sausage", "salami", "pepperoni"
        ]
        ingredients_json = parse_structured_column(recipe_row["ingredients"])
        ingredient_names = [item.get("food", "").lower() for item in ingredients_json]
        has_fish = any(fish in ingredient for fish in fish_keywords for ingredient in ingredient_names)
        has_meat = any(meat in ingredient for meat in meat_keywords for ingredient in ingredient_names)
        if has_meat:
            return False
        if not has_fish and "vegetarian" not in health_labels_lower:
            return False

    # allergy checks
    allergy_map = {"hasDairy":    "Dairy",
        "hasGluten":   "Gluten",
        "hasEggs":     "Egg",
        "hasFish":     "Fish",
        "hasShellfish":"Shellfish",
        "hasTreeNuts": "Tree-Nuts",
        "hasPeanuts":  "Peanuts",
        "hasSoy":      "Soy",}
    for key, label in allergy_map.items():
        if vec[req[key]] and label in cautions:
            return False

    return True


#pantry scoring

def score_pantry(recipe_row, pantry_items):
    # calculates two scores for a recipe based on what the user owns, pantry match and expiry
    # expiry weighting prioritises recipes that use up food before it is wasted.

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
                    # if units match, also check quantity is sufficient if units don't match (eg recipe says "cup", pantry says "ml") counts as matched anyway to avoid penalising unit mismatches
                    if pantry_unit and recipe_unit and pantry_unit.lower() == recipe_unit:
                        if pantry_quantity >= recipe_quantity:
                            matched += 1
                    else:
                        matched += 1

                if expiry_date:
                    try:
                        days_left = (datetime.fromisoformat(expiry_date) - datetime.now()).days
                        if days_left < 0:
                            expiring_count += 1.0  #already expired is full urgency
                        elif days_left <= 5:
                            expiring_count += 0.5  #expiring soon is partial urgency
                    except:
                        pass
                break

    pantry_match = matched / total_ingredients
    expiry_priority = expiring_count / total_ingredients
    return pantry_match, expiry_priority


#behavior scoring

def score_behaviour(recipe_row, user_history_df, recipes_lookup):
    #scores a recipe based on how similar it is to recipes the user has previously interacted with (rated, favourited, or added to shopping list).
    # similarity is calculated across three dimensions: ingredients, cuisine and diet then the similarity is scaled by ratings and favourites
    #the final score is the average weighted similarity across all interacted recipes + a small intent bonus if this specific recipe was previously added to the shopping list.

    if user_history_df.empty:
        return 0

    recipe_name = recipe_row["recipe_name"]
    recipe_ingredients = get_food_names(parse_structured_column(recipe_row["ingredients"]))
    recipe_cuisine = set(parse_structured_column(recipe_row["cuisine_type"]))
    recipe_diets = set(parse_structured_column(recipe_row["diet_labels"]))
    similarity_scores = []

    #group by recipe so each interacted recipe is only processed once
    grouped_history = user_history_df.groupby("recipe_name")

    for interacted_name, interactions in grouped_history:

        if interacted_name not in recipes_lookup.index:
            continue

        match_row = recipes_lookup.loc[interacted_name]
        match_ingredients = get_food_names(parse_structured_column(match_row["ingredients"]))
        match_cuisine = set(parse_structured_column(match_row["cuisine_type"]))
        match_diets = set(parse_structured_column(match_row["diet_labels"]))

        # gives a value between 0 (no shared ingredients) and 1 (identical)
        ingredient_union = recipe_ingredients | match_ingredients
        if ingredient_union:
            ingredient_similarity = len(recipe_ingredients & match_ingredients) / len(ingredient_union)
        else:
            ingredient_similarity = 0

        cuisine_similarity = 1 if recipe_cuisine & match_cuisine else 0
        diet_similarity = 1 if recipe_diets & match_diets else 0

        similarity = (ingredient_similarity + cuisine_similarity + diet_similarity) / 3

        #scales similarity by rating 
        rated_rows = interactions[interactions["action"] == "rated"]
        if not rated_rows.empty:
            max_rating = rated_rows["rating"].max()
            similarity = similarity * (max_rating / 5)

        #further boost if the recipe was favourited
        if any(interactions["action"] == "favourite"):
            similarity = min(similarity * 1.5, 1.0)

        similarity_scores.append(similarity)

    base_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0

    #small bonus if this exact recipe was previously added to the shopping list
    intent_bonus = 0.05 if not user_history_df[
        (user_history_df["recipe_name"] == recipe_name) &
        (user_history_df["action"] == "shopping_list")
    ].empty else 0

    return min(base_similarity + intent_bonus, 1)


#combines scores and ranks

def recommend_recipes(user_requirements):
    #loads all recipes, applies dietary filtering, scores each one and returns two sorted dataframes for the two home page layers.
    # if there is no history yet layer 1 is shuffled randomly so it looks different from layer 2 even before personalisation has begun.

    recipes_df = db_utils.load_recipes()
    pantry_items = db_utils.get_all_pantry_items()
    user_history = db_utils.get_user_history()

    #dietary filtering. recipes with fewer than 5 ingredients are skipped as they tend to be incomplete or poorly formatted entries in the dataset
    filtered = []
    for _, row in recipes_df.iterrows():
        ingredients = parse_structured_column(row["ingredients"])
        if len(ingredients) < 5:
            continue
        if recipe_matches_requirements(row, user_requirements):
            filtered.append(row)

    filtered_df = pd.DataFrame(filtered)
    if filtered_df.empty:
        empty_df = pd.DataFrame()
        return empty_df, empty_df

    #index by recipe name for fast lookup during behaviour scoring
    recipes_lookup = recipes_df.set_index("recipe_name")

    #score every filtered recipe
    layer1_scores = []
    layer2_scores = []
    pantry_scores = []

    for _, row in filtered_df.iterrows():
        pantry_match, expiry_priority = score_pantry(row, pantry_items)
        behaviour_score = score_behaviour(row, user_history, recipes_lookup)

        layer1_score = ((behaviour_score * 0.8) + (pantry_match * 0.1) + (expiry_priority * 0.1))
        layer2_score = ((expiry_priority * 0.55) + (pantry_match * 0.35) + (behaviour_score * 0.1))

        layer1_scores.append(layer1_score)
        layer2_scores.append(layer2_score)
        pantry_scores.append(pantry_match)

    filtered_df["layer1_score"] = layer1_scores
    filtered_df["layer2_score"] = layer2_scores
    filtered_df["pantry_match"] = pantry_scores

    #sort and return
    layer2_df = filtered_df.sort_values(by="layer2_score", ascending=False)

    if user_history.empty:
        #if theres no history yet then shuffle layer 1 so it looks different from layer 2
        layer1_df = filtered_df.sample(frac=1, random_state=42).reset_index(drop=True)
    else:
        layer1_df = filtered_df.sort_values(by="layer1_score", ascending=False)

    #this excludes the top 20 recipes from layer 1 from layer 2 so it doesnt suggest the same recipes at the start when theres little or no hisgtory
    layer1_names = set(layer1_df["recipe_name"])
    layer2_df = layer2_df[~layer2_df["recipe_name"].isin(layer1_names)]

    return layer1_df, layer2_df

