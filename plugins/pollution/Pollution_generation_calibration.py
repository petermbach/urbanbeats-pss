# ||||||||||||||||||||||||||||||| IMPORT PACKAGES, DATABASES AND BLOCKS |||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Import the libraries necessary for our code
import psycopg2 as ps
import itertools
import numpy as np

# Connect to the database
try:
    con = ps.connect(
        host="localhost",
        database="pollution",
        user="postgres",
        password="DrKuller4you")
except:
    print("Unable to connect to the database")

# Create a cursor
cur = con.cursor()

# |||||||||||||||||||||||||||||||| DEFINE FUNCTIONS |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


def calculatePollutionConcentrations(adwp, vol, temp, para_tss="", para_tn="", para_tp="", type="ALL"):
    """This function calculates runoff concentration for an UrbanBEATS block and the pollutants TSS, TP and TN"""

    if type == "TSS":
        c_tss = (para_tss[2] + para_tss[1] * adwp) ** (-vol * para_tss[0])
        parameters = c_tss
    elif type == "TN":
        c_tn = (para_tn[2] + para_tn[1] * adwp) ** (-vol * para_tn[0])
        parameters = c_tn
    elif type == "TP":
        c_tp = (para_tp[1] * adwp * temp) ** (-vol * para_tp[0])
        parameters = c_tp
    else:
        c_tss = (para_tss[2] + para_tss[1] * adwp) ** (-vol * para_tss[0])
        c_tn = (para_tn[2] + para_tn[1] * adwp) ** (-vol * para_tn[0])
        c_tp = (para_tp[1] * adwp * temp) ** (-vol * para_tp[0])
        parameters = [c_tss, c_tn, c_tp]

    return parameters


# |||||||||||||||||||||||||||||||| SET OR IMPORT THE GLOBAL VARIABLES |||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Generate ranges of parameter values for calibration
k_tss = np.arange(0.1, 0.4, 0.1)
beta_tss = np.arange(0.1, 0.4, 0.1)
alpha_tss = np.arange(0.1, 0.4, 0.1)

list_ranges_tss = [k_tss, beta_tss, alpha_tss]
comb_ranges_tss = list(itertools.product(*list_ranges_tss))

# Input variables which should be loaded from input files containing climate series (rain and temperature).
# These files should be stored in our database.
# rain_series = [0, 0, 0.5, 1, 1.5, 1, 0, 0]
# temp_series = [23, 23, 22.5, 22.5, 22, 22.5, 22.5, 23.5]

# |||||||||||||||||||||||||||||||| DO THE SIMULATION ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Create a table for the pollutant to calibrate for.
table_name = "cal_tss"
cur.execute(f"CREATE TABLE {table_name} (timestep serial PRIMARY KEY);")
con.commit()

# Get the number of time steps from our rain series in the database.
cur.execute("SELECT count(*) FROM rain_series")
count = cur.fetchone()[0]

# Insert timesteps into table.
for timestep in range(count):
    cur.execute(f"INSERT INTO {table_name} (timestep) VALUES ({timestep});")
    con.commit()



# This for loop checks for each time step if it rains and calculates the concentrations for each time step if it
# rains. If it does not rain, the concentrations are recorded as 0.

number = 1
for parameters in comb_ranges_tss:
    column_name = "column_" + str(number)
    number += 1
    cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} float;")
    con.commit()

    # set ADWP and cumulative volume (or depth) and the rainfall at the start of the simulation
    # time = 0
    adwp = 0
    volume = 0
    rainfall = 0.0

    for timestep in range(count):
        rainfall_previous = rainfall
        cur.execute(f"SELECT rainfall FROM rain_series WHERE timestep = {timestep}")
        rainfall = cur.fetchone()[0]
        if rainfall == 0:
            if rainfall_previous == 0:
                adwp += 1
            else:
                adwp = 0
                volume = 0

            # Add the time step and concentration of 0 (no rain) to the pollutograph.
            cur.execute(f"UPDATE {table_name} SET {column_name} = 0 WHERE timestep = {timestep};")
            con.commit()
        else:
            volume += rainfall
            cur.execute(f"SELECT temp FROM temp_series WHERE timestep = {timestep}")
            temperature = cur.fetchone()[0]

            concentration = calculatePollutionConcentrations(adwp=adwp, vol=volume, temp=temperature,
                                                             para_tss=parameters, type="TSS")
            cur.execute(f"UPDATE {table_name} SET {column_name} = {concentration} WHERE timestep = {timestep};")
            con.commit()

# Close the database cursor and connection
cur.close()
con.close()
