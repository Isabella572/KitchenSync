import db_utils as db

from entities.user import User


def add_profile(profile: User):
    db.add_profile(profile)
