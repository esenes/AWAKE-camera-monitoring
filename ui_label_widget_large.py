'''
@author: esenes
Last modified: 7 Nov 2022
'''
import time 
import datetime
import camerapoll

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal

class Ui_label_widget_large(QtWidgets.QWidget):

	sigRefresh = pyqtSignal()

	def __init__(self, parent=None):
		super().__init__(parent)
		uic.loadUi("./ui_label_widget_large.ui", self)
		self.show()

		self.fesaName = None
		self.japc = None
		self.cameraDevice = None
		self.cameraName = None

	def setup_widget(self, fesaName, japc, camName, check_images=False):
		if fesaName == None:
			pass
		else:
			self.fesaName = fesaName
			self.japc = japc
			self.cameraName = camName
			self.check_images = check_images

			self.cameraDevice = camerapoll.CameraPoll(self.fesaName, self.japc, user_callback=self.sigRefresh.emit, check_images=self.check_images)
			self.sigRefresh.connect( self.refresh_widget )
			self.name_label.setText(camName)

	def subscribe_camera(self):
		self.cameraDevice.subscribe()
		
	def unix2HumanTime(self, unixTime):
		return datetime.datetime.utcfromtimestamp(unixTime)

	def update_message(self):   # lastAcqStamp
		state = self.cameraDevice.lastAcqStamp
		if isinstance(state, datetime.datetime):
			if self.check_images:
				msg = str(state.strftime("%Y-%m-%d\n%H:%M:%S.%f"))[:-5]
			else:
				msg = str(state.strftime("%Y-%m-%d\n%H:%M:%S"))
		else:
			msg = str(state)[:17]

		self.last_acq_label.setText(msg)

	def update_label(self):   # overallstatus here
		if self.cameraDevice.overallStatus == 'OK':
			self.cam_label.setStyleSheet("color: white; background-color: green")
			self.cam_label.setText('OK')	
		elif self.cameraDevice.overallStatus == 'ERROR':
			self.cam_label.setStyleSheet("color: white; background-color: red")
			self.cam_label.setText('ERROR')
		elif self.cameraDevice.overallStatus == 'FESA ERROR':
			self.cam_label.setStyleSheet("color: white; background-color: red")
			self.cam_label.setText('FESA DEAD')
		elif self.cameraDevice.overallStatus == 'LATE':
			self.cam_label.setStyleSheet("color: white; background-color: orange")
			self.cam_label.setText('LATE')
		else:
			print(f'Check the status')				

	def update_fesa_state(self):  
		if self.cameraDevice.fesaState == 'OK':
			self.fesa_state_label.setStyleSheet("color: green")
			self.fesa_state_label.setText(self.cameraDevice.fesaState)
		else:
			self.fesa_state_label.setStyleSheet("color: red")
			self.fesa_state_label.setText(self.cameraDevice.fesaState)	

	def refresh_widget(self):
		self.update_label()
		self.update_fesa_state()
		self.update_message()

