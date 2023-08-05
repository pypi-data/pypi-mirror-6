######################################################################################
################################### Classes ##########################################
######################################################################################
class CommException(Exception): pass

class Comm(object):
    """
        This class is responsible for low level communication

        Constants:
        ACKNOWLEDGE     - Acknowledge string used to handshake
        BUFFER_SIZE     - Receive buffer size
        RECV_TIMEOUT    - Receive timeout

        Variable:
    """
    ACKNOWLEDGE = b'ACKNOWLEDGE'
    BUFFER_SIZE = 4096
    RECV_TIMEOUT = 30

    def send(self,data):
        """
            This function sends data.
            Transmission protocol:
            <-- data length
            --> acknowledge
            <-- data
            --> acknowledge

            Input:
            date        - data to send

            Returns:
            Nothing
        """
        if not isinstance(data, str):
            raise CommException(str(type(data)) + " is wrong type. Data to send has to be string")

        data_length = len(data)
        self._lowLevelSend(str(data_length))
        data_received = self._lowLevelRecv(len(self.ACKNOWLEDGE))

        if data_received != self.ACKNOWLEDGE:
            raise CommException("Sending error. Data size. Did not received acknowledge. Received: " + data_received)

        sent_data_lenght = 0
        while sent_data_lenght < data_length:
            sent_data_lenght += self._lowLevelSend(data[sent_data_lenght:])

        data_received = self._lowLevelRecv(len(self.ACKNOWLEDGE))

        if data_received != self.ACKNOWLEDGE:
            raise CommException("Sending error. Data load. Did not received acknowledge. Received: " + data_received)

    def receive(self):
        """
            This function receives data.
            Transmission protocol:
            --> data length
            <-- acknowledge
            --> data
            <-- acknowledge

            Input:
            Nothing

            Returns:
            data        - Received data
        """
        data_received = self._lowLevelRecv(self.BUFFER_SIZE)

        try: data_length = int(data_received)
        except ValueError: raise CommException("Received data length is invalid.")

        self._lowLevelSend(self.ACKNOWLEDGE)
        received_data_length = 0
        data_received = ""
        while received_data_length < data_length:
            data_received = data_received + self._lowLevelRecv(self.BUFFER_SIZE)
            received_data_length = len(data_received)

        self._lowLevelSend(self.ACKNOWLEDGE)

        return data_received

    def close(self):
        """
            This function closes socket connection

            Input:
            Nothing

            Returns:
            Nothing
        """
        self._lowLevelClose()

    def open(self):
        """
            This function opens socket

            Input:
            Nothing

            Returns:
            Nothing
        """
        self._lowLevelOpen()

    def _commLogSend(self,data):
        """
            This function logs frames that were send

            Input:
            data    - Frame to be logged

            Returns:
            Nothing
        """
        display.output.log(data,8)

    def _commLogReceive(self,data):
        """
            This function logs frames that were received

            Input:
            data    - Frame to be logged

            Returns:
            Nothing
        """
        display.output.log(data,7)

    def _lowLevelRecv(self,buffer):
        """
            Low level receive function.
            NOTE: This function has to be overloaded in class that inharits from this

            Input:
            buffer  - Buffer size

            Returns:
            Received data
        """
        raise CommException("_lowLevelRecv function not defined")

    def _lowLevelSend(self,data):
        """
            Low level send function.
            NOTE: This function has to be overloaded in class that inharits from this

            Input:
            data    - data to send

            Returns:
            Send data size
        """
        raise CommException("_lowLevelSend function not defined")

    def _lowLevelOpen(self):
        """
            Low level open socket function
            NOTE: This function has to be overloaded in class that inharits from this

            Input:
            Nothing

            Returns:
            Nothing
        """
        raise CommException("_lowLevelOpen function not defined")

    def _lowLevelClose(self):
        """
            Low level close function.
            NOTE: This function has to be overloaded in class that inharits from this

            Input:
            Nothing

            Returns:
            Nothing
        """
        raise CommException("_lowLevelClose function not defined")

######################################################################################
################################### Functions ########################################
######################################################################################

def getHostName():
    """
        This function reads host name

        Input:
        Nothing

        Returns:
        Host name
    """
    import socket
    return socket.gethostname()

def getUserName():
    """
        This function reads user name

        Input:
        Nothing

        Returns:
        User name
    """
    import getpass
    return getpass.getuser()
