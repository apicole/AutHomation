#install module from /home/pi/.xxx/config/post_main.d/sococli.sh
# vi ~/.xxx/config/user_crontab     # crontab -e   // cd /home/pi/xxx/config
# cd C:\Users\xxx\Documents\xxx\xxx; python tuya.py

import importlib
import subprocess
import sys

def install_and_import(package):
    try:
        importlib.import_module(package)
    except ImportError:
        print(f"{package} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    finally:
        globals()[package] = importlib.import_module(package)

# List of modules your script uses
required_packages = ["tinytuya","astral","urllib3","datetime","logging","pprint","asyncio","requests","socket","json","time","os","sys","csv","subprocess","multiprocessing","uuid","random","string","hmac","hashlib","base64","unicodedata","errno"]# Add your packages here

for package in required_packages:
    install_and_import(package)
    
import requests, socket, json, time, os, sys, csv, subprocess, multiprocessing
import uuid, random, string, hmac, hashlib, base64, unicodedata, errno
import datetime, logging, pprint, asyncio
import urllib3, yeelight, re #, warnings
import tinytuya

from datetime import datetime, date, timedelta
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests import HTTPError
from http import HTTPStatus
from yeelight.flows import *
from yeelight.transitions import *
from yeelight import Flow
from yeelight import discover_bulbs, Bulb, flows, transitions as tr
from tinytuya.Contrib import SocketDevice
from tinytuya import Device
from astral import LocationInfo
from astral.sun import sun
from subprocess import Popen, PIPE
from re import findall
from meross_iot.controller.mixins.roller_shutter import RollerShutterTimerMixin
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.model.enums import OnlineStatus

meross_root_logger = logging.getLogger("meross_iot")
meross_root_logger.setLevel(logging.ERROR)
#warnings.simplefilter('ignore')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 
def log2file(text,ntfy=False,ntags="+1"):   # Enregistre les logs dans un fichier texte, et optionellement les partage sur notify si Internet est joignable
    exclude = ["status for bulb YeeLight_kan", "status of Relais_VMC"]
    if all(excl not in text for excl in exclude):
        script_filename = os.path.splitext(os.path.basename(sys.argv[0]))[0]  # Get the script filename without extension
        if 'win' in sys.platform: 
            myfolder= "" 
        else:
            myfolder= "/home/pi/xxx/config/"
        #with open(myfolder+time.strftime("%Y%m%d")+f"_{script_filename}.log", 'a') as f:
        with open(myfolder+time.strftime("%Y")+f"_{script_filename}.log", 'a') as f:
            logstring = time.strftime("%Y-%m-%d %H:%M:%S") + " - " + script_filename + ";" + text
            print (logstring) # Affiche en console
            f.write(f'{logstring}\n')# ;Ecrit dans le fichier    
        f.close()
        if (ntfy):
            send_to_telegram('txt',text)
        
def is_connected(ip="1.1.1.1"):                         # Evalue si Internet est joignable
    try:
        socket.create_connection((ip, 53))
        return True
    except OSError: pass
    return False

def send_to_telegram(typ="txt",message="MessageOrPicturePath"):
    chat_id= read_mydevice_value("AppSettings","tlgChatID")
    #if (read_mydevice_value("send_to_telegram","status")=="on"):
    if (is_connected()):
        if (typ== "txt"):
            try:
                response = requests.post(read_mydevice_value("AppSettings","tlgapiURL")+"sendMessage", json={'chat_id': chat_id, 'text': message})
                if 'Chargepoint:' in message:
                    chat_id= read_mydevice_value("AppSettings","tlgChatRAID")
                    response = requests.post(read_mydevice_value("AppSettings","tlgapiURL")+"sendMessage", json={'chat_id': chat_id, 'text': message})

                #if mydebug: log2file("send_to_telegram:"+(response.text))
            except Exception as e:
                log2file("error send_to_telegram:"+str(e))
        if (typ== "img"):
            try:
                response = requests.post(read_mydevice_value("AppSettings","tlgapiURL")+"sendPhoto", data={'chat_id': chat_id}, files={'photo': open(message, 'rb')})
                #if mydebug: log2file("send_to_telegram:"+(response.text))
            except Exception as e:
                log2file("error send_to_telegram:"+str(e))
#else:
#    log2file("status of send_to_telegram != on",False)

def find_mydevice_label_by_value(attribute, value): #if it's not inside the IPs.. 
    for mydevice_label, mydevice in mydevices.items():
        if getattr(mydevice, attribute, None) == value:
            return mydevice_label
    return None

def is_home2():
    # Ping each IP address in home_ips list
    Home_ip_list = read_mydevice_value("Pierrick","PCPro")+","+ read_mydevice_value("Pierrick","Smartphone")+","+read_mydevice_value("Ramon","PCPro")+","+read_mydevice_value("Ramon","PCPerso")+","+ read_mydevice_value("Ramon","Smartphone")+","+read_mydevice_value("Etan","PCPro")+","+ read_mydevice_value("Etan","Smartphone")+","+ read_mydevice_value("Elas","Smartphone")+","+ read_mydevice_value("Elas","PCPerso")
    Home_ips = Home_ip_list.split(',')
    #print (Home_ips)
    for ip in Home_ips:
        # Execute ping command
        #print ("ping " + ip)
        command = ["ping", "-c", "1", ip]  # For Unix-based systems like Linux and macOS
        if 'win' in sys.platform:
            command = ["ping", "-n", "1", ip]  # For Windows
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            #log2file("is_home2 : " +  ip,False) 
            return ip  # If ping was successful, consider yourself at home
    return False  # If no successful ping, consider yourself not at home
    
def yee_sunrise(lbl_bulb, duration=5):
    if (read_mydevice_value(lbl_bulb,"status")=="on"):
        ip_bulb = read_mydevice_value(lbl_bulb,'ip')
        if (get_power_status(lbl_bulb))!= 'on':
            bulb = Bulb(ip_bulb) 
            try:
                bulb.turn_off() 
            except Exception as e:
                log2file("set_bulb_status "+ lbl_bulb+" - {:<15}".format(ip_bulb) + " > Device failed to turn off: Sunrise {e}",False) 
            time.sleep(1)
            try: 
                bulb.turn_on() 
            except Exception as e:
                log2file("set_bulb_status "+ lbl_bulb+" - {:<15}".format(ip_bulb) + " > Device failed to turn on: Sunrise {e}",False)
            duration = duration * 1000 * 60
            transitions = [
                # First set to minimum temperature, low brightness, nearly immediately.
                tr.TemperatureTransition(1700, duration=50, brightness=1),
                # Then slowly transition to higher temperature, max brightness.5000 is about regular daylight white.
                tr.TemperatureTransition(2100, duration=duration / 2, brightness=50),
                tr.TemperatureTransition(4000, duration=duration / 2, brightness=100),
            ]
            flow = yeelight.Flow(count=1, action=yeelight.flow.Action.stay, transitions=transitions)
            try:
                bulb.start_flow(flow)
            except Exception as e:
                log2file("set_bulb_status "+ lbl_bulb+" - {:<15}".format(ip_bulb) + " > Device failed to flow : Sunrise {e}",False)
    else:
        log2file("status of "+lbl_bulb+" != on",False)

def get_power_status(lbl_bulb):
    if (read_mydevice_value(lbl_bulb,"status")=="on"):
        ip_bulb = read_mydevice_value(lbl_bulb,'ip')
        #print (lbl_bulb + ": "+ip_bulb)
        try:
            bulb = Bulb(ip_bulb)
            properties = bulb.get_properties()
            #print (str(properties))
            power = properties.get('power')
            #print (lbl_bulb + ": " + power)
            return power
        except Exception as e:
            log2file(f"Error getting power status for bulb "+lbl_bulb + " at "+ ip_bulb,False)
            return None
    else:
        log2file("status of "+lbl_bulb+" != on",False)
        return None
        
def kitchen_solar():
    if (read_mydevice_value("Enphase","status")=="on"):
        ConsoNow = read_mydevice_value("Enphase",'PV_Power_Now') #
        #ConsoNow = Difference betwene Production and Consumption >> if is more than > 0 = Produce 
        if (int(ConsoNow) > 0) :    #print ( "Produit > Set light to Green")
            #set_lamp_status('YeeStrip_Kitchen','on', '0,128,0',80) #print ( "Produit > green")
            status = "on"
        else:                       #print ( "Consomme > Set light to red")
            #set_lamp_status('YeeStrip_Kitchen','off', '0,128,0',80) #print ( "Consomme > Off")
            status = "off"
        return status
    else:
        log2file("status of Enphase != on",False)
        return "off"

def get_rgb_status(lbl_bulb):
    if (read_mydevice_value(lbl_bulb,"status")=="on"):
        ip_bulb = read_mydevice_value(lbl_bulb,'ip')
        try:
            bulb = Bulb(ip_bulb)
            properties = bulb.get_properties()
            rgb = properties.get('flowing')
            return rgb
        except Exception as e:
            log2file(f"Error getting power status for bulb "+lbl_bulb + " at {ip_bulb}: {e}",False)
            return None
    else:
        log2file("status of "+lbl_bulb+" != on",False)
        return None

def set_lamp_status(lbl_bulb, state, rgb='255,255,255', bright=1):
    if (read_mydevice_value(lbl_bulb,"status")=="on"):
        ip_bulb = read_mydevice_value(lbl_bulb,'ip')
        rbghex  = rgb_string_to_decimal(rgb)
        #print (lbl_bulb + " > " + state)
        if (is_ip_responsive3(lbl_bulb)):
            bulb = Bulb(ip_bulb) 
            #updt_status(lbl_bulb, "state", state)
            #updt_status(lbl_bulb, "ip", ip_bulb)
            bulb.stop_flow()
            if state.lower() == 'off':
                bulb.turn_off() 
                #log2file("set_bulb_status "+ lbl_bulb+" - {:<15}".format(ip_bulb) + " > Device turned off",False)
                return
            if (get_power_status(lbl_bulb))!= state: #,ip_bulb
                if (state.lower() == "on"):
                    r, g, b = map(int, rgb.split(","))
                    bulb.turn_on() 
                    #log2file("set_bulb_status "+ lbl_bulb+" - {:<15}".format(ip_bulb) + " > " + 'Device turn on: '+state+' rgb('+rgb+")",False)
                else:
                    bulb.turn_off() 
                    #log2file("set_bulb_status "+ lbl_bulb+" - {:<15}".format(ip_bulb) + " > Device turned off",False)
            if (int(rbghex) != int(get_rgb_status(lbl_bulb))):
                bulb.turn_off() 
                #log2file("set_bulb_status "+ lbl_bulb+" - {:<15}".format(ip_bulb) + " > Device turned off",False)
                r, g, b = map(int, rgb.split(","))
                bulb.turn_on() 
                #log2file("set_bulb_status "+ lbl_bulb+" - {:<15}".format(ip_bulb) + " > " + 'Device turn on: '+state+' rgb('+rgb+")",True)
                bulb.set_rgb(r,g,b)
            if (bright <100):
                bulb.set_brightness(int(bright))
            else:
                bulb.set_brightness(100)
    else:
        log2file("status of "+lbl_bulb+" != on",False)

def set_lamp_lsd(lbl_bulb):  # kan
    if (read_mydevice_value(lbl_bulb,"status")=="on"):
        ip_bulb = read_mydevice_value(lbl_bulb,'ip')
        if is_ip_responsive3(lbl_bulb):
            #if (read_mydevice_value(lbl_bulb,"Alert")!="True"):
            #print( "set_lamp_lsd " + lbl_bulb)
            bulb = Bulb(ip_bulb) 
            #updt_status(lbl_bulb+"_IP",ip_bulb)
            flow = Flow(  count=0, transitions=lsd() )
            bulb.set_brightness(1)
            bulb.turn_on()
            bulb.start_flow(flow)
        else:
            log2file("set_lamp_lsd error ping "+ lbl_bulb)
    else:
        log2file("status of "+lbl_bulb+" != on",False)

def set_lamp_night(lbl_bulb, brightness): # Kitchen
    if (read_mydevice_value(lbl_bulb,"status")=="on"):
        ip_bulb = read_mydevice_value(lbl_bulb,'ip')
        #if (read_mydevice_value(lbl_bulb,"Alert")!="True"):
        #print( "set_lamp_night " + lbl_bulb)
        bulb = Bulb(ip_bulb) 
        #updt_status(lbl_bulb+"_IP",ip_bulb)
        #NIGHT
        transition = [ RGBTransition(0xFF, 0x99, 0x00, duration=500, brightness=brightness)]
        flow = Flow( count=0, action=Action.recover, transitions=transition)
        #HOME
        #transition = [ TemperatureTransition(degrees=3200, duration=500, brightness=81)]
        #flow = Flow(count=0, action=Action.recover, transitions=transition)
        #OTHER
        #transition = tr.christmas()
        #flow = Flow( count=0, action=Action.recover, transitions=transition)
        bulb.turn_on()
        bulb.start_flow(flow)
    else:
        log2file("status of "+lbl_bulb+" != on",False)
        
def rgb_string_to_decimal(rgb_str):
    r, g, b = map(int, rgb_str.split(','))
    return (r << 16) + (g << 8) + b
    
def rgb_to_decimal(r, g, b):
    return (r << 16) + (g << 8) + b
    
def decimal_to_rgb(decimal_value):
    r = (decimal_value >> 16) & 0xFF
    g = (decimal_value >> 8) & 0xFF
    b = decimal_value & 0xFF
    return r, g, b

def is_ip_responsive1(lbl_plug):
    ip = read_mydevice_value(lbl_plug,"ip")
    #print ("ip for : "+lbl_plug + " >> " +str(ip))
    command = ["ping", "-c", "3", ip]  # For Unix-based systems like Linux and macOS
    if 'win' in sys.platform:
        command = ["ping", "-n", "3", ip]  # For Windows
    #if (read_mydevice_value(lbl_plug,"Alert")!="True"):
    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        log2file("is_ip_responsive {:<15}".format(ip) + " " + lbl_plug + " > False. Device Offline",True)
        #updt_status(lbl_plug, "Alert","True")
        return False

def is_ip_responsive3(lbl_plug):
    ip = read_mydevice_value(lbl_plug,"ip")
    command = ["ping", "-c", "3", str(ip)]  # For Unix-based systems like Linux and macOS
    if 'win' in sys.platform:
        command = ["ping", "-n", "3", str(ip)]  # For Windows
    try:
        #if (lbl_plug == "Volet_Salon"):
        #    log2file(lbl_plug + "> " + str(command),False)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    except subprocess.CalledProcessError:
        log2file("is_ip_responsive3 {:<15}".format(ip) + " " + lbl_plug + " > False. Device Offline",True)
    if result.returncode == 0:
        return ip
    return False

def airthings_data():
    if (read_mydevice_value("Airthings","status")=="on"):
        if is_connected():
            authorisation_url = read_mydevice_value("Airthings","AuthUrl")
            airthings_device_id=read_mydevice_value("Airthings","airthings_device_id")
            device_url = f"https://ext-api.airthings.com/v1/devices/{airthings_device_id}/latest-samples"
            token_req_payload = {
                "grant_type": "client_credentials",
                "scope": "read:device:current_values",
            }

            # Request Access Token from auth server
            try:
                token_response = requests.post(
                    authorisation_url,
                    data=token_req_payload,
                    allow_redirects=False,
                    auth=(read_mydevice_value("Airthings","airthings_client_id"),read_mydevice_value("Airthings","airthings_secret") ),
                )
            except HTTPError as e:
                logging.error(e)

            token = token_response.json()["access_token"]
            # end auth token

            # Get the latest data for the device from the Airthings API.
            try:
                api_headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(url=device_url, headers=api_headers)
            except HTTPError as e:
                logging.error(e)

            #print(pprint.pprint(response.json()))
            #print (response.json())
            return response.json()
    else:
        log2file("status of Airthing != on",False)
        return 0

def is_connected2(host="8.8.8.8", port=53, timeout=3):
  try:
    socket.setdefaulttimeout(timeout)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    return True, None
  except Exception as ex:
    #print ex.message
    return False, str(ex)
    

def ewel_create_signature(credentials):
    app_details = {'email': credentials['email'],'password': credentials['password'],'version': '6','ts': int(time.time()),'nonce': ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8)),'appid': read_mydevice_value("Ewelink","Ewe_AppID"),'imei': credentials['imei'],'os': 'iOS','model': 'iPhone11,8','romVersion': '13.2','appVersion': '3.11.0'}
    decryptedAppSecret=read_mydevice_value("Ewelink","Ewe_Secret").encode('utf-8')
    hex_dig = hmac.new(decryptedAppSecret,str.encode(json.dumps(app_details)),digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hex_dig).decode()
    return (sign, app_details)

