#install module from /home/pi/.xxx/config/post_main.d/sococli.sh
# vi ~/.xxx/config/user_crontab     # crontab -e   // cd /home/pi/xxx/config
# cd C:\Users\xxx\Documents\xxx\xxx; python meross.py
#script_filename = os.path.splitext(os.path.basename(sys.argv[0]))[0]  # Get the script filename without extension

import asyncio
import os, time
from meross_iot.controller.mixins.roller_shutter import RollerShutterTimerMixin
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.model.enums import OnlineStatus

mydelay = 0
mydebug = False

if mydebug:
    start_time = time.time() 
    print("START :", time.time() - start_time, "seconds")
else:
    time.sleep(mydelay)
    
from funcpiev2 import *

if __name__ == "__main__":
    if (read_mydevice_value("KillSwitch",os.path.splitext(os.path.basename(sys.argv[0]))[0])=='True'):
        log2file("KillSwitch = TRUE",False)
        exit()
    usrcity = LocationInfo(read_mydevice_value("Forecast","city"), 'France','Europe/Paris',98.015, 7.54)
    s = sun(usrcity.observer, date=date.today(), tzinfo=usrcity.timezone)

    heure_actuelle = datetime.now().time()
    dusk  = datetime.strptime(s["dusk"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time()   #horizon
    duskdone = (datetime.combine(datetime.today(), dusk) + timedelta(minutes=2)).time()
    dawn = datetime.strptime(s["dawn"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time()


    if mydebug: print("ENDSET1 VALUES :", time.time() - start_time, "seconds")
    if mydebug: print ("tuya from "+ str(dusk) + " to "  + str(duskdone))
    if (heure_actuelle > dusk and heure_actuelle < duskdone ):               # le soleil est couché
        print("Ferme")
        set_blind_height("Volet_Salon",0)       # Ferme volet salon à 0%
        update_status("Volet_Salon", "height",0)
        set_blind_height("Volet_Parent",0)   # Ferme volet salon à 0%
        update_status("Volet_Parent", "height",0)
        meross_roller("Volet_TV","close")       # Ferme volet TV à 0%
        update_status("Volet_TV", "height",0)
        toggle_velux("Volet_Velux",2,"on")          # Ferme Velux via ewelink 
        update_status("Volet_Velux", "height",0)
    else:
        print("Ouvre")
        set_blind_height("Volet_Salon",100)       # Ouvre volet salon à 100%
        update_status("Volet_Salon", "height",100)
        set_blind_height("Volet_Parent",100)   # Ouvre volet salon à 100%
        update_status("Volet_Parent", "height",100)
        meross_roller("Volet_TV","open")       # Ouvre volet TV à 100%
        update_status("Volet_TV", "height",100)
        toggle_velux("Volet_Velux",1,"on")          # Ouvre Velux via ewelink 
        update_status("Volet_Velux", "height",100)
    if mydebug: print("ENDSET2 VALUES :", time.time() - start_time, "seconds")
    quit()