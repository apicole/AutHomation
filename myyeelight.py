#install module from /home/pi/.xxx/config/post_main.d/sococli.sh
# vi ~/.xxx/config/user_crontab     # crontab -e   // cd /home/pi/xxx/config
# cd C:\Users\xxx\Documents\xxx\xxx; python myyeelight.py
#FLOWS : https://gitlab.com/stavros/python-yeelight/-/blob/master/yeelight/flows.py?ref_type=heads
#Horaires :
# xxx 6h50 - 7h20 sunrise  >>  20h30 - 22h cyan 
# Monrning and evening Kitchen 
# During Sun time :
# YeeStrip_Kitchen Green if solar +

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
    #if mydebug: remove_Alert_status()
    #script_filename = os.path.splitext(os.path.basename(sys.argv[0]))[0]  # Get the script filename without extension

    # list  : from yeelight import discover_bulbs
    #   bulbs = discover_bulbs()
    #   ips = [bulb['ip'] or bulb in bulbs]
    #	print(ips) # Print

    current_time = int(datetime.now().strftime('%H%M'))
    current_day_of_week = int(datetime.now().isoweekday())
    heure_actuelle = datetime.now().time()

    usrcity = LocationInfo(read_mydevice_value("Forecast","city"), 'France','Europe/Paris',48.015, 7.54)
    s = sun(usrcity.observer, date=date.today(), tzinfo=usrcity.timezone)
    sunrise = datetime.strptime(s["sunrise"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time()#srise
    sunset = datetime.strptime(s["sunset"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time()#sset
    sunsetminus10   = (datetime.combine(datetime.today(), sunset) + timedelta(minutes=-10)).time() # 30 min after rise
    riseplus30 = (datetime.combine(datetime.today(), sunrise) + timedelta(minutes=30)).time() # 30 min after rise
    riseplus20 = (datetime.combine(datetime.today(), sunrise) + timedelta(minutes=20)).time() # 30 min after rise
    riseplus10 = (datetime.combine(datetime.today(), sunrise) + timedelta(minutes=10)).time()  # 10 min after rise
    setkitchen = (datetime.combine(datetime.today(), sunset) + timedelta(minutes=-20)).time() # 20 min before set
    if mydebug: print("STEP1 :", time.time() - start_time, "seconds - morning sunrise  <"+ str(riseplus20) )
    if (current_day_of_week <=5 ):  # Weekdays    
        if heure_actuelle < riseplus20:
            if (620 <= current_time < 621):
                if mydebug: print ( "   > YeeStrip_Kitchen:35")
                set_lamp_night("YeeStrip_Kitchen",35)
                update_status("YeeLight_kan", "state","on")
            if (650 <= current_time < 651):
                if mydebug: print ( "   > YeeLight_kan:15")
                yee_sunrise("YeeLight_kan",15)
                update_status("YeeLight_kan", "state","on")
        if (730 <= current_time < 731):
            if mydebug: print ( "   > YeeLight_kan:off")
            set_lamp_status("YeeLight_kan",'off') 
            update_status("YeeLight_kan", "state","off")

    if mydebug: print ("  >> from "+ str(riseplus30) + " to "  + str(sunsetminus10) + "  - PV_Power_Now:"+ read_mydevice_value("Enphase",'PV_Power_Now'))
    if mydebug: print("STEP2 :", time.time() - start_time, "seconds - day between  "+ str(riseplus20)+ "  <= " + str(sunsetminus10) + " = YeeStrip_Kitchen green or off")
    if (riseplus20 <= heure_actuelle < sunsetminus10) :
        #kitchen_status = "off"
        iphome = is_home2()
        if mydebug: print ("   > ishome : "+ str(iphome))
        if int(read_mydevice_value("Enphase",'PV_Power_Now')) > 0 and (iphome != False ):
            if mydebug: print ("   > "+str(read_mydevice_value("Enphase",'PV_Power_Now')) +" Watts:Set lamp to green")
            set_lamp_status('YeeStrip_Kitchen',"on", '0,128,0',80) #print ( "Produit > green")
            update_status("YeeStrip_Kitchen", "state","on")
        else:
            set_lamp_status('YeeStrip_Kitchen',"off", '0,128,0',80) #print ( "Consomme > off")
            if mydebug: print (str(read_mydevice_value("Enphase",'PV_Power_Now')) + " Watts:Set lamp to off")
            #update_status("YeeStrip_Kitchen", "state","off")
    #print ("if " + str(heure_actuelle ) + " > " + str(sunsetminus10 )+ " and 1810 < " + str(current_time )+ " < 2130")
    if mydebug: print("STEP3 :", time.time() - start_time, "seconds -  sun is down AND time is between 1700 untill 2130")
    if ((heure_actuelle > sunsetminus10) and ( 1700 <= current_time < 2130)):  # if sun is down AND time is between 1700 untill 2130
        set_lamp_night("YeeStrip_Kitchen",35)
        if mydebug: print ( "YeeStrip_Kitchen:35")
        if (2020 <= current_time < 2021):
            set_lamp_lsd("YeeLight_kan") 
            if mydebug: print ( "YeeLight_kan:lsd")
            update_status("YeeLight_kan", "state","on")
            #set_lamp_status(lbl_YeeLight_kan,ip_YeeLight_kan,'on', '43,250,250')   # 2882298 print ("set YeeLight_kan cyan")


    if mydebug: print("STEP4 :", time.time() - start_time, "seconds - after 21:30 = Éteint YeeLight_kan et YeeStrip_Kitchen")
    if (2130 <= current_time < 2131):    # Éteint YeeLight_kan
        if mydebug: print ( "YeeLight_kan:off")
        set_lamp_status("YeeLight_kan",'off')
        update_status("YeeLight_kan", "state","off")
    if (2230 <= current_time < 2231):    # Éteint YeeLight_kan
        if mydebug: print ( "YeeLight_kan:off")
        set_lamp_status("YeeLight_kan",'off')
        update_status("YeeLight_kan", "state","off")
        set_lamp_status("YeeStrip_Kitchen",'off')
        update_status("YeeStrip_Kitchen", "state","off")
    if (2330 <= current_time < 2331):    # Éteint YeeLight_kan
        if mydebug: print ( "YeeLight_kan:off")
        set_lamp_status("YeeLight_kan",'off')
        update_status("YeeLight_kan", "state","off")

    #write_config_file(myfolder + "configv2.py")
    if mydebug: print("END  :", time.time() - start_time, "seconds")
    quit()
    
    #rgb= (decimal_to_rgb(16768190))
    #bulb = Bulb(ip_YeeStrip_Kitchen)
    #ransitions = [  TemperatureTransition(1700, duration=1000),  SleepTransition(duration=1000),  TemperatureTransition(6500, duration=1000)]
    #low = Flow( count=0, action=Flow.actions.recover, transitions=transitions)
    #transitions = [ RGBTransition(255, 255, 255, SleepTransition(duration=1000),duration=100)]
    #flow = Flow( count=0, action=Flow.actions.recover,transitions=transitions)