def ewel_login(credentials, api_region='eu'):
    if (read_mydevice_value("Ewelink","status")=="on"):
        if is_connected():
            sign, payload = ewel_create_signature(credentials)
            headers = {'Authorization' : 'Sign ' + sign,'Content-Type'  : 'application/json;charset=UTF-8'}
            r = requests.post(read_mydevice_value("Ewelink","Ewe_LoginURL").format(api_region),headers=headers, json=payload)
            if not (r.status_code == HTTPStatus.OK):
                return ({"error": "Unable to access coolkit api server [{}]".format(r.text)})
            resp = r.json()
            if 'error' in resp and 'region' in resp and resp['error'] == HTTPStatus.MOVED_PERMANENTLY:
                api_region = resp['region']
                #print('API region set to: {}'.format(api_region))
                return login(credentials, api_region)
            return {"response": resp, "region": api_region, "imei": credentials['imei']}
    else:
        log2file("status of Ewelink != on",False)
        return 0

def get_current_tempatthree(city,country):
    if is_connected():
        url = f'https://api.openweathermap.org/data/2.5/forecast?q={city},{country}&appid={read_mydevice_value("Forecast","owapi")}&units=metric'
        #print (url)
        response = requests.get(url)
        fdate = datetime.now()
        # Add 1 day to today's date
        fnext = fdate + timedelta(days=1)
        # Format the date as a string in "YYYY-MM-DD" format
        todayatthree = fnext.strftime('%Y-%m-%d')+ " 03:00:00"
        #tempatthree = formatted_date + " 03:00:00"  # Find the forecast for 3 am
        #print (todayatthree)
        if response.status_code == 200:
            data = response.json()
            for forecast in data["list"]:
                #print ("1 = " + str(forecast))
                #print (forecast["dt_txt"])
                if forecast["dt_txt"] == todayatthree:
                    #print ("******")
                    temperature = forecast["main"]["temp"]
                    break
            else:
                temperature="-10"
        else:
            temperature="-10"
        #print ("return: temperature="+ str(temperature))
        #updt_status("tempatthree",temperature)
        return temperature

