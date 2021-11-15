import json
from dotenv import dotenv_values
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT

class AWSMQTT():
    #AWS configuration from env file
    def __init__(self):
        self.config = dotenv_values("/home/programs/nxp_config.env")
        self.endpoint = self.config["AWS_ENDPOINT"]
        self.client_id = self.config["CLIENT_ID"]
        self.cert = self.config["PATH_TO_CERT"]
        self.key = self.config["PATH_TO_KEY"]
        self.root = self.config["PATH_TO_ROOT"]
        self.topic = self.config["TOPIC"]

        #Initialize AWS IoT client
        self.aws_client = AWSIoTPyMQTT.AWSIoTMQTTClient(self.client_id)
        self.aws_client.configureEndpoint(self.endpoint, 8883)
        self.aws_client.configureCredentials(self.root, self.key, self.cert)
 
    #Connect AWS client
    def connect(self):
        try: 
            self.aws_client.connect()
        except Exception as error:
            print("Error connecting AWS client {}".format(error))

    def send_message(self,msg):
        try: 
            self.aws_client.publish(self.topic, json.dumps(msg),1)         
        except Exception as error:
            print("Error sending MQTT message to AWS {}".format(error))

    def disconnect(self):
        self.aws_client.disconnect()