import utils
from city import City
from city import Zone
from unit import Unit
class Passenger(Unit):
    def __init__(self, t0, passenger_id, ozone:Zone, dzone:Zone):
        # 4 status: -1 cannot be served, 0 not picked up, 1 waited to be picked up, 2 traveling, 3 reached
        super().__init__(passenger_id, ozone, 0)
        self.id = passenger_id
        self.target_zone = dzone 
        self.dx, self.dy = self.target_zone.generate_location()
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
        # recorded choices for passengers
        self.dist_info = [0, 0, 0, 0, 0]
        # vertical detour status 
        self.vd_status = 0

    def update_dist_info(self, dist_info:list):
        self.dist_info = dist_info
        return 

    # return the trip distance from passenger's current location to the destination
    def dist(self):
        return abs(self.dx - self.x) + abs(self.dy - self.y)

    def odzone(self):
        return (self.zone.id, self.target_zone.id)

    def location(self):
        return (self.x, self.y), (self.dx, self.dy)

    def print(self):
        print(f"pos {(self.x, self.y)}, target pos {(self.dx, self.dy)}, zone {self.zone.id}, target zone{self.target_zone.id}")
        return 
