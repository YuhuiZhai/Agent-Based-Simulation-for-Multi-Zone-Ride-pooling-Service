import numpy as np

def assign_type():
        table = {"1":"Euclidean", "2":"Manhattan", "3":"real-world", 
                "Euclidean":"Euclidean", "Manhattan":"Manhattan", "real-world":"real-world"}
        print("Please enter the type of city? \n [1: Euclidean, 2:Manhattan, 3:real-world]")
        answer = input()
        if answer in table.keys():
            return table[answer]
        else:
            print("Wrong input, please try again")
            return 

class City:
    def __init__(self, type_name="", length=3.6, max_v=18.0, origin=(0, 0), id=0):
        # 3 types: Eucledean, Manhatten, real-world
        self.type_name, self.length, self.max_v, self.origin, self.id = type_name, length, max_v, origin, id
        self.rng = np.random.default_rng(seed=3)
        if (self.type_name == ""):
            type = assign_type()
            while (type == None):
                type = assign_type()
            self.type_name = type

    def set_origin(self, new_origin:tuple):
        self.origin = new_origin
        return
    
    def generate_location(self):
        if self.type_name == "Euclidean" or self.type_name == "Manhattan":  
            x = self.origin[0] + self.length*self.rng.random()
            y = self.origin[1] + self.length*self.rng.random()
            return x, y 
