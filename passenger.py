import utils
from city import City
from city import Zone
from unit import Unit
class Passenger(Unit):
    def __init__(self, t0, passenger_id, ozone:Zone, dzone:Zone):
        # 4 status: -1 cannot be served, 0 not picked up, 1 waited to be picked up, 2 traveling, 3 reached
        super().__init__(passenger_id, ozone, 0)
        self.id = passenger_id
        self.ozone, self.dzone = ozone, dzone 
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
        return abs(self.dx - self.x) + abs(self.dy - self.y)

    def location(self):
        return (self.x, self.y), (self.dx, self.dy)
    
    def assignTargetZone(self, zone:Zone):
        self.target_zone = zone
        self.dx, self.dy = self.target_zone.generate_location()

    def print(self):
        print(f"pos {(self.x, self.y)}, target pos {(self.dx, self.dy)}, zone {self.zone.id}, target zone{self.target_zone.id}")
        return 