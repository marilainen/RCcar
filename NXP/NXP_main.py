import sys
import signal
from dotenv import dotenv_values
import paho.mqtt.client as mqtt
import NXP_aws 
import temperature

class MQTTSubscriber:
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGINT, self.exit)

        # Configuration from env file
        self.config = dotenv_values("/home/programs/nxp_config.env")
        self.mqtt_server =  self.config["MQTT_SERVER"]
        self.mqtt_channel = self.config["MQTT_CHANNEL"]
        
        #Init MQTT and AWS clients
        self.client = mqtt.Client()
        self.aws_client = NXP_aws.AWSMQTT()
        self.aws_client.connect()

    def exit(self, signum, frame):  
        self.shutdown = True

    #Connecting to client.
    #Subscribing here, if connection is lost, on reconnect it will also resubscribe.
    def on_connect(self, client, userdata, rc, properties = None):
        self.client.subscribe(self.mqtt_channel)

    # The callback for when a message is received from the server.
    def on_message(self, client, userdata, msg):
        self.aws_client.send_message(str(msg.payload.decode("utf-8")))
        
    def run(self):
        try: 
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(self.mqtt_server)
            self.client.loop_forever()
        except Exception as error:
            print("Error connecting to MQTT client {}".format(error))

    # Cleanup before exiting program
    def stop_program(self):
        self.aws_client.disconnect()
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    mqtt_subscriber = MQTTSubscriber()
 
    # Runs if no errors occured. If CPU temp exceeds 75, stops the program.
    while not mqtt_subscriber.shutdown:
        if (temperature.get_temperature() > 75):
            mqtt_subscriber.stop_program()
            sys.exit(0)
        mqtt_subscriber.run()
 
    mqtt_subscriber.stop_program()
    sys.exit(0)