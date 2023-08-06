import logging
import widgets
from PyQt4 import QtGui, QtNetwork, QtCore
from PyQt4.Qt import Qt as QtConst
from pyqtgraph.dockarea import DockArea
import numpy as np
import json

logging.root.setLevel(logging.WARNING)

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Liveplot")
        self.dockarea = DockArea()
        self.setCentralWidget(self.dockarea)
        self.namelist = NameList(self)
        self.addDockWidget(QtConst.LeftDockWidgetArea, self.namelist)

        self.listener = QtNetwork.QLocalServer()
        self.listener.removeServer("LivePlotter")
        self.listener.listen("LivePlotter")
        logging.debug('connection set to %s' % self.listener.fullServerName())
        while self.listener.hasPendingConnections():
            self.accept()
        self.listener.newConnection.connect(self.accept)
        self.bytes = bytearray()
        self.target_size = 0
        self.meta = None
        self.insert_dock_right = True
        self.conns = []

    def accept(self):
        logging.debug('connection accepted')
        conn = self.listener.nextPendingConnection()
        self.conns.append(conn)
        conn.readyRead.connect(lambda: self.read_from(conn))

    # noinspection PyNoneFunctionAssignment
    def read_from(self, conn):
        logging.debug('reading data')
        if not self.target_size:
            self.meta = json.loads(str(conn.read(200).rstrip('\x00')))
            self.target_size = self.meta['arrsize']
        if self.target_size > 0:
            self.bytes.extend(bytearray(conn.read(self.target_size - len(self.bytes))))
        if len(self.bytes) == self.target_size:
            self.process_bytes()
        if conn.bytesAvailable():
            self.read_from(conn)

    def process_bytes(self):
        self.target_size = 0
        if len(self.bytes) > 0:
            arr = np.frombuffer(buffer(self.bytes), dtype=self.meta['dtype'])
            try:
                arr.resize(self.meta['shape'])
            except ValueError:
                arr = arr.reshape(self.meta['shape'])
        else:
            arr = None
        self.bytes = bytearray()
        self.do_operation(arr)

    def do_operation(self, arr=None):
        meta = self.meta
        operation = meta['operation']
        name = meta['name']

        if name in self.namelist:
            pw = self.namelist[name]
            if pw.closed:
                pw.closed = False
                self.dockarea.addDock(pw)

        else:
            if operation == 'clear':
                return
            pw = self.add_new_plot(meta['rank'], name)

        if operation == 'clear':
            pw.clear()
        elif operation == 'plot_y':
            start_step = meta['start_step']
            if start_step is not None:
                x0, dx = start_step
                nx = len(arr)
                xs = np.linspace(x0, x0 + (nx-1)*dx, nx)
                pw.plot(xs, arr)
            else:
                pw.plot(arr)
        elif operation == 'plot_xy':
            pw.plot(arr[0], arr[1], parametric=True)
        elif operation == 'plot_z':
            start_step = meta['start_step']
            if start_step is not None:
                (x0, dx), (y0, dy) = start_step
                pw.setImage(arr, pos=(x0, y0), scale=(dx, dy))
            else:
                pw.setImage(arr)
        elif operation == 'append_y':
            xs, ys = pw.get_data()
            new_ys = list(ys)
            new_ys.append(meta['value'])
            start_step = meta['start_step']
            if start_step is not None:
                x0, dx = start_step
                nx = len(new_ys)
                xs = np.linspace(x0, x0 + (nx-1)*dx, nx)
                pw.plot(xs, new_ys)
            else:
                pw.plot(new_ys)
        elif operation == 'append_xy':
            xs, ys = pw.get_data()
            xn, yn = meta['value']
            new_xs = list(xs)
            new_xs.append(xn)
            new_ys = list(ys)
            new_ys.append(yn)
            pw.plot(new_xs, new_ys, parametric=True)

        elif operation == 'append_z':
            image = pw.get_data()
            if image is None:
                image = np.array([arr])
            else:
                image = np.vstack((image, [arr]))
            start_step = meta['start_step']
            if start_step is not None:
                (x0, dx), (y0, dy) = start_step
                pw.setImage(image, pos=(x0, y0), scale=(dx, dy))
            else:
                pw.setImage(image)


    def add_new_plot(self, rank, name):
        pw = widgets.get_widget(rank, name)
        self.add_plot(pw)
        self.namelist[name] = pw
        return pw

    def add_plot(self, pw):
        self.insert_dock_right = not self.insert_dock_right
        self.dockarea.addDock(pw, position=['bottom', 'right'][self.insert_dock_right])

    def sizeHint(self):
        return QtCore.QSize(1000, 600)

class NameList(QtGui.QDockWidget):
    def __init__(self, window):
        super(NameList, self).__init__('Current Plots')
        self.namelist_model = QtGui.QStandardItemModel()
        self.namelist_view = QtGui.QListView()
        self.namelist_view.setModel(self.namelist_model)
        self.setWidget(self.namelist_view)
        self.window = window
        self.plot_dict = {}

        self.namelist_view.doubleClicked.connect(self.activate_item)

    def activate_item(self, index):
        item = self.namelist_model.itemFromIndex(index)
        plot = self.plot_dict[str(item.text())]
        if plot.closed:
            plot.closed = False
            self.window.add_plot(plot)

    def __getitem__(self, item):
        return self.plot_dict[item]

    def __setitem__(self, name, plot):
        model = QtGui.QStandardItem(name)
        model.setEditable(False)
        self.namelist_model.appendRow(model)
        self.plot_dict[name] = plot

    def __contains__(self, value):
        return value in self.plot_dict

    def __delitem__(self, name):
        self.namelist_model.removeRow(self.namelist_model.findItems(name)[0].index().row())
        self.plot_dict[name].close()
        del self.plot_dict[name]

def main():
    app = QtGui.QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
