import utils
from city import City
from unit import Unit
class Passenger(Unit):
    def __init__(self, t0, passenger_id, city:City):
        # 4 status: -1 cannot be served, 0 not picked up, 1 waited to be picked up, 2 traveling, 3 reached
        super().__init__(passenger_id, city, 0)
        self.id = passenger_id
        self.city = city
        if self.city.type_name == "Euclidean" or self.city.type_name == "Manhattan":    
            self.dx, self.dy = utils.generate_location(city)
        if city.type_name == "real-world":
            self.d_link, self.d_len = utils.generate_location(city)
        self.vehicle = None
        # time when passenger appears
        self.t_start = t0
        # time when passenger is picked up
        self.t_s = None
        # time when passenger is reached 
        self.t_end = None
        self.shared = False
    def isShared(self):
        self.shared = True
        return 

    def location(self):
        if self.city.type_name == "Euclidean" or self.city.type_name == "Manhattan":    
            return (self.x, self.y), (self.dx, self.dy)
        
        if self.city.type_name == "real-world":
            ox, oy = utils.location_helper(self.link, self.len) 
            dx, dy = utils.location_helper(self.d_link, self.d_len) 
            return (ox, oy), (dx, dy)