def get_current_temp(city,country):
    if is_connected():
        openweathermapurl = f'http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={read_mydevice_value("Forecast","owapi")}&units=metric'
        response = requests.get(openweathermapurl)
        if response.status_code == 200:    # Check if the request was successful (status code 200)
            data = response.json()
            temperature = data['main']['temp']
        else:
            temperature = '22'
        return temperature

def get_current_temperature(city):
    if is_connected():
        base_url = "https://www.prevision-meteo.ch/services/json/"
        url = f"{base_url}{city}"
        response = requests.get(url)
        try:
            data = response.json()
            if "current_condition" in data:
                temperature = data["current_condition"]["tmp"]
        except KeyError:
            temperature = 22  # or set a default value of your choice
        return temperature
        
def get_plug_state(lbl_plug, version=3.3):
    #print(" GET_PLUG_STATE" + lbl_plug)
    if (read_mydevice_value(lbl_plug,"status")=="on"):
        id_plug = read_mydevice_value(lbl_plug,"id")
        key_plug = read_mydevice_value(lbl_plug,"key")
        ip_plug = read_mydevice_value(lbl_plug,"ip")
        if not is_ip_responsive3(lbl_plug):
            ret_plug_state = "N/A"
            return ret_plug_state
        else: 
            device = Device(id_plug, ip_plug, key_plug, 'default')
            device.set_version(version)
            #device.set_socketPersistent( True )
            device.set_socketTimeout(10)
            #print( device.status() )
            #device.add_dps_to_request(17)
            #device.updatedps([17,18,19,20])
            device.close()
            data = device.status()
            ret_plug_state = "off"
            plug_powerA = 0
            plug_powerW = 0
            #print (data['dps']['1'])
            #print ("get_plug_state " + lbl_plug + " > " +  str(plug_powerA)+ "mA;" + str(plug_powerW)+ "W" )
            #log2file("check_plug_power {:<15}".format(lbl_plug) + " > " + 'set_status() result %r' % data,True)
            try:
                plug_state = data['dps']['1']
                #print("plug is on: " + str(plug_state))
                if str(plug_state) == "True":
                    ret_plug_state = "on"
                    plug_powerA = data['dps']['18']
                    plug_powerW = data['dps']['19'] / 10
                    #print("  T' -> " + ret_plug_state)
                #else:
                    #print("  F' -> " + ret_plug_state)
            except KeyError:
                plug_state = False
                ret_plug_state = "off"

            return ret_plug_state
    else:
        #log2file("status of "+lbl_plug+" != on",False)
        return "N/A"
 
