import utils
from city import City
class Passenger:
    def __init__(self, t0, passenger_id, city:City):
        # t0 is the start time
        # passenger_id is od
        # city is City class object
        # connected is citylink
        self.id = passenger_id
        self.city = city
        if self.city.type_name == "Euclidean" or self.city.type_name == "Manhattan":    
            self.ox, self.oy = utils.generate_location(city)
            self.dx, self.dy = utils.generate_location(city)
        if city.type_name == "real-world":
            self.o_link, self.o_len = utils.generate_location(city)
            self.d_link, self.d_len = utils.generate_location(city)
        self.vehicle = None
        self.t_start = t0
        self.t_end = None
        self.status = "not picked up"

    def location(self):
        if self.city.type_name == "Euclidean" or self.city.type_name == "Manhattan":    
            return (self.ox, self.oy)
        
        if self.city.type_name == "real-world":
            x1, y1 = self.o_link.origin.x, self.o_link.origin.y 
            x2, y2 = self.o_link.destination.x, self.o_link.destination.y
            x3, y3 = None, None
            if (x1 == x2):
                x3 = x1
                if (y1 < y2):
                    y3 = y1 + self.o_len
                else:
                    y3 = y1 - self.o_len
                return (x3, y3)
            k = (y2 - y1)/(x2 - x1)
            if (x1 < x2):
                x3 = x1 + self.o_len / self.o_link.length * abs(x2 - x1)
                y3 = y1 + k*(x3 - x1)
            if (x1 > x2):
                x3 = x1 - self.o_len / self.o_link.length * abs(x2 - x1)
                y3 = y1 + k*(x3 - x1)   
            return (x3, y3)