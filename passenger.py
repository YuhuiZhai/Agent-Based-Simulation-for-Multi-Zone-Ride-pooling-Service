import utils
class Passenger:
    def __init__(self, t0, passenger_id, city, connected):
        # t0 is the start time
        # passenger_id is od
        # city is City class object
        # connected is citylink

        self.id = passenger_id
        self.o_node, self.o_len = utils.generate_location(city, connected)
        self.d_node, self.d_len = utils.generate_location(city, connected)
        self.pick_up = None
        self.deliver = None
        self.trip = (city, self.o_node, self.o_len, self.d_node, self.d_len)
        self.vehicle = None
        self.t_start = t0
        self.t_end = None

    def xy(self, city):
        ox = city.links[self.o_node.id].ox
        oy = city.links[self.o_node.id].oy
        dx = city.links[self.o_node.id].dx
        dy = city.links[self.o_node.id].dy
        diff_x = dx-ox
        diff_y = dy-oy
        if city.links[self.o_node.id].length == 0:
            print("link length = 0:")
            print(self.o_node.id)
            return ox, oy
        else:
            percentage = self.o_len/city.links[self.o_node.id].length
            return ox+percentage*diff_x, oy+percentage*diff_y