def increm_error(lbl_plug):
    plug_error=int(read_mydevice_value(lbl_plug,"errors"))
    plug_error=plug_error +1
    return plug_error

def check_plug_power(lbl_plug, version=3.3):
    if (read_mydevice_value(lbl_plug,"status")=="on"):
        id_plug = read_mydevice_value(lbl_plug,"id")
        key_plug = read_mydevice_value(lbl_plug,"key")
        ip_plug = read_mydevice_value(lbl_plug,"ip")
        if not is_ip_responsive3(lbl_plug):
            plug_powerA = 88
            plug_powerW = 88
            return  
        device = Device(id_plug, ip_plug, key_plug, 'default')
        device.set_version(version)
        #device.set_socketPersistent( True )
        device.set_socketTimeout(10)
        #print( device.status() )
        #device.add_dps_to_request(17)
        #device.updatedps([17,18,19,20])
        device.close()
        data = device.status()
        try:
            plug_powerA = data['dps']['18']
            plug_powerW = (data['dps']['19'])/10
            #print (" > " +  str(plug_powerA)+ "mA;" + str(plug_powerW)+ "W" )
        except KeyError:
            plug_powerA = 88
            plug_powerW = 88
        #print (" > " +  str(plug_powerA)+ "mA;" + str(plug_powerW)+ "W" )
        #updt_status(lbl_plug,"powerW",plug_powerW)
        return plug_powerW
    else:
        log2file("status of "+lbl_plug+" != on",False)
        return 88
        
def set_plug_status(lbl_plug, state, version=3.3):
    if (read_mydevice_value(lbl_plug,"status")=="on"):
    #print("set_plug_status > " + lbl_plug + " > " + str(state))
        try:
            id_plug = read_mydevice_value(lbl_plug, "id")
            key_plug = read_mydevice_value(lbl_plug, "key")
            ip_plug = read_mydevice_value(lbl_plug, "ip")
            if not ip_plug:
                raise ValueError("IP address for the device not found.")
            device = Device(id_plug, ip_plug, key_plug, 'default')
            device.set_version(version)
            device.set_value('1', state)
            data = device.status()
            #print(data)
            return True
        except Exception as e:
            print(f"Error setting plug status: {e}")
            return False
    else:
        log2file("status of "+lbl_plug+" != on",False)
        return False

def check_blind_light(lbl_plug, version=3.3):
    if (read_mydevice_value(lbl_plug,"status")=="on"):
        id_plug = read_mydevice_value(lbl_plug,"id")
        key_plug = read_mydevice_value(lbl_plug,"key")
        ip_plug = read_mydevice_value(lbl_plug,"ip")
        if is_ip_responsive3(lbl_plug)!= False:
            #if not is_ip_responsive(ip_plug):
                #blind_light = 0
                #return blind_light
            device = Device(id_plug, ip_plug, key_plug, 'default') # lbl_plug
            device.set_version(version)
            data = device.status()
            try:
                blind_light = data['dps']['7']
            except KeyError:
                blind_light = 0  # or set a default value of your choice
            return blind_light
    else:
        log2file("status of "+lbl_plug+" != on",False)
        return 0
        
def set_blind_backlt (lbl_plug, state, version=3.3):
    if (read_mydevice_value(lbl_plug,"status")=="on"):
        id_plug = read_mydevice_value(lbl_plug,"id")
        key_plug = read_mydevice_value(lbl_plug,"key")
        ip_plug = read_mydevice_value(lbl_plug,"ip") 
        if (check_blind_light(lbl_plug) != state): #print( "toggle parent")
            device = Device(id_plug, ip_plug, key_plug, 'default') # lbl_volet
            device.set_version(version)
            device.set_value('7', state)
            #print(device.status)
            data = device.status() 
            #print("{} state height set to {}".format(lbl_volet, state))
            log2file("set_blind_backlt {:<15}".format(lbl_plug) + " > " + 'set_status() result %r' % data,False)
    else:
        log2file("status of "+lbl_plug+" != on",False)

def set_blind_height (lbl_plug, state, version=3.3):
    #print ("set_blind_height" + lbl_plug + " to " + str(state))
    if (read_mydevice_value(lbl_plug,"status")=="on"):
        id_plug = read_mydevice_value(lbl_plug,"id")
        key_plug = read_mydevice_value(lbl_plug,"key")
        ip_plug = read_mydevice_value(lbl_plug,"ip")
        #if is_ip_responsive3(lbl_plug)!= False:
        if (get_blind_height(lbl_plug) != state ):
            #if (get_blind_height(lbl_plug, id_plug,ip_plug,key_plug) > 0 ):
            device = Device(id_plug, ip_plug, key_plug, 'default')  # lbl_plug
            device.set_version(version)
            device.set_value('2', int(state))
            #print(device.status)
            try:
                data = device.status() 
            except KeyError:
                data = 0  # or set a default value of your choice
            #log2file("set_blind_height {:<15}".format(lbl_plug) + " = " + str(state),False)
    else:
        log2file("status of "+lbl_plug+" != on",False)

def get_blind_height(lbl_plug, version=3.3):
    if (read_mydevice_value(lbl_plug,"status")=="on"):
        id_plug = read_mydevice_value(lbl_plug,"id")
        key_plug = read_mydevice_value(lbl_plug,"key")
        ip_plug = read_mydevice_value(lbl_plug,"ip")
        blind_heigh = 0 
        if is_ip_responsive3(lbl_plug)!= False:
            device = Device(id_plug, ip_plug, key_plug, 'default')
            device.set_version(version)
            data = device.status()
            #print (data)
            try:
                blind_heigh = data['dps']['2']
            except KeyError:
                blind_heigh = 0  # or set a default value of your choice
            return blind_heigh
        else:
            return blind_heigh
    else:
        log2file("status of "+lbl_plug+" != on",False)
        return 0

def get_chauff_ant(lbl_chauff, version=3.3):
    if (read_mydevice_value(lbl_chauff,"status")=="on"):
        device_id = read_mydevice_value(lbl_chauff,"id")
        device_key = read_mydevice_value(lbl_chauff,"key")
        device_ip = read_mydevice_value(lbl_chauff,"ip")
        #updt_status(lbl_chauff+"_IP",device_ip)
        if is_ip_responsive3(lbl_chauff)!= False:
            #'dps': {
                #'1': True, 
                #'2': 'auto',   #System Mode
                #'16': 17,      # Consigne
                #'19': 30, 
                #'24': 210,     # Current Temp /10
                #'36': 'close', 
                #'40': True, 
                #'45': 0
               # }}
            # 16 - actual, 19=max,

            device = Device(device_id, device_ip, device_key, 'default')
            device.set_version(version)
            data = device.status()
            #print (data)
            try:
                temp_chauff_Antony = data['dps']['16']
                #updt_status(lbl_chauff,"Consigne",temp_chauff_Antony)
                #updt_status(lbl_chauff,"Current",(data['dps']['24'])/10)
                #updt_status(lbl_chauff,device_ip)
            except KeyError:
                temp_chauff_Antony = 0  # or set a default value of your choice
                #updt_status(lbl_chauff,"Consigne","n/a")
                #updt_status(lbl_chauff,"Current","n/a")
            return temp_chauff_Antony
    else:
        log2file("status of "+lbl_chauff+" != on",False)
        return 0
        
