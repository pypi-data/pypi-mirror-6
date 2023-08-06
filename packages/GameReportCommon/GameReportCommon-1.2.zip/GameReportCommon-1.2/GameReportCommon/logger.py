from logging import FileHandler
import logging
import os


class Logger(object):

    def __init__(self, name):
        #Creating the logger
        self.logger_instance = logging.getLogger(name)

        self.logger_instance.setLevel(logging.DEBUG)
        #We define the log's format
        self.formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

        directory = os.getcwd()

        if not os.path.exists(directory+"/logs"):
            os.makedirs(directory+"/logs")

        file_handler = FileHandler(directory+'/logs/'+str(name)+'_activity.log', 'a', None, 0)

        #We set the log's output to the console
        if not self.logger_instance.handlers:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.DEBUG)
            stream_handler.setFormatter(self.formatter)
            self.logger_instance.addHandler(stream_handler)

            #Adding the log file to the logger if exists
            try:
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(self.formatter)
                self.logger_instance.addHandler(file_handler)
            except NameError:
                pass