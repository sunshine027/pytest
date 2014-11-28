import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from exceptions import IOError, AttributeError

from exception.testexception import TestException

class XMLParser:
    
    ''' A class to parsing xml profile '''
    
    def __init__(self, cfg):
        try:
            self.tree = ET.parse(cfg)
        except IOError, e:
            raise TestException("Error: the file: " + str(cfg) + " can not be found")
        except ExpatError, e:
            raise TestException("Error: the file: " + str(cfg) + " is invalid, please check if all tags are matched or missed some signs.")

    def ClientParser(self):
        root = self.tree.getroot()
        dict = {}
        etl = list(root)
        for child in etl:
            dict.setdefault(child.tag, child.text)
        return dict
    

class ETParser:
    
    def __init__(self):
        pass
    
    def ETtoDict(self, et):
        dict = {}
        etl = list(et)
        for child in etl:
            dict.setdefault(child.tag, child.text)
        return dict