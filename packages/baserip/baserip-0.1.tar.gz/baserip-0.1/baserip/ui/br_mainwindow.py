# -*- coding: utf-8 -*-

"""
Module implementing BR_MainWindow.
"""

from PyQt4.QtGui import QMainWindow, QIntValidator, QFileDialog, QMessageBox, QLabel
from PyQt4.QtCore import pyqtSlot, QModelIndex, QThread, pyqtSignal, QSettings
from .Ui_br_mainwindow import Ui_BR_MainWindow
from .br_jobdock import BR_JobDock
from baserip.dvd import DVDTreeModel
from baserip.utils import FreqTable
from baserip.mencoder import Mencoder
from baserip import _version
from pkg_resources import resource_stream
from datetime import datetime
import xml.etree.ElementTree as et
import subprocess as subp
import re
import os

# Pixel aspect ratios
# See: http://en.wikipedia.org/wiki/Pixel_aspect_ratio
PAR = {
    'PAL': {
        '4/3': 12.0 / 11.0, 
        '16/9': 16.0 / 11.0
        }, 
    'NTSC': {
        '4/3': 10.0 / 11.0, 
        '16/9': 40.0 / 33.0
        }
    }

class BR_MainWindow(QMainWindow, Ui_BR_MainWindow):
    """
    baserip main window.
    """
    cropdata = pyqtSignal(tuple)
    encodeclose = pyqtSignal(str)
            
    def __init__(self, parent=None):
        
        """
        Constructor

        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        self.populate_dvd_tree()
        self.dvdtreemodel.rowsInserted.connect(self.on_rows_inserted)
        self.DVDTree.clicked.connect(self.on_dvdtree_clicked)
        self.DVDTree.expanded.connect(self.on_dvdtree_expanded)
        self.btnCropDetect.clicked.connect(self.on_cropdetect_clicked)
        self.cropdata.connect(self.on_crop_data)
        self.btnAuto.clicked.connect(self.on_auto_clicked)
        self.txtVBitrate.textChanged.connect(self.on_vbitrate_textchanged)
        self.txtFilesize.textEdited.connect(self.on_filesize_edited)
        self.btnSelDir.clicked.connect(self.on_seldir_clicked)
        self.btnStart.clicked.connect(self.on_start_clicked)
        self.spnScaleW.valueChanged[int].connect(self.on_scalew_changed)
        self.chkScale.stateChanged[int].connect(self.enable_scaleh)
        self.chkLockAR.stateChanged[int].connect(self.enable_scaleh)
        self.btnExit.clicked.connect(self.close)
        
        try:
            f = resource_stream('baserip', 'profiles.xml')
            self.profiles = et.ElementTree(file=f)
        except:
            self.profiles = et.ElementTree(element=et.fromstring('<profiles></profiles>'))
        
        root = self.profiles.getroot()
        vcodecs = root.findall('./vcodec')
        self.cboVCodec.addItems([vc.attrib['type'] for vc in vcodecs])
        acodecs = root.findall('./acodec')
        self.cboACodec.addItems([ac.attrib['type'] for ac in acodecs])
        self.cboVCodec.currentIndexChanged[str].connect(self.on_vcodec_change)
        self.cboACodec.currentIndexChanged[str].connect(self.on_acodec_change)
        self.cboVCodec.setCurrentIndex(len(vcodecs) - 1)
        self.cboACodec.setCurrentIndex(len(acodecs) - 1)
        
        self.txtVBitrate.setValidator(QIntValidator(100, 9999))
        self.txtFilesize.setValidator(QIntValidator(1, 9999))
        
        self.txtOutputdir.setText(os.path.join(os.environ['HOME'], '%T', 'Title_%N'))
        self.jobs = {}
        
        sblabel = QLabel('Baserip version: {}, \u00A9 2014, Geoff Clements'.format(_version))
        self.statusbar.addWidget(sblabel)

    def populate_dvd_tree(self):
        self.dvdtreemodel = DVDTreeModel(self)
        self.DVDTree.setModel(self.dvdtreemodel)
        self.DVDTree.resizeColumnToContents(0)
        
    @pyqtSlot()
    def on_rows_inserted(self):
        self.DVDTree.resizeColumnToContents(0)
        
    @pyqtSlot(QModelIndex)
    def on_dvdtree_expanded(self, index):
        self.DVDTree.resizeColumnToContents(0)

    @pyqtSlot(QModelIndex)
    def on_dvdtree_clicked(self, index):
        node = index.internalPointer()
        if node.typeInfo() == 'DVD_Drive':
            self.cboALang.clear()
            self.cboSLang.clear()
        elif node.typeInfo() == 'Track':
            self.DVDTree.resizeColumnToContents(1)
            row = index.row()
            node = index.parent().internalPointer()
            track = node.lsdvd['track'][row]
            alist = track['audio']
            self.cboALang.clear()
            self.cboALang.addItems(
                ['{0}: {1}, {2}, {3} ch'.format(a['ix'], a['language'] or 'Undefined', 
                a['format'], a['channels']) for a in alist])
            slist = track['subp']
            self.cboSLang.clear()
            self.cboSLang.addItems(
                ['{0}: {1}'.format(s['ix'], s['language']) for s in slist])
        
            self.spnWidth.setValue(track['width'])
            self.spnHeight.setValue(track['height'])
            self.spnHorizontal.setValue(0)
            self.spnVertical.setValue(0)
            self.spnScaleW.setValue(track['width'])
            
            # Read settings
            sets = QSettings('Baserip', 'baserip')
            sets.beginGroup(':'.join((node.lsdvd['title'], str(track['ix']))))
            if sets.value('savetime') is not None:
                self.statusbar.showMessage(
                    'Retrieved settings from {}'.format(sets.value('savetime').ctime()), 
                    5000)
                try:
                    self.chkALang.setChecked(sets.value('audio', type=bool))
                    self.cboALang.setCurrentIndex(sets.value('audio_lang', type=int) - 1)
                    self.chkSLang.setChecked(sets.value('subp', type=bool))
                    self.cboSLang.setCurrentIndex(sets.value('subp_lang', type=int) - 1)
                    self.cboVCodec.setCurrentIndex(self.cboVCodec.findText(sets.value('vcodec')))
                    self.spnPasses.setValue(sets.value('passes', type=int))
                    self.txtVBitrate.setText(sets.value('vbitrate'))
                    self.cboVProfile.setCurrentIndex(self.cboVProfile.findText(sets.value('vprofile')))
                    self.spnMotion.setValue(sets.value('motion', type=int))
                    self.chkCrop.setChecked(sets.value('crop', type=bool))
                    self.spnWidth.setValue(sets.value('cwidth', type=int))
                    self.spnHorizontal.setValue(sets.value('chorizontal', type=int))
                    self.spnHeight.setValue(sets.value('cheight', type=int))
                    self.spnVertical.setValue(sets.value('cvertical', type=int))
                    self.chkScale.setChecked(sets.value('scale', type=bool))
                    self.spnScaleW.setValue(sets.value('swidth', type=int))
                    self.spnScaleH.setValue(sets.value('sheight', type=int))
                    self.chkLockAR.setChecked(sets.value('arlock', type=bool))
                    self.cboACodec.setCurrentIndex(self.cboACodec.findText(sets.value('acodec')))
                    self.cboAProfile.setCurrentIndex(self.cboAProfile.findText(sets.value('aprofile')))
                    self.txtOutputdir.setText(sets.value('opdir'))
                    self.txtFileName.setText(sets.value('filename'))
                except:
                    pass
                sets.endGroup()

    @pyqtSlot(str)
    def on_vcodec_change(self, vcodec):
        root = self.profiles.getroot()
        vprofs = root.findall('./vcodec[@type="{0}"]//profile'.format(vcodec))
        self.cboVProfile.clear()
        self.cboVProfile.addItems([p.attrib['name'] for p in vprofs])
        if vprofs:
            self.spnPasses.setMaximum(int(root.find(
                './vcodec[@type="{0}"]'.format(vcodec)).attrib['passes']))
            self.cboVProfile.setCurrentIndex(len(vprofs) - 1)
        else:
            self.spnPasses.setMaximum(0)
            
    @pyqtSlot(str)
    def on_acodec_change(self, acodec):
        root = self.profiles.getroot()
        aprofs = root.findall('./acodec[@type="{0}"]//profile'.format(acodec))
        self.cboAProfile.clear()
        self.cboAProfile.addItems([a.attrib['name'] for a in aprofs])
        if aprofs:
            self.cboAProfile.setCurrentIndex(len(aprofs) - 1)
            
    @pyqtSlot()
    def on_cropdetect_clicked(self):
        indexes = self.DVDTree.selectedIndexes()
        if not indexes:
            return
        index = indexes[0]
        node = index.internalPointer()
        if node.typeInfo() != 'Track':
            return

        row = index.row()
        node = index.parent().internalPointer()
        track = node.lsdvd['track'][row]
        cropdetect = CropDetect(self.cropdata, track, node.lsdvd['device'], self)
        self.btnCropDetect.setDisabled(True)
        cropdetect.start()
        
    @pyqtSlot(tuple)
    def on_crop_data(self, croplist):
        clist = [c for c in map(int, croplist)]
        track = self.selected_track()
        if (clist[0] + clist[2]) <= track['width']:
            self.spnWidth.setValue(clist[0])
            self.spnHorizontal.setValue(clist[2])
        if (clist[1] + clist[3]) <= track['height']:
            self.spnHeight.setValue(clist[1])
            self.spnVertical.setValue(clist[3])
        self.btnCropDetect.setEnabled(True)
        self.on_scalew_changed(self.spnScaleW.value())
        
    @pyqtSlot()
    def on_auto_clicked(self):
        """
        Slot method when auto button is clicked.
        Sets the value of the video bitrate text box dependent upon user
        selections.
        """
        
        track = self.selected_track()
        if not track:
            return
        
        width, height = self.get_op_width_height(track)            
        root = self.profiles.getroot()
        xcodec = root.find('./vcodec[@type="{0}"]'.format(self.cboVCodec.currentText()))
        bpp = float(xcodec.attrib['bpp'])
        vbitrate = width * height * track['fps'] * self.spnMotion.value() * bpp / 1000
        self.txtVBitrate.setText(str(int(round(vbitrate))))
        
    def get_width_height(self, track):
        """
        Return the width and height of the selected track.
        Respects the crop settings.
        
        :param dict track: The selected track
        :return: Width and height of selected track
        :rtype: Tuple
        """

        if self.chkCrop.isChecked():
            width, height = self.spnWidth.value(), self.spnHeight.value()
        else:
            width, height = track['width'], track['height']
        
        return (width, height)
        
    def get_op_width_height(self, track):
        """
        Return the calculated *output* width and height of the selected track.
        
        :param dict track: The selected track
        :return: Width and height of selected track
        :rtype: Tuple
        """
        
        if self.chkScale.isChecked():
            if self.chkLockAR.isChecked():
                width, height = self.spnScaleW.value(), self.auto_calc_h(self.spnScaleW.value())
            else:
                width, height = self.spnScaleW.value(), self.spnScaleH.value()
        else:
            width, height = self.get_width_height(track)
            
        return (width, height)

    def selected_track(self):
        indexes = self.DVDTree.selectedIndexes()
        if not indexes:
            return False
        index = indexes[0]
        node = index.internalPointer()
        if node.typeInfo() != 'Track':
            return False
        row = index.row()
        node = index.parent().internalPointer()
        track = node.lsdvd['track'][row]
        return track
        
    @pyqtSlot(str)
    def on_vbitrate_textchanged(self, vbitrate):
        root = self.profiles.getroot()
        try:
            abitrate = root.find(
                './acodec[@type="{0}"]/profile[@name="{1}"]/bitrate'.format(
                    self.cboACodec.currentText(), self.cboAProfile.currentText())).text
            abitrate = float(abitrate) / 1000.0
        except:
            abitrate = float(vbitrate) / 10.0

        track = self.selected_track()
        try:
            filesize = track['length'] * (float(vbitrate) + abitrate) / 8192
        except:
            filesize = 0
        self.txtFilesize.setText(str(int(round(filesize))))

    @pyqtSlot(str)
    def on_filesize_edited(self, filesize):
        root = self.profiles.getroot()
        try:
            abitrate = root.find(
                './acodec[@type="{0}"]/profile[@name="{1}"]/bitrate'.format(
                    self.cboACodec.currentText(), self.cboAProfile.currentText())).text
            abitrate = float(abitrate) / 1000.0
        except:
            abitrate = float(filesize) / 10.0

        track = self.selected_track()
        try:
            vbitrate = float(filesize) * 8192 / track['length'] - abitrate
        except:
            vbitrate = 0
            
        if vbitrate < 0: vbitrate = 0
        self.txtVBitrate.setText(str(int(round(vbitrate))))
        
    @pyqtSlot()
    def on_seldir_clicked(self):
        dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory',
            self.txtOutputdir.text(), 
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
            
        if dir:
            self.txtOutputdir.setText(dir)
            
    @pyqtSlot()
    def on_start_clicked(self):
        indexes = self.DVDTree.selectedIndexes()
        if not indexes:
            return
        index = indexes[0]
        node = index.internalPointer()
        if node.typeInfo() != 'Track':
            return

        row = index.row()
        node = index.parent().internalPointer()
        track = node.lsdvd['track'][row]
        job_id = ':'.join((node.lsdvd['title'], str(track['ix'])))
 
        if job_id in self.jobs:
            return
            
        # Output directory mangling
        opdir = self.txtOutputdir.text() or os.path.join(os.environ['HOME'], '%T', 'Title_%N')
        bitrate = self.txtVBitrate.text() or 500
        language = self.cboALang.currentText().split(':')[1].split()[0].rstrip(',')
        width, height = self.get_op_width_height(track)
        opdir = re.sub('%T', node.lsdvd['title'].title(), opdir)
        opdir = re.sub('%N', str(track['ix']), opdir)
        opdir = re.sub('%L', str(track['length']), opdir)
        opdir = re.sub('%f', node.lsdvd['title'][0], opdir)
        opdir = re.sub('%b', str(bitrate), opdir)
        opdir = re.sub('%l', language, opdir)
        opdir = re.sub('%w', str(width), opdir)
        opdir = re.sub('%h', str(height), opdir)
        if not os.path.isdir(opdir):
            try:
                os.makedirs(opdir)
            except:
                return
            
        # Filename mangling
        fname = self.txtFileName.text() or '%T_%bkbps-%wX%h'
        fname = os.path.splitext(fname)[0]
        fname = re.sub('%T', node.lsdvd['title'].title(), fname)
        fname = re.sub('%N', str(track['ix']), fname)
        fname = re.sub('%L', str(track['length']), fname)
        fname = re.sub('%f', node.lsdvd['title'][0], fname)
        fname = re.sub('%b', str(bitrate), fname)
        fname = re.sub('%l', language, fname)
        fname = re.sub('%w', str(width), fname)
        fname = re.sub('%h', str(height), fname)

        root = self.profiles.getroot()
        vprof = root.find(
            './vcodec[@type="{0}"]/profile[@name="{1}"]/mencoder'.format(
                self.cboVCodec.currentText(), self.cboVProfile.currentText()))
        aprof = root.find(
            './acodec[@type="{0}"]/profile[@name="{1}"]/mencoder'.format(
                self.cboACodec.currentText(), self.cboAProfile.currentText()))
                
        mjob = Mencoder(bitrate, self.spnPasses.value())
        mjob.add_opt('dvd://{}'.format(track['ix']))
        mjob.add_opt('-dvd-device', node.lsdvd['device'])
        
        if self.chkALang.isChecked():
            aid = self.get_astream_id(track)
            mjob.add_opt('-aid', aid)
        else:
            mjob.add_opt('-nosound')

        if self.chkSLang.isChecked():
            sid = int(self.cboSLang.currentText().split(':')[0]) - 1
            mjob.add_opt('-vobsubout', fname)
            mjob.add_opt('-sid', sid)
        else:
            mjob.add_opt('-nosub')
            
        mjob.add_opts(zip(vprof.text.split()[::2], vprof.text.split()[1::2]))
        mjob.add_opts(zip(aprof.text.split()[::2], aprof.text.split()[1::2]))
        
        if self.chkCrop.isChecked():
            crop = ',crop={}:{}:{}:{}'.format(
                self.spnWidth.value(), self.spnHeight.value(), 
                self.spnHorizontal.value(), self.spnVertical.value())
        else:
            crop = ''
            
        if self.chkScale.isChecked():
            scale = ',scale={0}:{1}'.format(self.spnScaleW.value(), 
                not self.chkLockAR.isChecked() and self.spnScaleH.value() or -10)
        else:
            scale = ''
            
        mjob.add_opt('-vf', 'pp=de,hqdn3d' + crop + scale)
        
        opfile = os.path.join(opdir, fname + '.avi')
        mjob.add_opt('-o', opfile)
        
        jobwin = BR_JobDock(mjob, job_id, self.encodeclose, node.lsdvd['title'], self)
        self.jobs[job_id] = jobwin
        jobwin.show()
        jobwin.start(opdir)
        
        # Save settings
        if self.chkSaveSettings.isChecked():
            sets = QSettings('Baserip', 'baserip')
            sets.beginGroup(job_id)
            sets.setValue('audio', self.chkALang.isChecked())
            sets.setValue('audio_lang', self.cboALang.currentText().split(':')[0])
            sets.setValue('subp', self.chkSLang.isChecked())
            sets.setValue('subp_lang', self.cboSLang.currentText().split(':')[0])
            sets.setValue('vcodec', self.cboVCodec.currentText())
            sets.setValue('passes', self.spnPasses.value())
            sets.setValue('vbitrate', self.txtVBitrate.text())
            sets.setValue('vprofile', self.cboVProfile.currentText())
            sets.setValue('motion', self.spnMotion.value())
            sets.setValue('crop', self.chkCrop.isChecked())
            sets.setValue('cwidth', self.spnWidth.value())
            sets.setValue('chorizontal', self.spnHorizontal.value())
            sets.setValue('cheight', self.spnHeight.value())
            sets.setValue('cvertical', self.spnVertical.value())
            sets.setValue('scale', self.chkScale.isChecked())
            sets.setValue('swidth', self.spnScaleW.value())
            sets.setValue('sheight', self.spnScaleH.value())
            sets.setValue('arlock', self.chkLockAR.isChecked())
            sets.setValue('acodec', self.cboACodec.currentText())
            sets.setValue('aprofile', self.cboAProfile.currentText())
            sets.setValue('opdir', self.txtOutputdir.text())
            sets.setValue('filename', self.txtFileName.text())
            sets.setValue('savetime', datetime.today())
            sets.endGroup()
     
    def get_astream_id(self, track):
        audios = track['audio']
        for audio in audios:
            if audio['ix'] == int(self.cboALang.currentText().split(':')[0]):
                return audio['streamid']
        return '0x80'
        
    @pyqtSlot(str)
    def on_jobclose(self, job_id):
        try:
            del self.jobs[job_id]
        except:
            pass
            
    @pyqtSlot(int)
    def on_scalew_changed(self, value):
        """
        Slot method - called when scale width value is changed.
        The scale height value is updated if the aspect ratio is locked.
        
        :param int value: The scale width value
        """
        
        if self.chkLockAR.isChecked():
            self.spnScaleH.setValue(self.auto_calc_h(value))
            
    def auto_calc_h(self, new_width):

        def roundup16(val):
            rval = int((val / 16.0) + 1)
            return rval * 16

        track = self.selected_track()
        try:
            par = PAR[track['format']][track['aspect']]
        except KeyError:
            par = 1.0
        width, height = self.get_width_height(track)
        new_height = (new_width * height / width) / par
        return roundup16(new_height)
            
    @pyqtSlot(int)
    def enable_scaleh(self, value):
        self.spnScaleH.setEnabled(
            self.chkScale.isChecked() and not self.chkLockAR.isChecked())
            
    def closeEvent(self, event):
        if self.jobs:
            msg = QMessageBox(
                QMessageBox.Question, 
                'Exiting Baserip', 
                'There are running jobs!\nAre you sure you want to exit Baserip?')
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            ans = msg.exec_()
            if ans == QMessageBox.Yes:
                for job in self.jobs:
                    self.jobs[job].cancel()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

class CropDetect(QThread):
    def __init__(self, datasig, track, device, parent=None):
        self.datasig = datasig
        self.track = track
        self.device = device
        super().__init__(parent)
        
    def run(self):
        recrop = re.compile(
            r'\(-vf crop=(?P<width>\d+):(?P<height>\d+):(?P<horiz>\d+):(?P<vert>\d+)\)')
        widfreq = FreqTable(); hgtfreq = FreqTable(); horfreq = FreqTable(); verfreq = FreqTable()
        length = self.track['length']
        sample_points = (p*length/10 for p in range(1, 10))
        for point in sample_points:
            p = subp.Popen(
                ('mplayer', 'dvd://{}'.format(self.track['ix']), 
                '-dvd-device', '{}'.format(self.device), 
                '-vo', 'null', 
                '-ss', '{}'.format(point), 
                '-frames', 
                '100', 
                '-nosound', 
                '-benchmark', 
                '-vf', 'cropdetect=round,format=yv12'), 
                stdout=subp.PIPE, 
                stderr=subp.DEVNULL, 
                universal_newlines=True)
            for mpop in p.stdout:
                match = recrop.search(mpop)
                if match:
                    widfreq.mark(match.group('width'))
                    hgtfreq.mark(match.group('height'))
                    horfreq.mark(match.group('horiz'))
                    verfreq.mark(match.group('vert'))
        
        self.datasig.emit((widfreq.max(), hgtfreq.max(), horfreq.max(), verfreq.max()))