def get_chargepoint_info2(lbl_Chargepoint, version=3.3):
    if (read_mydevice_value(lbl_Chargepoint,"status")=="on"):
        command = ["ping", "-c", "1", read_mydevice_value(lbl_Chargepoint,"ip")]  # For Unix-based systems like Linux and macOS
        if 'win' in sys.platform:
            command = ["ping", "-n", "1", read_mydevice_value(lbl_Chargepoint,"ip")]  # For Windows
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            try:
                id_Chargepoint = read_mydevice_value(lbl_Chargepoint,"id")
                key_Chargepoint = read_mydevice_value(lbl_Chargepoint,"key")
                ip_Chargepoint = read_mydevice_value(lbl_Chargepoint,"ip")
                current_time = int(datetime.now().strftime('%H%M'))
                #updt_status(lbl_Chargepoint+"_IP",ip_Chargepoint)
                #if is_ip_responsive3(lbl_Chargepoint)!= False:
                #{'dps': {
                    #'10': 0, 
                    #'101': 'no_connect', 
                    #'102': 16, = Ampères  8A/10A/13A/16A/25A/32A
                    #'104': 0,  = Delay
                    #'106': 0,  = Used KWh  (/10) ******
                    #'107': 398 = Voltage, 
                    #'108': 0,  = Car_Amps  (/10)
                    #'109': 0,  = Car_Powecr
                    #'110': 202,= Temperature (/10)
                    #'111': Set,= Charging current  8A/10A/13A/16A/25A/32A
                    #'112': False,Manual stop charge switch
                    #'113': 0,  = Charging elapsed /10  ******
                    #'114': 0   = Charge Length
                    #}}

                device = Device(id_Chargepoint, ip_Chargepoint, key_Chargepoint, 'default') # lbl_Chargepoint
                device.set_version(version)
                data = device.status()
                #d = tinytuya.OutletDevice(id_Chargepoint, ip_Chargepoint, key_Chargepoint)
                #d.set_version(3.3)
                #data = d.status() 
                #print('Device status: %r' % data)
                #d = tinytuya.OutletDevice( dev_id=id_Chargepoint,address=ip_Chargepoint,local_key=key_Chargepoint,version=3.3)
                #data = d.status() 
                #print('set_status() result %r' % data)
                
                return data
            except Exception as e:
                print(f"Error setting plug status: {e}")
                increm_error(lbl_Chargepoint)
                return "" 
        else:
            log2file("Ping " + read_mydevice_value(lbl_Chargepoint,"ip") + " failed",False)
            increm_error(lbl_Chargepoint)
            return ""
    else:
        log2file("status of "+lbl_Chargepoint+" != on",False)
        return ""
        
def get_chargepoint_info(lbl_Chargepoint, version=3.3):
    if (read_mydevice_value(lbl_Chargepoint,"status")=="on"):
        id_Chargepoint = read_mydevice_value(lbl_Chargepoint,"id")
        key_Chargepoint = read_mydevice_value(lbl_Chargepoint,"key")
        ip_Chargepoint = read_mydevice_value(lbl_Chargepoint,"ip")
        current_time = int(datetime.now().strftime('%H%M'))
        #updt_status(lbl_Chargepoint+"_IP",ip_Chargepoint)
        #if is_ip_responsive3(lbl_Chargepoint)!= False:
        #{'dps': {
            #'10': 0, 
            #'101': 'no_connect', 
            #'102': 16, = Ampères  8A/10A/13A/16A/25A/32A
            #'104': 0,  = Delay
            #'106': 0,  = Used KWh  (/10) ******
            #'107': 398 = Voltage, 
            #'108': 0,  = Car_Amps  (/10)
            #'109': 0,  = Car_Powecr
            #'110': 202,= Temperature (/10)
            #'111': Set,= Charging current  8A/10A/13A/16A/25A/32A
            #'112': False,Manual stop charge switch
            #'113': 0,  = Charging elapsed /10  ******
            #'114': 0   = Charge Length
            #}}

        device = Device(id_Chargepoint, ip_Chargepoint, key_Chargepoint, 'default') # lbl_Chargepoint
        device.set_version(version)
        data = device.status()
        #print( data)
        try:
           Chargepoint109CarP= (data['dps']['109'])/10 # Current delivered power /10
           if (Chargepoint109CarP >= 1):
               Chargepoint102Courant= (data['dps']['102'])
               ChargePoint106_KW= (data['dps']['106']) /10  # used for charging
               Chargepoint108Amp= (data['dps']['108'])/10
               Chargepoint110Temp= (data['dps']['110'])/10
               #updt_status(lbl_Chargepoint,"102Courant",Chargepoint102Courant)
               #updt_status(lbl_Chargepoint,"104Delay", (data['dps']['104'])/10)
               #updt_status(lbl_Chargepoint,"106_KW",ChargePoint106_KW)
               #updt_status(lbl_Chargepoint,"107Volts", (data['dps']['107']))
               #updt_status(lbl_Chargepoint,"108Amp",Chargepoint108Amp)
               #updt_status(lbl_Chargepoint,"109CarP",Chargepoint109CarP)
               #updt_status(lbl_Chargepoint,"110Temp", Chargepoint110Temp)
               #updt_status(lbl_Chargepoint,"112StartStop", data['dps']['112'])
               #updt_status(lbl_Chargepoint,"113ETime", (data['dps']['113'])/10)
               #updt_status(lbl_Chargepoint,"114Temps", (data['dps']['114'])/10)
               if (read_mydevice_value(lbl_Chargepoint,"state")!="on"):
                    #updt_status(lbl_Chargepoint,"state","on")
                    #print("_Time",time.strftime("%H:%M"))
                    #updt_status(lbl_Chargepoint,"_Time",time.strftime("%H:%M"))
                    if (800 <= current_time < 2200):
                        log2file("Chargepoint:" +time.strftime("%H:%M") + " start charge@"+str(Chargepoint108Amp) + "Amp",True)
                    else:
                        log2file("Chargepoint:" +time.strftime("%H:%M") + " start charge@"+str(Chargepoint108Amp) + "Amp",False)
               #updt_status("ChargePoint","off")
           else:
               ChargePoint106_KW=read_mydevice_value(lbl_Chargepoint,"ChargePoint106_KW")
               Chargepoint108Amp=read_mydevice_value(lbl_Chargepoint,"Chargepoint108Amp")
               if (read_mydevice_value(lbl_Chargepoint,"state")=="on"):
                    #updt_status(lbl_Chargepoint,"state","off")
                    #updt_status(lbl_Chargepoint,"Chargepoint109CarP",Chargepoint109CarP)
                    #print("ChargePoint_EndTime",time.strftime("%H:%M"))
                    if (800 <= current_time < 2200):
                        log2file("Chargepoint:" +time.strftime("%H:%M") + " stop charge@"+str(Chargepoint108Amp) + "Amp",True)
                    else:
                        log2file("Chargepoint:" +time.strftime("%H:%M") + " stop charge@"+str(Chargepoint108Amp) + "Amp",False)
                    end_time = datetime.strptime(time.strftime("%H:%M"), '%H:%M')
                    start_time = datetime.strptime(read_mydevice_value(lbl_Chargepoint,"ChargePoint_Time"), '%H:%M')
                    time_difference = int((end_time - start_time).total_seconds() / 60)
                    timedif = time_difference.strftime("%H:%M")
                    #updt_status(lbl_Chargepoint,"LastChargeDate",datetime.now().time())
                    #updt_status(lbl_Chargepoint,"Time","0:0")
                    #updt_status(lbl_Chargepoint,"LastChargeData",str(time_difference) + "min@" + read_mydevice_value(lbl_Chargepoint,"Chargepoint108Amp") + "A = "+ str(ChargePoint106_KW) + "kW")
                    #print ("Chargepoint:" + str(time_difference) + "min@" + read_mydevice_value(lbl_Chargepoint,"Chargepoint108Amp") + "A = "+ str(ChargePoint106_KW) + "kW")
                    if (800 <= current_time < 2200):
                        log2file("Chargepoint:" + str(time_difference)+"min@" + read_mydevice_value(lbl_Chargepoint,"Chargepoint108Amp") + "A = "+ str(ChargePoint106_KW) + "kW)",True)
                    else:
                        log2file("Chargepoint:" + str(time_difference)+"min@" + read_mydevice_value(lbl_Chargepoint,"Chargepoint108Amp") + "A = "+ str(ChargePoint106_KW) + "kW)",False)
                    #log2file("Chargepoint:" + str(time_difference)+"min@" + read_mydevice_value(lbl_Chargepoint,"Chargepoint108Amp") + "A = "+ str(ChargePoint106_KW) + "kW)",True)
     
        except KeyError:
            ChargePoint106_KW = 0  # or set a default value of your choice
        return ChargePoint106_KW
    else:
        log2file("status of "+lbl_Chargepoint+" != on",False)
        return 0

