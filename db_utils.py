import sqlite3
import json

from entities.user import User
from entities.diet_requirements import Diet_Requirements

def add_profile(profile: User):
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    requirements_tuple = profile.requirements.requirements_vector
    requirements_json = json.dumps(requirements_tuple)

    cursor.execute("""
insert into user(name, requirements) values (?, ?)
""", [profile.name, requirements_json])
    connection.commit()
    connection.close()


def update_profile(profile: User):
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    requirements_tuple = profile.requirements.requirements_vector
    requirements_json = json.dumps(requirements_tuple)

    cursor.execute("""
    update user set requirements = ?, name = ? where userId = ?
    """, [requirements_json, profile.name, profile.id])
    connection.commit()
    connection.close()


def delete_profile(profile: User):
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    cursor.execute("""
                   delete from user where userId = ?
    """, [profile.id])
    connection.commit()
    connection.close()


def get_profile(name: str) -> User:
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    # NOTE: assumes name is unique identifier. We don't allow multiple users with the
    # same name
    cursor.execute("select * from user where name = ?", [name])

    user_db = cursor.fetchone()

    requirements_json = user_db[2]

    requirements_tuple = json.loads(requirements_json)

    diet_requirements = Diet_Requirements(requirements_tuple)

    user = User(user_db[0], user_db[1], diet_requirements)

    print("json:", requirements_json)

    return user


def get_all_profiles() -> list[User]:
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    cursor.execute("select * from user")

    profiles = cursor.fetchall()
    connection.close()

    users: list[User] = []
    for profile in profiles:
        requirements_json = profile[2]
        requirements_tuple = json.loads(requirements_json)
        users.append(User(profile[0], profile[1], Diet_Requirements(*requirements_tuple)))

    return users


def check_user_exists(id: int, name: str) -> bool:
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    name = name.lower()

    cursor.execute(
        "select count(*) from user where lower(name) = ? and userId <> ?", (name,id))

    return cursor.fetchone()[0] >= 1