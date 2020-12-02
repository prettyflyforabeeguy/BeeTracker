import RPi.GPIO as GPIO
from gpiozero import MotionSensor, LED
from RCamera import RCamera
from credentials import Credentials
from azure.iot.device.aio import IoTHubDeviceClient
from datetime import datetime
from utils import CredentialInfo
from message_payload import MessagePayload
from tf_classify import TFClassify
import sys, json, logging, argparse, app_logger, asyncio, signal, os
import device_connect_service
from iotc.aio import IoTCClient
from iotc import IOTCConnectType, IOTCLogLevel, IOTCEvents
import iot_events.device_events as device_events
from app_settings import AppSettings
import iot_events.iot_commands as iot_commands
import busio, board       #needed for i2c interface with proximity sensors
import adafruit_vcnl4040  #needed for the vcnl4040 proximity sensor
import adafruit_vcnl4010  #needed for the vcnl4010 proximity sensor
import time
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

#Define some globals
GPIO.setmode(GPIO.BCM)
camera = RCamera()  #Camera connected to camera pins
credentials: Credentials = Credentials()
device_client: IoTCClient = None #IoTHubDeviceClient.create_from_connection_string(credentials.get_credentail_info(CredentialInfo.connection_string))
start_time = datetime.now()
tfclassifier = TFClassify()
log:logging.Logger = app_logger.get_logger()
#print(f"TensorFlow took {datetime.now() - start_time} seconds to load")
log.info(f"TensorFlow took {datetime.now() - start_time} seconds to load")
_app_settings = AppSettings()
_app_settings.ensure_label_folders_exist()
_USE_TEST_MODE = False
_USE_BLOB_STORGE = False

_app_settings = AppSettings()
#These commands are sent by IoT Central to the device
_IoT_Commands = {
    'DownloadModel': iot_commands.iot_download_model,
    'UploadImages': iot_commands.iot_upload_images,
    'Blink': iot_commands.iot_blink
}

#These commands are sent by IoT Central to the device
_IoT_Commands = {
    'DownloadModel': iot_commands.iot_download_model,
    'UploadImages': iot_commands.iot_upload_images,
    'Blink': iot_commands.iot_blink
}

async def send_iot_message(message=""):
    await device_events.send_iot_message(device_client, message)

# Connect to storage acccount
def connect_storage_account():
    global tier1_container
    global blob_service_client
    with open("./blob_config.json") as json_data_file:
        data = json.load(json_data_file)
        connection_str = data["blob"]["connection_string"]
        tier1_container = data["blob"]["tier1_container"]
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_str)
    except Exception as e:
        log.error("Exception in get_storage_account_details(): {e}")
        print("Exception in get_storage_account_details(): " + e)

# Send image to Azure Storage Blob
def upload_to_storage_account(blob_service_client, container_name, img_file):
    try:
        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=img_file)

        print("\nUploading to Azure Storage as blob:\n\t" + img_file)

        # Upload the created file
        cwd = os.getcwd()
        upload_file_path = cwd + "/" + img_file
        with open(upload_file_path, "rb") as data:
            blob_client.upload_blob(data)
    except Exception as e:
        log.error("Exception in upload_to_storage_account(): {e}")
        print("Exception in upload_to_storage_account(): " + e)


# Calibrate the proximity sensor
def calibratePSensor(vcnl):
    print("Calibrating Proximity Sensor...")
    percent = None
    motionSense=[]
    for i in range (3):
        proximity = vcnl.proximity
        print("Proximity: {0}".format(proximity))
        motionSense.append(proximity)
        time.sleep(1)

    avg = sum(motionSense) / len(motionSense)
    print("Average Proximity: " + str(avg))
    # Increase average proximity by 2% as "motion"
    percent = avg + (avg * .02)
    print("Plus 2%: " + str(percent))
    return percent


async def movement_detected():
    global start_time, _USE_TEST_MODE
    log.info("Movement Detected!")
    if args.sensor == 'motion':
        red_led.on()
    # Take a picture and save it to the folder specified; "" for current folder
    flash_led.on()
    pic_info = camera.take_picture("img/", credentials.get_credentail_info(CredentialInfo.device_id), _USE_TEST_MODE)
    flash_led.off()
    picture_name = pic_info[1]
    tfclassifier.reset()
    tfclassifier.addImage(picture_name)
    start_time = datetime.now()
    picture_classification = tfclassifier.doClassify()
    log.info(f"Image Classification took {datetime.now() - start_time} seconds")
    #Only send telemetry if we see one of the classifications we care about; else, delete the photo
    valid_labels = _app_settings.get_TFLabels() # Labels classified
    #print(picture_classification)
    if ((picture_classification[0]['Prediction'] in valid_labels)): #See appsettings.json ["Honeybee", "Invader", "Male Bee"]):
        message = f"{picture_classification[0]}"
        os.rename(picture_name, os.path.join("img", picture_classification[0]['Prediction'].__str__(), picture_classification[0]['Prediction'] + "_" + pic_info[0])) 
        picture_name =  os.path.join("img", picture_classification[0]['Prediction'].__str__(),picture_classification[0]['Prediction'] + "_" + pic_info[0])
        #asyncio.run(send_iot_message(message))
        await send_iot_message(message)
        if(_USE_BLOB_STORAGE):
            container_name = tier1_container
            #upload the image to Azure
            upload_to_storage_account(blob_service_client, container_name, picture_name)
    if ((picture_classification[0]['Confidence'] > 0.60) and _USE_TEST_MODE == False):
        if os.path.exists(picture_name):
            os.remove(picture_name)

