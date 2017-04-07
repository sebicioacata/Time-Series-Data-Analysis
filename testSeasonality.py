"""
Credit:
    Codul foloseste libraria seasonal (https://github.com/welch/seasonal)
"""


import subprocess
import re

class testSeasonality:
    
    __result = None
    file = None
    def __init__(self, file):
        self.file = file
    
    def getResult(self):
        cmd = "seasonal " + self.file.name
        p = subprocess.Popen(cmd , shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        out = p.communicate()[0]
        out = str(out)
        regex = r'\\n[0-9]*?\\t'
        seasonality = re.findall(regex, out)
        regex = r'[0-9]*'
        seasonality = re.findall(regex, str(seasonality))
        seasonality = int(seasonality[5])
        self.__result = seasonality
        
        return self.__result
        
