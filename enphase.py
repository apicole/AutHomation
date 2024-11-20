#install module from /home/pi/.xxx/config/post_main.d/sococli.sh
# vi ~/.xxx/config/user_crontab     # crontab -e   // cd /home/pi/xxx/config
# cd C:\Users\xxx\Documents\xxx\xxx; python enphase.py

import enphase_api
from enphase_api.cloud.authentication import Authentication
from enphase_api.local.gateway import Gateway

import time

mydelay = 1
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
    current_minute = int(time.strftime("%M"))
    current_time = datetime.now().strftime('%H%M')
    current_day_of_week = int(datetime.now().isoweekday())
    heure_actuelle = datetime.now().time()
    usrcity = LocationInfo(read_mydevice_value("Forecast","city"), 'France','Europe/Paris',48.015, 7.54)
    s = sun(usrcity.observer, date=date.today(), tzinfo=usrcity.timezone)
    sunrise = datetime.strptime(s["sunrise"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time()#sun rise
    sunset  = datetime.strptime(s["sunset"].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").time() #sun set
    risekitchen = (datetime.combine(datetime.today(), sunrise) + timedelta(minutes=30)).time() # 30 min after rise
    setkitchen  = (datetime.combine(datetime.today(), sunset) + timedelta(minutes=-20)).time() # 20 min before set

    if mydebug: print((
        f'Sunrise: {format(s["sunrise"].strftime("%Y-%m-%d %H:%M"))}\n'#    f'Dawn:    {format(s["dawn"].strftime("%Y-%m-%d %H:%M:%S"))}\n'
        f'Sunset:  {format(s["sunset"].strftime("%Y-%m-%d %H:%M"))}\n'#    f'Noon:    {format(s["noon"].strftime("%Y-%m-%d %H:%M:%S"))}\n'
    #    f'Dusk:    {format(s["dusk"].strftime("%Y-%m-%d %H:%M:%S"))}\n'
        ))
    #print ("enphase: "+str(sunrise ) + "<= " + str(heure_actuelle ) + "< " +str(sunset))
    if (sunrise <= heure_actuelle < sunset) or mydebug:
    #if True:
        try:
            if (is_ip_responsive3("Enphase")):
                if (is_connected()):
                    #update_status("IP_Envoy", iqGatewayIp)
                    authentication = Authentication()
                    authentication.authenticate(read_mydevice_value("Enphase","usremail"), read_mydevice_value("Enphase","usrpassword"))
                    TOKEN = authentication.get_token_for_commissioned_gateway(read_mydevice_value("Enphase","gw"))
                    gateway = Gateway( 'https://'+ read_mydevice_value("Enphase","ip"))

                    if gateway.login(TOKEN):
                        jsonproduction = gateway.api_call('/production.json')
                        #print(jsonproduction)
                        inverters=jsonproduction['production'][0]
                        production=jsonproduction['production'][1]
                        consumption=jsonproduction['consumption'][0]
                        #data = json.loads(jsonproduction)
                        #json_formatted_str = json.dumps(data, indent=2)
                        #print(json_formatted_str)
                        mybuffer = int(0.25 * int(consumption['wNow']))
                        nbinverters= int(read_mydevice_value("Enphase","nbinverters"))
                        #print('Production read {} Watts; Consumption reads {} Watts, Delta is {} Watts, Buffer is {} Watts'.format(production['wNow'], consumption['wNow'], ConsoNow, int(mybuffer)))
                        if (int(inverters['activeCount'] < nbinverters)) :
                            log2file("\n /!\ \n /!\ Warning :  " + str(inverters['activeCount']) + " inverters / "+str(nbinverters)+" !! \n /!\ \n",True)
                        #print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(production['readingTime'])) +' - '+str(inverters['activeCount'])+'/'+str(nbinverters)+';Prod:'+str(int(production['wNow']))+';Cons:'+str(int(consumption['wNow']))+' --> '+ConsoNow)
                        iqGateway_production = gateway.api_call('/production.json?details=1')
                        #data = json.loads(iqGateway_production.text)
                        data = iqGateway_production
                        json_formatted_str = json.dumps(iqGateway_production, indent=2)
                        if mydebug: print(json_formatted_str)
                        Prod="Prod:"+str(int(data['production'][1]['wNow']))+";ph1:" + str(int(data['production'][1]['lines'][0]['wNow']))+";ph2:" + str(int(data['production'][1]['lines'][1]['wNow']))+";ph3:" + str(int(data['production'][1]['lines'][2]['wNow']))
                        Cons="Cons:"+str(int(data['consumption'][0]['wNow']))+";ph1:" + str(int(data['consumption'][0]['lines'][0]['wNow']))+";ph2:" + str(int(data['consumption'][0]['lines'][1]['wNow']))+";ph3:" + str(int(data['consumption'][0]['lines'][2]['wNow']))
                        ConsoNow =  str(int(production['wNow']) - int(consumption['wNow']) - mybuffer)
                        update_status("Enphase","PV_Prod_Inst",int(production['wNow']))
                        update_status("Enphase","PV_Cons_Inst",int(consumption['wNow']))
                        update_status("Enphase","PV_Power_Now",ConsoNow)
                        if mydebug: print ( "ConsoNow:"+str(int(production['wNow']))+"-"+str(int(consumption['wNow']))+"-"+str(mybuffer)+"="+str(ConsoNow) )
                        update_status("Enphase","PV_Buffer", int(mybuffer))
                        PV_Prod_Day = int(jsonproduction['production'][1]['whToday'])
                        PV_Cons_Day = int(jsonproduction['consumption'][0]['whToday'])
                        update_status("Enphase","PV_Prod_Day", int(PV_Prod_Day))
                        update_status("Enphase","PV_Cons_Day", int(PV_Cons_Day))

                        if (1100 <= int(current_time) < 1500 ):
                            if current_minute % 30 == 0:
                                if (int(data['production'][1]['wNow']) < 10 ) : log2file( "Alert on Production between 11' and 15' ! Please check connection".format(iqGatewayIp),True)
                                if (int(data['consumption'][0]['wNow'])< 100) : log2file( "Alert on Consumption between 11' and 15' ! Please check connection".format(iqGatewayIp),True)
                        #if (risekitchen <= heure_actuelle < setkitchen) :
                            #if (800 <= int(current_time) < 2100):
                                #update_status("YeeStrip_Kitchen", "state",kitchen_solar())
                        #print("PV_Prod_Day:"+str(PV_Prod_Day)+";PV_Cons_Day:"+ str(PV_Cons_Day))
                        
                        if current_minute % 30 == 0:
                            uploadprod = requests.get('https://xxx/favoris/xxx?statut=' + str(ConsoNow)+","+Prod+","+Cons+",Buffer:"+str(mybuffer)+","+time.strftime("%H:%M"), verify=False)
                            #print('https://xxx/favoris/xxx?statut=' + str(ConsoNow)+","+Prod+","+Cons+";Buffer:"+str(mybuffer)+";"+time.strftime("%H:%M"))
                            if mydebug: print ("ConsoNow (" + ConsoNow + ") : prod(" +  str(production['wNow']) + ") - cons(" + str(consumption['wNow']) + ") - buffer("+  str(mybuffer)+ ")")
                            #log2file ("ConsoNow (" + ConsoNow + ") : prod(" +  str(production['wNow']) + ") - cons(" + str(consumption['wNow']) + ") - buffer("+  str(mybuffer)+ ")", False)
                    else:
                        log2file( "Could not connect to Envoy on {}, please check connection".format(iqGatewayIp),True)
                else:
                    log2file( 'Could not connect to Envoy on {}, please check connection'.format(iqGatewayIp),True)
                #log2file("ConsoNow (" + ConsoNow + ") : prod(" +  str(production['wNow']) + ") - cons(" + str(consumption['wNow']) + ") - buffer("+  str(mybuffer)+ ")",False)
                write_config_file(myfolder + "configv2.py")
        
        except KeyboardInterrupt:
            print ("Interruption Clavier")
            pass

