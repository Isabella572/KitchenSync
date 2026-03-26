#this is diet_requirements.py it stores the users dietary needs as a vector and lookup table and is used by the recommender and profile system to filter out any unsafe recipes

class Diet_Requirements:
    def __init__(self,
            isVegetarian=False,
            isVegan=False,
            isPescatarian=False,
            hasDairy=False,    
            hasGluten=False,
            hasEggs=False,
            hasFish=False,
            hasShellfish=False,
            hasTreeNuts=False,
            hasPeanuts=False,
            hasSoy=False,):
        
        #it stores all the requirements as an ordered tuple so they can be passed to database as a sequence of values
        self.requirements_vector = (isVegetarian,
            isVegan,
            isPescatarian,
            hasDairy,
            hasGluten,
            hasEggs,
            hasFish,
            hasShellfish,
            hasTreeNuts,
            hasPeanuts,
            hasSoy,)

        #this maps each requirement name to its index in the vector so that values are accesed by name not position
        self.lookup_table = {"isVegetarian": 0,
            "isVegan": 1,
            "isPescatarian": 2,
            "hasDairy": 3,
            "hasGluten": 4,
            "hasEggs": 5,
            "hasFish": 6,
            "hasShellfish": 7,
            "hasTreeNuts": 8,
            "hasPeanuts": 9,
            "hasSoy": 10,}

        self.requirement_from_index = {v: k for k, v in self.lookup_table.items()}