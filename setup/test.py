import sqlite3 as sql
import pandas as pd

conn = sql.connect("food.db")

cursor = conn.cursor()

cursor.execute("select * from recipes limit 1")

print(cursor.fetchone())