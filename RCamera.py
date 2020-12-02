from picamera import PiCamera
from picamera.array import PiRGBArray
import asyncio
import uuid
from pathlib import Path
import time
from os import listdir, system
from os.path import isfile, join
import random
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.OUT)


try:
    from cv2 import cvtColor, Laplacian, mean, COLOR_RGB2GRAY, CV_16U
    #AUTO_FOCUS = True
    AUTO_Focus = False
except Exception as err: #pylint: disable=broad-except
    #print("ERR: '{}", str(err))
    AUTO_FOCUS = False

class RCamera:
    def __init__(self):
        global AUTO_FOCUS
        self.camera = PiCamera()
        if AUTO_FOCUS:
            self.auto_focus()
        self.cam_setup()

    #Set up some basic stuff like image size and rotation
    def led_on(self):
        GPIO.output(23, GPIO.HIGH)

    def led_off(self):
        GPIO.output(23, GPIO.LOW)

    def cam_setup(self):
        #_camera = PiCamera()
        self.camera.rotation = 0
        self.camera.resolution = (2592,1944)#(2592,1944)(640,480)

    def get_demo_pics(self) -> []:
        return [f for f in listdir("img_test/") if isfile(join("img_test/", f))]

    def laplacian(self, image):
        img_gray = cvtColor(image, COLOR_RGB2GRAY)
        img_sobel = Laplacian(img_gray, CV_16U)
        return mean(img_sobel)[0]

    def calculate_focal_index(self):
        raw_capture = PiRGBArray(self.camera)
        self.camera.capture(raw_capture, format="bgr", use_video_port=True)
        image = raw_capture.array
        raw_capture.truncate(0)
        return self.laplacian(image)

    def focus(self, val):
        value = (val << 4) & 0x3ff0
        data1 = (value >> 8) & 0x3f
        data2 = value & 0xf0
        system("i2cset -y 1 0x13 %d %d" % (data1, data2))

    def auto_focus(self):
        '''
        Loop around fine tuning the focal index of the lense and
        finall set it and get back out of preview mode.
        '''
        self.camera.resolution = (640, 480)
        self.camera.start_preview()
        print("Start focusing")
        max_index = 10
        max_value = 0.0
        last_value = 0.0
        dec_count = 0
        focal_distance = 10

        beg_time = time.time()
        while True:
            #Adjust focus
            self.focus(focal_distance)
            #Take image and calculate image clarity
            val = self.calculate_focal_index()
            #print(f"'{val}'' > '{max_value}''")
            #Find the maximum image clarity
            if val > max_value:
                max_index = focal_distance
                max_value = val

            #If the image clarity starts to decrease
            #print(f"'{val}'' < '{last_value}''")
            if val < last_value:
                dec_count += 1
            else:
                dec_count = 0
            #Image clarity is reduced by six consecutive frames
            if dec_count > 6:
                break
            last_value = val

            #Increase the focal distance
            focal_distance += 10
            if focal_distance > 1000:
                break
            #print(f"'{dec_count}' '{focal_distance}'")
        end_time = time.time()
        print("focus time: '{}' max index: '{}' max value: '{}'".format(end_time-beg_time, max_index, max_value))
        #Adjust focus to the best
        self.focus(max_index)
        self.camera.stop_preview()
        self.camera.resolution = (2592,1944)
        #self.camera.capture("test.jpg")

    #Takes a photo and saves it to the path specified, with the device_id specified as a prefix
    #Returns: Array: [file_name, file_path_and_name]
    #use_demo_pics: Set to TRUE and this will simply return a filepath to a random picture in the img_test folder
    def take_picture(self, storage_location="", device_id="", use_demo_pics=False) -> []:
        file_path = ""
        if use_demo_pics:
            #"img/"
            file_path = Path(f"img_test/{random.choice(self.get_demo_pics())}").__str__()
        else:
            file_name = f"{device_id}_{uuid.uuid4().__str__()}{'.jpg'}"
            file_path = Path(f"{storage_location}{file_name}").__str__()
            #filepath = Path(f"{storage_location}{device_id}_{uuid.uuid4().__str__()}{'.jpg'}").__str__()
            self.camera.capture(file_path)

        return [file_name, file_path]


