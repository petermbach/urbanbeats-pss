# ||||||||||||||||||||||||||||||| IMPORT PACKAGES, DATABASES AND BLOCKS |||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Import the libraries necessary for our code
import psycopg2 as ps
import itertools
import numpy as np
import time
import random as rn

# Set clock for measuring time of simulation
start_time = time.time()

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


def calculatePollutionConcentrations(adwp, vol, temp, para_tss="", para_tn="", para_tp="", pol_type="ALL"):
    """This function calculates runoff concentration for an UrbanBEATS block and the pollutants TSS, TP and TN,
    either separately or all together"""

    if pol_type == "tss":
        c_tss = (para_tss[2] + para_tss[1] * adwp) ** (-vol * para_tss[0])
        parameters = c_tss
    elif pol_type == "tn":
        c_tn = (para_tn[2] + para_tn[1] * adwp) ** (-vol * para_tn[0])
        parameters = c_tn
    elif pol_type == "tp":
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

# Indicate the pollutant type and concentration series for calibration
pol_type = "tss"

# |||||||||||||||||||||||||||||||| DO THE SIMULATION ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Create a table for the pollutant to calibrate for.
if pol_type == "tss":
    table_name = "cal_tss"
elif pol_type == "tn":
    table_name = "cal_tn"
elif pol_type == "tp":
    table_name = "cal_tp"

cur.execute(f"CREATE TABLE {table_name} (iterations serial PRIMARY KEY, k float, beta float, alpha float, E float);")
con.commit()

# Get the number of time steps from our runoff series in the database.
cur.execute("SELECT count(*) FROM runoff_series")
count = cur.fetchone()[0]

# Load the measured pollutograph
C_measured = []
for timestep in range(count):
    cur.execute(f"SELECT {pol_type} FROM measured_pollution WHERE timestep = {timestep}")
    concentration = cur.fetchone()[0]
    C_measured.append(concentration)

# This for loop checks for each time step if there's runoff and calculates the concentrations for each time step if
# there's runoff. If it there's none, the concentrations are recorded as 0.
iterations = 1000

for iteration in range(iterations):
    # set ADWP at the start of the simulation
    # time = 0
    adwp = 23
    C_modelled = []

    # Randomly sample parameters from their flat distribution
    if pol_type == "tss":
        alpha = rn.uniform(0, 100000)  # unit kg
        beta = rn.uniform(0, 2)
        k = rn.uniform(0, 3)
    elif pol_type == "tn":
        alpha = rn.uniform(0, 5000)  # unit kg
        beta = rn.uniform(0, 2)
        k = rn.uniform(0, 0.1)
    elif pol_type == "tp":
        alpha = rn.uniform(0, 1000)  # unit mg
        beta = rn.uniform(0, 3)
        k = rn.uniform(0, 3)
    parameters = [k, beta, alpha]

    # Model the pollutograph using the randomly sampled parameters
    runoff_previous = 0
    for timestep in range(count):
        cur.execute(f"SELECT runoff FROM runoff_series WHERE timestep = {timestep}")
        runoff = cur.fetchone()[0]
        if runoff == 0:
            if runoff_previous == 0:
                adwp += 1
            else:
                adwp = 1

            # Add the time step and concentration of 0 (no runoff) to the pollutograph.
            C_modelled.append(0)
        else:
            cur.execute(f"SELECT temp FROM temp_series WHERE timestep = {timestep}")
            temperature = cur.fetchone()[0]

            if pol_type == 'tss':
                concentration = calculatePollutionConcentrations(adwp=adwp, vol=runoff, temp=temperature,
                                                             para_tss=parameters, pol_type=pol_type)
            elif pol_type == 'tn':
                concentration = calculatePollutionConcentrations(adwp=adwp, vol=runoff, temp=temperature,
                                                                 para_tn=parameters, pol_type=pol_type)
            elif pol_type == 'tp':
                concentration = calculatePollutionConcentrations(adwp=adwp, vol=runoff, temp=temperature,
                                                             para_tp=parameters, pol_type=pol_type)
            C_modelled.append(concentration)
            runoff_previous = runoff

    # Calculate the Nash-Sutcliffe coefficient E
    E_part1 = []  # numerator for Nash-Sutcliffe (O-M)^2
    E_part2 = []  # denominator for Nash-Sutcliffe (O-Oavg)^2
    for item in range(count):
        E_part1.append((float(C_modelled[item]) - float(C_measured[item])) ** 2)
        E_part2.append((float(C_measured[item]) - sum(C_measured) / len(C_measured)) ** 2)
    E = 1 - (sum(E_part1) / sum(E_part2))

    # Write everything to the database
    cur.execute(f"INSERT INTO {table_name} (iterations, k, beta, alpha, E) VALUES (%s, %s, %s, %s, %s)",
                (iteration, k, beta, alpha, E))
    con.commit()
    print("Modelled concentrations: " + str(C_modelled))
    print("Measured concentrations: "  + str(C_measured))

# Close the database cursor and connection
cur.close()
con.close()

# Make a record of the time
end_time = time.time()    #records time of simulation end
run_time = end_time - start_time   #calculates total simulation time
print("Total runtime: %s sec"%(run_time))
print("Time elapsed: %s min" % ((end_time - start_time)/60))
