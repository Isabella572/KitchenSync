class Diet_Requirements:
    def __init__(
            self,
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
            hasSoy=False,

    ):
        self.requirements_vector = (
            isVegetarian,
            isVegan,
            isPescatarian,
            hasDairy,
            hasGluten,
            hasEggs,
            hasFish,
            hasShellfish,
            hasTreeNuts,
            hasPeanuts,
            hasSoy,
        )

        #key: meaning; val: index of lookup
        self.lookup_table = {
        "isVegetarian": 0,
        "isVegan": 1,
        "isPescatarian": 2,
        "hasDairy": 3,
        "hasGluten": 4,
        "hasEggs": 5,
        "hasFish": 6,
        "hasShellfish": 7,
        "hasTreeNuts": 8,
        "hasPeanuts": 9,
        "hasSoy": 10,
    }


        self.requirement_from_index = {v: k for k, v in self.lookup_table.items()}