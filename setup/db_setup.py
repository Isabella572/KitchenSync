import sqlite3 as sql

connection = sql.connect('../food.db')

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





