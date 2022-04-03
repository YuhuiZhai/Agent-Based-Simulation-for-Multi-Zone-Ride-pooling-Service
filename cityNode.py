class CityNode:
    def __init__(self, id, x, y):
        # x, y is the longnitude and latitude
        self.id = int(id)
        self.x = x
        self.y = y
        # neighbour citynode
        self.neighbour = {}
        # citylink between this node and neighbour citynode
        self.adjacent = {}
        # distance of citylink between this node and neighbour citynode
        self.dist2neighbour = {}

    def add_link(self, next_node, link):
        # next_node is added citynode
        # link is added citylink
        self.neighbour[next_node.id] = next_node
        self.adjacent[link.id] = link
        self.dist2neighbour[next_node.id] = link.length

