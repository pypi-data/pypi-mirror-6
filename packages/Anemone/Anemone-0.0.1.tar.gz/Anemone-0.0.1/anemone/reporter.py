import zmq
import threading
from Queue import Queue, Empty

class Reporter(object):
    def __init__(self, program_name, analysis_name):
        """
        The only anemone class to use for the data generating program
        The analysis name should be the name of the input file
        or some other easily recognizable name such that a user of
        the GUI inspector program understands that he or she has 
        connected to the right analysis
        """
        self._program_name = program_name
        self._analysis_name = analysis_name
        self._queue = Queue()
    
    def start(self, address):
        self.server = Server(self._program_name, self._analysis_name, self._queue)
        self.thread = threading.Thread(target=self.server.serve, args=(address,))
        self.thread.daemon = True
        self.thread.start()
    
    def report_2dplot(self, report_name, x, y):
        rep = (report_name, TYPE_2D_PLOT, (x, y))
        self._queue.put(rep)

TYPE_2D_PLOT = '2dplot'

class Server(object):
    
    def __init__(self, program_name, analysis_name, queue):
        """
        Internal class to handle communication with the listening GUIs
        """
        self.queue = queue
        self.program_name = program_name
        self.analysis_name = analysis_name
        self.reports = {}
    
    def serve(self, address):
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.REP)
        self.zmq_socket.bind(address)
        
        while True:
            try:
                item = self.queue.get(block=True, timeout=0.1)
                self.handle_queue_item(item)
            except Empty:
                # No items waiting, do nothing
                pass
            
            try:
                request = self.zmq_socket.recv_pyobj(flags=zmq.NOBLOCK)
                self.handle_zmq_request(request)
            except zmq.Again:
                # No requests waiting, do nothing
                pass
    
    def handle_queue_item(self, item):
        """
        Get new report data from the analysis thread through the queue and
        append it to the reports we currently hold
        """
        name, type, data = item
        if name not in self.reports:
            if type == TYPE_2D_PLOT:
                self.reports[name] = (type, ([], []))
        
        if type == TYPE_2D_PLOT:
            self.reports[name][1][0].append(data[0])
            self.reports[name][1][1].append(data[1])
        
    def handle_zmq_request(self, request):
        """
        Handle a request for information from the remote GUI
        """
        print 'request:', request
        
        # The resuest must be a tuple
        if not isinstance(request, tuple):
            self.zmq_socket.send_pyobj('ERROR: unknown command')
            return
        
        # The tuple must have at least one item
        if len(request) < 1:
            self.zmq_socket.send_pyobj('ERROR: unknown command')
            return
        
        cmd = request[0]
        if cmd == 'get_analysis_info':
            # Return tuple containing (program_name, analysis_name, num_reports)
            response = (self.program_name, self.analysis_name, len(self.reports))
        elif cmd == 'get_reports':
            # Return list of (name, type) tuples
            response = [(name, self.reports[name][0]) for name in self.reports]
        elif cmd == 'get_report' and len(request) == 3:
            # Return  the data for the selected report
            name, start_index = request[1:]
            
            # Check that the requested report exists
            if not name in self.reports:
                self.zmq_socket.send_pyobj('ERROR: unknown report')
                return
            
            # Check that the start_index is an integer >= 0
            if not isinstance(start_index, int) or start_index < 0:
                self.zmq_socket.send_pyobj('ERROR: malformed start index')
                return
            
            type, data = self.reports[name]
            if type == TYPE_2D_PLOT:
                if len(data[0]) > start_index:
                    response = (data[0][start_index:], data[1][start_index:])
                else:
                    response = ([], [])
        else:
            self.zmq_socket.send_pyobj('ERROR: unknown command')
            return
        
        self.zmq_socket.send_pyobj(response)
