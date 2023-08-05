# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import sys
from TaskTemplate import *
from DaqChannelGui import *
from acq4.devices.Device import TaskGui
from acq4.util.SequenceRunner import *
from acq4.pyqtgraph.WidgetGroup import WidgetGroup
#from PyQt4 import Qwt5 as Qwt
from acq4.pyqtgraph import PlotWidget
import numpy
import weakref
from acq4.util.debug import *

class DAQGenericTaskGui(TaskGui):
    
    #sigSequenceChanged = QtCore.Signal(object)  ## defined upstream
    
    def __init__(self, dev, task, ownUi=True):
        TaskGui.__init__(self, dev, task)
        self.plots = weakref.WeakValueDictionary()
        self.channels = {}
        
        if ownUi:
            self.ui = Ui_Form()
            self.ui.setupUi(self)
            self.stateGroup = WidgetGroup([
                (self.ui.topSplitter, 'splitter1'),
                (self.ui.controlSplitter, 'splitter2'),
                (self.ui.plotSplitter, 'splitter3'),
            ])
            self.createChannelWidgets(self.ui.controlSplitter, self.ui.plotSplitter)
            self.ui.topSplitter.setStretchFactor(0, 0)
            self.ui.topSplitter.setStretchFactor(1, 1)
            
        else:
            ## If ownUi is False, then the UI is created elsewhere and createChannelWidgets must be called from there too.
            self.stateGroup = None
        
    def createChannelWidgets(self, ctrlParent, plotParent):
        ## Create plots and control widgets
        for ch in self.dev._DGConfig:
            (w, p) = self.createChannelWidget(ch)
            plotParent.addWidget(p)
            ctrlParent.addWidget(w)
        

    def createChannelWidget(self, ch, daqName=None):
        conf = self.dev._DGConfig[ch]
        p = PlotWidget(self)
        
        units = ''
        if 'units' in conf:
            units = conf['units']
            
        #p.setAxisTitle(PlotWidget.yLeft, ch+units)
        p.setLabel('left', text=ch, units=units)
        #print "Plot label:", ch, units
        self.plots[ch] = p
        
        p.registerPlot(self.dev.name() + '.' + ch)
        
        if conf['type'] in ['ao', 'do']:
            w = OutputChannelGui(self, ch, conf, p, self.dev, self.taskRunner, daqName)
            #QtCore.QObject.connect(w, QtCore.SIGNAL('sequenceChanged'), self.sequenceChanged)
            w.sigSequenceChanged.connect(self.sequenceChanged)
        elif conf['type'] in ['ai', 'di']:
            w = InputChannelGui(self, ch, conf, p, self.dev, self.taskRunner, daqName)
        else:
            raise Exception("Unrecognized device type '%s'" % conf['type'])
        # w.setUnits(units)
        self.channels[ch] = w
        
        return (w, p)

    def saveState(self):
        if self.stateGroup is not None:
            state = self.stateGroup.state().copy()
        else:
            state = {}
        state['channels'] = {}
        for ch in self.channels:
            state['channels'][ch] = self.channels[ch].saveState()
        return state

    def restoreState(self, state):
        try:
            if self.stateGroup is not None:
                self.stateGroup.setState(state)
            for ch in state['channels']:
                try:
                    self.channels[ch].restoreState(state['channels'][ch])
                except KeyError:
                    printExc("Warning: Cannot restore state for channel %s.%s (channel does not exist on this device)" % (self.dev.name(), ch))
                    continue    
                self.channels[ch].restoreState(state['channels'][ch])
        except:
            printExc('Error while restoring GUI state:')
            #sys.excepthook(*sys.exc_info())
        #self.ui.waveGeneratorWidget.update()
            
        
    def listSequence(self):
        ## returns sequence parameter names and lengths
        l = {}
        for ch in self.channels:
            chl = self.channels[ch].listSequence()
            for k in chl:
                l[ch+'.'+k] = chl[k]
        return l
        
    def sequenceChanged(self):
        #self.emit(QtCore.SIGNAL('sequenceChanged'), self.dev.name())
        self.sigSequenceChanged.emit(self.dev.name())
        
    def taskStarted(self, params):  ## automatically invoked from TaskGui
        ## Pull out parameters for this device
        params = dict([(p[1], params[p]) for p in params if p[0] == self.dev.name()])
        
        for ch in self.channels:
            ## Extract just the parameters the channel will need
            chParams = {}
            search = ch + '.'
            for k in params:
                if k[:len(search)] == search:
                    chParams[k[len(search):]] = params[k]
            self.channels[ch].taskStarted(chParams)
            
    def taskSequenceStarted(self):  ## automatically invoked from TaskGui
        for ch in self.channels:
            self.channels[ch].taskSequenceStarted()
        
        
    def generateTask(self, params=None):
        #print "generating task with:", params
        if params is None:
            params = {}
        p = {}
        for ch in self.channels:
            ## Extract just the parameters the channel will need
            chParams = {}
            search = ch + '.'
            for k in params:
                if k[:len(search)] == search:
                    chParams[k[len(search):]] = params[k]
            ## request the task from the channel
            #print "  requesting %s task with params:"%ch, chParams
            p[ch] = self.channels[ch].generateTask(chParams)
        #print p
        return p
        
    def handleResult(self, result, params):
        #print "handling result:", result
        if result is None:
            return
        for ch in self.channels:
            #print "\nhandle result for", ch
            #print 'result:', type(result)
            #print result
            #print "--------\n"
            #if ch not in result:
                #print "  no result"
                #continue
            #print result.infoCopy()
            if result.hasColumn(0, ch):
                self.channels[ch].handleResult(result[ch], params)
            
    def getChanHolding(self, chan):
        """Return the holding value that this channel will use when the task is run."""
        return self.dev.getChanHolding(chan)
            
    def quit(self):
        TaskGui.quit(self)
        for ch in self.channels:
            self.channels[ch].quit()
        
