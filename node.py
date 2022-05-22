from vehicle import Vehicle
from passenger import Passenger
class Node:
    def __init__(self, time, event_type, vehicle:Vehicle, passenger:Passenger):
        self.time = time
        self.type = event_type
        self.vehicle = vehicle
        self.passenger = passenger
