'''
applog.py
Simple module to log messages instead of calling print everywhere
'''
import time
import io

import appconfig as params

class APPLOG:
    '''
    Simple class to write log messages from the application
    '''
    TRACE = 5
    DEBUG = 4
    INFO = 3
    WARN = 2
    ERROR = 1   
    FATAL = 0

    def __init__(self, log_level=INFO, msgstack_size=params.APPLOG_DEFAULT_MSGSTACK_SIZE):
        self._log_level = log_level
        self._msgstack_size = msgstack_size
        self._msgtab = []
        self._severities = ["fatal", "error", "warn", "info", "debug", "trace"]
 
    @property
    def log_level(self):
        return self._log_level
    
    @log_level.setter
    def log_value(self, level:int):
        if (level >= 0 and level <= self.TRACE):
            self._log_level = level

    def severity_text(self, severity:int):
        if (severity >= 0 and severity <= self.TRACE):
            return self._severities[severity]
        return("")

    @property
    def msgtab(self):
        return self._msgtab
   
    # Simple method to write a log message
    def log_msg(self, severity:int, msg, permanent= False):
        '''
        Writes the log message on standard output. The last
        20 messages are stored in a buffer and can be fetched
        for viewing in a webpage. Messages with a fatal severity
        or  messages with the parameter permanent set to True will
        be written to permanent storage on the device into
        the file named app.log.
        '''
        try:
            if (severity >= 0 and severity <= self.log_level):
                ts  = time.localtime()
                t = "{0:4d}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6}"\
                    .format(ts[0], ts[1], ts[2], ts[3], ts[4], ts[5], ts[6])
                
                m = (t, severity, str(msg))
                if (severity < self.TRACE): # Don't push trace messages on the messsage stack
                    self._msgtab.insert(0, m)

                    # Only keep the last self._msgstack_size messages
                    while (len(self._msgtab) > self._msgstack_size):
                        self._msgtab.pop()

                # A fatal event or permanent is saved so the event can be 
                # found after the device has been rebooted. 
                if (severity == self.FATAL or permanent):
                    try:
                        m = (t, severity, str(msg))
                        f  = io.open(params.APPLOG_LOGFILE, "a+")
                        f.write(m[0] + "\t"+ self.severity_text(m[1]) + "\t" + m[2] + "\n")
                        f.close()
                    except Exception as e:
                        print("Error writing {}: ".format(params.APPLOG_LOGFILE) + str(e))

                print(m[0], self.severity_text(m[1]), m[2])
        except Exception as e:
            print("applog error writing log message " + str(msg))
            


