# Get Device ID  : https://eu.iot.tuya.com/cloud/basic?id=pxxxb=related&region=EU
# Get Local_Key  : https://eu.iot.tuya.com/cloud/explorer  device management > Query Device Details 
# vi ~/.xxx/config/user_crontab     # crontab -e   // cd /home/pi/xxx/config
# cd C:\Users\xxx\Documents\xxx\xxx; python tuya.py


time.sleep(mydelay)
        
import csv, asyncio
#python-eufy-security
from aiohttp import ClientSession
from eufy_security import async_login
from eufy_security.errors import EufySecurityError

import time

mydelay = 3
mydebug = True

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


_LOGGER: logging.Logger = logging.getLogger()

EUFY_EMAIL    = eufy_mail
EUFY_PASSWORD = eufy_passwd


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)
    async with ClientSession() as websession:
        try:
            # Create an API client:
            api = await async_login(EUFY_EMAIL, EUFY_PASSWORD, websession)

            # Loop through the cameras associated with the account:
            for camera in api.cameras.values():
                _LOGGER.info("------------------")
                _LOGGER.info("Camera Name: %s", camera.name)
                _LOGGER.info("Serial Number: %s", camera.serial)
                _LOGGER.info("Station Serial Number: %s", camera.station_serial)
                _LOGGER.info("Last Camera Image URL: %s", camera.last_camera_image_url)

                _LOGGER.info("Starting RTSP Stream")
                stream_url = await camera.async_start_stream()
                _LOGGER.info("Stream URL: %s", stream_url)

                _LOGGER.info("Stopping RTSP Stream")
                stream_url = await camera.async_stop_stream()
        except EufySecurityError as err:
            print(f"There was a/an {type(err)} error: {err}")


asyncio.get_event_loop().run_until_complete(main())