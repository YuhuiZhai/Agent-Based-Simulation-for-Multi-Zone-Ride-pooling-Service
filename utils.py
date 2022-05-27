from asyncio.windows_events import NULL
import math
import random 
def onplotdist(node_1, node_2):
        lo1 = node_1.x
        la1 = node_1.y
        lo2 = node_2.x
        la2 = node_2.y
        return 60 * ((lo1 - lo2)**2 + (la1 - la2)**2)**(1/2)

def generate_location(city):
    """
    generate a random location on a link
    `city`: City
    `return`: (x, y) or (city link, distance from link's node_o)
    """
    if city.type_name == "Euclidean" or city.type_name == "Manhattan":  
        x = city.origin[0] + city.length*random.random()
        y = city.origin[1] + city.length*random.random()
        return x, y 

    if city.type_name == "real-world":
        n_max = city.num_link
        idx = random.randint(0, n_max-1)
        l = random.random() * city.links[idx].length / 2
        return city.links[idx], l

def optimal_M(city, arrival_rate):
    if city.type_name == "real-world":
        print("real-world fleet size must be defined")
        return -1
    k = 0.5
    l = 2**(1/2)*2/3*city.length
    if city.type_name == "Manhattan":
        k = 0.63
        l = 2/3*city.length
    R = city.length**2
    v = city.max_v
    lmdR = arrival_rate
    opt_Ta = (2*k**2*R/v**2/lmdR)**(1/3)
    opt_M = k**2*R/(v*opt_Ta)**2 + lmdR*opt_Ta + lmdR*l/v
    return opt_M


    