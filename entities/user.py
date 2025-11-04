from entities.diet_requirements import Diet_Requirements


class User:
    def __init__(self, id: int, name: str, requirements: Diet_Requirements):
        self.id = id
        self.name = name
        self.requirements = requirements
