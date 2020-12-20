import json
from pathlib import Path
from utils import CredentialInfo
import os

#modelTier = "tier1"
class AppSettings:
    def __init__(self):
        self.appsettings_file = 'appsettings.json'
        #self.modelTier = "tier1"
        #self.modelTier = "" 
        self.SignaturePath = ""
        self.SubTierNumber = ""
        self.TFLabels = ""
        self.appsettings_dict = {}
        self.read_credentials()
        self.version = ""
        self.date_time = ""

    #Reads the credentials from the creds.json file
    def read_credentials(self):
        #filepath = Path(self.credsFile)
        try:
            with open(Path(self.appsettings_file)) as cred_data:
                appsettings = json.load(cred_data)
                self.appsettings_dict = appsettings
        except Exception as e:
            print(f"There was an error reading appsettings from: {self.appsettings_file}")


    def __str__(self) -> str:
        return f"{self.TFLabels}"

    #Get the specified credential info, using the Enum specified from the credentials.CredentialInfo class
    def get_SignaturePath(self, modelTier) -> str:
        return self.appsettings_dict[modelTier]["SignaturePath"]

    def get_TFLabels(self, modelTier) -> str:
        return [label.strip() for label in self.appsettings_dict[modelTier]["TFLabels"].split(",")]

    def get_SubTierNumber(self, modelTier) -> str:
        return self.appsettings_dict[modelTier]["SubTierNumber"]

    def get_SubTierTrigger(self, modelTier) -> str:
        return self.appsettings_dict[modelTier]["SubTierTrigger"]

    def get_Version(self, modelTier) -> str:
        return self.appsettings_dict[modelTier]["Version"]

    def get_DateTime(self, modelTier) -> str:
        return self.appsettings_dict[modelTier]["Date_Time"]

    #Ensures that folders corresponding to the TFLabels exist in the "img" folder
    def ensure_label_folders_exist(self, modelTier):
        for label in self.get_TFLabels(modelTier):
            label_path = os.path.join("img",label)
            if not os.path.exists(label_path):
                os.makedirs(label_path)


if __name__ == '__main__':
    app = AppSettings()
    sigpath = AppSettings().get_SignaturePath(modelTier)
    labels = AppSettings().get_TFLabels(modelTier)
    subtiernumber = AppSettings().get_SubTierNumber(modelTier)
    subtiertrigger = AppSettings().get_SubTierTrigger(modelTier)
    dt = AppSettings().get_DateTime(modelTier)
    ver = AppSettings().get_Version(modelTier)
    #labels = [label.strip() for label in app.get_TFLabels().split(",")]
    print(sigpath)
    print(labels)
    print(subtiernumber)
    print(subtiertrigger)
    print(ver)
    print(dt)
