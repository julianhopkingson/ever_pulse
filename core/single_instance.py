from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QObject, Signal

class SingleInstance(QObject):
    """
    Class to handle single instance application logic using QLocalServer/QLocalSocket.
    """
    request_activate = Signal()

    def __init__(self, app_key="ever_pulse_unique_key"):
        super().__init__()
        self._app_key = app_key
        self._server = QLocalServer()
        self._socket = QLocalSocket()

    def check(self):
        """
        Check if an instance is already running.
        Returns:
            True if another instance is running (we should exit).
            False if we are the first instance (we should run).
        """
        # Try to connect to existing server
        self._socket.connectToServer(self._app_key)
        if self._socket.waitForConnected(500):
            # Connected to existing instance
            # Send wakeup message
            self._socket.write(b"WAKEUP")
            self._socket.waitForBytesWritten(1000)
            self._socket.disconnectFromServer()
            return True
        
        # No existing instance found (or connection failed)
        # We become the server
        self._start_server()
        return False

    def _start_server(self):
        # Clean up any leftover server file (especially on Unix)
        # On Windows, this might effectively be a no-op for pipes if not in use,
        # but good practice to ensure we can bind.
        QLocalServer.removeServer(self._app_key)
        
        if not self._server.listen(self._app_key):
             # If listening fails, it's possible a zombie process holds the lock
             # or permissions issue. We'll proceed as if we are the instance,
             # but logging this would be good. For now, just proceed with a warning check.
             # In a production app, we might log this or handle it more gracefully.
             pass

        self._server.newConnection.connect(self._handle_new_connection)

    def _handle_new_connection(self):
        socket = self._server.nextPendingConnection()
        if socket:
            socket.readyRead.connect(lambda: self._read_socket(socket))
    
    def _read_socket(self, socket):
        data = socket.readAll()
        if data == b"WAKEUP":
            self.request_activate.emit()
            # We don't need to keep the connection open
            socket.disconnectFromServer()
