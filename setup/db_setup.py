import os




import sqlite3 as sql
import pandas as pd

db_name = 'food.db'

print("Using DB at:", os.path.abspath(db_name))

# region UserTable 

connection = sql.connect(db_name)

cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS User;")

cursor.execute("""
               create table User(
userID integer primary key autoincrement,
name text,
requirements text -- e.g. vegetarian: [meat, fish]. Allergic vegan: [meat, fish, otherAnimalProduct, peanuts]
) ;""")

cursor.execute("DROP TABLE IF EXISTS Pantry;")

cursor.execute("""

create table Pantry(
ingredientID integer primary key autoincrement,
quantity integer,
expiryDate date);

""")

cursor.execute("drop table if exists Ingredient;")

cursor.execute("""
               create table Ingredient(
ingredientID integer primary key autoincrement,
name text,
category text, -- meat, fish, otherAnimalProduct, vegetable, fruit etc.
notSuitableFor text
)
""")

#cursor.commit()
connection.commit()
connection.close()

# endregion

# region recipeTable

df = pd.read_csv("recipes-with-nutrition.csv")

conn = sql.connect(db_name)

df.to_sql("recipes", conn, if_exists='replace', index=False)

conn.close()



# endregion

# region fridge table

connection = sql.connect(db_name)

cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS Fridge;")

cursor.execute("""
               create table Fridge(
item text unique,
quantity float,
units text,
expiryDate date
) ;""")

connection.commit()
connection.close()


# endregion

