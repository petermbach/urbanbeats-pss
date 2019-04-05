# ||||||||||||||||||||||||||||||| IMPORT PACKAGES, DATABASES AND BLOCKS |||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Import the libraries necessary for our code
import psycopg2 as ps

# Import the list of blocks (objects?) from another part of UrbanBEATS. Each item in the list is a block object (??)
# that contains all the information such as land use mix, slope, population etc...
blocks = [1, 2]

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

def calculateParameters(land_uses, para_lu_tss, para_lu_tn, para_lu_tp):
    """This function calculates the parameters for an UrbanBEATS block and the pollutants TSS, TP and TN
    It returns a list of three lists containing parameters k, beta and alpha for each pollutant"""

    # some equations (the ones below are just placeholders for test running)
    para_tss = [1.2, 15.0, 70.1]
    para_tn = [1.4, 0.404, 2.67]
    para_tp = [1.3, 0.005]

    return [para_tss, para_tn, para_tp]


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

# |||||||||||||||||||||||||||||||| DO THE SIMULATION ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Create a table for each block to write the pollutographs for our three pollutants to.
for block in blocks:
    try:
        table_name = "block_" + str(block)
        cur.execute(f"CREATE TABLE {table_name} (timestep serial PRIMARY KEY, c_tss float, c_tn float, c_tp float);")
    except:
        print(f"I can't create our {table_name} table!")
    con.commit()

# Get the number of time steps from our rain series in the database.
cur.execute("SELECT count(*) FROM rain_series")
count = cur.fetchone()[0]

# set ADWP and cumulative volume (or depth) and the rainfall at the start of the simulation
# time = 0
adwp = 0
volume = 0
rainfall = 0.0

# This for loop checks for each time step if it rains and calculates the concentrations for each time step if it
# rains. If it does not rain, the concentrations are recorded as 0.
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

        # Add the time step and concentration of 0 (no rain) to each pollutograph.
        for block in blocks:
            table_name = "block_" + str(block)
            cur.execute(f"INSERT INTO {table_name} (timestep, c_tss, c_tn, c_tp) VALUES (%s, %s, %s, %s)",
                        (timestep, 0, 0, 0))
            con.commit()
    else:
        # Set all variables for this time step.
        # temperature = temp_series[timestep]
        volume += rainfall
        cur.execute(f"SELECT temp FROM temp_series WHERE timestep = {timestep}")
        temperature = cur.fetchone()[0]

        # Calculate concentrations block by block for this time step with rain
        for block in blocks:
            # Take the land use mix for this particular block, which should look like
            # {"LU1": 0.2, "LU2": 0.0, "LU3": 0.8}
            # land_uses = block.landuse (use once blocks are classes)
            land_uses = {"LU1": 0.2, "LU2": 0.0, "LU3": 0.8}

            # Using the function defined above, we calculate the parameters k, beta and alpha for each pollutant
            # for this block.
            parameters = calculateParameters(land_uses=land_uses, para_lu_tss=para_lu_tss,
                                             para_lu_tn=para_lu_tn, para_lu_tp=para_lu_tp)
            para_tss = parameters[0]
            para_tn = parameters[1]
            para_tp = parameters[2]

            # Using the function defined above, we calculate the concentrations for this time step for each pollutant.
            concentrations = calculatePollutionConcentrations(adwp=adwp, vol=volume, temp=temperature,
                                                              para_tss=para_tss, para_tn=para_tn, para_tp=para_tp)

            # Add the time step and concentration as calculated above to each pollutograph.
            table_name = "block_" + str(block)
            cur.execute(f"INSERT INTO {table_name} (timestep, c_tss, c_tn, c_tp) VALUES (%s, %s, %s, %s)",
                        (timestep, concentrations[0], concentrations[1], concentrations[2]))
            con.commit()

# Close the database cursor and connection
cur.close()
con.close()
