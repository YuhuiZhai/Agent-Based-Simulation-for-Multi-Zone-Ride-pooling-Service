import random
import numpy as np
from city import City
from fleet import Fleet
from eventQueue import EventQueue
from tqdm import tqdm
import pandas as pd
from animation import Animation
class Simulation:
    def __init__(self, city:City, fleet_size:int, T:float, lmd:float):
        self.city = city 
        self.fleet_size = fleet_size
        self.T = T
        self.lmd = lmd
        self.fleet = Fleet(fleet_size, city)
        self.events = EventQueue(city, T, lmd)
        # na, ns, ni, p vs t
        self.timeline = None
        self.a = []
        self.s = []
        self.i = []
        self.p = []
        # fleet info at each time t
        self.fleet_info = []

    
    def make_animation(self, compression = 100, fps=15):
        print("animation plotting")
        animation = Animation(self.city, self.fleet_info, self.events)
        animation.plot(compression, fps)

    def reset(self):
        self.fleet = Fleet(self.fleet_size, self.city)
        self.events = EventQueue(self.city, self.T, self.lmd)
        self.timeline = None
        self.a = []
        self.s = []
        self.i = []
        self.p = []

    def simple_serve(self, res:float):
        self.reset()
        prev = 0
        self.timeline = np.arange(0, self.T, res)
        head_time, head = self.events.head()
        for t in tqdm(self.timeline, desc="simple_serve loading"):
            self.a.append(self.fleet.assigned_num)
            self.s.append(self.fleet.inservice_num)
            self.i.append(self.fleet.idle_num)
            
            self.fleet_info.append(self.fleet.sketch_helper())

            while (not self.events.empty() and head_time < t):
                prev += 1
                self.fleet.simple_serve(head.passenger)
                self.events.dequeue()
                head_time, head = self.events.head()
            self.fleet.move(res)
            self.p.append(prev)
        return 

    def batch_serve(self, res:float, dt:float):
        self.reset()
        self.timeline = np.arange(0, self.T, res)
        batch_timeline = np.arange(0, self.T, dt)
        head_time, head = self.events.head()
        batch_idx = 0
        prev = 0
        
        for t in tqdm(self.timeline, desc="batch_matching loading"):
            self.a.append(self.fleet.assigned_num)
            self.s.append(self.fleet.inservice_num)
            self.i.append(self.fleet.idle_num)
            
            self.fleet_info.append(self.fleet.sketch_helper())

            # when it is batching time, starts serving
            if (batch_idx >= len(batch_timeline)):
                batch_time = self.timeline[-1]
            else:
                batch_time = batch_timeline[batch_idx] 
            if batch_time <= t:
                passengers = []
                while (not self.events.empty() and head_time < batch_time):
                    prev += 1
                    passengers.append(head.passenger)
                    self.events.dequeue()
                    head_time, head = self.events.head()

                if len(passengers) != 0:
                    self.fleet.batch_serve(passengers)
                batch_idx += 1
            self.fleet.move(res)
            self.p.append(prev)     
        return   



    def export(self, name=""):
        dist_a, dist_s, ta, ts, freq, unserved = self.fleet.info()
        veh_num = {
            'time': self.timeline, 
            'passenger' : self.p,
            'na': self.a, 
            'ns': self.s, 
            'ni': self.i 
        }
        fleet_info = {
            'dist_a' : dist_a,
            'dist_s' : dist_s,
            'total_ta' : ta,
            'total_ts' : ts,
            'total_ti' : self.T - np.array(ta) - np.array(ts), 
            'freq' : freq
        }
        output_1 = pd.DataFrame(veh_num)
        output_2 = pd.DataFrame(fleet_info)
        output_1.to_csv(name + '_veh_num_M_' + str(self.fleet_size) + '_lambda_' + str(self.lmd) + '.csv')
        output_2.to_csv(name + '_fleet_info_M_' + str(self.fleet_size) + '_lambda_' + str(self.lmd) + '.csv')
        print("unserved number: ", unserved)
        return 

    


