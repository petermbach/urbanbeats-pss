# ||||||||||||||||||||||||||||||| IMPORT PACKAGES, DATABASES AND BLOCKS |||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Import the libraries necessary for our code
import psycopg2 as ps
import itertools
import numpy as np
import time
import random as rn
import math

start_time = time.time()

# Import the list of blocks (objects?) from another part of UrbanBEATS. Each item in the list is a block object (??)
# that contains all the information such as land use mix, slope, population etc...
blocks = [0, 1]
imp_frac = [0.6, 0.2]
block_size = 500 # meters of a side of the square block

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

def calculate_parameters(land_uses, para_lu_tss, para_lu_tn, para_lu_tp):
    """This function calculates the parameters for an UrbanBEATS block and the pollutants TSS, TP and TN
    It returns a list of three lists containing parameters k, beta and alpha for each pollutant"""

    # some equations (the ones below are just placeholders for test running)
    para_tss = [0.184, 4.22, 93.0]
    para_tn = [0.109, 0.079, 1.71]
    para_tp = [2.11, 0.422, 0.13]

    return [para_tss, para_tn, para_tp]


def calculate_pollution_conc(adwp, depth, temp, para_tss="", para_tn="", para_tp="", pol_type="ALL"):
    """This function calculates runoff concentration for an UrbanBEATS block and the pollutants TSS, TP and TN,
    either separately or all together"""

    if pol_type == "tss":
        c_tss = (para_tss[2] + para_tss[1] * adwp) * math.exp(-depth * para_tss[0])
        output = c_tss
    elif pol_type == "tn":
        c_tn = (para_tn[2] + para_tn[1] * adwp) * math.exp(-depth * para_tn[0])
        output = c_tn
    elif pol_type == "tp":
        c_tp = (para_tp[2] * adwp * (temp)/15) * math.exp(-depth * para_tp[0])
        output = c_tp
    else:
        c_tss = (para_tss[2] + para_tss[1] * adwp) * math.exp(-depth * para_tss[0])
        c_tn = (para_tn[2] + para_tn[1] * adwp) * math.exp(-depth * para_tn[0])
        c_tp = (para_tp[2] * adwp * temp/15) * math.exp(-depth * para_tp[0])
        output = [c_tss, c_tn, c_tp]

    return output

def flatten_list(input_list):
    """This function flattens a list of lists or list of tuples into a flat list, necessary to create a normal list
    from the results of a cursor.fetchall() operation."""

    flat_list = []
    for sublist in input_list:
        for item in sublist:
            flat_list.append(item)

    return flat_list

def calculate_runoff(rainfall, evaporation, infiltration, imp_frac, block_size):
    """This function calculates the runoff from the rainfall, evaporation and infiltration (series) dependent on
    the impervious fraction of the block. It returns (series of) runoff depth as well as volume, based on the
    block size."""

    # counter = 0
    # runoff_depth_series = []
    # runoff_volume_series = []
    #
    # for rainfall in rain_series:
    #     if rainfall == 0:
    #         runoff_depth_series.append(0)
    #         runoff_volume_series.append(0)
    #     else:
    #         runoff = rainfall - evapo_series[counter] - ((1 - imp_frac) * infilt_series[counter])
    #         if runoff > 0:
    #             runoff_depth_series.append(runoff)
    #             volume = block_size * block_size * (0.001 * runoff)
    #             runoff_volume_series.append(volume)
    #         else:
    #             runoff_depth_series.append(0)
    #             runoff_volume_series.append(0)
    #     counter += 1
    #
    # return [runoff_depth_series, runoff_volume_series]

    net_rain = rainfall - evaporation - ((1 - imp_frac) * infiltration)
    if net_rain > 0:
        runoff_depth = net_rain
        runoff_volume = block_size * block_size * (0.001 * net_rain)
    else:
        runoff_depth = 0
        runoff_volume = 0

    return [runoff_depth, runoff_volume]

def calculate_loads(concentrations, runoff_volume):
    """Returns load values from concentrations and volume"""

    loads = []
    for concentration in concentrations:
        load = concentration * runoff_volume * 1000 # to calculate load from per liter concentrations
        loads.append(load)

    return loads


# |||||||||||||||||||||||||||||||| SET OR IMPORT THE GLOBAL VARIABLES |||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Input variable that can be hard-coded or drawn from user input specifying wha the impervious fractions for each
# land use are.


# Input variables which should be loaded from input files containing climate series (rain and temperature).
# These files should be stored in our database.
# rain_series = [0, 0, 0.5, 1, 1.5, 1, 0, 0]
# temp_series = [23, 23, 22.5, 22.5, 22, 22.5, 22.5, 23.5]

# Calibration parameters dependent on land-use type: first: k, second: beta, third: alpha. These variables are input
# and should be acquired from calibration with "pure" catchments.
para_lu_tss = {"LU1": [1.2, 15.0, 70.1], "LU2": [1.2, 15.0, 70.1], "LU3": [1.2, 15.0, 70.1]}
para_lu_tn = {"LU1": [1.4, 0.404, 2.67], "LU2": [1.2, 0.404, 2.67], "LU3": [1.2, 0.404, 2.67]}
para_lu_tp = {"LU1": [1.3, 0.005], "LU2": [1.3, 0.005], "LU3": [1.3, 0.005]}

