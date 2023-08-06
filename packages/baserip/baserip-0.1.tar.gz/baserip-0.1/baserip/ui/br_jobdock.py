# -*- coding: utf-8 -*-

"""
Module implementing BR_JobDock.
"""

from PyQt4.QtCore import pyqtSlot, Qt, pyqtSignal
from PyQt4.QtGui import QDockWidget, QMessageBox
from .Ui_br_jobdock import Ui_BR_JobDock
from threading import Thread, Event
from datetime import timedelta
import subprocess as subp
import re

class BR_JobDock(QDockWidget, Ui_BR_JobDock):
    """
    Class documentation goes here.
    """
    
    mencoder_data = pyqtSignal(dict) 
    job_complete = pyqtSignal()

    def __init__(self, job, job_id, closesig, name, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(name, parent)
        self.setupUi(self)
        self.job = job
        self.job_id = job_id
        self.closesig = closesig

        self.setWindowTitle(name)
        self.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)
        
        self.progressBar.setRange(0, 100)

        self.btnCancel.clicked.connect(self.on_cancel_clicked)
        self.mencoder_data.connect(self.on_mencoder_data)
        self.closesig.connect(parent.on_jobclose)
        
    def start(self, dir):
        self.runjob = MencoderJob(self.job, dir, self.mencoder_data, self.job_complete)
        self.runjob.completesig.connect(self.on_job_complete)
        self.runjob.start()
      
    @pyqtSlot(dict)
    def on_mencoder_data(self, match):
        self.lblTimeLeft.setText('{trem}'.format(**match))
        self.lblFileSize.setText('{estsize}'.format(**match))
        timeenc = timedelta(seconds=round(float(match['timeenc'])))
        self.lblTimeEncoded.setText('{}'.format(timeenc))
        self.lblPass.setText('{pass} of {passes}'.format(**match))
        self.progressBar.setValue(int(match['percent']))
    
    @pyqtSlot()
    def on_cancel_clicked(self):
        if self.runjob.is_alive():
            msg = QMessageBox(QMessageBox.Question, 'Cancelling Job', 
                'Do you want to cancel the running job?')
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            ans = msg.exec_()
            if ans == QMessageBox.Yes:
                self.runjob.cancel()
        
    @pyqtSlot()
    def on_job_complete(self):
        self.closesig.emit(self.job_id)
        self.close()
        
    def cancel(self):
        self.runjob.cancel()
        self.runjob.join()
    
class MencoderJob(Thread):
    def __init__(self, job, dir, datasig, completesig):
        super().__init__()
        self.job = job
        self.dir = dir
        self.datasig = datasig
        self.completesig = completesig
        self._cancel = Event()
        
    def run(self):
        remop = re.compile(r'^Pos:\W*(?P<timeenc>\d+\.\d+)s\W+(?P<frames>\d+)f\W+\(\W?(?P<percent>\d+)%\)\W+(?P<fps>\d+\.\d+)fps\W+Trem:\W+(?P<trem>\d+\w+)\W+(?P<estsize>\d+\w+)')
        try:
            for job in self.job.gen_passes():
                proc = subp.Popen(job, stdout=subp.PIPE, stderr=subp.DEVNULL, 
                    cwd=self.dir, universal_newlines=True)
                count = 0
                for mop in proc.stdout:

                    if self._cancel.is_set():
                        proc.terminate()
                        proc.communicate()
                        proc.wait()
                        return
                        
                    match = remop.search(mop)
                    if match:
                        count = (count + 1) % 100
                        if count == 0:
                            men_data = match.groupdict()
                            men_data['pass'] = int(self.job.pass_) + 1
                            men_data['passes'] = self.job.passes
                            self.datasig.emit(men_data)
            
        except(subp.SubprocessError):
            return
            
        finally:
            self.completesig.emit()
                        
    def cancel(self):
        self._cancel.set()
