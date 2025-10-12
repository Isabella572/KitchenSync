from entities.diet_requirements import Diet_Requirements


class User:
    def __init__(self, name: str, requirements: Diet_Requirements):
        self.name = name
        self.requirements = requirements
