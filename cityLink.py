import utils
class CityLink:
    def __init__(self, id, origin, destination):
        self.id = int(id)
        # origin and destination citynode
        self.origin = origin
        self.destination = destination
        self.ox = self.origin.x
        self.oy = self.origin.y
        self.dx = self.destination.x
        self.dy = self.destination.y
        self.length = utils.distance(self.origin, self.destination)
