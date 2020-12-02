import json
from pathlib import Path
from utils import CredentialInfo

class Credentials:
    def __init__(self):
        self.credsFile = 'creds.json'
        self.filepath = Path(self.credsFile)
        self.connection_string = ""
        self.device_id = ""
        self.latitude = ""
        self.longitude = ""
        self.owner_email = ""
        self.provisioning_host = ""
        self.registration_id = ""
        self.id_scope = ""
        self.symmetric_key = ""
        self.blob_token = ""
        self.credential_dict = {}
        self.read_credentials()

    #Reads the credentials from the creds.json file
    def read_credentials(self):
        #filepath = Path(self.credsFile)
        try:
            with open(self.filepath) as cred_data:
                credentials = json.load(cred_data)
                self.device_id = credentials['device_id']
                self.longitude = credentials['longitude']
                self.latitude = credentials['latitude']
                self.owner_email = credentials['owner_email']
                self.provisioning_host = credentials['provisioning_host']
                self.registration_id = credentials['registration_id']
                self.id_scope = credentials['id_scope']
                self.symmetric_key = credentials['symmetric_key']
                self.blob_token = credentials['blob_token']
                self.tf_models = credentials['tf_models']
                self.credential_dict = credentials
        except Exception as e:
            print(f"There was an error reading credentials from: {self.credsFile}")

    #Writes credentials back out to file
    def write_credentials(self, credential_dict: dict):
        self.credential_dict = credential_dict
        try:
            with open(self.filepath, 'w') as outfile:
                json.dump(credential_dict, outfile)
        except Exception as e:
            print(f"There was an error writing to the credentials file at: {self.credsFile}")


    def __str__(self) -> str:
        return f"Device_ID: {self.device_id}, Latigude: {self.latitude}, Longitude: {self.longitude}, Owner_Email: {self.owner_email}"

    #Get the specified credential info, using the Enum specified from the credentials.CredentialInfo class
    def get_credentail_info(self, credential_info:CredentialInfo) -> str:
        return self.credential_dict[credential_info]
