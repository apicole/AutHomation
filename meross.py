#install module from /home/pi/.xxx/config/post_main.d/sococli.sh
# vi ~/.xxx/config/user_crontab     # crontab -e   // cd /home/pi/xxx/config
# cd C:\Users\xxx\Documents\xxx\xxx; python meross.py
#script_filename = os.path.splitext(os.path.basename(sys.argv[0]))[0]  # Get the script filename without extension

import asyncio
import os, time, logging
from meross_iot.controller.mixins.roller_shutter import RollerShutterTimerMixin
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.model.enums import OnlineStatus

meross_root_logger = logging.getLogger("meross_iot")
meross_root_logger.setLevel(logging.ERROR)

mydelay = 0
mydebug = True

if mydebug:
    start_time = time.time() 
    print("START :", time.time() - start_time, "seconds")
else:
    time.sleep(mydelay)

def meross_roller2(device="Volet_TV",action="open"):
    async def _action_device():
        http_api_client = await MerossHttpClient.async_from_user_password(email='bxxxe', password='axxx1', api_base_url='https://iotx-us.meross.com')
        manager = MerossManager(http_client=http_api_client)
        await manager.async_init()
        await manager.async_device_discovery()
        roller_shutters = manager.find_devices(device_type="mrs100", online_status=OnlineStatus.ONLINE)
        if len(roller_shutters) < 1:
            print ("No online MRS100 roller shutter timers found...")
            #print("No online MRS100 roller shutter timers found...")
        else:
            dev = roller_shutters[0]
            await dev.async_update()
            print("params: '"+device+"', '"+action+"'")
            if (dev.name == device):
                if action == "open":
                    await dev.async_open(channel=0)
                    print (f"Opening {dev.name}...")
                if action == "close":
                    print (f"Closing {dev.name}...")
                    await dev.async_close(channel=0)
                if action == "stop":
                    print (f"Stoping {dev.name}...")
                    await dev.async_stop(channel=0)
                await asyncio.sleep(2)
        manager.close()
        await http_api_client.async_logout()
    asyncio.run(_action_device())

def get_blind_meros_height2(device="Volet_TV"):
    async def _action_device(future):
        http_api_client = await MerossHttpClient.async_from_user_password(email='bxxxe', password='axxx1', api_base_url='https://iotx-us.meross.com')
        manager = MerossManager(http_client=http_api_client)
        await manager.async_init()
        await manager.async_device_discovery()

        roller_shutters = manager.find_devices(device_type="mrs100", online_status=OnlineStatus.ONLINE)
        
        if len(roller_shutters) < 1:
            print("No online MRS100 roller shutter timers found...")
            future.set_result(0)
        else:
            dev = roller_shutters[0]
            await dev.async_update()
            if dev.name == device:
                height = dev.get_position(channel=0)
                print("height =", height)
                future.set_result(height)
            else:
                future.set_result(None)
        
        manager.close()  # Removed await since close might not be async
        await http_api_client.async_logout()
    
    future = asyncio.Future()
    asyncio.run(_action_device(future))
    return future.result()
    
if __name__ == "__main__":
    
    
    #if (read_mydevice_value("KillSwitch",os.path.splitext(os.path.basename(sys.argv[0]))[0])=='True'):
        #log2file("KillSwitch = TRUE",False)
        #exit()


    #open_status = dev.get_is_open()
    #if open_status:
        #print(f"Door {dev.name} is open")
    #else:
        #print(f"Door {dev.name} is closed")

    if mydebug: print("ENDSET1 VALUES :", time.time() - start_time, "seconds")
    #if (heure_actuelle > dusk and heure_actuelle < duskdone ):               # le soleil est couché
    if True:
        meross_roller2("Volet_TV","open")       # Ferme volet TV à 0%
        meross_roller2("Volet_TV","stop")       # Ferme volet TV à 0%
        print("Yes Yet")
    else:
        print("Not yet")
    if mydebug: print("ENDSET2 VALUES :", time.time() - start_time, "seconds")
    quit()
