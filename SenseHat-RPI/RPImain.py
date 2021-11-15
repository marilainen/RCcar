import os
import time
import paramiko
from dotenv import dotenv_values
from multiprocessing import Process
import paho.mqtt.client as mqtt
import json
import RPI_sensehat as senseh
import temperature

class MainProgram:
    def __init__(self):
        #Leaving this here, in case of issues with SSH, this helps to debug.
        #paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
        self.sensehat = senseh.SenseH()
        self.shutdown = False
        
        # Configuration from env file
        self.config = dotenv_values("config.env")
        
        self.nxp_host = self.config["NXP_IP"]
        self.nxp_user = self.config["NXP_USER"]
        self.nxp_pw = self.config["NXP_PW"]
        self.nxp_cmd =  self.config["NXP_CMD"]
        
        self.rpi_host = self.config["RPI_IP"]
        self.rpi_user = self.config["RPI_USER"]
        self.rpi_pw = self.config["RPI_PW"]
        self.rpi_cmd =  self.config["RPI_CMD"]
        self.key_path = self.config["KEY_PATH"]
        self.key = paramiko.RSAKey.from_private_key_file(os.path.expanduser(self.key_path))
        self.port = 22
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        self.mqtt_server =  self.config["MQTT_SERVER"]
        self.mqtt_channel = self.config["MQTT_CHANNEL"]
        self.mqtt_client = mqtt.Client()

    #Tries to connect to MQTT client, if error, shuts down program
    def connect_mqtt_client(self):
        try: 
            self.mqtt_client.connect(self.mqtt_server)
            print("MQTT conn successful")
        except Exception as error:
            print("Error connecting to MQTT broker {}".format(error))
            self.shutdown = True
    
    #Tries to create subprocess for RPI and connects to it with SSH, if error, shuts down program
    def create_rpi_process(self):
        try: 
            self.client.connect(self.rpi_host, self.port, self.rpi_user, pkey=self.key, look_for_keys=False)
            self.rpi_transport = self.client.get_transport()
            self.rpi_channel = self.rpi_transport.open_session()
            self.rpi_channel.get_pty()
            self.rpi_channel.exec_command(self.rpi_cmd)
            print("SSH conn to RPI successful")
            
            #Receives messages from RPI while program is running.
            while not self.shutdown:
                print(self.rpi_channel.recv(4096))
                
                #If RPI subprocess is not running, shuts down program
                if (self.rpi_channel.exit_status_ready() == True):
                    self.shutdown = True            
                    
        except Exception as error:
            print("Error connecting to RPI with SSH {}".format(error))
            self.shutdown = True
    
    #Tries to create subprocess for NXP and connects to it with SSH, if error, shuts down program
    def create_nxp_process(self):
        try: 
            self.client.connect(self.nxp_host, self.port, self.nxp_user, pkey=self.key, look_for_keys=False)
            self.nxp_transport = self.client.get_transport()
            self.nxp_channel = self.nxp_transport.open_session()
            self.nxp_channel.get_pty()
            self.nxp_channel.exec_command(self.nxp_cmd)
            print("SSH conn to NXP successful")
            print(self.nxp_channel.recv(4096))
            #Receives messages from NXP while program is running.
            while not self.shutdown:
                print(self.nxp_channel.recv(4096))
                #If NXP subprocess is not running, shuts down program
                if (self.nxp_channel.exit_status_ready() == True):
                    self.shutdown = True            
        except Exception as error:
            print("Error connecting to NXP with SSH {}".format(error))
            self.shutdown = True     
                 
    #Method to start RPI process, if error, shuts down program      
    def start_rpi_process(self):
        try:
            self.rpi_process = Process(target=self.create_rpi_process)
            self.rpi_process.start()
        except Exception as error:
            print("Error starting RPI process {}".format(error))
            self.shutdown = True 
            
    #Method to start NXP process, if error, shuts down program
    def start_nxp_process(self):
        try:
            self.nxp_process = Process(target=self.create_nxp_process)
            self.nxp_process.start()
        except Exception as error:
            f = open("./RPIS_debug.txt", "a")
            f.write("Error starting NXP process {}".format(error))
            print("Error starting NXP process {}".format(error))
            f.close()  
            
    #Format data from sensehat and add timestamp in seconds
    def format_message(self, end_time):
        self.acceleration = self.sensehat.get_acceleration()
        message = {"acceleration X": self.acceleration[0],"acceleration Y": self.acceleration[1], "time (s)": end_time-self.start_time}
        return message

    #Cleanup before exiting program
    def stop(self):
        self.client.close()
        self.nxp_process.terminate()
        self.rpi_process.terminate()
        self.mqtt_client.disconnect()
        print("Cleanup done")

    # If no errors and everything is up and running, starts sending data to NXP via MQTT.
    # Monitors CPU temperature and stops the program if it exceeds 75C
    def run(self):
        self.start_time = time.time()
        self.connect_mqtt_client()

        if (temperature.get_temperature() > 75):
            self.shutdown = True
                
        self.mqtt_client.loop_start()
        message = self.format_message(time.time())            
        self.mqtt_client.publish(self.mqtt_channel, json.dumps(message))
        time.sleep(0.5)
        print("Publishing message {} to topic {}".format(str(message), self.mqtt_channel))
            
if __name__ == "__main__":
    
    # Start all processes. Small delay (1 second) to make sure subprocesses are up and running.
    try:
        mainp = MainProgram()
        mainp.start_nxp_process()
        mainp.start_rpi_process()
        time.sleep(1)
        while not mainp.shutdown:
            mainp.run()
    except KeyboardInterrupt:
        mainp.stop()
        print('Program stops')