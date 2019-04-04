import psycopg2 as ps

blocks = [1, 2]

# Connect to the database
con = ps.connect(
    host="localhost",
    database="pollution",
    user="postgres",
    password="DrKuller4you")

# Create a cursor
cur = con.cursor()

#cur.execute("SELECT timestep, time, rainfall FROM rain_series")
#rows = cur.fetchall()
# for r in rows:
#     print(f"timestep {r[0]} time {r[1]} rainfall {r[2]}")

for block in blocks:
    try:
        table_name = "block_" + str(block)
        cur.execute(f"CREATE TABLE {table_name} (timestep serial PRIMARY KEY, c_tss float, c_tn float, c_tp float);")
    except:
        print(f"I can't create our {table_name} table!")
    con.commit()

# cur.execute("SELECT count(*) FROM rain_series")
# count = cur.fetchone()[0]
# rainfall = 0
# cum_rain = 0
# for timestep in range(count):
#     # rainfall_previous = rainfall
#     cur.execute(f"SELECT rainfall FROM rain_series WHERE timestep = {timestep}")
#     rainfall = cur.fetchone()[0]
#     cum_rain += rainfall
#     cur.execute("INSERT INTO test (timestep, cum_vol) VALUES (%s, %s)", (timestep, cum_rain))
#
# con.commit()

# Close the database connection
con.close()
