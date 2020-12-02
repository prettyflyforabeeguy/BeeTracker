 #IoT Device Registration and Connection Service
import asyncio
import os
import json
import datetime
import random

from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import MethodResponse
from azure.iot.device import Message
from credentials import Credentials
from iotc import IOTCConnectType, IOTCLogLevel, IOTCEvents
from iotc.aio import IoTCClient
import app_logger
credentials: Credentials = Credentials()


async def register_device():
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host = credentials.provisioning_host,
        registration_id = credentials.registration_id,
        id_scope = credentials.id_scope,
        symmetric_key = credentials.symmetric_key)

    registration_result = await provisioning_device_client.register()
    print(f'Registration result: {registration_result.status}')
    return registration_result


async def register_device():
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=credentials.provisioning_host,
        registration_id=credentials.registration_id,
        id_scope=credentials.id_scope,
        symmetric_key=credentials.symmetric_key)

    registration_result = await provisioning_device_client.register()
    print(f'Registration result: {registration_result.status}')
    return registration_result

#Connect to IoTCentral
async def connect_iotc_device() -> IoTCClient:
    log: logging.Logger = app_logger.get_logger()
    device_client = None
    #asyncio.sleep(0)
    registration_result = await register_device()
    if registration_result.status == 'assigned':
        try:
            device_client = IoTHubDeviceClient.create_from_symmetric_key(
                symmetric_key=credentials.symmetric_key,
                hostname=registration_result.registration_state.assigned_hub,
                device_id=registration_result.registration_state.device_id,
            )
            #device_client = IoTCClient(credentials.device_id, credentials.id_scope, IOTCConnectType.IOTC_CONNECT_DEVICE_KEY, credentials.symmetric_key)
            await device_client.connect()
            log.info('Connected to IoTCentral')
        except Exception as e:
            s = e
            log.error("Error Connecting to IoTCentral: {e}")
        finally:
            return device_client
