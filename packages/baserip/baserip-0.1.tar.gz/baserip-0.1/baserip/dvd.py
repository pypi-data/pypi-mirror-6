"""
dvd.py - Basic DVD routines.

Routines to detect DVD changes, to read the DVD contents
and to hold the DVD data.

"""
import pyudev
from pyudev.pyqt4 import QUDevMonitorObserver
from PyQt4 import QtCore, QtGui
from baserip.utils import Node
from datetime import timedelta
import subprocess as subp

class LsDvd(QtCore.QThread):
    """
    Thread class to run the lsdvd command.
    Data is returned via a signal.
    
    :param str device: device node of DVD e.g. /dev/sr0
    :param unbound_signal datasig: signal to use for return data
    :param PyQt4.QtCore.QObject parent: parent object
    """

    def __init__(self, device, datasig, parent=None):
        self.device = device
        self.datasig = datasig
        super().__init__(parent)
        
    def run(self):
        """
        Start the lsdvd thread. Emits datasig on completion.
        """
        
        try:
            contents = subp.check_output(
                ['lsdvd',  '-x',  '-Oy',  self.device.device_node],  
                stderr=subp.DEVNULL)
        except (subp.CalledProcessError):
            return

        # lsdvd data is returned as python code so execute it
        glbs = {}
        exec(str(contents, errors='ignore'),  glbs)
        self.datasig.emit(self.device, glbs['lsdvd'])
    
class DVD_Drive(Node):
    """
    DVD node for the Qt abstract data model.
    For use in the Tree Widget.

    :param pyudev.Device device: the device to be associated with
    :param dict lsdvd: data returned by lsdvd, default None
    :param baserip.utils.Node parent: parent node
    """
    
    def __init__(self, device, lsdvd=None, parent=None):
        super().__init__(device.device_path, parent)
        self.device = device
        self.lsdvd = lsdvd
        
    def typeInfo(self):
        """
        Returns the node type - DVD_Drive
        
        :return: The node type
        :rtype: str
        """
        
        return 'DVD_Drive'
        
class Track(Node):
    """
    Title node for the Qt abstract data model.
    For use in the Tree Widget.

    :param str name: the name of the title
    :param str length: time length of the title
    :param baserip.utils.Node parent: parent node
    """
    
    def __init__(self, name, length='', parent=None):
        super().__init__(name, parent)
        self.length = length

    def typeInfo(self):
        """
        Returns the node type - Track
        
        :return: The node type
        :rtype: str
        """
        
        return 'Track'

