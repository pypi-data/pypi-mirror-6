#import gevent
import logging
import daemon
import time

#from gevent.lock import Semaphore
#from gevent.server import StreamServer

logging.basicConfig(filename="pytheas.log")
logger = logging.getLogger("pytheas")
logger.setLevel(logging.INFO)

class Pytheas(object):
    """
    Intended usage:
        Define your fetcher and sender classes (as extending from patterns.Fetcher
        and patterns.Sender). Then, create a Pytheas object from instances of
        those classes. Call the run method of this Pytheas object and you're set.
    """
    
    def __init__(self, fetcher, sender, sleep_time=1):
        self.__fetcher = fetcher
        self.__sender = sender
        self.sleep_time = sleep_time
        #self.__external_server = StreamServer(("127.0.0.0", 16981), self.__listen_external)
        self.__ticket_counter = 1
        #self.__ticket_counter_lock = Semaphore()

    def __sendfetch(self):
        self.__sender.send(self.__fetcher.fetch())
        #gevent.sleep(1)

    def __listen_external(self, socket, address):
        """
        Sends two messages to any external client that has issued a command:
          - The first message is of the format "OK <ticketno>" where ticketno
            is a unique number identifying this transaction.
          - When it has finished processing the transaction and the processing
            is successful, it will send "T <ticketno>". Otherwise, send
            "F <ticketno>".

        All messages (commands and replies) are terminated by newlines (`\n`).
        """
        logger.info("external server received connection")
        sockfile = socket.makefile()

        while True:
            command = sockfile.readline()
            logger.info("issued command " + command)
            if not command:
                break
            else:
                ticketno = -1
                self.__ticket_counter_lock.acquire()
                ticketno = self.__ticket_counter
                self.__ticket_counter += 1
                self.__ticket_counter_lock.release()
                sockfile.write("OK " + str(ticketno))
                sockfile.write("T " + str(ticketno))
                sockfile.flush()

    def run(self):
        logger.info("about to run daemon")
        logger.info(str(dir(daemon)))
        errfile = open("err.out", "w")
        with daemon.DaemonContext(stderr=errfile):
            logger.info("daemon started")
            #self.__external_server.start()
            #logger.info("external server started")
            while True:
                self.__sender.send(self.__fetcher.fetch())
                #gevent.sleep(self.sleep_time)
                time.sleep(self.sleep_time)