# Set the length of the timestep used for the simulation.
timestep_length = 2 # In minutes

# |||||||||||||||||||||||||||||||| DO THE SIMULATION ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Create a table for each block to write the pollutographs for our three pollutants to.
for block in blocks:
    try:
        table_name = "block_" + str(block)
        cur.execute(f"CREATE TABLE {table_name} (timestep serial PRIMARY KEY, c_tss float, c_tn float, c_tp float,"
                    f"l_tss float, l_tn float, l_tp float, runoff_volume float);")
    except:
        print(f"I can't create our {table_name} table!")
    con.commit()

# Get the rain series, temperature series, evaporation series and infiltration series from the database in a list.
cur.execute("SELECT rainfall FROM rain_series")
fetched = cur.fetchall()
rain_series_list = flatten_list(fetched)
cur.execute("SELECT temperature FROM rain_series")
fetched = cur.fetchall()
temp_series_list = flatten_list(fetched)
cur.execute("SELECT evaporation FROM rain_series")
fetched = cur.fetchall()
evapo_series_list = flatten_list(fetched)
cur.execute("SELECT infiltration FROM rain_series")
fetched = cur.fetchall()
infilt_series_list = flatten_list(fetched)

# set ADWP and cumulative volume (or depth) and the rainfall at the start of the simulation
# time = 0
adwp = 0
adwp_counter = 0
cum_runoff_depth = 0.0
rainfall_previous = 0.0
timestep = 0

# This for loop checks for each time step if it rains and calculates the concentrations for each time step if it
# rains. If it does not rain, the concentrations are recorded as 0.
for rainfall in rain_series_list:
    if rainfall == 0.0:
        if rainfall_previous == 0.0:
            adwp_counter += 1
        else:
            adwp_counter = 0
            cum_runoff_depth = 0.0

        # Add the time step and concentration of 0 (no rain) to each pollutograph.
        for block in blocks:
            table_name = "block_" + str(block)
            cur.execute(f"INSERT INTO {table_name} (timestep, c_tss, c_tn, c_tp, l_tss, l_tn, l_tp, runoff_volume) "
                        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (timestep, 0, 0, 0, 0, 0, 0, 0))
            con.commit()
    else:
        # Set all variables for this time step.
        temperature = temp_series_list[timestep]
        adwp = (adwp_counter*timestep_length)/1440 # Translate adwp into days

        # Calculate concentrations block by block for this time step with rain
        for block in blocks:
            # Take the land use mix for this particular block, which should look like
            # {"LU1": 0.2, "LU2": 0.0, "LU3": 0.8}
            # land_uses = block.landuse (use once blocks are classes)
            land_uses = {"LU1": 0.2, "LU2": 0.0, "LU3": 0.8}

            # Using the function defined above, we calculate the parameters k, beta and alpha for each pollutant
            # for this block.
            parameters = calculate_parameters(land_uses=land_uses, para_lu_tss=para_lu_tss,
                                             para_lu_tn=para_lu_tn, para_lu_tp=para_lu_tp)
            para_tss = parameters[0]
            para_tn = parameters[1]
            para_tp = parameters[2]

            runoff = calculate_runoff(rainfall=rainfall, evaporation=evapo_series_list[timestep],
                                            infiltration=infilt_series_list[timestep], imp_frac=imp_frac[block], 
                                            block_size=block_size)

            if runoff[0] == 0:
                table_name = "block_" + str(block)
                cur.execute(f"INSERT INTO {table_name} (timestep, c_tss, c_tn, c_tp, l_tss, l_tn, l_tp, runoff_volume) "
                            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (timestep, 0, 0, 0, 0, 0, 0, 0))
                con.commit()
            else:
                # Using the function defined above, we calculate the concentrations for this time step for each pollutant.
                cum_runoff_depth += runoff[0]
                runoff_volume = runoff[1]

                concentrations = calculate_pollution_conc(adwp=adwp, depth=cum_runoff_depth, temp=temperature,
                                                                  para_tss=para_tss, para_tn=para_tn, para_tp=para_tp)

                loads = calculate_loads(concentrations=concentrations, runoff_volume=runoff_volume)

                # Add the time step and concentration as calculated above to each pollutograph.
                table_name = "block_" + str(block)
                cur.execute(f"INSERT INTO {table_name} (timestep, c_tss, c_tn, c_tp, l_tss, l_tn, l_tp, runoff_volume) "
                            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (timestep, concentrations[0], concentrations[1],
                            concentrations[2], loads[0], loads[1], loads[2], runoff_volume))
                con.commit()
    timestep += 1
    rainfall_previous = rainfall

# Close the database cursor and connection
cur.close()
con.close()

end_time = time.time()    #records time of simulation end
run_time = end_time - start_time   #calculates total simulation time
print("Total runtime: %s sec"%(run_time))
print("Time elapsed: %s min" % ((end_time - start_time)/60))