class DVDTreeModel(QtCore.QAbstractItemModel):
    """
    A tree model for a Qt Tree widget.
    Represents a list of DVD nodes with title nodes
    underneath each DVD showing the length of the
    title.

    :param PyQt4.QtCore.QObject parent: parent object
    """
    
    lsdvddata = QtCore.pyqtSignal(pyudev.Device, dict)
    """Signal emitted when lsdvd returns data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rootNode = Node('DVD Root') # create root node - never displayed
        self.lsdvddata.connect(self.on_lsdvd_data)

        # Find any already inserted DVDs and add them to the tree
        udevctx = pyudev.Context()
        for dev in udevctx.list_devices(subsystem='block', ID_CDROM_MEDIA_DVD='1'):
            if dev.get('ID_FS_LABEL') is not None:
                self.insertDVD(dev)

        # Set up a monitor to spot disk insertions and removals
        udevmon = pyudev.Monitor.from_netlink(udevctx)
        udevmon.filter_by('block', 'disk')
        udevobs = QUDevMonitorObserver(udevmon, self)
        udevobs.deviceChanged.connect(self.on_device_changed)
        udevmon.start()

    def rowCount(self, parent):
        """
        Necessary override. Returns the number of rows under the given *parent*.
        
        :param PyQt4.QtCore.QModelIndex parent: parent row
        :returns: Number of rows
        :rtype: int
        """

        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        """
        Necessary override. Returns the number of columns for the children of the given *parent*.
        
        :param PyQt4.QtCore.QModelIndex parent: parent row
        :returns: Number of columns
        :rtype: int
        """
        
        return 2

    def data(self, index, role):
        """
        Necessary override. Returns the data stored under the given *role* for the item referred 
        to by the *index*.
        
        :param PyQt4.QtCore.QModelIndex index: Row index
        :param PyQt4.QtCore.Qt.DisplayRole role: Display role
        :return: Data for the given index and role
        :rtype: PyQt4.QtCore.QVariant
        """
        
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                if node.typeInfo() == 'DVD_Drive':
                    return node.device.get('ID_FS_LABEL')
                elif node.typeInfo() == 'Track':
                    return 'Title ' + str(node.getName())
            elif index.column() == 1:
                if node.typeInfo() == 'Track':
                    return str(timedelta(seconds=round(node.length)))

        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                if node.typeInfo() == "DVD_Drive":
                    return QtGui.QIcon(QtGui.QPixmap(':/icons/media-optical-dvd.png'))
                elif node.typeInfo() == "Track":
                    return QtGui.QIcon(QtGui.QPixmap(':/icons/video-x-generic.png'))
                
    def headerData(self, section, orientation, role):
        """
        Necessary override. Returns the data for the given *role* and *section* in the header with 
        the specified *orientation*.
        
        :param int section: Column Number
        :param PyQt4.QtCore.Qt.Orientation orientation: Orientation
        :param PyQt4.QtCore.Qt.DisplayRole role: Display Role
        """
        
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return 'DVD Tracks'
            elif section == 1:
                return 'Length'

    def flags(self, index):
        """
        Necessary override. Returns the item flags for the given *index*.
        
        :param PyQt4.QtCore.QModelIndex index: Row index
        :return: Returns the item flags
        :rtype: PyQt4.QtCore.Qt.QItemFlags
        """
        
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self, index):
        """
        Necessary override. Returns the parent of the node with the given *QModelIndex*.
        
        :param PyQt4.QtCore.QModelIndex index: Row index
        :return: Returns parent of the node
        :rtype: PyQt4.QtCore.QObject
        """
        
        node = self.getNode(index)
        parentNode = node.parent()

        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        """
        Necessary override. Return a QModelIndex that corresponds to the given *row*, *column* and 
        *parent* node.
        
        :param int row: Row number
        :param int column: Coloumn number
        :return: Returns the index of the item
        :rtype: PyQt4.QtCore.QModelIndex
        """
        
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()
            
    def getNode(self, index):
        """
        Returns the underlying node from an *index*. If the index is invalid then return 
        the root node.
        
        :param PyQt4.QtCore.QModelIndex index: Row index
        :return: The node at index
        :rtype: baserip.utils.Node
        """
        
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode

    def insertDVD(self, device):
        """
        Actions to take when a DVD is inserted:
        
        #. Start lsdvd
        #. Insert the DVD node into the model tree
        
        :param pyudev.Device device: The device in which the DVD is inserted
        :returns: If inserting into the tree was successful
        :rtype: bool
        """
        
        lsdvd = LsDvd(device, self.lsdvddata, self)
        lsdvd.start()
        
        parent = QtCore.QModelIndex()
        parentNode = self._rootNode
        position = self.rowCount(parent)

        self.beginInsertRows(parent, position, position)
        childNode = DVD_Drive(device)
        success = parentNode.insertChild(position, childNode)
        self.endInsertRows()
        return success

    def insertTracks(self, tracklist, parent):
        """
        Insert a list of titles into the data tree under a DVD node.
        
        :param list tracklist: A list of dicts as returned by lsdvd representing each title
        :param baserip.utils.Node parent: The parent DVD node under which these titles will be added
        :return: Success of insert
        :rtype: bool
        """
        
        parentNode = self.getNode(parent)
        position = self.rowCount(parent)
        self.beginInsertRows(parent, position, len(tracklist) - 1)
        for track in tracklist:
            childNode = Track(track['ix'], track['length'])
            success = parentNode.insertChild(position, childNode) #TODO: record all successes
            position += 1
        self.endInsertRows()
        
        return success

    def removeDVD(self, position):
        """
        Remove a DVD node from the data tree.
        
        :param int position: The DVD to remove
        :return: Success of removal
        :rtype: bool
        """
        
        parent = QtCore.QModelIndex()
        parentNode = self._rootNode
        self.beginRemoveRows(parent, position, position)
        success = parentNode.removeChild(position)
        self.endRemoveRows()
        return success

    def findDVD(self, devpath):
        """
        Find the DVD position in the data tree from its device path, e.g. /dev/sr0.
        
        :param str devpath: The device path of the DVD to find
        :return: The row of the DVD in the data tree
        :rtype: int
        """
        
        rootNode = self._rootNode
        for pos in range(rootNode.childCount()):
            if rootNode.child(pos).getName() == devpath:
                return pos
        return None
    
    @QtCore.pyqtSlot(pyudev.Device)
    def on_device_changed(self, dev):
        """
        Slot method. Actions to take when udev signals a device change.
        
        :param pyudev.Device dev: The device which has changed
        """
        
        # If the device is a DVD and has a filesystem label assume it is an inserted DVD
        if dev.get('ID_CDROM_MEDIA_DVD') == '1' and dev.get('ID_FS_LABEL') is not None:
            self.insertDVD(dev)
        else:
            # Otherwise a DVD may have been removed
            pos = self.findDVD(dev.device_path)
            if pos is not None:
                self.removeDVD(pos)

    @QtCore.pyqtSlot(pyudev.Device, dict)
    def on_lsdvd_data(self, device, lsdvd):
        """
        Slot method. Receive data from lsdvd. Add the data to the associated
        DVD node.
        
        :param pyudev.Device device: The device from which the data was read
        :param dict lsdvd: The output from lsdvd
        """
        
        dvd = self.findDVD(device.device_path)
        if dvd is not None:
            self._rootNode.child(dvd).lsdvd = lsdvd
            self.insertTracks(lsdvd['track'], self.index(dvd, 0, QtCore.QModelIndex()))

if __name__ == '__main__':
   pass 
