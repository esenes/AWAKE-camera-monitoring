'''
@author: esenes
Last modified: 7 Nov 2022
'''
import datetime
import numpy as np

class CameraPoll:

    def __init__(self, fesaName, japc, user_callback=None, check_images=False):

        self.fesaName = fesaName
        self.japc = japc
        self.ext_callback = user_callback
        self.check_images = check_images

        self.img_delay_tolerance = datetime.timedelta(seconds=1)
        self.status_delay_tolerance = datetime.timedelta(seconds=30)

        self.fesaIsUp = None
        self.fesaState = None

		# for higher level access
        self.overallStatus = None 
        self.lastAcqStamp = None

    def subscribe(self):
        self.japc.subscribeParam(self.fesaName+'/AcquisitionStatus#acqCameraStatus', onValueReceived=self.callback_fesa_state, onException=self.exception_fesa_state, getHeader=True, unixtime=True)
        if self.check_images:
            self.japc.subscribeParam(self.fesaName+'/LastImage', onValueReceived=self.callback_get_images, onException=self.exception_fesa_state, getHeader=True, unixtime=True)

	# get the property AcquisitionState#acqCameraState for comparison. Hopefully this will match the method above in the final version
    def callback_fesa_state(self, paramName, value, headerInfo):
        self.fesaIsUp = True

        self.fesaState = value[1]
        self.lastAcqStamp = self.unix2HumanTime(headerInfo['acqStamp'])

        self.updateStatus()

        try:
            self.ext_callback()
        except:
            pass

    def callback_get_images(self, paramName, value, headerInfo):
        self.fesaIsUp = True
        self.lastAcqStamp = self.unix2HumanTime(headerInfo['acqStamp'])

        if ( datetime.datetime.utcnow() - self.lastAcqStamp ) > self.img_delay_tolerance:
            self.overallStatus = 'LATE'
        else:
            self.updateStatus()

        try:
            self.ext_callback()
        except:
            pass

    def exception_fesa_state(self, parameterName, description, exception):
        self.fesaIsUp = False

        self.fesaState = None
        self.lastAcqStamp = None

        self.updateStatus()

    def updateStatus(self):
        # callback exception
        if self.fesaIsUp == False:
            self.overallStatus = 'FESA ERROR'
        # callback ok
        elif self.fesaIsUp == True:
            #cam ok 
            if self.fesaState == 'OK':
                self.overallStatus = 'OK'
            # everything frozen OK, but not updated
            elif ( datetime.datetime.utcnow() - self.lastAcqStamp ) > self.status_delay_tolerance :
                self.overallStatus = 'LATE'
            # any other error
            else:
                self.overallStatus = 'ERROR'

        # print(f'Camera status {self.overallStatus}\nFesa State {self.fesaState}\nOverall status {self.overallStatus}\nLast Acq Stamp {self.lastAcqStamp}\n')

    def unix2HumanTime(self, unixTime):
        return datetime.datetime.utcfromtimestamp(unixTime)

