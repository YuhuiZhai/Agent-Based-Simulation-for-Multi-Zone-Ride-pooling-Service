from multiprocessing import Event
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from city import City
from fleet import Fleet
from eventQueue import EventQueue
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter

class Animation:
    def __init__(self, city:City, fleet_info:list, passenger_info:list):
        self.city = city
        self.fleet_info = fleet_info
        self.passenger_info = passenger_info
    
    def plot(self, compression, fps, path=""):
        fig, ax = plt.subplots()
        self.city.sketch()
        ln1, = plt.plot([], [], 'yo', markersize = 7)
        ln2, = plt.plot([], [], 'ro', markersize = 7)
        ln3, = plt.plot([], [], 'go', markersize = 7)
        ln4, = plt.plot([], [], 'k*', markersize = 10)
        ln5, = plt.plot([], [], 'bv', markersize = 7)

        a, s, i, inter = self.fleet_info[0]
        p = self.passenger_info[0]
        def update(frame):
            a, s, i, inter = self.fleet_info[frame]   
            p = self.passenger_info[frame]
            ln1.set_data(a[0], a[1])
            ln2.set_data(s[0], s[1])
            ln3.set_data(i[0], i[1])
            ln4.set_data(inter[0], inter[1])
            ln5.set_data(p[0], p[1])
            return ln1, ln2, ln3, ln4, ln5

        animation = FuncAnimation(fig, update, blit=True, frames = range(0, len(self.fleet_info), compression))
        
        if self.city.type_name == "Euclidean" or self.city.type_name == "Manhattan":  
            plt.xlim(0, self.city.length)
            plt.ylim(0, self.city.length)
            ax.text(5/6*self.city.length, 1/6*self.city.length, "in service", color = 'r',  fontsize = 10)
            ax.text(5/6*self.city.length, 0.8/6*self.city.length, "assigned", color = 'y', fontsize = 10)
            ax.text(5/6*self.city.length, 0.6/6*self.city.length, "idle", color = 'g', fontsize = 10)
            ax.text(5/6*self.city.length, 0.4/6*self.city.length, "inter", color = 'k', fontsize = 10)
            ax.text(5/6*self.city.length, 0.2/6*self.city.length, "passenger", color = 'b', fontsize = 10)
            plt.xlabel("x (mile)")
            plt.ylabel("y (mile)")

        if self.city.type_name == "real-world":
            ax.text(-88.1,40.3, "in service", color = 'r',  fontsize = 10)
            ax.text(-88.1,40.3-0.002, "assigned", color = 'y', fontsize = 10)
            ax.text(-88.1,40.3-0.004, "idle", color = 'g', fontsize = 10)
            ax.text(-88.1,40.3-0.006, "passenger", color = 'b', fontsize = 10)
            plt.xlabel("longitude")
            plt.ylabel("latitude")      

        writergif = PillowWriter(fps) 
        animation.save(path + "/simulation.gif", writer=writergif)
