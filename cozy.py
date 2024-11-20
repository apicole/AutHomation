#io:DerogationRemainingTimeState : "value": 60 time in minute
#core:DerogationOnOffState : On 
#io:PassAPCHeatingModeState  > internalScheduling (auto) ou comfort
# cd C:\Users\xxx\Documents\xxx\xxx; python tuya.py
#From Prof to Manual
 # core:ComfortHeatingTargetTemperatureState > 16 / core:TargetTemperatureState > 16 / io:PassAPCHeatingModeState > comfort

#import requests, json, time, unicodedata, os, sys, errno
#print ("Forecast-temperature ("+ str(read_mydevice_value("Forecast","temperature")) + ") <> Cozytouch-ConsHome ("+ str(read_mydevice_value("Cozytouch","ConsComfort"))+")")

import time

mydelay = 3
mydebug = False
mydebug2 = True

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
    current_minute = int(time.strftime("%M"))
    current_time = int(datetime.now().strftime('%H%M'))
    current_day_of_week = int(datetime.now().isoweekday()) 
    current_month = datetime.now().month
    
    if (current_month >= 10 or current_month <= 4):#Only in winter
        if float(read_mydevice_value("Forecast","temperature")) < float(read_mydevice_value("Cozytouch","ConsComfort")):
            #if (sunrise <= datetime.now().time() < sunset):  print ("Daylight")
            if is_connected():
                #print ( read_mydevice_value("Cozytouch","cozy_user")+" "+ read_mydevice_value("Cozytouch","cozy_passwd"))
                if cozytouch_login(read_mydevice_value("Cozytouch","cozy_user"), read_mydevice_value("Cozytouch","cozy_passwd")):
                    decouverte_devices(mydebug)
                    actualeco_temp = float(cozytouch_GETP('setup','core:EcoHeatingTargetTemperatureState'))
                    actualconfort_temp = float(cozytouch_GETP('setup','core:ComfortHeatingTargetTemperatureState'))
                    HeatingOnOffState = str(cozytouch_GETP('setup','core:HeatingOnOffState').lower())
                    PassAPCHeatingProfileState = str(cozytouch_GETP('setup','io:PassAPCHeatingProfileState').lower())
                    PassAPCHeatingModeState =  str(cozytouch_GETP('setup','io:PassAPCHeatingModeState').lower())
                    if ( HeatingOnOffState == "on"):
                        if (PassAPCHeatingModeState == "internalscheduling"):
                            #if mydebug: print ("  * HeatingOnOffState:On & PassAPCHeatingModeState:internalScheduling")
                            iphome = is_home2()
                            #iphome = False
                            #ConsNight #17
                            #ConsHome  #18
                            #ConsComfort #20.5
                            consigne= read_mydevice_value("Cozytouch","ConsNight")#17
                            if mydebug: log2file("Cozy: ***********WEEKDAY *************************",False)
                            if mydebug: log2file("Cozy: *0-----6---730--------------16---21---23-00*",False)
                            if mydebug: log2file("Cozy: *  17    21          18        21   18   17*",False)
                            if mydebug: log2file("Cozy: ***********WEEKEND *************************",False)
                            if mydebug: log2file("Cozy: *0------8--9--------------15---21---23---00*",False)
                            if mydebug: log2file("Cozy: *  17    21          18        21   18   17*",False)
                            
                            if (current_day_of_week <=5 ):  # Weekdays
                                if (0 <= current_time < 600):
                                    mymode="ConsNight"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsNight")#17
                                if (600<= current_time < 730):
                                    mymode="ConsComfort"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsComfort")#20.5
                                if (730 <= current_time < 1700):
                                    mymode="ConsHome"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsHome")#18
                                if (1600 <= current_time < 2100):
                                    mymode="ConsComfort"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsComfort")#20.5
                                if (2100 <= current_time < 2300):
                                    mymode="ConsHome"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsHome")#18
                                if (2300 <= current_time < 2359):
                                    mymode="ConsNight"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsNight")#17
                                #si ping pierrick/Ramon/Etan alors setEcoHeatingTargetTemperature 18 sinon 16
                            if (current_day_of_week > 5 ):  # Weekdays
                                if (0 <= current_time < 800):
                                    mymode="ConsNight"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsNight")#17
                                if (800<= current_time < 900):
                                    mymode="ConsComfort"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsComfort")#20.5
                                if (900 <= current_time < 1500):
                                    mymode="ConsHome"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsHome")#18
                                if (1500 <= current_time < 2100):
                                    mymode="ConsComfort"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsComfort")#20.5
                                if (2100 <= current_time < 2300):
                                    mymode="ConsHome"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsHome")#18
                                if (2300 <= current_time < 2359):
                                    mymode="ConsNight"
                                    if mydebug: print (mymode)
                                    consigne=read_mydevice_value("Cozytouch","ConsNight")#17
                                #si ping pierrick/Ramon/Etan alors setEcoHeatingTargetTemperature 18 sinon 16
                            #log2file("Cozy: 0-6:Night(17);6-730:Comfort(21);730-17:Home(18);17-21:Comfort(21);21-23:Home(18);23-00:Night(17)",False)
                            #if (iphome == False ):
                                #mydelta  = read_mydevice_value("Cozytouch","ConsDeltaAway")#16
                                #mymode="iphome=False;mydelta="+str(mydelta)
                                #consigne =  float(consigne) - float(mydelta)
                            #if mydebug2: print("  * is_home= " + str(iphome) + "; Consigne=" + str(consigne) + "; Profile=" + str(PassAPCHeatingProfileState)+ " * T_eco:" +str(actualeco_temp) + "T_comf: "+str(actualconfort_temp) )
                            #log2file(" >> is_home= " + str(iphome) + "; Consigne=" + str(consigne) + "; Profile=" + str(PassAPCHeatingProfileState)+ "; T_eco:" +str(actualeco_temp) + "; T_comf: "+str(actualconfort_temp) )
                            #log2file(" >> Consigne=" + str(consigne) + "; Profile=" + str(PassAPCHeatingProfileState)+ "; mymode="+str(mymode)+ "; T_eco:" +str(actualeco_temp) + "; T_comf: "+str(actualconfort_temp) )
                            if PassAPCHeatingProfileState == 'comfort':
                                #if mydebug: print ("  >> loop to comfort")
                                if (actualconfort_temp != float(consigne)):
                                    log2file(" >> Consigne=" + str(consigne) + "; Profile=" + str(PassAPCHeatingProfileState)+ "; mymode="+str(mymode)+ "; T_eco:" +str(actualeco_temp) + "; T_comf: "+str(actualconfort_temp) )
                                    if mydebug: print ("   > Passe la consigne Confort de "+ str(actualconfort_temp) + " vers "+ str(consigne))
                                    log2file(" ip:" + str(iphome) + "; Passe la consigne Confort de "+ str(actualconfort_temp) + " vers "+ str(consigne))
                                    cozytouch_POST('io://0832-9912-8032/15934413#7','setComfortHeatingTargetTemperature',float(consigne))
                                    actualconfort_temp = consigne
                                else:
                                    if mydebug: print ("   > Consigne:"+str(actualconfort_temp) + " == "+ str(consigne))

                            if PassAPCHeatingProfileState == 'eco':
                                #if mydebug: print ("  >> loop to eco")
                                if (actualeco_temp != float(consigne)):
                                    log2file(" >> Consigne=" + str(consigne) + "; Profile=" + str(PassAPCHeatingProfileState)+ "; mymode="+str(mymode)+ "; T_eco:" +str(actualeco_temp) + "; T_comf: "+str(actualconfort_temp) )
                                    if mydebug: print ("   > Passe la consigne Eco de "+ str(actualeco_temp) + " vers "+ str(consigne))
                                    log2file(" ip:" + str(iphome) + "; Passe la consigne Eco de "+ str(actualeco_temp) + " vers "+ str(consigne))
                                    cozytouch_POST('io://0832-9912-8032/15934413#7','setEcoHeatingTargetTemperature',float(consigne))
                                    actualeco_temp = consigne
                                else:
                                    if mydebug: print ("   > Consigne:"+str(actualeco_temp) + " == "+ str(consigne))
                        else:
                            log2file("Cozy: PassAPCHeatingModeState:" + str(PassAPCHeatingModeState))
                    else:
                        #if (current_month >= 10 or current_month <= 5):#Only in winter
                        log2file("Cozy: HeatingOnOffState != on",False)

                    if mydebug: 
                        print("STEP : ", time.time() - start_time, "seconds = update_status")
                        update_status("Cozytouch","core:TemperatureState", str(cozytouch_GETP('setup','core:TemperatureState')))
                        update_status("Cozytouch","core:ComfortHeatingTargetTemperatureState", str(actualconfort_temp))
                        update_status("Cozytouch","core:EcoHeatingTargetTemperatureState", str(actualeco_temp))
                        update_status("Cozytouch","core:DerogationOnOffState", str(cozytouch_GETP('setup','core:DerogationOnOffState')))
                        update_status("Cozytouch","io:PassAPCHeatingProfileState", str(cozytouch_GETP('setup','io:PassAPCHeatingProfileState')))
                        #update_status("Cozytouch","io:DerogationRemainingTimeState", str(cozytouch_GETP('setup','io:DerogationRemainingTimeState')))

                        print ("***SETUP***********")
                        print ("  * OnOffState: " + str(HeatingOnOffState))
                        print ("  * Temp Actu : " + read_mydevice_value("Cozytouch","core:TemperatureState"))
                        print ("  * Profile   : " + read_mydevice_value("Cozytouch","io:PassAPCHeatingProfileState"))
                        print ("  * Confort   : " + str(actualconfort_temp) + " |  ConsComfo : "+str(read_mydevice_value("Cozytouch","ConsComfort")))
                        print ("  * Eco-Home  : " + str(actualeco_temp) + " |  ConsHome  : "+str(read_mydevice_value("Cozytouch","ConsHome")))
                        print ("  * ConsNight : "+str(read_mydevice_value("Cozytouch","ConsNight"))+ "   |  ConsAway  : "+str(read_mydevice_value("Cozytouch","ConsDeltaAway")))
                        print ("  * DerogOnOff: " + read_mydevice_value("Cozytouch",'core:DerogationOnOffState'))
                        print ("*******************")
                        #print ("DerogTime : " + read_mydevice_value("Cozytouch",'io:DerogationRemainingTimeState'))

                    #print ("Test Read: "+ read_mydevice_value("Cozytouch","core:TemperatureState"))
                    #cozytouch_POST('io://0832-9912-8032/15934413#7','setEcoHeatingTargetTemperature',18)
                    #cozytouch_POST('io://0832-9912-8032/15934413#7','setComfortHeatingTargetTemperature',21)

                else:
                    #log2file("!!!! Echec connexion serveur Cozytouch")
                    #print("!!!! Echec connexion serveur Cozytouch")
                    sys.exit(errno.ECONNREFUSED)

            #write_config_file(myfolder + "configv2.py")
        #else:
            #if current_minute % 30 == 0:
                #log2file("Ignored : Forecast-temperature ("+ str(read_mydevice_value("Forecast","temperature")) + ") > Cozytouch-ConsHome ("+ str(read_mydevice_value("Cozytouch","ConsComfort"))+")",False)
            
    if mydebug: print("END  :", time.time() - start_time, "seconds")
    quit()