def set_chargepoint_info(lbl_Chargepoint, parm, valparm,version=3.3):
    if (read_mydevice_value(lbl_Chargepoint,"status")=="on"):
        id_Chargepoint = read_mydevice_value(lbl_Chargepoint,"id")
        key_Chargepoint = read_mydevice_value(lbl_Chargepoint,"key")
        ip_Chargepoint = read_mydevice_value(lbl_Chargepoint,"ip")
        #updt_status(lbl_Chargepoint+ "_IP",ip_Chargepoint)
        #DPS	Action
        #101	Etat
        #102	Définir le courant
        #104	Délai avant Démarrage
        #106	Energie restituée
        #107	Voltage
        #108	Ampérage
        #109	Puissance fournie
        #110	Température
        #112	Arreter
        #112	Démarrer la charge
        #113	Temps depuis que la voiture charge
        #114	Temps de charge borne
        #255	Limite de puissance
            #'10': 0, 
            #'101': 'no_connect', 
            #'102': 16, = Ampères  8A/10A/13A/16A/25A/32A
            #'104': 0,  = Delay
            #'106': 0,  = Used KWh
            #'107': 398 = Voltage, 
            #'108': 0,  = Current Amps
            #'109': 0,  = Power
            #'110': 202,= Temperature (/10)
            #'111': Set,= Charging current  8A/10A/13A/16A/25A/32A
            #'112': False,Manual stop charge switch
            #'113': 0,  = Delayed charging remaining /10 
            #'114': 0   = Charge Length
        device = Device(id_Chargepoint, ip_Chargepoint, key_Chargepoint, 'default')  # lbl_Chargepoint
        device.set_version(version)
        #print ( "set value " + str(parm) + " =" + str(int(valparm)))
        device.set_value(parm, int(valparm))
        #print(device.status)
        try:
            data = device.status() 
        except KeyError:
            data = 0  # or set a default value of your choice
        #updt_status(lbl_Chargepoint , str(parm),int(valparm))
    else:
        log2file("status of "+lbl_Chargepoint+" != on",False)

def cozytouch_GETP(json, target_name):
    if (read_mydevice_value("Cozytouch","status")=="on"):
        global cookie
        headers = {
            'cache-control': "no-cache",
            'Host': "ha110-1.overkiz.com",
            'Connection': "Keep-Alive",
        }
        myurl = read_mydevice_value("Cozytouch","url_cozytouchlog") + json
        req = requests.get(myurl, headers=headers, cookies=cookie)
        
        #print(u'  '.join((u'GETP-> ', myurl, ' : ' str(req.status_code))).encode('utf-8'))

        if req.status_code == 200:
            data = req.json()
            devices = data.get('devices', [])
            for device in devices:
                states = device.get('states', [])
                for state in states:
                    if state.get('name') == target_name:
                        return state.get('value')

        http_error(req.status_code, req.reason)
        time.sleep(1)
        return None
    else:
        log2file("status of Cozytouch != on",False)
        return None
        
def cozytouch_GET(json):
    if (read_mydevice_value("Cozytouch","status")=="on"):
        global cookie
        headers = {
        'cache-control': "no-cache",
        'Host' : "ha110-1.overkiz.com",
        'Connection':"Keep-Alive",
        }
        myurl=read_mydevice_value("Cozytouch","url_cozytouchlog")+json
        req = requests.get(myurl,headers=headers,cookies=cookie)
        #if debug>=2:
        #    print(u'  '.join((u'GET-> ',myurl,' : ',str(req.status_code))).encode('utf-8'))

        if req.status_code==200 : # Réponse HTTP 200 : OK
                data=req.json()
                return data

        http_error(req.status_code,req.reason) # Appel fonction sur erreur HTTP
        time.sleep(1) # Tempo entre requetes
        return None
    else:
        log2file("status of Cozytouch != on",False)
        return None

def cozytouch_POST(url_device, name, parametre):
    if (read_mydevice_value("Cozytouch","status")=="on"):
        #log2file("cozytouch_POST: "+ name + "=" + str(parametre),False)
        global cookie
        if isinstance(parametre, int) or isinstance(parametre, float):
            parametre = str(parametre)
        # si str, on teste si c'est un objet JSON '{}' dans ce cas on ne met pas de double quotes, sinon on applique par défaut
        elif isinstance(parametre, str) and parametre.find('{') == -1:
            parametre = '"' + parametre + '"'

        # Headers HTTP
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        myurl = read_mydevice_value("Cozytouch","url_cozytouch")  + '../../enduserAPI/exec/apply'
        payload = '{"actions": [{"deviceURL": "' + url_device + '" ,\n"commands": [{"name": "' + name + '",\n"parameters":[' + parametre + ']}]}]}'
        #if debug>=2:
        #    print("POST url:" + str(url_device) + " name:" + str(name) + " param:" + str(parametre))
        #cookies = var_restore('cookies')
        cookies = cookie
        req = requests.post(myurl, data=payload, headers=headers, cookies=cookies)
        #if debug>=0:
        #    print("POST " + name+ " param:" + parametre + " : " + str(req.status_code))

        if req.status_code != 200:  # Réponse HTTP 200 : OK
            http_error(req.status_code, req.reason)
        return req.status_code
    else:
        log2file("status of Cozytouch != on",False)
        return 0

