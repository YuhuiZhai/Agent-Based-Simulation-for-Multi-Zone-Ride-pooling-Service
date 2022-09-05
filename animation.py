import matplotlib.pyplot as plt
from city import City
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter

class Animation:
    def __init__(self, city:City, fleet_info:list, passenger_info:list):
        self.city = city
        self.fleet_info = fleet_info
        self.passenger_info = passenger_info
    
    # pattern is a tuple of (
    #   status table {status : status name},
    #   color table {status : status color}
    #   shape e.g. '*'
    # )
    def plot(self, compression, fps, fleet_pattern:tuple,
                passenger_pattern, name="simulation", path=""):
        fleet_status, fleet_color, fleet_shape = fleet_pattern
        passenger_status, passenger_color, passenger_shape = passenger_pattern
        fig, ax = plt.subplots()
        self.city.sketch()
        fleet_list, passenger_list = [], []
        for i in range(len(self.fleet_info[0])):
            ln, = plt.plot([], [], fleet_color[i]+fleet_shape, markersize = 7) 
            fleet_list.append(ln)
        for i in range(len(self.passenger_info[0])):
            ln, = plt.plot([], [], passenger_color[i]+passenger_shape, markersize = 7) 
            passenger_list.append(ln)
        
        def update(frame):
            for i in range(len(self.fleet_info[frame])):
                fleet_list[i].set_data(self.fleet_info[frame][i])
            for i in range(len(self.passenger_info[frame])):
                passenger_list[i].set_data(self.passenger_info[frame][i])
            return *fleet_list, *passenger_list

        animation = FuncAnimation(fig, update, blit=True, frames = range(0, len(self.fleet_info), compression))
        
        plt.xlim(0, self.city.length)
        plt.ylim(0, self.city.length)
        for i in range(len(self.fleet_info[0])):
            ax.text(4.75/6*self.city.length, (0.3+i*0.3)/6*self.city.length, fleet_status[i], color = fleet_color[i], fontsize = 10)
        for i in range(len(self.passenger_info[0])):
            ax.text(4.75/6*self.city.length, (0.3+len(self.fleet_info[0])*0.3+i*0.3)/6*self.city.length, passenger_status[i], color = passenger_color[i], fontsize = 10)
        plt.xlabel("x (mile)")
        plt.ylabel("y (mile)")
      

        writergif = PillowWriter(fps) 
        if path == "":
            animation.save(name + ".gif", writer=writergif)
        else: 
            animation.save(path + "/" + name + ".gif", writer=writergif)
