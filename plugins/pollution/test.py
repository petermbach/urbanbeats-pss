import psycopg2 as ps
# import itertools
# import numpy as np
import time

start_time = time.time()

try:
    con = ps.connect(
        host="localhost",
        database="pollution",
        user="postgres",
        password="DrKuller4you")
except:
    print("Unable to connect to the database")


cur = con.cursor()

cur.execute("SELECT rainfall FROM rain_series")
time_series_list = cur.fetchall()
flat_list = []
for sublist in time_series_list:
    for item in sublist:
        flat_list.append(item)
print(flat_list)

# for timestep in range(len(time_series_list)):
#     print(timestep)

# cur.execute("SELECT count(*) FROM rain_series")
# count = cur.fetchone()[0]

# time_series_list = []
# for timestep in range(count):
#     cur.execute(f"SELECT rainfall FROM rain_series WHERE timestep = {timestep}")
#     rainfall = cur.fetchone()
#     print(timestep)
#     time_series_list.append(rainfall)
#
# print(time_series_list)
#
# end_time = time.time()    #records time of simulation end
# run_time = end_time - start_time   #calculates total simulation time
# print("Total runtime: %s sec"%(run_time))
# print("Time elapsed: %s min" % ((end_time - start_time)/60))