def set_cookie(value):
    global cookie
    cookie = value

def http_error(code_erreur, texte_erreur):
    ''' Evaluation des exceptions HTTP '''
    log2file("Erreur HTTP "+str(code_erreur)+" : "+texte_erreur,False)
    #print("Erreur HTTP "+str(code_erreur)+" : "+texte_erreur)


def cozytouch_login(login, password):
    try:
        # Assuming read_mydevice_value function retrieves values correctly
        Auth_Basic = read_mydevice_value("Cozytouch", "Auth_Basic")
        url_atlantic = read_mydevice_value("Cozytouch", "url_atlantic")
        url_cozytouchlog = read_mydevice_value("Cozytouch", "url_cozytouchlog")
        #print ("1")
    except Exception as e:
        log2file("Error retrieving values:" + " "+ str(e),False)
        #print("Error retrieving values:" + " "+ str(e))
        return False

    #print ("2")
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': Auth_Basic
    }
    data = {
        'grant_type': 'password',
        'username': login,
        'password': password
    }
    url = f"{url_atlantic}/token"

    try:
        req = requests.post(url, data=data, headers=headers)
        req.raise_for_status()  # Raise exception if request fails
        atlantic_token = req.json()['access_token']
        
        headers = {'Authorization': 'Bearer ' + atlantic_token}
        reqjwt = requests.get(f"{url_atlantic}/magellan/accounts/jwt", headers=headers)
        reqjwt.raise_for_status()  # Raise exception if request fails
        jwt = reqjwt.content.decode("utf-8").replace('"', "")
        data = {"jwt": jwt}
    
        jsession = requests.post(f"{url_cozytouchlog}/login", data=data)
        jsession.raise_for_status()  # Raise exception if request fails

        if jsession.status_code == 200:
            cookies = {'JSESSIONID': jsession.cookies['JSESSIONID']}
            set_cookie(cookies)
            return True
    except requests.exceptions.RequestException as e:
        log2file("HTTP Error:"+ str(e),False)
        #print("HTTP Error:"+ str(e))
    except KeyError as e:
        log2file("KeyError:"+ str(e),False)
        #print("KeyError:"+ str(e))
    except Exception as e:
        log2file("Error:"+ str(e),False)
        #print("Error:"+ str(e))

    #print("Failed to authenticate with Cozytouch server")
    #log2file("Failed to authenticate with Cozytouch server",False)
    return False


def decouverte_devices(dump=False):
    data = cozytouch_GET('setup')
    if dump:
        f1=open('./dump_cozytouchs.txt', 'w+')
        f1.write((json.dumps(data, indent=4, separators=(',', ': '))))
        f1.close()

def toggle_velux(lbl_plug, outlet=2, status="on"):
    if (read_mydevice_value(lbl_plug,"status")=="on"):
        device_id = read_mydevice_value(lbl_plug,"id")
        device_ip = read_mydevice_value(lbl_plug,"ip")
        #if not is_ip_responsive3(lbl_velux):
        #    log2file("set_plug_status {:<15}".format(lbl_plug, ) + " : is_ip_responsive = False",False)
        #    return str(status)
        user_info = ewel_login({'email': read_mydevice_value("Ewelink","Ewe_email"),'password': read_mydevice_value("Ewelink","Ewe_password"),'imei': str(uuid.uuid4())},read_mydevice_value("Ewelink","Ewe_region"))    # Velux via ewelink !
        headers = {'Authorization': 'Bearer ' + user_info['response']['at'],'Content-Type': 'application/json'}  # Set the correct Content-Type
        data = {"action": "update","deviceid": device_id,"params": {"switches": [{"switch": status, "outlet": outlet}]}}
        r = requests.post('https://{}-api.coolkit.cc:8080/api/user/device/status'.format(user_info['region']),data=json.dumps(data), headers=headers)
        #print(r.json())   #print("Control Device - Response Code:", r.status_code)   #print("Control Device - Response Content:", r.content)
        if r.status_code == HTTPStatus.OK:
            status="ok"
        else:
            log2file("Failed toggle_velux {:<15}".format(device_id) + " : " + str(outlet) + " = " + "!"+ str(status),False)
            #print("Failed to change relay {} status to {}".format(outlet, status))
    else:
        log2file("status of "+lbl_plug+" != on",False)

def wakeonlan():
    log2file("wakeonlan",False)
    add_oct = 'xx:09:xx:49:xx:D1'.split(':')
    hwa = struct.pack('BBBBBB', int(add_oct[0],16),
    int(add_oct[1],16),
    int(add_oct[2],16),
    int(add_oct[3],16),
    int(add_oct[4],16),
    int(add_oct[5],16))
    # Build magic packet
    msg = b'\xff' * 6 + hwa * 16
    # Send packet to broadcast address using UDP port 9
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
    soc.sendto(msg,('192.168.18.255',7))
    soc.close()
    #pip install wakeonlan
    #from wakeonlan import send_magic_packet
    #send_magic_packet('xx.09.xx.49.xx.D1')
            
def tuya2php(): 
    #update_status("time",time.strftime("%H:%M"))
    with open('tuya.csv', mode='r') as file:
        reader = csv.DictReader(file)
        status = {row['Device']: row['Status'] for row in reader}
    uploadprod = requests.get('https://xxx/favoris/xxx?statut=' + str(status), verify=False)

def func_test():
    print(check_blind_height(lbl_plug_salon, id_plug_salon,ip_plug_salon,key_plug_salon))
    print(check_plug_state(lbl_relais_VMC, id_relais_VMC,ip_relais_VMC,key_relais_VMC))

def listall2csv():
    data = []
    data.append(["hour:" + str(current_hour)])

class mymydevice:
    def __init__(self, label, **kwargs):
        self.label = label
        self.ip = None
        self.id = None
        self.key = None
        self.alert = None
        self.state = None
        self.enable = None
        self.powerA = None
        self.powerW = None
        self.status = None
        self.attributes = kwargs

    def read_mydevice_value(self, attribute):
        return getattr(self, attribute, None)

    def add_value(self, attribute, value):
        setattr(self, attribute, value)


def read_config_2(filename):
    mydevices = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and lines starting with #
                continue
            #print(line)
            label, attributes = line.split('(', 1)
            label = label.strip()
            attributes = attributes[:-1].split(',')
            mydevice = mymydevice(label)
            for attribute in attributes:
                split_attribute = attribute.split('=', 1)  # Split by first occurrence of '='
                key = split_attribute[0].strip()
                if len(split_attribute) == 2:
                    value = split_attribute[1].strip().strip("'")
                    for additional_value in split_attribute[2:]:  # Handle additional '=' signs in value
                        value += '=' + additional_value.strip()
                else:
                    value = ''  # Assign empty string if no equals sign found
                #print (label + " > " + key +  " = "+  value)
                setattr(mydevice, key, value)
            mydevices[label] = mydevice
    return mydevices


