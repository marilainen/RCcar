from sense_hat import SenseHat

class SenseH():
    def __init__(self):
        self.sense_hat = SenseHat()

    def get_acceleration(self):
        try: 
            raw = self.sense_hat.get_accelerometer_raw()
            x = abs(raw["x"]*9.81)
            y = abs(raw["y"]*9.81)
            z = abs(raw["z"]*9.81)
            return [x,y,z]
        except Exception as error:
            print("Error getting acceleration data from Sensehat {}".format(error))