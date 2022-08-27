from passenger import Passenger
from taxi import Taxi
from city import City
import numpy as np
import matplotlib.pyplot as plt
city = City(length=6, n=3)
city.sketch()
taxi = Taxi(vehicle_id=0, zone=city.getZone(0), city=city, init_status=(city.getZone(0).id, -1,-1,-1))
plt.plot(taxi.x, taxi.y, 'ro')
passenger = Passenger(t0=10/3600, passenger_id=0, zone=city.getZone(0))
passenger.assignTargetZone(city.getZone(8))
plt.plot(passenger.x, passenger.y, 'bv')
plt.plot(passenger.dx, passenger.dy, 'bo')


T = 60/60
dt = 1/3600
x, y = [], []
for t in np.arange(0, T, 1/3600):
    if t == passenger.t_start:
        taxi.assign(passenger)
    x.append(taxi.x)
    y.append(taxi.y)
    taxi.move(dt=dt)
plt.plot(x, y)
plt.xlim(0, 6)
plt.ylim(0, 6)
plt.show()