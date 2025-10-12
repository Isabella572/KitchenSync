import sqlite3
import json

from entities.user import User

connection = sqlite3.connect('food.db')

def add_profile(profile: User):
    cursor = connection.cursor()

    requirements_tuple = profile.requirements.requirements_vector
    requirements_json = json.dumps(requirements_tuple)

    cursor.execute("""
insert into user(name, requirements) values (?, ?)
""", [profile.name, requirements_json])

