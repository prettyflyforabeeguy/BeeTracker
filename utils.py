#Defines the Enum class that's used to drive the CredentialInfo enum
class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

#Implementation of Enum that lets you request this info from the get_credential_info method in the credentials.Credentials class
CredentialInfo = Enum(["device_id", "connection_string", "latitude", "longitude",
                    "owner_email", "blob_hostname", "blob_container",
                       "provisioning_host", "registration_id", "id_scope", "symmetric_key", "blob_token", "tf_models"
                    ])
