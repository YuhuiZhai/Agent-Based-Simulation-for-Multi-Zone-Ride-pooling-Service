import pandas as pd
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

def optimal(city, arrival_rate):
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
    opt_ni = k**2*R/(v*opt_Ta)**2
    opt_na = lmdR*opt_Ta 
    opt_ns = lmdR*l/v
    opt_M = opt_ni + opt_na + opt_ns 
    return opt_Ta, opt_ni, opt_na, opt_ns, opt_M


def zip_csv(namelist:list, datalist:list, name="data"):
    data_table = {}
    for i in range(len(namelist)):
        data_table[namelist[i]] = datalist[i] 
    output = pd.DataFrame(data_table)
    output.to_csv(name+'.csv')

def location_helper(link, len):
    x1, y1 = link.origin.x, link.origin.y
    x2, y2 = link.destination.x, link.destination.y
    x3, y3 = None, None
    if (x1 == x2):
        x3 = x1
        if (y1 < y2): y3 = y1 + len
        else: y3 = y1 - len
        return (x3, y3)
    k = (y2 - y1)/(x2 - x1)
    if (x1 < x2):
        x3 = x1 + len / link.length * abs(x2 - x1)
        y3 = y1 + k*(x3 - x1)
    if (x1 > x2):
        x3 = x1 - len / link.length * abs(x2 - x1)
        y3 = y1 + k*(x3 - x1)   
    return (x3, y3)

def func(l:list, dx:float):
    l.sort()
    left = dx
    curr = 0
    distri = []
    if len(l) == 0: return []
    while True:
        count = 0
        while l[curr] <= left:
            count += 1
            curr += 1
            if curr == len(l):
                return distri
        distri.append((left, left+dx, count))
        left += dx