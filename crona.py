# Get Device ID  : https://eu.iot.tuya.com/cloud/basic?id=pxxxtm&toptab=related&region=EU
# Get Local_Key  : https://eu.iot.tuya.com/cloud/explorer  device management > Query Device Details 
# vi ~/.xxx/config/user_crontab     # crontab -e   // cd /home/pi/xxx/config
# cd C:\Users\xxx\Documents\xxx\xxx; python crona.py

import asyncio
import os, time, logging
from meross_iot.controller.mixins.roller_shutter import RollerShutterTimerMixin
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.model.enums import OnlineStatus

meross_root_logger = logging.getLogger("meross_iot")
meross_root_logger.setLevel(logging.ERROR)

mydelay = 2
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
    #script_filename = os.path.splitext(os.path.basename(sys.argv[0]))[0]  # Get the script filename without extension
    usrcity = LocationInfo(read_mydevice_value("Forecast","city"), 'France','Europe/Paris',98.015, 7.54)
    s = sun(usrcity.observer, date=date.today(), tzinfo=usrcity.timezone)
    
    heure_actuelle = datetime.now().time()
    current_month = datetime.now().month
    current_day = datetime.now().weekday()
    current_hour = datetime.now().hour
    current_minute = int(time.strftime("%M"))
    current_time = int(datetime.now().strftime('%H%M'))
    current_day_of_week = int(datetime.now().isoweekday())

    sunset = datetime.strptime(s["sunset"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time()#sset
    dusk  = datetime.strptime(s["dusk"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time()   #horizon
    fourtymtosunset = (datetime.combine(datetime.today(), dusk) - timedelta(minutes=40)).time() 
    thirtytosunset = (datetime.combine(datetime.today(), dusk) - timedelta(minutes=30)).time() 
    duskdone = (datetime.combine(datetime.today(), dusk) + timedelta(minutes=5)).time() 

    if (900 <= current_time < 2350):
        if mydebug: print ("CHECK PV : values for nbinverters; PV_Prod_Day; PV_Cons_Day")
        if int(read_mydevice_value("Enphase","nbinverters")) != 11 :  log2file("Enphase;nbinverters="+ str(read_mydevice_value("Enphase","nbinverters")),True)
        if int(read_mydevice_value("Enphase","PV_Prod_Day")) < 2 :  log2file("Enphase;PV_Prod_Day="+ str(read_mydevice_value("Enphase","PV_Prod_Day")),True)
        if int(read_mydevice_value("Enphase","PV_Cons_Day")) < 2 :  log2file("Enphase;PV_Cons_Day="+ str(read_mydevice_value("Enphase","PV_Cons_Day")),True)
    
    if (is_connected()):
        temperature = get_current_temp(read_mydevice_value("Forecast","city"),read_mydevice_value("Forecast","country_code"))
    else:
        temperature = 20
    temperature = int(float(temperature))
    if (temperature < 0 or temperature > 50): temperature = 22
    if mydebug: print ("GET BLINDERS")
    update_status("Forecast", "temperature",temperature)
    #update_status("Volet_Salon","Summer_height",round(max(20, 100 - 2.5 * temperature)))
    Volet_Salon_height = str(read_mydevice_value("Volet_Salon","height"))
    #Volet_Parent_height= get_blind_height("Volet_Parent")
    volet_TV_height = int(read_mydevice_value("Volet_TV","height"))
    #print ("volet_TV_height:"+ str(Volet_Salon_height) + " "+ str(volet_TV_height))
    if current_minute % 20 == 0:
        volet_TV_height    = get_blind_meros_height("Volet_TV")
        update_status("Volet_TV", "height",volet_TV_height)
    
    if mydebug: print ("SET BLINDERS")
    #if mydebug: print ("volet_TV_height" + str(volet_TV_height))
    #if mydebug: print ("Volet_Salon_height" + str(Volet_Salon_height))
    #if mydebug: print ("current_time" + str(current_time))
    
    #Monte Volet_TV si matin et Volet_Salon ouvert.
    if (600 <= current_time < 900 and int(Volet_Salon_height) > 75 and int(volet_TV_height) < int(Volet_Salon_height)):
        if (int(volet_TV_height) < 10):
            meross_roller("Volet_TV","open")       # Ouvre volet TV à 100%
            update_status("Volet_TV", "height",100)

    #print ("VoletTV")
    #print (int(volet_TV_height))
    if (1700 <= current_time < 2030 and (int(Volet_Salon_height) < 26) and ( int(volet_TV_height) >  int(Volet_Salon_height)) and int(volet_TV_height) > 0 ):
        print("volettv_1700 <= current_time < 2030 and Volet_Salon_height....")
        if (int(volet_TV_height) > 80):
            meross_roller("Volet_TV","close")       # Ferme volet TV à 0%
            update_status("Volet_TV", "height",0)

    if (heure_actuelle > thirtytosunset and current_time < 2030 and int(volet_TV_height) > 0 ):   #if (2030 <= current_time < 2040):
        print("volettv_heure_actuelle > thirtytosunset and current_time < 2030")
        #if (int(volet_TV_height) > 80):
        meross_roller("Volet_TV","close")       # Ferme volet TV à 0%
        update_status("Volet_TV", "height",0)
            #time.sleep(20)
            #meross_roller("Volet_TV","open")       # ouvre volet TV à 0%
            #time.sleep(2)
            #if (int(temperature) > 22):
            #    time.sleep(10)
            #   meross_roller("Volet_TV","open")       # Ouvre volet TV à 100%
            #    meross_roller("Volet_TV","stop")       # stop volet TV à 100%
            #    time.sleep(2)
            #    update_status("Volet_TV", "height",int(volet_TV_height))

    if mydebug: print("INIT GETYEE :", time.time() - start_time, "seconds")    
    update_status("YeeStrip_Kitchen", "state",get_power_status("YeeStrip_Kitchen"))
    update_status("YeeLight_kan", "state",get_power_status("YeeLight_kan"))

    if (2340 <= current_time < 2350): update_status("Volet_TV", "height",0) #Reset value - in case of... 

    if (current_month >= 10 or current_month <= 4):#Only in winter
        if mydebug: print("INIT COZY :", time.time() - start_time, "seconds")
        if cozytouch_login(read_mydevice_value("Cozytouch","cozy_user"), read_mydevice_value("Cozytouch","cozy_passwd")):
            decouverte_devices(mydebug)
            actualeco_temp = float(cozytouch_GETP('setup','core:EcoHeatingTargetTemperatureState'))
            actualconfort_temp = float(cozytouch_GETP('setup','core:ComfortHeatingTargetTemperatureState'))
            update_status("Cozytouch","core:TemperatureState", str(cozytouch_GETP('setup','core:TemperatureState')))
            update_status("Cozytouch","core:ComfortHeatingTargetTemperatureState", str(actualconfort_temp))
            update_status("Cozytouch","core:EcoHeatingTargetTemperatureState", str(actualeco_temp))
            update_status("Cozytouch","core:DerogationOnOffState", str(cozytouch_GETP('setup','core:DerogationOnOffState')))
            update_status("Cozytouch","io:PassAPCHeatingProfileState", str(cozytouch_GETP('setup','io:PassAPCHeatingProfileState')))
            update_status("Cozytouch","io:DerogationRemainingTimeState", str(cozytouch_GETP('setup','io:DerogationRemainingTimeState')))

    if mydebug: print("INIT GETPLUG1 :", time.time() - start_time, "seconds")
    bureaust= get_plug_state("Prise_Bureau")
    #bureaust = "N/A"
    update_status("Prise_Bureau", "state",bureaust)
    update_status("Prise_Bureau", "powerW",check_plug_power("Prise_Bureau"))
    if str(bureaust) == "N/A": update_status("Prise_Bureau","errors",increm_error("Prise_Bureau"))
    
    relaisst = 0
    if (current_month >= 9 or current_month <= 5):#Only in Winter : VMC
        relaisst = get_plug_state("Relais_VMC")
        if mydebug: print("INIT GETPLUG2 :", time.time() - start_time, "seconds")
        update_status("Relais_VMC", "state",relaisst)
    #if str(bureaust) == "N/A": update_status("Relais_VMC","errors",increm_error("Relais_VMC"))
    
    if mydebug: print("INIT CHARGEPOINT :", time.time() - start_time, "seconds")
    #get_chargepoint_info("Chargepoint") # key_Chargepoint, 112, 1), # key_Chargepoint, 112, 0) # Stop
    
    data = get_chargepoint_info2("Chargepoint") # key_Chargepoint, 112, 1), # key_Chargepoint, 112, 0) # Stop
    #print (data)
    if data != "" :
        try:
           Chargepoint109CarP= (data['dps']['109'])/10 # Current delivered power /10
           if (Chargepoint109CarP >= 1):
               Chargepoint102Courant= (data['dps']['102'])
               ChargePoint106_KW= (data['dps']['106']) /10  # used for charging
               Chargepoint108Amp= (data['dps']['108'])/10
               Chargepoint110Temp= (data['dps']['110'])/10
               update_status("Chargepoint","102Courant",Chargepoint102Courant)
               update_status("Chargepoint","104Delay", (data['dps']['104'])/10)
               update_status("Chargepoint","106_KW",ChargePoint106_KW)
               update_status("Chargepoint","107Volts", (data['dps']['107']))
               update_status("Chargepoint","108Amp",Chargepoint108Amp)
               update_status("Chargepoint","109CarP",Chargepoint109CarP)
               update_status("Chargepoint","110Temp", Chargepoint110Temp)
               update_status("Chargepoint","112StartStop", data['dps']['112'])
               update_status("Chargepoint","113ETime", (data['dps']['113'])/10)
               update_status("Chargepoint","114Temps", (data['dps']['114'])/10)
               if (read_mydevice_value("Chargepoint","state")!="on"):
                    update_status("Chargepoint","state","on")
                    update_status("Chargepoint","ChargePoint_Time",time.strftime("%H:%M"))
                    if (800 <= current_time < 2200):
                        log2file("Chargepoint:" +time.strftime("%H:%M") + " start charge@"+str(Chargepoint108Amp) + "Amp",True)
                    else:
                        log2file("Chargepoint:" +time.strftime("%H:%M") + " start charge@"+str(Chargepoint108Amp) + "Amp",False)
               #updt_status("ChargePoint","off")
           else:
               ChargePoint106_KW=read_mydevice_value("Chargepoint","106_KW")
               Chargepoint108Amp=read_mydevice_value("Chargepoint","108Amp")
               if (read_mydevice_value("Chargepoint","state")=="on"):
                    update_status("Chargepoint","state","off")
                    update_status("Chargepoint","Chargepoint109CarP",Chargepoint109CarP)
                    #print("ChargePoint_EndTime",time.strftime("%H:%M"))
                    if (800 <= current_time < 2200):
                        log2file("Chargepoint:" +time.strftime("%H:%M") + " stop charge@"+str(Chargepoint108Amp) + "Amp",True)
                    else:
                        log2file("Chargepoint:" +time.strftime("%H:%M") + " stop charge@"+str(Chargepoint108Amp) + "Amp",False)
                    end_time = datetime.strptime(time.strftime("%H:%M"), '%H:%M')
                    start_time = datetime.strptime(read_mydevice_value("Chargepoint","ChargePoint_Time"), '%H:%M')
                    time_difference = (end_time - start_time).total_seconds() / 60
                    #time_difference = int((end_time - start_time).total_seconds() / 60)
                    #timedelta_difference = timedelta(minutes=time_difference)
                    #timedif = time_difference.strftime("%H:%M")
                    #formatted_timedelta = str(timedelta_difference)
                    update_status("Chargepoint","LastChargeDate",datetime.now().time())
                    update_status("Chargepoint","ChargePoint_Time","0:0")
                    update_status("Chargepoint","LastChargeData",str(time_difference) + "min@" + read_mydevice_value("Chargepoint","108Amp") + "A = "+ str(ChargePoint106_KW) + "kW")
                    #print ("Chargepoint:" + str(time_difference) + "min@" + read_mydevice_value("Chargepoint","Chargepoint108Amp") + "A = "+ str(ChargePoint106_KW) + "kW")
                    if (800 <= current_time < 2200):
                        log2file("Chargepoint:" + str(time_difference)+"min@" + read_mydevice_value("Chargepoint","108Amp") + "A = "+ str(ChargePoint106_KW) + "kW)",True)
                    else:
                        log2file("Chargepoint:" + str(time_difference)+"min@" + read_mydevice_value("Chargepoint","108Amp") + "A = "+ str(ChargePoint106_KW) + "kW)",False)
                    #log2file("Chargepoint:" + str(time_difference)+"min@" + read_mydevice_value("Chargepoint","108Amp") + "A = "+ str(ChargePoint106_KW) + "kW)",True)
     
        except KeyError:
            ChargePoint106_KW = 0  # or set a default value of your choice
            update_status("Chargepoint","106_KW",ChargePoint106_KW)
    else:
        update_status("Chargepoint","errors",increm_error("Chargepoint"))

    if (current_month >= 10 or current_month <= 4):#Only in Winter
        temp_chauff_Antony=get_chauff_ant("Chauffage_Antony")
    else: temp_chauff_Antony = 16

    if mydebug: print("GET PLUG NAS :", time.time() - start_time, "seconds")
    nasst = get_plug_state("Prise_NAS")
    update_status("Prise_NAS", "state",nasst)
    if str(nasst) == "N/A": update_status("Prise_NAS","errors",increm_error("Prise_NAS"))
    #update_status("Prise_NAS", "state",get_plug_state("Prise_NAS",3.4))
    if mydebug: print("GET PLUG 3D :", time.time() - start_time, "seconds")
    blpst = get_plug_state("Prise_3D")
    update_status("Prise_3D", "state",blpst)
    if str(blpst) == "N/A": update_status("Prise_3D","errors",increm_error("Prise_3D"))
    #update_status("Prise_3D", "state",get_plug_state("Prise_3D",3.4))
    if mydebug: print("GET PLUG Antony:", time.time() - start_time, "seconds")
    antst = get_plug_state("Prise_Antony")
    update_status("Prise_Antony", "state",antst)
    if str(antst) == "N/A": update_status("Prise_Antony","errors",increm_error("Prise_Antony"))
    #update_status("Prise_Antony", "state",get_plug_state("Prise_Antony"))

    if mydebug: print("SET VALUES :", time.time() - start_time, "seconds")
    #current_time = 1201
    if (0 <= current_time < 10) : 
        set_blind_backlt("Volet_Parent",False)
        #print ( "Reset PV")
        # FOR EACH LBL PLUG/RELAIS > False
        #remove_Alert_status()
        update_status("Forecast","Current_Month",current_month)
        update_status("Forecast","Current_WeekDay",current_day)
        #update_status("Current_Hour",current_hour)
        update_status("Forecast","Dawn",datetime.strptime(s["dawn"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time())
        update_status("Forecast","Sunrise",datetime.strptime(s["sunrise"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time())
        update_status("Forecast","Sunset",datetime.strptime(s["sunset"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time())
        update_status("Forecast","Dusk",datetime.strptime(s["dusk"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time())
        update_status("Forecast","Duskdone",duskdone)
        update_status("Forecast","Air_Radon",0)
        update_status("Airthings","Air_Battery",0)
        update_status("Airthings","Air_Co2",0)
        update_status("Enphase","PV_Prod_Day", 0)
        update_status("Enphase","PV_Cons_Day", 0)

    write_config_file(myfolder + "configv2.py")
    if mydebug: print("ENDSET2 VALUES :", time.time() - start_time, "seconds")
    quit()
