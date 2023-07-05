'''
webserver.py
Simple webserver alowwing the user coonnect to the PICO and interact with it
through the web page.

Source based on:
Source: https://projects.raspberrypi.org/en/projects/get-started-pico-w/1
Source: https://youtu.be/eym8NpHr9Xw
Compilation: Durim Miziraj
2023-06-04T21:55:19
'''

import gc
import machine
import socket
import time

import appconfig as params
from applog import APPLOG
from dht11 import DHT11
from netconn import NETCONN

class WEBSERVER:
    def __init__(self, log:APPLOG, conn:NETCONN, dht11:DHT11):
        self._log = log
        self._conn = conn
        self._dht11 = dht11
        self._socket: socket.socket
        self._is_listening = False
        self._display_msgtab = True


    # Open a port to listen on
    def _open_socket(self):
        ip = self._conn.connect().ifconfig()[0]
        s = socket.socket()		# Creating a socket.
        address = (ip, params.listen_port) 	# Port 80 is the default port for http requests.
        n = 0
        while n < 15:
            n +=1 
            try:
                self._log.log_msg(APPLOG.TRACE, "Bind")
                s.bind(address) 		# Binding the socket to the ip and port number.
                n = 10
            except Exception as e:
                if (n == 10):
                    raise e
                time.sleep(2)

        self._log.log_msg(APPLOG.DEBUG, "Listen")
        s.listen(1)				# Starts listening to requests that come in. The number is the max size of the queue for requests.
        self._is_listening = True
        self._log.log_msg(APPLOG.INFO, "listening on " + str(address) + " port " + str(params.listen_port))
        return s


    #Returns a string showing uptim, the time between now and when the PICO was started
    def _uptime(self):
        self._log.log_msg(APPLOG.TRACE, 'Entering _uptime')
        # Calculating total uptime in seconds, minutes, hours and days
        uptime_seconds = int(round((time.ticks_ms())/1000))
        uptime_minutes = int(round(uptime_seconds/60))
        uptime_hours = int(round(uptime_minutes/60))
        uptime_days = int(round(uptime_hours/24))

        # Calculating the current duration of uptime in a standard 
        current_seconds = uptime_seconds % 60
        current_minutes = uptime_minutes % 60
        current_hours = uptime_hours % 60

        # Printing the current uptime in days, hours, minutes and seconds
        t = str(uptime_days) + " days, " + str(current_hours) + " hours, " + \
            str(current_minutes) + " minutes, " +  str(current_seconds) + " seconds"
        return(t)    


    #Construct the web page to show for the end user
    def _webpage(self):
        self._log.log_msg(APPLOG.TRACE, 'Entering webserver._webpage')

        temperature = 0
        humidity = 0
        measure_ts = ""
        try:
            (temperature, humidity, measure_ts) = self._dht11.measures
        except Exception as e:
            self._log.log_msg(APPLOG.ERROR, "webpage: " + str(e))

        msgtab = self._log.msgtab
        msgtab_button = "showpermmsg?"
        msgtab_txt = "Show Permanent Messages"
        if (not self._display_msgtab):
            msgtab = self._log.permtab
            msgtab_button = "showlivemsg?"
            msgtab_txt = "Show Live Messages"
     
        html1 = f"""
                <!DOCTYPE html>
                <html>
                    <body>
                        <table style="table-layout: fixed; width: 100%;">
                            <tr>
                                <td style="width:20%;">
                                    <form action="./refresh"> 
                                        <input type="submit" value="Refresh" />
                                    </form>
                                </td>
                                <td style="width:20%;">
                                    <form action="./terminate"> 
                                        <input type="submit" value="Terminate application" />
                                    </form>
                                </td>
                                <td style="width:20%;">
                                    <form action="./restart"> 
                                        <input type="submit" value="Restart device" />
                                    </form>
                                </td>
                            </tr>
                            <tr>
                                <td style="width:20%;">
                                    <form action="./{msgtab_button}"> 
                                        <input type="submit" value="{msgtab_txt}" />
                                    </form>
                                </td>
                                <td style="width:20%;"></td>
                                <td style="width:20%;"></td>
                            </tr>
                        </table>
                        <br>
                        <table align=left style="float:left;  text-align:left; table-layout: fixed; width: 100%;" >
                            <tr>
                                <td style=" text-align:left; width:20%;"><b>Device uptime</b></td>
                                <td style=" text-align:left; width:30%;">{self._uptime()}</td>
                                <td style=" text-align:left; width:50%;"></td>
                            </tr>
                        </table>
                        <br>
                        <table align=left style="float:left;  text-align:left; table-layout: fixed; width: 100%;" >
                            <tr>
                                <td style=" text-align:left; width:20%;"><b>CPU frequency MHz</b></td>
                                <td style=" text-align:right; width:5%;">{int(machine.freq()/1000000)}</td>
                                <td style=" text-align:left; width:75%;"></td>
                            </tr>
                            <tr>
                                <td style=" text-align:left; width:20%;"><b>Memory allocated</b></td>
                                <td style=" text-align:right; width:5%;">{gc.mem_alloc()}</td>
                                <td style=" text-align:left; width:75%;"></td>
                            </tr>
                            <tr>
                                <td style=" text-align:left; width:20%;"><b>Memory free</b></td>
                                <td style=" text-align:right; width:5%;">{gc.mem_free()}</td>
                                <td style=" text-align:left; width:75%;"></td>
                            </tr>
                            <tr>
                                <td style=" text-align:left; width:20%;"></td>
                                <td style=" text-align:left; width:5%;"></td>
                                <td style=" text-align:left; width:75%;"></td>
                            </tr>
                            <tr>
                                <td style=" text-align:left; width:20%;"></td>
                                <td style=" text-align:left; width:5%;"></td>
                                <td style=" text-align:left; width:75%;"></td>
                            </tr>
                        </table>
                        <br>
                        <table align=left style="float:left;  text-align:left; table-layout: fixed; width: 50%;" >
                            <tr>
                                <td style=" text-align:left; width:20%;"><b>Measures read time</b></td>
                                <td style=" text-align:left; width:30%;">{measure_ts}</td>
                            </tr>
                            <tr>
                                <td style=" text-align:left; width:20%;"><b>Temerature in degrees</b></td>
                                <td style=" text-align:left; width:30%;">{temperature}</td>
                            </tr>
                            <tr>
                                <td style=" text-align:left; width:20%;"><b>Humidity</b></td>
                                <td style=" text-align:left; width:30%;">{humidity}%</td>
                            </tr>
                            <tr>
                                <td style=" text-align:left; width:20%;"></td>
                                <td style=" text-align:left; width:30%;"></td>
                            </tr>
                            <tr>
                                <td style=" text-align:left; width:20%;"></td>
                                <td style=" text-align:left; width:30%;"></td>
                            </tr>
                        </table>
                """
        
        html2 = f"""
                        <table style="float:left; text-align:left; table-layout: fixed; width: 100%;">
                            <tr>
                                <th style=" text-align:left; width:20%;">Log time</th>
                                <th style=" text-align:left; width:10%;">Severity</th>
                                <th style=" text-align:left; width:70%;">Message</th>
                            </tr>
                """

        msg_count = len(msgtab)
        for n in range(0,msg_count):
            html2 += f"""
                            <tr>
                                <td style=" text-align:left; width:20%;">{msgtab[n][0]}</td>
                                <td style=" text-align:left; width:10%;">{self._log.severity_text(msgtab[n][1])}</td>
                                <td style=" text-align:left; width:70%;">{str(msgtab[n][2]).replace('<','&lt').replace('>','&gt')}</td>
                            </tr>
                     """

        html3 = f"""
                        </table>
                    </body>
                </html>
                """
        return str(html1 + html2 + html3)


    def serve(self):
        '''
        Handle request if there is any to handle
        '''
        self._log.log_msg(APPLOG.TRACE, 'Entering webserver.serve')

        if (not self._is_listening):
            self._socket = self._open_socket()

        temperature = 0 
        self._socket.setblocking(False)
        client: socket.socket
        try:
            (client, client_adress) = self._socket.accept() # Accepts the connection of the device that is connectiong to it
            self._socket.setblocking(True)
        except Exception as e :
            self._socket.setblocking(True)
            return

        # There is a request to handle if we landed here
        client.setblocking(True)
        request = str(client.recv(2048))	# Recieving data (a request) from the client device that is up
                                            # to 2 kb. Stores the request as a string.
        self._log.log_msg(APPLOG.TRACE, "Accepted request {}".format(request))

        try:
            request = request.split()[1] # First index is a html GET method, the other is the type of request.
            self._log.log_msg(APPLOG.TRACE, request)
        except IndexError:	
            # Catches errors when the request does not have any specified GET variable
            client.close()	
            return

        if request == '/refresh?':
            pass
        elif request == '/showpermmsg?':	
            self._msgtab = self._display_msgtab = False
        elif request == '/showlivemsg?':	
            self._msgtab = self._display_msgtab = True
        elif request == '/restart?':	
            client.close()
            self._log.log_msg(APPLOG.INFO, "Restarting device by machine.reset()")
            machine.reset()
            return # We never reach this point
        elif request == '/terminate?':	
            client.close()
            self._log.log_msg(APPLOG.INFO, "Terminating application by simulating CTRL-C")
            raise KeyboardInterrupt
            
        html = self._webpage()	# Stores the html code with the variables that are meant to be shown to the user.
        n = client.write(html) # Sends the  html code to the client.
        client.close() # Closes the connection to the client device


    def close(self):
        '''
        Stop listening on port
        '''
        self._log.log_msg(APPLOG.TRACE, "Entering webserver.close")
        if (self._is_listening):
            self._is_listening = False

            try:
                self._socket.close()
            except Exception as ignored:
                self._log.log_msg(APPLOG.WARN," Error closing socket: " + str(ignored))

