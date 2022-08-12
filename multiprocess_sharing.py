from multiprocessing import Pool, Lock
from itertools import product
from taxi_simul.simulation import Simulation
from city import City
import xlsxwriter as xw
import time 
import numpy as np
start = time.time()
lock = Lock()

def func(info: tuple):
    fs, d, idx, lmd = info
    city = City(type_name="Manhattan")
    s = Simulation(city, fleet_size=fs, T=10, lmd=lmd, lr=False, swap=False)
    s.sharing_serve(res=5/3600, detour_dist=d)
    
    (t1, t2, t3), (ta1, ta2, ta3) = s.passenger_data_share()
    (avgtm, avgta) = s.fleet_data()[0]
    (na, ns, ni) = s.num_data()
    
    # do not change
    lock.acquire()
    print(f"count: {idx}, time: {time.time()-start}")
    lock.release()

    return (ta1, ta2, ta3, t1, t2, t3, avgta, na, ns, ni)

if __name__ == "__main__":
    with Pool(processes=12) as pool:   
        start = time.time()

        lmd = 5000
        fs_g = [1000]
        detour_list = [i for i in np.arange(0, 3.6, 0.05)]

        result = pool.map(func, [(fs, d, i, lmd) for i, (fs, d) in enumerate(product(fs_g, detour_list))])
        pool.close()

        workbook = xw.Workbook(f"sharing_M{fs_g[0]}_{fs_g[-1]}lmd{lmd}_dt{detour_list[0]}_{detour_list[-1]}.xlsx")
        for i in range(len(fs_g)):
            worksheet1 = workbook.add_worksheet(f"M{fs_g[i]}")
            worksheet1.write(0, 0, "detour distance")
            worksheet1.write(0, 1, "pax avg assigned time (idle)")
            worksheet1.write(0, 2, "pax avg assigned time (sharing)")
            worksheet1.write(0, 3, "pax avg assigned time (combined)")
            worksheet1.write(0, 4, "pax avg traveling time (idle)")
            worksheet1.write(0, 5, "pax avg traveling time (sharing)")
            worksheet1.write(0, 6, "pax avg traveling time (combined)")
            worksheet1.write(0, 7, "taxi avg assigned time")
            worksheet1.write(0, 8, "avg_na")
            worksheet1.write(0, 9, "avg_ns")
            worksheet1.write(0, 10, "avg_ni")
            for k in range(len(detour_list)):
                worksheet1.write(k+1, 0, detour_list[k])
                worksheet1.write(k+1, 1, result[i*len(detour_list)+k][0])
                worksheet1.write(k+1, 2, result[i*len(detour_list)+k][1])
                worksheet1.write(k+1, 3, result[i*len(detour_list)+k][2])
                worksheet1.write(k+1, 4, result[i*len(detour_list)+k][3])
                worksheet1.write(k+1, 5, result[i*len(detour_list)+k][4])
                worksheet1.write(k+1, 6, result[i*len(detour_list)+k][5])
                worksheet1.write(k+1, 7, result[i*len(detour_list)+k][6])
                worksheet1.write(k+1, 8, result[i*len(detour_list)+k][7])
                worksheet1.write(k+1, 9, result[i*len(detour_list)+k][8])
                worksheet1.write(k+1, 10, result[i*len(detour_list)+k][9])
        workbook.close()
        print(time.time() - start)