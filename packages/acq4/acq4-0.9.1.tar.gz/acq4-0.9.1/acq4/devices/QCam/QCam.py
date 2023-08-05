#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
from acq4.devices.Camera import Camera
from acq4.drivers.QImaging.QImagingDriver import *
from PyQt4 import QtCore
import time, sys, traceback
from numpy import *
from acq4.util.metaarray import *
import acq4.util.ptime as ptime
from acq4.util.Mutex import Mutex, MutexLocker
from acq4.util.debug import *

class QCam(Camera):
    def __init__(self, *args, **kargs):
        self.camLock = Mutex(Mutex.Recursive)  ## Lock to protect access to camera
        Camera.__init__(self, *args, **kargs)  ## superclass will call setupCamera when it is ready.
        
    def setupCamera(self):
        self.qcd = QCamDriverClass()
        cams = self.qcd.listCameras()
        #print "Cameras:", cams
        if len(cams) < 1:
            raise Exception('No cameras found by QCam driver')
        
        #if self.camConfig['serial'] is None:  ## Just pick first camera
        #    ind = 0
        #else:
        #    if self.camConfig['serial'] in cams:
        #        ind = cams.index(self.camConfig['serial'])
        #    else:
        #        raise Exception('Can not find pvcam camera "%s"' % str(self.camConfig['serial']))
        #print "Selected camera:", cams[ind]
        #self.cam = self.pvc.getCamera(cams[ind])
        #print "QCam: Opening camera ...."
        self.cam = self.qcd.getCamera(cams[0]) #open first camera
       # print "QCam: Camera opened."
        
    #def start(self, block=True):
        #if not self.isRunning():
            ##print "  not running already; start camera"
            #Camera.start(self, block)
            #self.startTime = ptime.time()
            
        #if block:
            #tm = self.getParam('triggerMode')
            #if tm != 'Normal':
                ##print "  waiting for trigger to arm"
                #waitTime = 0.3  ## trigger needs about 300ms to prepare (?)
            #else:
                #waitTime = 0
            
            #sleepTime = (self.startTime + waitTime) - ptime.time()
            #if sleepTime > 0:
                ##print "  sleep for", sleepTime
                #time.sleep(sleepTime)
            
    def listParams(self, params=None):
        """List properties of specified parameters, or of all parameters if None"""
        with self.camLock:
            return self.cam.listParams(params)
            
    def setParams(self, params, autoRestart=True, autoCorrect=True):
        """Set camera parameters. Options are:
           params: a list or dict of (param, value) pairs to be set. Parameters are set in the order specified.
           autoRestart: If true, restart the camera if required to enact the parameter changes
           autoCorrect: If true, correct values that are out of range to their nearest acceptable value
        
        Return a tuple with: 
           0: dictionary of parameters and the values that were set.
              (note this may differ from requested values if autoCorrect is True)
           1: Boolean value indicating whether a restart is required to enact changes.
              If autoRestart is True, this value indicates whether the camera was restarted."""
        #params: a list of (param, value) pairs to be set
        #print "PVCam: setParams", params
        with self.camLock:
            newVals, restart = self.cam.setParams(params, autoCorrect=autoCorrect)
        #restart = True  ## pretty much _always_ need a restart with these cameras.
        
        if autoRestart and restart:
            self.restart()
        #self.emit(QtCore.SIGNAL('paramsChanged'), newVals)
        self.sigParamsChanged.emit(newVals)
        return (newVals, restart)
        
    def getParams(self, params=None):
        if params is None:
            params = self.listParams().keys()
        with self.camLock:
            return self.cam.getParams(params)


    #def setParam(self, param, value, autoRestart=True, autoCorrect=True):
        #return self.setParams({param: value}, autoRestart=autoRestart, autoCorrect=autoCorrect)
        
    def getParam(self, param):
        with self.camLock:
            return self.cam.getParam(param)

        
    def quit(self):
        #print "quit() called from QCamDevice."
        Camera.quit(self)
        self.qcd.quit()
        
    def newFrames(self):
        with self.camLock:
            a = self.cam.newFrames()
        return a
      
    
    def startCamera(self):
        with self.camLock:
            #sys.stdout.flush()
            #time.sleep(0.1)
            #print "QCam: Start camera"
            self.cam.start()
            
    def stopCamera(self):
        with self.camLock:
            #sys.stdout.flush()
            #time.sleep(0.1)
            #print "QCam: Stop camera"
            self.cam.stop()
            time.sleep(0.06)

        