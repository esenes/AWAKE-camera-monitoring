'''
@author: esenes
Last modified: 27 Feb 2023
'''
import sys
import time
import datetime

import pyjapc

from xml_parser import load_config
import argparse

from PyQt5 import QtWidgets, uic, QtCore

class Ui_lite(QtWidgets.QMainWindow):
	
	def __init__(self, large_window=False, select_switch=None, get_images=False):
		super(Ui_lite, self).__init__()

		# want the large window ? 
		self.large_window = large_window
		self.get_images = get_images

		if self.large_window:
			uic.loadUi('./ui_main_panel_large.ui', self)
		else:
			uic.loadUi('./ui_main_panel.ui', self)

		# JAPC init
		self.japc = pyjapc.PyJapc(selector='', incaAcceleratorName='SPS')

		# start the UI
		self.show()

		# load the config file
		if select_switch == 'beamline':
			config_list, gui_list = load_config('./config/beam_cameras_setup.xml')
		elif select_switch == 'laser':
			config_list, gui_list = load_config('./config/laser_cameras_setup.xml')
		elif select_switch == 'awake_all':
			config_list, gui_list = load_config('./config/awake_all_cameras_setup.xml')
		elif select_switch == 'test':
			config_list, gui_list = load_config('./config/test.xml')
		elif select_switch == 'clear':
			config_list, gui_list = load_config('./config/clear.xml')

		self.widget_list = [] # only the used labels
		for cam in config_list:
			widg = getattr(self, 'w'+cam['port'])
			widg.setup_widget(cam['fesaName'], self.japc, cam['camName'], check_images=self.get_images)
			widg.cameraDevice.subscribe()
			self.widget_list.append(widg)

		self.setup_gui(gui_list)

		# start the subscriptions
		self.japc.startSubscriptions()

		# timer to check if anything got frozen 
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update_panel)
		self.timer.start(30000)

	def setup_gui(self, labelDict):
		self.title_label.setText(labelDict['title'])
		self.serverName_label.setText(labelDict['serverName'])

	def update_panel(self):
		for widg in self.widget_list:
			widg.refresh_widget()		

	def update_messagebox(self, message=''):
		now = datetime.datetime.utcnow()
		self.messagebox_label.setText(str(now.strftime("%Y-%m-%d %H:%M:%S") + ' : ' + message))		


def main():
	# handle inputs
	parser = argparse.ArgumentParser(description='BI camera monitor & reboot GUI')
	parser.add_argument('--large', help='Open the larger version for the control room', action="store_true")
	parser.add_argument('--get_image_mode', help='Get all the images to check timestamps. MEMORY INTENSE.', action="store_true")

	excl_group = parser.add_mutually_exclusive_group(required=True)
	excl_group.add_argument('--laser', help='Open laser cameras', action="store_true")
	excl_group.add_argument('--beamline', help='Open beamline cameras', action="store_true")
	excl_group.add_argument('--awake_all', help='A mix of beamline and laser cameras', action="store_true")
	excl_group.add_argument('--clear', help='Open CLEAR cameras', action="store_true")
	excl_group.add_argument('--test', help='Test', action="store_true")

	args = parser.parse_args()

	# init application
	app = QtWidgets.QApplication(sys.argv)
	# select system --> multiple trues handled by the parser
	if args.laser:
		camlist = 'laser'
	elif args.beamline:
		camlist = 'beamline'
	elif args.awake_all:
		camlist = 'awake_all'
	elif args.test:
		camlist = 'test'
	elif args.clear:
		camlist = 'clear'
	# launch app
	window = Ui_lite(large_window=args.large, select_switch=camlist, get_images=args.get_image_mode)	

	# closing routine
	ret = app.exec_()
	window.japc.stopSubscriptions()
	sys.exit(ret)


if __name__ == '__main__':
	main()