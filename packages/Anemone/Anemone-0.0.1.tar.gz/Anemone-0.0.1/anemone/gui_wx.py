import sys, time
import zmq
import wx

import matplotlib
matplotlib.use('WxAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

MIN_TIME_BETWEEN_REQUESTS = 0.5 # seconds

class AnemoneWX(wx.Frame):
    def __init__(self, address):
        """
        A user interface for Anemone written using the WX GUI toolkit
        """
        wx.Frame.__init__(self, None, size=(800,600), title='Anemone')
        
        splitter = wx.SplitterWindow(self)
        splitter.SetMinimumPaneSize(50)
        splitter.SetSashGravity(1.0)
        self.plot_panel = PlotPanel(splitter)
        self.select_panel = wx.ListBox(splitter)
        splitter.SplitVertically(self.plot_panel, self.select_panel, -200)
        
        self.select_panel.Bind(wx.EVT_LISTBOX, self.on_select_report)
        
        status = wx.StatusBar(self)
        self.SetStatusBar(status)
        self.SetStatusText('Connecting ...')
        self.connected = False
        
        # Connect to the remote analysis
        self.connect(address)
        
        # Update the current plot data when idle
        self.Bind(wx.EVT_IDLE, lambda evt: self.get_monitor_data())
        
    def connect(self, address):
        """
        Setup the connection to the remote server
        ZeroMQ will allmost allways succeed, even if the remote server is not present, it will then hope
        the server will come online to answer us at a later time. This is dealt with in .get_info()
        """
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.REQ)
        self.zmq_socket.connect(address)
        self.get_info()
        self.last_request_time = 0
        self.selected_monitor_name = None
        self.selected_monitor_x = []
        self.selected_monitor_y = []
    
    def get_info(self, first_try=True):
        """
        The first contact with the analysis program. Get some info
        about the program and the list of available reports
        """
        if first_try:
            self.zmq_socket.send_pyobj(('get_analysis_info',))
        
        try:
            self.info = self.zmq_socket.recv_pyobj(flags=zmq.NOBLOCK)
        except zmq.Again:
            self.SetStatusText('Unable to connect, trying again in one second')
            wx.CallLater(1000, self.get_info, first_try=False)
            return
        
        self.zmq_socket.send_pyobj(('get_reports',))
        reports = self.zmq_socket.recv_pyobj()
        self.report_infos = reports
        
        for report_name, report_type in sorted(self.report_infos):
            self.select_panel.Append('%s (%s)' % (report_name, report_type), report_name)
        
        self.connected = True
        self.SetStatusText('Connected to analysis "%s" running in %s' % (self.info[1], self.info[0]))
    
    def on_select_report(self, event):
        """
        The user has selected a new monitor to show
        """
        report_name = event.GetClientObject()
        self.selected_monitor_name = report_name
        self.selected_monitor_x = []
        self.selected_monitor_y = []
        
    def get_monitor_data(self):
        """
        The program is idle, lets use the time to update the currently selected monitor
        with any new data that is available
        """
        now = time.time()
        if now - self.last_request_time < MIN_TIME_BETWEEN_REQUESTS:
            return
        self.last_request_time = now
        
        if self.selected_monitor_name is None:
            self.selected_monitor_x = []
            self.selected_monitor_y = []
        else:
            self.zmq_socket.send_pyobj(('get_report', self.selected_monitor_name, len(self.selected_monitor_x)))
            data = self.zmq_socket.recv_pyobj()
            assert isinstance(data, tuple), 'Got %r, not tuple' % data
            self.selected_monitor_x.extend(data[0])
            self.selected_monitor_y.extend(data[1])
        
        self.show_monitor()
    
    def show_monitor(self):
        """
        Show whatever is available of the currently selected monitor at the current time
        """
        plt = self.plot_panel.plotter
        plt.clear()
        plt.plot(self.selected_monitor_x, self.selected_monitor_y)
        

class PlotPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.SetBackgroundColour(wx.NamedColour("WHITE"))

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, wx.ID_ANY, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        self.toolbar.update()
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        
        self.SetSizer(self.sizer)
        
        self.plotter = WxMatplotlibProxy(self, self.axes, self.canvas)
        
    def OnPaint(self, event):
        self.canvas.draw()
        wx.Panel.OnPaint(self, event)

class WxMatplotlibProxy(object):
    def __init__(self, panel, axes, canvas):
        """
        This proxy exists to automatically call canvas.draw() after all
        plotting operations
        """
        self._panel = panel
        self._axes = axes
        self._canvas = canvas
        
    def _refresh_plot(self):
        self._canvas.draw()
        self._panel.Refresh()
    
    def __getattr__(self, attr):
        wx.CallAfter(self._refresh_plot)
        return getattr(self._axes, attr)

def run_wxgui(address):
    app = wx.App()
    gui = AnemoneWX(address)
    gui.Show()
    app.MainLoop()

if __name__ == '__main__':
    address = sys.argv[1]
    run_wxgui(address)
