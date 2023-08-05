'''
 log.py

 changelog
 2013-12-11[10:19:52]:copyright

 This is from the Internet.

 @info yinyong,osx-x64,Undefined,10.129.164.77,py,/Volumes/yinyong/ursa2/src
 @author yinyong@sogou-inc.com
 @version 0.0.1
 @since 0.0.1
'''
import logging
import time
import logging.handlers
try:
    import curses
    curses.setupterm()
except:
    curses = None

    #COLOR_BLACK    0
    #COLOR_RED      1
    #COLOR_GREEN    2
    #COLOR_YELLOW   3
    #COLOR_BLUE     4
    #COLOR_MAGENTA  5
    #COLOR_CYAN     6
    #COLOR_WHITE    7
    
class MessageFormatter(logging.Formatter):
    def __init__(self, color, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)
        self._color = color
        if color and curses:
            fg_color = unicode(curses.tigetstr("setaf") or curses.tigetstr("setf") or "", "ascii")
            self._colors = {
                # GREEN
                logging.DEBUG: unicode(curses.tparm(fg_color, 2), "ascii"),
                # COLOR_CYAN
                logging.INFO: unicode(curses.tparm(fg_color, 6), "ascii"), 
                # Yellow
                logging.WARNING: unicode(curses.tparm(fg_color, 3), "ascii"),
                # COLOR_MAGENTA
                logging.ERROR: unicode(curses.tparm(fg_color, 5), "ascii"),
                # Red
                logging.FATAL: unicode(curses.tparm(fg_color, 1), "ascii"),
                }
            self._normal = unicode(curses.tigetstr("sgr0"), "ascii")

    def format(self, record):
        try:
            record.message = record.getMessage()
        except Exception, e:
            record.message = "Bad message (%r): %r" % (e, record.__dict__)
        record.asctime = time.strftime("%Y/%m/%d %H:%M:%S", self.converter(record.created))
        
        prefix = '[%(levelname)-7s %(asctime)s] ' % record.__dict__
        #if self._color and curses:
        #    prefix = (self._colors.get(record.levelno, self._normal) + prefix + self._normal)
        formatted = prefix + record.message#unicode(record.message, 'utf-8', 'ignore')
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            formatted = formatted.rstrip() + "\n" + record.exc_text
        if self._color and curses:
            formatted = (self._colors.get(record.levelno, self._normal) + formatted + self._normal)
        return formatted.replace("\n", "\n    ")

class GMessageLog(object):
    def __init__(self):
        self._LEVE = {1:logging.INFO, 2:logging.WARNING, 3:logging.ERROR, 4:logging.DEBUG, 5:logging.FATAL}
        self.loger = logging.getLogger()
        self.init()
    
    def init(self):
        handler = logging.StreamHandler()
        handler.setFormatter(MessageFormatter(color=True))
        self.loger.addHandler(handler)
        
    def message(self, msg, leve=1):
        if leve == 1: self.loger.info(msg)
        elif leve == 2: self.loger.warning(msg)
        elif leve == 3: self.loger.error(msg)
        elif leve == 4: self.loger.debug(msg)
        elif leve == 5: self.loger.fatal(msg)

    def setLevel(self,level):
        self.loger.setLevel(level)

    def info(self,msg):
        self.message(msg,1)

    def warn(self,msg):
        self.message(msg,2)

    def debug(self,msg):
        self.message(msg,4)

    def error(self,msg):
        self.message(msg,3)

    def fatal(self,msg):
        self.message(msg,5)

if __name__ == '__main__':
    log=GMessageLog()
    log.setLevel(logging.FATAL)
    log.fatal("hello word")