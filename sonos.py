#install module from /home/pi/.xxx/config/post_main.d/sococli.sh
# vi ~/.xxx/config/user_crontab     # crontab -e   // cd /home/pi/xxx/config
# cd C:\Users\xxx\Documents\xxxv\xxx; python sonos.py
#script_filename = os.path.splitext(os.path.basename(sys.argv[0]))[0]  # Get the script filename without extension

import time

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
    current_time = int(datetime.now().strftime('%H%M'))
    current_month= datetime.now().month
    current_day_of_week = int(datetime.now().isoweekday())

    def sonosmp3(appliance, mp3):
        if mydebug: print ("play " + mp3 + " on "+ appliance)
        mysonoscmd = ["/usr/local/bin/sonos",appliance, "if_stopped", "play_file", mp3]
        subprocess.run(mysonoscmd, capture_output=False, text=True)

    def sonosvol(appliance, volume):
        if mydebug: print (" volume " + str(volume) + " on "+ appliance)
        mysonoscmd = ["/usr/local/bin/sonos",appliance,  "if_stopped", "group_volume", str(volume)]
        subprocess.run(mysonoscmd, capture_output=False, text=True)

    def sonosgroup(appliance, group="Kitchen"):
        if mydebug: print ("group " + appliance + " with "+ group)
        mysonoscmd = ["/usr/local/bin/sonos",appliance, "group", group]
        subprocess.run(mysonoscmd, capture_output=False, text=True)

    def sonosungroup(appliance):
        if mydebug: print (" ungroup " + appliance)
        mysonoscmd = ["/usr/local/bin/sonos",appliance, "if_stopped", "ungroup"]
        subprocess.run(mysonoscmd, capture_output=False, text=True)

    def setsonos(): 
        if mydebug: print (" setsonos()")
        if (is_ip_responsive3 ("Sonos_Fireplace") != False): 
            sonosgroup("Fireplace","kitchen")
            #update_status("Sonos_Fireplace", "triger","SetSonos")
        if (is_ip_responsive3 ("Sonos_LivingRoom") != False):
            sonosgroup("LivingRoom" , "Kitchen")
            #update_status("Sonos_LivingRoom", "triger","SetSonos")


    def resetsonos(): 
        if mydebug: print (" resetsonos()")
        sonosvol("kitchen", 10)
        if (is_ip_responsive3 ("Sonos_Antony") != False): 
            sonosungroup("Antony")
            #update_status("Sonos_Antony", "triger","ResetSonos")
        if (is_ip_responsive3 ("Sonos_Bureau") != False):
            sonosungroup("Bureau")
            #update_status("Sonos_Bureau", "triger","ResetSonos")

    def sonosvolmp3(appliance,volume=23,mp3="/home/pi/xxx/config/mettrelatable.mp3"):
        if mydebug: print ("sonosvolmp3 " + mp3)
        setsonos()
        sonosvol(appliance, volume)
        sonosmp3(appliance, mp3)
        resetsonos()
    #sonosvolmp3("kitchen", 19, "/home/pi/xxx/config/mettrelatable.mp3")

    if (current_day_of_week <=5 ):  # Weekdays
        if (700 <= current_time < 701):
            sonosvolmp3("kitchen", 19,"/home/pi/xxx/config/ilest7hBonjour.mp3")
        if (750 <= current_time < 751):
            sonosvolmp3("kitchen", 20,"/home/pi/xxx/config/nomdezeus.mp3")
        if (800 <= current_time < 801):
            sonosvolmp3("kitchen", 19,"/home/pi/xxx/config/ilest8h.mp3")

    if (current_day_of_week ==5 ):  # Friday 5
        if (740 <= current_time < 746):
            sonosvolmp3("kitchen", 22, "/home/pi/xxx/config/joggingkan.mp3")
        
    if (current_day_of_week > 5):
        if (700 <= current_time < 701):
            if (is_ip_responsive3 ("Sonos_Antony") != False): 
                sonosungroup("Antony")
                #update_status("Sonos_Antony", "triger",701)
            if (is_ip_responsive3 ("Sonos_Bureau") != False): 
                sonosungroup("Bureau")
                #update_status("Sonos_Bureau", "triger",701)

    # Programme de tous les midis & soirs
    if (1150 <= current_time < 1151):
        sonosvolmp3("kitchen", 19, "/home/pi/xxx/config/mettrelatable.mp3")

    if (1820 <= current_time < 1821):
        sonosvolmp3("kitchen", 19, "/home/pi/xxx/config/ilest18h20.mp3")

    if (1900 <= current_time < 1901):
        if (is_ip_responsive3 ("Sonos_Antony") != False): 
            sonosgroup("Antony", "Kitchen")
            #update_status("Sonos_Antony", "triger",1901)
        if (is_ip_responsive3 ("Sonos_Bureau") != False): 
            sonosgroup("Bureau", "Kitchen")
            #update_status("Sonos_Bureau", "triger",1901)
        sonosvolmp3("kitchen", 22, "/home/pi/xxx/config/ilest19h.mp3")

    #current_time = 2030
    if (2030 <= current_time < 2031):
        sonosvolmp3("kitchen", 18, "/home/pi/xxx/config/ilest20h30.mp3")

    if (current_day_of_week==1 ):  # Monday
    # Le lundi soir 19h10 et 19h20 et 20h10 et 20h20
        if ((1940 <= current_time < 1941) or (2010 <= current_time < 2011) or (2020 <= current_time < 2021)):
            sonosvolmp3("kitchen", 24, "/home/pi/xxx/config/ilfautsortirlapoubelle.mp3")

    #write_config_file(myfolder + "configv2.py")
    if mydebug: print("ENDSET2 VALUES :", time.time() - start_time, "seconds")
    quit()