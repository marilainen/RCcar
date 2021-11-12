#!/usr/bin/env python
'''
**********************************************************************
Code source: https://github.com/sunfounder/SunFounder_PCA9685
License
This is the code for SunFounder PCA9685. This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied wa rranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

SunFounder PCA9685 comes with ABSOLUTELY NO WARRANTY; for details run ./show w. This is free software, and you are welcome to redistribute it under certain conditions; run ./show c for details.

SunFounder, Inc., hereby disclaims all copyright interest in the program 'SunFounder PCA9685' (which makes passes at compilers).

Mike Huang, 21 August 2015

Mike Huang, Chief Executive Officer

Email: service@sunfounder.com, support@sunfounder.com

**********************************************************************
'''
'''
**********************************************************************
* Filename    : Servo.py
* Description : Driver module for servo, with PCA9685
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-13    New release
*               Cavon    2016-09-21    Change channel from 1 to all
**********************************************************************
'''
import PCA9685 

class Servo(object):
	'''Servo driver class'''
	_MIN_PULSE_WIDTH = 600
	_MAX_PULSE_WIDTH = 2400
	_DEFAULT_PULSE_WIDTH = 1500
	_FREQUENCY = 60

	def __init__(self, channel, offset=0, lock=True, bus_number=None, address=0x40):
		''' Init a servo on specific channel, this offset '''
		if channel<0 or channel > 16:
			raise ValueError("Servo channel \"{0}\" is not in (0, 15).".format(channel))
		self.channel = channel
		self.offset = offset
		self.lock = lock

		self.pwm = PCA9685.PWM(bus_number=bus_number, address=address)
		self.frequency = self._FREQUENCY
		self.write(90)

	def setup(self):
		self.pwm.setup()

	def _angle_to_analog(self, angle):
		''' Calculate 12-bit analog value from giving angle '''
		pulse_wide   = self.pwm.map(angle, 0, 180, self._MIN_PULSE_WIDTH, self._MAX_PULSE_WIDTH)
		analog_value = int(float(pulse_wide) / 1000000 * self.frequency * 4096)
		return analog_value

	@property
	def frequency(self):
		return self._frequency

	@frequency.setter
	def frequency(self, value):
		self._frequency = value
		self.pwm.frequency = value

	@property
	def offset(self):
		return self._offset

	@offset.setter
	def offset(self, value):
		''' Set offset for much user-friendly '''
		self._offset = value

	def write(self, angle):
		''' Turn the servo with giving angle. '''
		if self.lock:
			if angle > 180:
				angle = 180
			if angle < 0:
				angle = 0
		else:
			if angle<0 or angle>180:
				raise ValueError("Servo \"{0}\" turn angle \"{1}\" is not in (0, 180).".format(self.channel, angle))
		val = self._angle_to_analog(angle)
		val += self.offset
		self.pwm.write(self.channel, 0, val)