#No-movement detected method
async def no_movement_detected():
    log.info("No movement...")
    red_led.off()

#Clean up
def destroy():
    try:
        tfclassifier = None
        camera = None
        GPIO.cleanup()  # Release GPIO resource
    except Exception as e:
        log.info(f"Exiting..")
        sys.exit(0)


#Main app loop.
async def main_loop():
    global _IoT_Commands
    global device_client
    global percent
    global proximity

    try:
        device_client = await device_connect_service.connect_iotc_device()
        if(args.sensor == 'motion'):
            move_sensor.when_motion = movement_detected
            move_sensor.when_no_motion = no_movement_detected
    except Exception as e:
        log.error("Exception in main_loop: {e}")
        print("Exeption in main_loop: " + e)
        pass

    print("Ready to detect motion...")
    while True:
        try:
            if(args.sensor == 'vcnl4010' or args.sensor == 'vcnl4040'):
                proximity = vcnl.proximity
                if proximity >= percent:
                    await movement_detected()
            else:
                method_request = await device_client.receive_method_request()
                await _IoT_Commands[method_request.name](method_request, device_client, credentials)
        except KeyboardInterrupt as kbi:
            log.error("KeyboardInterrupt: {kbi}")
            GPIO.cleanup()
            sys.exit(0)
        except Exception as e:
            log.error("Exception in main_loop: {e}")
            print("Exception in main_loop: " + e)
            GPIO.cleanup()
            sys.exit(0)

async def main():
    global device_client
    start_time = datetime.now()
    log.info(f"Ready! Starting took {datetime.now() - start_time} seconds")

def signal_handler(signal, frame):
    destroy()
    sys.exit(0)


def startup():
    asyncio.run(main())
    signal.signal(signal.SIGINT, signal_handler)
    log.info("Starting main loop")
    asyncio.run(main_loop())

if __name__ == '__main__':
    # Welcome Message
    print("**************************************************************************")
    print("**  Welcome to Beetracker!                                              **")
    print("**  Supported sensors: vcnl4010, vcnl4040, and motion                   **")
    print("**************************************************************************")
    log.info('Starting...')
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', required=False, help="Enable test mode")
    parser.add_argument('--sensor', required=False, action='store', dest='sensor', choices=['vcnl4010','vcnl4040', 'motion'], help="Select a Motion or Proximity Sensor")
    parser.add_argument('--blobstorage', required=False, help="Enable blob storage")
    args = parser.parse_args()
    _USE_TEST_MODE = args.test
    _USE_BLOB_STORAGE = args.blobstorage
    if (_USE_TEST_MODE):
        log.info("Starting in TEST Mode")
    if (_USE_BLOB_STORAGE):
        log.info("Blob Storage Enabled.")
        connect_storage_account()
    if args.sensor == 'vcnl4010':
            log.info("Calibrating VCNL4010 motion sensor")
            i2c = busio.I2C(board.SCL, board.SDA)
            vcnl = adafruit_vcnl4010.VCNL4010(i2c)
            percent = calibratePSensor(vcnl)
            flash_led = LED(23)   #LED connected on GPIO pin 23
    if args.sensor == 'vcnl4040':
            log.info("Calibrating VCNL4040 motion sensor")
            i2c = busio.I2C(board.SCL, board.SDA)
            vcnl = adafruit_vcnl4040.VCNL4040(i2c)
            percent = calibratePSensor(vcnl)
            flash_led = LED(23)   #LED connected on GPIO pin 23
    if args.sensor == 'motion':
            log.info("Using Motion Sensor")
            move_sensor = MotionSensor(17)  #Motion Sensor control connected to GPIO pin 17
            red_led = LED(18)   #LED connected to GPIO pin 18

    try:
        startup()
    except SystemExit:
        pass
    finally:
        GPIO.cleanup()
        sys.exit(0)
