# Bee Tracker
> An OpenHack codebase to support a Bee Health (mite) tracking IoT App. This app uses a TensorFlow model to perform image classification on-device. Telemetry data is sent to **Azure IoT Central**.

## Getting Started
### Installation of pre-requisites
Use the requirements.txt file to install required libraries, using the command: pip install -r requirements.txt

### Required hardware
- Raspberry Pi 0+
- Raspberry Pi PIR Motion Sensor
- Raspberry Pi Camera
- Some knowledge of how to use/configure a Raspberry Pi

### Azure Resources Required
- Azure IoT Hub: Your device will need to be enrolled, and it's connection string updated in the **creds.json** file discussed below
- Azure Storage: Optionally used to archive telemetry data from the device
- Azure Stream Analytics: Optionally used for telemetry analysis 

### Hardware wiring
The following wiring is required:
- LED l sor at GPIO 17
- Raspberry Pi Camera connected to the camera port

![alt text](https://raw.githubusercontent.com/marlinspike/beetracker/master/Raspberry_Pi_board_wiring.jpg)

### Configuring the Credentials file (creds.json)
This app needs a **creds.json** file to store certain required credential and status info. It's not contained in the repo for obvious reasons, but here's the structure you'll need:

```json
{
    "device_id" : "<your device id>",
    "latitude" : "",
    "longitude" : "",
    "owner_email" : "",
    "provisioning_host": "global.azure-devices-provisioning.net",
    "registration_id": "<same as device id>",
    "id_scope": "",
    "symmetric_key": "",
    "blob_token":"<blob_sas_token_for_images>",
    "tf_models":"<blob_token_for_tfmodels>"
}
```
Save this in a file called **creds.json** in the root folder of the application.

## Running the app
Run the app using the command: python motion.py

Note that the initial startup time for the app is approx 30-45 seconds, as it loads the TensorFlow model. Performing image classification on the first image takes substantially longer (30s), than every subsequent image (1.1s).

## Running in TEST Mode
Test mode tells the app to use the sample images in the **img_test** folder instead of ones it takes with the camera. These images are not ones used to train the model used, but ones that will test the classification and allow the app to run without the need for Bees to look at!

**To run in TEST Mode:**
```bash
python motion.py --test True
```
