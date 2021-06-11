import pandas as pd

import dronelogbook as dlb
import os

wxuas_dir = os.path.join(os.path.expanduser("~"), ".wxuas")

# Connect to DroneLogbook
dlb_conn = dlb.DLB()

# Get all the drones in the database
drones = dlb_conn.get_drones()

with open(f"{wxuas_dir}/copterID.csv", 'w') as fh:
    for drone in drones:
        fh.write(f'{drone.sysid},{drone.id_number}\n')

# Get all the scoops in the database and write the info to the appropriate files
scoops = [s for s in dlb_conn.get_all_equipment() if s.is_scoop()]

# imet1,imet2,imet3,rh1,rh2,rh3,wind

with open(f"{wxuas_dir}/scoops.csv", 'w') as fh:
    fh.write("name,imet1,imet2,imet3,rh1,rh2,rh3\n")
    for scoop in scoops:
        fh.write(f"{scoop.name},{','.join(scoop.imet_sn+scoop.hyt_sn)}\n")




