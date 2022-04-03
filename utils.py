from asyncio.windows_events import NULL
import math
import random 
def distance(node_1, node_2):
    lo1_ = node_1.x
    la1_ = node_1.y
    lo2_ = node_2.x
    la2_ = node_2.y
    return distance_helper(lo1_, la1_, lo2_, la2_)

def distance_helper(lo1, la1, lo2, la2):
    # approximate radius of earth in km
    R = 6373000

    lat1 = math.radians(la1)
    lon1 = math.radians(lo1)
    lat2 = math.radians(la2)
    lon2 = math.radians(lo2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    dist = R * c
    return dist/1000


def solve_three(m, lamda):
    a = m/lamda - 2/3
    err = 1e-6

    diff = 1
    x1 = 0
    while diff > err:
        #print(a, x1)
        new_x = math.sqrt(math.pi)/(math.sqrt(8*lamda)*math.sqrt(a-x1))
        diff = abs(new_x - x1)
        x1 = new_x

    diff = 1
    x2 = a
    while diff > err:
        new_x = a - math.pi/(8*lamda*x2*x2)
        diff = abs(new_x - x2)
        x2 = new_x

    return x1, x2


def fleet_status(m, lamda):
    lamda *= 0.1
    x1, x2 = solve_three(m, lamda)
    in_service = lamda*2/3
    assigned_1 = lamda*x1
    assigned_2 = lamda*x2
    idle_1 = m - in_service - assigned_1
    idle_2 = m - in_service - assigned_2
    status_1 = (idle_1, assigned_1, in_service)
    status_2 = (idle_2, assigned_2, in_service)
    return status_1, status_2


def generate_location(city, connected: dict):
    """
    generate a random location on a link
    `city`: City
    `connected`: in-neigh node list
    `return`: (city link, distance from link's node_o)
    """
    n_max = city.num_link
    idx = -1
    while True:
        n = random.randint(0, n_max-1)
        node = city.links[n].origin
        if node.id in connected:
            idx = n
            break

    l_max = city.links[idx].length
    l = random.random() * l_max
    return city.links[idx], l


def dist(city, o_id, o_len, d_id,d_len):
    """
    Get the distance from one link to the other link
    `o_id`: id of starting link
    `o_len`: distance from starting link
    `d_id`: id of end link
    `d_len`: distance from ending link  
    `return`: distance 
    """
    ret = 0
    if (o_id.destination.id, d_id.origin.id) in city.dj_path.keys():
        ret += city.dj_path[o_id.destination.id, d_id.origin.id][0]
    else:
        print("error not connected:")
        print(o_id.destination.id, d_id.origin.id)
        return 1
    ret += o_id.length - o_len
    ret += d_len
    return ret


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

    dist, opt_path = city.dj_path[o_link.destination.id, d_link.origin.id]

    # real distance is the distance of shortest path plus two random lengths 
    ret_dist = dist - o_len + d_len

    # path_tuple = [current link, current link len, next link, next_len]
    ret_path = []

    # radom starting path
    first_path = city.links[city.map(opt_path[0], opt_path[1])]
    ret_path.append([o_link, o_len, first_path, first_path.length])

    for i in range(len(opt_path) - 2):
        path_info = []
        link_id_1 = city.map(opt_path[i], opt_path[i+1])
        link_id_2 = city.map(opt_path[i+1], opt_path[i+2])
        link_1 = city.links[link_id_1]
        link_2 = city.links[link_id_2]

        path_info.append(link_1)
        path_info.append(link_1.length)
        path_info.append(link_2)
        path_info.append(link_2.length)
        
        ret_path.append(path_info)
    
    # random ending point
    last_path = city.links[city.map(opt_path[-2], opt_path[-1])]
    ret_path.append([last_path, last_path.length, d_link, d_len])

    return ret_path, ret_dist
