import numpy as np
import math 
from tqdm import tqdm
import matplotlib.pyplot as plt
np.random.seed(2)
c = 100
fleet_size = 200
f = 10
oxs, oys = np.random.random(fleet_size), np.random.random(fleet_size)  
oxs[-1], oys[-1] = 0.5, 0.5
v = 0.01
num = 2000
def sign(num):
    num = float(num)
    return (num > 0) - (num < 0)
    
def force(dist):
    # maxdist = (1/fleet_size)**0.5*2
    # if dist >= maxdist:
    #     return 0
    return 5**(1/(dist+v))

def force_boundary(x, y, delta=(1/fleet_size/3.1415)**0.5):
    M = 10**6
    cx, cy = 0.5, 0.5
    xdir, ydir = sign(cx-x), sign(cy-y) 
    forcevec = np.array([M*((0.5-abs(cx-x))<delta)*xdir, M*(0.5-abs(cy-y)<delta)*ydir]) 
    return forcevec


x, y = [[] for i in range(fleet_size)], [[] for i in range(fleet_size)]
for t in tqdm(range(num)):
    for i in range(fleet_size):
        ox1, oy1 = oxs[i], oys[i]
        total_impulsion = np.array([0.0, 0.0])
        for j in range(fleet_size):
            if i == j:
                continue
            ox2, oy2 = oxs[j], oys[j]
            oo = np.array([sign(ox1-ox2)*force(abs(ox1-ox2)), sign(oy1-oy2)*force(abs(oy1-oy2))])
            total_impulsion += oo
        bf = force_boundary(ox1, oy1)
        alpha, beta = total_impulsion[0], total_impulsion[1]
        if bf[0] == 0 and bf[1] == 0:
            if abs(alpha) <= f*v and abs(beta) <= f*v:
                alpha_, beta_ = 0, 0
            else:
                alpha_, beta_ = alpha/(abs(alpha)+abs(beta)), beta/(abs(alpha)+abs(beta)) 
            oxs[i], oys[i] = oxs[i] + alpha_*v, oys[i] + beta_*v
        else:
            # oxs[i] += 0.9*sign(bf[0])*0.5*v + 0.1*(np.random.random()-0.5)*v
            # oys[i] += 0.9*sign(bf[1])*0.5*v + 0.1*(np.random.random()-0.5)*v
            oxs[i] += sign(bf[0])*0.5*v
            oys[i] += sign(bf[1])*0.5*v
        x[i].append(oxs[i])
        y[i].append(oys[i])

from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
  
xs = [[] for i in range(fleet_size)]
ys = [[] for i in range(fleet_size)]
fig, ax = plt.subplots()
  
# Setting limits for x and y axis
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

lines = []
for i in range(fleet_size):
    ln, = plt.plot([], [], 'ro', markersize = 2) 
    lines.append(ln)
        
def update(frame):
    for j in range(fleet_size):
        lines[j].set_data([x[j][frame], y[j][frame]])
    return *lines,

animation = FuncAnimation(fig, update, blit=True, frames = range(0, num, 1))
writergif = PillowWriter(15) 
animation.save("animation.gif", writer=writergif)
