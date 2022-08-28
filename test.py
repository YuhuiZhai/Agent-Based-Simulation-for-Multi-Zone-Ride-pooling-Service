from passenger import Passenger
from taxi import Taxi
from city import City
import numpy as np
import matplotlib.pyplot as plt
print("---starting test---")
city = City(length=10, n=10)
city.sketch()
taxi = Taxi(vehicle_id=0, zone=city.getZone(0), city=city, init_status=(city.getZone(0).id, -1,-1,-1))
plt.plot(taxi.x, taxi.y, 'ro')
passenger1 = Passenger(t0=1/60, passenger_id=0, zone=city.getZone(0))
passenger1.assignTargetZone(city.getZone(99))
plt.plot(passenger1.x, passenger1.y, 'bv')
plt.plot(passenger1.dx, passenger1.dy, 'bo')
passenger2 = Passenger(t0=10/60, passenger_id=1, zone=city.getZone(11))
passenger2.assignTargetZone(city.getZone(99))
plt.plot(passenger2.x, passenger2.y, 'yv')
plt.plot(passenger2.dx, passenger2.dy, 'yo')



T = 2
dt = 1/3600
x, y = [], []
count = 0
temp1, temp2 = True, True
for t in np.arange(0, T, 1/3600):
    if temp1 and taxi.zone.id == passenger1.zone.id:
        taxi.assign(passenger1)
        temp1 = False
    if temp2 and taxi.zone.id == passenger2.zone.id:
        taxi.assign(passenger2)
        temp2 = False
    x.append(taxi.x)
    y.append(taxi.y)
    taxi.move(dt=dt)
    # if count % 30 == 0:
    #     print(taxi.status)
    count += 1
plt.plot(x, y)
plt.xlim(0, city.length)
plt.ylim(0, city.length)
plt.show()