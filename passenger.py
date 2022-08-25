import utils
from city import City
from city import Zone
from unit import Unit
class Passenger(Unit):
    def __init__(self, t0, passenger_id, zone:Zone):
        # 4 status: -1 cannot be served, 0 not picked up, 1 waited to be picked up, 2 traveling, 3 reached
        super().__init__(passenger_id, zone, 0)
        self.id = passenger_id
        self.zone = zone
        
        
        # Function need to be changed to let pax flow between cities
        if self.zone.type_name == "Euclidean" or self.zone.type_name == "Manhattan":    
            self.dx, self.dy = self.zone.generate_location()
            self.target_zone = Zone()
        
        
        
        
        
        
        self.vehicle = None
        # time when passenger appears
        self.t_start = t0
        # time when passenger is assigned
        self.t_a = None
        # time when passenger is picked up
        self.t_s = None
        # time when passenger is reached 
        self.t_end = None
        # ride sharing status can be either 0:caller or 1:seeker 
        self.rs_status = None

    # return the trip distance from passenger's current location to the destination
    def dist(self):
        if self.zone.type_name == "Euclidean":
            return ((self.dx - self.x)**2 + (self.dy - self.y)**2)**(0.5)

        elif self.zone.type_name == "Manhattan":
            return abs(self.dx - self.x) + abs(self.dy - self.y)

    # return whether the passenger is shared
    def isShared(self):
        self.shared = True
        return 

    def location(self):
        if self.zone.type_name == "Euclidean" or self.zone.type_name == "Manhattan":    
            return (self.x, self.y), (self.dx, self.dy)