# Get Device ID  : https://eu.iot.tuya.com/cloud/basic?id=p1688978183050hgrstm&toptab=related&region=EU
# Get Local_Key  : https://eu.iot.tuya.com/cloud/explorer  device management > Query Device Details 
# vi ~/.xxx/config/user_crontab     # crontab -e   // cd /home/pi/xxx/config
# cd C:\Users\xxx\Documents\xxx\xxx; python tuya.py

import time, subprocess, sys
mydelay = 30
mydebug = False

if 'win' in sys.platform: mydelay=1
if 'win' in sys.platform: mydebug=True
    
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
    #script_filename = os.path.splitext(os.path.basename(sys.argv[0]))[0]  # Get the script filename without extension
    usrcity = LocationInfo(read_mydevice_value("Forecast","city"), 'France','Europe/Paris',48.015, 7.54)
    s = sun(usrcity.observer, date=date.today(), tzinfo=usrcity.timezone)
    heure_actuelle = datetime.now().time()
    current_month = datetime.now().month
    current_day = datetime.now().weekday()
    current_hour = datetime.now().hour
    current_time = int(datetime.now().strftime('%H%M'))
    if mydebug: print("INIT VALUES :", time.time() - start_time, "seconds")
    sunset = datetime.strptime(s["sunset"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time()#sset
    dusk  = datetime.strptime(s["dusk"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time()   #horizon
    duskdone = (datetime.combine(datetime.today(), dusk) + timedelta(minutes=2)).time()
    fourtymtosunset = (datetime.combine(datetime.today(), dusk) - timedelta(minutes=40)).time() 
    thirtytosunset = (datetime.combine(datetime.today(), dusk) - timedelta(minutes=30)).time() 
    dawn = datetime.strptime(s["dawn"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time()
    temperature = 22
    
    if (is_connected()):
        temperature = get_current_temp(read_mydevice_value("Forecast","city"),read_mydevice_value("Forecast","country_code"))
    temperature = int(float(temperature))
    if (temperature < 0 or temperature > 50): temperature = 22
    #update_status("Forecast", "temperature",temperature)
    Summer_height = int(read_mydevice_value("Volet_Salon","Summer_height"))
    #update_status("Volet_Salon","Summer_height",Summer_height)
    update_status("Volet_Salon", "height",get_blind_height("Volet_Salon"))
    update_status("Volet_Parent", "height",get_blind_height("Volet_Parent"))
    #if mydebug: print("temperature:"+  str(temperature) + " Summer_height:" + str(Summer_height))

    if mydebug: print("INIT GETPLUG1 :", time.time() - start_time, "seconds")
    bureaust= get_plug_state("Prise_Bureau")
    bureaust = "N/A"
    update_status("Prise_Bureau", "state",bureaust)
    update_status("Prise_Bureau", "powerW",check_plug_power("Prise_Bureau"))
    if str(bureaust) == "N/A": update_status("Prise_Bureau","errors",increm_error("Prise_Bureau"))
    
    relaisst = get_plug_state("Relais_VMC")
    if mydebug: print("INIT GETPLUG2 :", time.time() - start_time, "seconds")
    update_status("Relais_VMC", "state",relaisst)
    if str(relaisst) == "N/A": update_status("Relais_VMC","errors",increm_error("Relais_VMC"))
    
    if (current_month >= 10 or current_month <= 4):#Only in Winter
        temp_chauff_Antony=get_chauff_ant("Chauffage_Antony")
    else: temp_chauff_Antony = 16

    if mydebug: print("ENDGET VALUES :", time.time() - start_time, "seconds")

    # Grabs Thermostat_Antony
    ##### SET VALUES 
    if mydebug: print("BEGSET1 VALUES :", time.time() - start_time, "seconds")
    
    if (temp_chauff_Antony is not None and int(temp_chauff_Antony)) > 16:
        log2file("temp_chauff_Antony: "+ str(temp_chauff_Antony),True)  # Temperature Chauff Antony
    temp_min =  int(read_mydevice_value("AppSettings","temp_min"))
    if (500 <= current_time <= 700 and temperature < temp_min): # que quand il fait plus de temp_min
        if (current_day > 5): # que les weekends !
            if (heure_actuelle > dawn):  # que si on est avant la lueur du jour 
                set_blind_height("Volet_Parent",0) # ferme les volets ( ouverture à 0%)
                update_status("Volet_Parent", "height",0)
                #update_status(lbl_volet_parent+"_height",0)

    if (read_mydevice_value("KillSwitch","Holiday")=='True'):
        if (900 <= current_time <= 915):
                toggle_velux("Volet_Velux",1,"on")  # Ouvre Velux via ewelink 
                update_status("Volet_Velux", "height",100)
                set_blind_height("Volet_Parent",100) # Ouvre les volets ( ouverture à 100%)
                update_status("Volet_Parent", "height",100)
                set_blind_height("Volet_Salon",100) # Ouvre les volets ( ouverture à 100%)
                update_status("Volet_Salon", "height",100)
    if (1800 <= current_time <= 1810):
        if ((current_month <6 or current_month > 8) or temperature < 10 ) :#Only when cold / in Winter
            if (read_mydevice_value("Volet_Velux","height") > 0 ):
                toggle_velux("Volet_Velux",2,"on")          # Ferme Velux via ewelink 
                update_status("Volet_Velux", "height",0)

    if (heure_actuelle > thirtytosunset  ):   #30 min before sunset for velux + TV
        if ( 5 < current_month < 9):#Only when warm / in summer
            if (read_mydevice_value("Volet_Velux","height") > 0 ):
                toggle_velux("Volet_Velux",2,"on")          # Ferme Velux via ewelink 
                update_status("Volet_Velux", "height",0)
                set_blind_height("Volet_Parent",15) # ferme les volets ( ouverture à 15%)
                update_status("Volet_Parent", "height",15)

    #update_status("Volet_Salon", "height",100)
    if mydebug: print ("CHANGE SALON HEIGHT Month:" + str(current_month) +  "; Time:"+ str(current_time) + "; get_blind_height(Volet_Salon):"+ str(get_blind_height("Volet_Salon")) + "; Summer_height:"+ str(Summer_height) + "; Temp:" + str(temperature) + "; max temp:" + str(read_mydevice_value("AppSettings","temp_max")))
    if (current_month >= 4 and current_month <= 9):#Only in summer
        if (1000 <= current_time <= 1600 and temperature >= int(read_mydevice_value("AppSettings","temp_max"))):  # entre 9 et 14 et tmp > max ajuste volets salon
            if (read_mydevice_value("Volet_Salon","height") > int(Summer_height)):
                log2file("Summer_Volet_Salon:"+ str(Summer_height),True)  # Temperature Chauff Antony
                #if mydebug: print ("Ajuste Volet_Salon"+ str(Summer_height))
                set_blind_height("Volet_Salon",int(Summer_height)) #  ferme les volets ( ouverture à volet_height (100-2.5*temperature)
                update_status("Volet_Salon", "height",int(Summer_height))
        if (1800 <= current_time <= 1810 and temperature < int(read_mydevice_value("AppSettings","temp_max"))): # à 18h, remonte un peu volet salon si temp < temp_max
            if (read_mydevice_value("Volet_Salon","height") < 76 ):
                set_blind_height("Volet_Salon",76) # ferme les volets ( ouverture à summer_volet_height (100-2.5*temperature)
                #volet_salon_height = 76
                update_status("Volet_Salon", "height",76)
        if (heure_actuelle > duskdone and current_time <= 2300 and temperature > int(temp_min)):  # si entre 23 et 23:20 et temp > temp_min alors
            if (read_mydevice_value("Volet_Salon","height") == 0) : 
                set_blind_height("Volet_Salon",15)      # Ouvre volet salon à 15%
                update_status("Volet_Salon", "height",15)
            if (read_mydevice_value("Volet_Parent","height")  == 0) : 
                set_blind_height("Volet_Parent",36) # Ouvre volet parent à 36%
                update_status("Volet_Parent", "height",36)

    #print ("tuya from "+ str(dusk) + " to "  + str(duskdone))
    #heure_actuelle =  (datetime.combine(datetime.today(), heure_actuelle) - timedelta(minutes=31)).time() 
    #print (heure_actuelle)

    volet_salon_height = read_mydevice_value("Volet_Salon","height")
    volet_parent_height= read_mydevice_value("Volet_Parent","height")
    
    if mydebug: print("ENDSET1 VALUES :", time.time() - start_time, "seconds")
    if (heure_actuelle > dusk and heure_actuelle < duskdone ):               # le soleil est couché
    #if (heure_actuelle > dusk  ):                # le soleil est couché
        #set_blind_backlt(lbl_volet_parent,id_volet_parent,ip_volet_parent,key_volet_parent,False)
        #tempfurio = int(float(get_current_tempatthree(read_mydevice_value("Forecast","city"),read_mydevice_value("Forecast","country_code"))))
        #update_status("Forecast","TempAtThree",tempfurio)
        #if (tempfurio <= 9): tempfurio = "Furio (3am):"+ str( tempfurio)+ "; "
        #else: tempfurio = ""            # Temperature at 3 am pour Furio
        atdata = airthings_data()
        atradon = int(atdata['data']['radonShortTermAvg'])
        atco2 =  int(atdata['data']['co2'])
        atbatt = int(atdata['data']['battery'])
        update_status("Airthings","Air_Radon",atradon)
        update_status("Airthings","Air_Battery",atbatt)
        update_status("Airthings","Air_Co2",atco2)
        myalerts="" 
        #myalerts=remove_Alert_status()
        #if len(myalerts) > 2:myalerts = "; Alerts:"+ myalerts
        if (atradon > 100):atradon = "Radon:"+ str(atradon) + "; "
        else:   atradon = ""
        if (atbatt < 10):  atbatt = "Air+: Battery low("+atbatt+"; " 
        else:     atbatt = "" 
        if (atco2 > 1000): atco2 = "Co2:"+ str(atco2) + "; "  
        else:        atco2 = "" 
        pvprod=int(read_mydevice_value("Enphase","PV_Prod_Day"))/1000
        pvcons=int(read_mydevice_value("Enphase","PV_Cons_Day"))/1000
        pvstat = "PV Prod:{:.1f}".format(pvprod ) + "; PV Cons:{:.1f}".format(pvcons)
        #print ("PVSTAT:"+pvstat)
        #log2file (tempfurio + atbatt + atradon + atco2 + pvstat + myalerts ,True)  # Furio / Radon / PV Details    
        log2file (atbatt + atradon + atco2 + pvstat + myalerts ,True)  # Radon / PV Details    
        toggle_velux("Volet_Velux",2,"on")          # Velux via ewelink 
        update_status("Volet_Velux", "height",0)
        #if mydebug: print ("temperature > temp_min:"+str(temperature)+ " "+ str(temp_min))
        #if mydebug: print ("volet_salon_height:"+str(volet_salon_height))
        set_blind_height("Volet_Salon",0) 
        if (volet_salon_height  != 0)  : 
            set_blind_height("Volet_Salon",0)       # Ouvre volet salon à 0%
            update_status("Volet_Salon", "height",0)
        if (volet_parent_height != 0)  : 
            set_blind_height("Volet_Parent",0)   # Ouvre volet salon à 0%
            update_status("Volet_Parent", "height",0)
    #log2file( "2 Gère les prises")        
    if mydebug: print("BEGget_Bureau_infoSET2 VALUES :", time.time() - start_time, "seconds")
    if (current_hour == 7 and 0 <= current_day <= 5):  # poweron prise PC at 7 am; Monday to Friday:
        if (read_mydevice_value("Prise_Bureau","state")!= 'Off' ):
            set_plug_status("Prise_Bureau",True )
            update_status("Prise_Bureau", "state","On")

    if (current_hour > 8 and 0 <= current_day <= 5):  # poweroff prise if unused after 9 am Monday to Friday:

        if (int(float(read_mydevice_value("Prise_Bureau","powerW"))) < int(read_mydevice_value("AppSettings","min_watt"))):
            if (read_mydevice_value("Prise_Bureau","state") != 'False'): 
                set_plug_status("Prise_Bureau",False)
                update_status("Prise_Bureau", "state","Off")
                
    #if mydebug: print(str(current_time )+ "  > VMC config = "+ read_mydevice_value("Relais_VMC","state")) 
    if (1000 <= current_time < 2100):
        #if mydebug: print(str(current_time )+ "  > its time  to set VMC ON")
        if (read_mydevice_value("Relais_VMC","state") == 'Off'): 
            set_plug_status("Relais_VMC",True)
            log2file("  > powered VMC ON ",False)
            update_status("Relais_VMC", "state","On")
    if (0 <= current_time < 1000 or  current_time > 2100 ):
        if (read_mydevice_value("Relais_VMC","state") != 'Off'): 
            set_plug_status("Relais_VMC",False)
            #log2file("  > powered VMC OFF " ,False)
            update_status("Relais_VMC", "state","Off")
    ##Éteint Ventilateur Antony
    if ((current_hour > 7 and current_hour < 12) or (current_hour < 3 and current_hour > 1)): 
        if (read_mydevice_value("Prise_Antony","state") != 'False'):
            set_plug_status("Prise_Antony",False);
            update_status("Prise_Antony", "state","Off")
    write_config_file(myfolder + "configv2.py")
    if mydebug: print("ENDSET2 VALUES :", time.time() - start_time, "seconds")
    quit()