from asyncio.windows_events import NULL
import math
import random 
def distance(node_1, node_2):
    lo1_ = node_1.x
    la1_ = node_1.y
    lo2_ = node_2.x
    la2_ = node_2.y
    return distance_helper(lo1_, la1_, lo2_, la2_)

def onplotdist(node_1, node_2):
        lo1 = node_1.x
        la1 = node_1.y
        lo2 = node_2.x
        la2 = node_2.y
        return ((lo1 - lo2)**2 + (la1 - la2)**2)**(1/2)

def distance_helper(lo1, la1, lo2, la2):
    # approximate radius of earth in km
    R = 6371
    lat1 = math.radians(la1)
    lon1 = math.radians(lo1)
    lat2 = math.radians(la2)
    lon2 = math.radians(lo2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    dist = R * c
    return dist

def generate_location(city):
    """
    generate a random location on a link
    `city`: City
    `return`: (x, y) or (city link, distance from link's node_o)
    """
    if city.type_name == "Euclidean" or city.type_name == "Manhattan":  
        x = 0.06*random.random()
        y = 0.06*random.random()
        return x, y 

    if city.type_name == "real-world":
        n_max = city.num_link
        idx = random.randint(0, n_max-1)
        l = random.random() * city.links[idx].length / 2
        return city.links[idx], l


def dist(city, o_link, o_len, d_link, d_len):
    """
    Get the distance from one link to the other link
    `o_link`: CityLink, starting link
    `o_len`: distance from starting link
    `d_link`: CityLink, end link
    `d_len`: distance from ending link  
    `return`: distance 
    """
    dist, path = city.dijkstra(o_link.origin.id, d_link.origin.id)
    if dist == -1:
        return -1
    dist = dist - o_len + d_len  
    return dist


def get_path(city, o_link, o_len, d_link, d_len):
    """
    Get path
    `city`: class City 
    `o_link`: citylink
    `o_len`: distance from o_link's o_node 
    `d_link`: citylink 
    `d_len`: distance from d_link's o_node 
    `return`: path[ ], total path length 
    """
    if (o_link.id == d_link.id):
        print("edge case")
        return -1, NULL

    ret_dist = city.dj_path[o_link.origin.id, d_link.origin.id][0] - o_len + d_len
    ret_path = city.dj_path[o_link.origin.id, d_link.origin.id][1]

    return ret_path, ret_dist