def read_config2(filename):
    mydevices = {}
    try:
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, start=1):
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and lines starting with #
                    continue
                try:
                    label, attributes = line.split('(', 1)
                    label = label.strip()
                    attributes = attributes[:-1].split(',')
                    mydevice = mymydevice(label)
                    for attribute in attributes:
                        split_attribute = attribute.split('=', 1)  # Split by first occurrence of '='
                        key = split_attribute[0].strip()
                        if len(split_attribute) == 2:
                            value = split_attribute[1].strip().strip("'")
                            for additional_value in split_attribute[2:]:  # Handle additional '=' signs in value
                                value += '=' + additional_value.strip()
                        else:
                            value = ''  # Assign empty string if no equals sign found
                        setattr(mydevice, key, value)
                    mydevices[label] = mydevice
                except Exception as e:
                    log2file(f"Error reading line {line_num}: {e}", False)
    except FileNotFoundError:
        log2file(f"File {filename} not found.",False)
    return mydevices
    
def export_config(mydevices, filename):
    with open(filename, 'w') as file:
        for label, mydevice in mydevices.items():
            attrs = []
            if mydevice.ip:
                attrs.append(f"ip='{mydevice.ip}'")
            if mydevice.id:
                attrs.append(f"id='{mydevice.id}'")
            if mydevice.key:
                attrs.append(f"key='{mydevice.key}'")
            if mydevice.alert:
                attrs.append(f"alert='{mydevice.alert}'")
            if mydevice.enable:
                attrs.append(f"enable='{mydevice.enable}'")
            if mydevice.powerA:
                attrs.append(f"powerA='{mydevice.powerA}'")
            if mydevice.powerW:
                attrs.append(f"powerW='{mydevice.powerW}'")
            if mydevice.status:
                attrs.append(f"status='{mydevice.status}'")
            attributes_str = ', '.join(attrs)
            file.write(f"{mydevice.label}({attributes_str})\n")


def meross_roller(device="Volet_TV",action="open"):
    async def _action_device():
        http_api_client = await MerossHttpClient.async_from_user_password(email=read_mydevice_value("Meroslink",'Mer_mail'), password=read_mydevice_value("Meroslink",'Mer_password'), api_base_url=read_mydevice_value("Meroslink",'Mer_base_url'))
        manager = MerossManager(http_client=http_api_client)
        await manager.async_init()
        await manager.async_device_discovery()
        roller_shutters = manager.find_devices(device_type="mrs100", online_status=OnlineStatus.ONLINE)
        if len(roller_shutters) < 1:
            log2file ("No online MRS100 roller shutter timers found...",False)
            #print("No online MRS100 roller shutter timers found...")
        else:
            dev = roller_shutters[0]
            await dev.async_update()
            #print("params: '"+device+"', '"+action+"'")
            if (dev.name == device):
                if action == "open":
                    await dev.async_open(channel=0)
                    log2file (f"Opening {dev.name}...",False)
                if action == "close":
                    log2file (f"Closing {dev.name}...",False)
                    await dev.async_close(channel=0)
                if action == "stop":
                    log2file (f"Stoping {dev.name}...",False)
                    await dev.async_stop(channel=0)
                await asyncio.sleep(2)
        manager.close()
        await http_api_client.async_logout()
    asyncio.run(_action_device())

def get_blind_meros_height(device="Volet_TV"):
    async def _action_device(future):
        http_api_client = await MerossHttpClient.async_from_user_password(
            email=read_mydevice_value("Meroslink", 'Mer_mail'),
            password=read_mydevice_value("Meroslink", 'Mer_password'),
            api_base_url=read_mydevice_value("Meroslink", 'Mer_base_url')
        )
        manager = MerossManager(http_client=http_api_client)
        await manager.async_init()
        await manager.async_device_discovery()

        roller_shutters = manager.find_devices(device_type="mrs100", online_status=OnlineStatus.ONLINE)
        
        if len(roller_shutters) < 1:
            log2file("No online MRS100 roller shutter timers found...", False)
            future.set_result(0)
        else:
            dev = roller_shutters[0]
            await dev.async_update()
            if dev.name == device:
                height = dev.get_position(channel=0)
                #print("height =" + device +" : "+  str(height))
                future.set_result(height)
            else:
                future.set_result(None)
        
        manager.close()  # Removed await since close might not be async
        await http_api_client.async_logout()
    
    future = asyncio.Future()
    asyncio.run(_action_device(future))
    return future.result()
     
def read_mydevice_value(mydevice_label, attribute):
    mydevice = mydevices.get(mydevice_label)
    if mydevice:
        value = mydevice.read_mydevice_value(attribute)
        if value is not None:
            return value
    return 0

def update_status(mydevice_label, attribute, value, write_to_file=False):
    #print ( " device:"+ mydevice_label + " attribute:"+attribute  + " value:"+ str(value))
    mydevice = mydevices.get(mydevice_label)
    if mydevice:
        mydevice.add_value(attribute, value)
        mydevice.add_value("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        print(f"No device found with label: {mydevice_label}. Adding new device.")
        new_device = mymydevice(mydevice_label)
        new_device.add_value(attribute, value)
        new_device.add_value("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
        mydevices[mydevice_label] = new_device
    if write_to_file:
        write_config_file("") 

def write_config_file(filename="configv2.py"):
    if( len(mydevices.items()) > 10):
        #print( time.strftime("%H:%M:%S") + " | " + os.path.basename(sys.argv[0]) + " > write_config_file "+ filename)
        with open(filename, 'w') as file:
            for mydevice_label, mydevice in mydevices.items():
                file.write(mydevice_label + "(")
                attributes = []
                for key, value in mydevice.__dict__.items():
                    if value:  # Check if value exists
                        attributes.append(f"{key}='{value}'")
                if attributes:  # Check if there are any attributes to write
                    file.write(", ".join(attributes))
                    file.write(")\n")
        #log2file("write_config_file",False)
    else:
        log2file ("NOT write_config_file "+ filename ,False)
        #print("NOT write_config_file "+ filename)

def isKillSwitch():
    #updt_status("KillSwitch", "off")
    KillSwitch = read_mydevice_value("KillSwitch","KillSwitch")
    if KillSwitch.lower() == "on":
        log2file ("KillSwitch is True.. exit",True)
        #print ("KillSwitch is True.. exit")
        exit()

def resetKillSwitch():
    update_status("KillSwitch", "on")

if 'win' in sys.platform: 
    myfolder= "" 
    mydebug=True
    mydelay=0
    start_time = time.time() 
else:
    #mydebug=False
    myfolder= "/home/pi/xxx/config/"

mydevices = read_config2(myfolder + 'configv2.py')
value = str(read_mydevice_value("Enphase",'PV_Power_Now'))
if len(value) < 1:
    log2file("read_config failed : " +  value + " watt",False)
