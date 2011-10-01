import serial
import sys
import os

def buildlist_incmac():
    if(sys.platform == "darwin"):
        devs = os.listdir("/dev/")
        devs = [filename for filename in devs if filename[0] == 'c']
        devs = [filename for filename in devs if filename[1] == 'u']
        return devs
    else:
        return range(256)

def scan():
    """scan for available ports. return a list of tuples (num, name)"""
    available = []
    for i in buildlist_incmac():
        try:
            s = serial.Serial(i)
            available.append( (i, s.portstr))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available

if __name__=='__main__':
    print "Found ports:"
    for n,s in scan():
        print "(%d) %s" % (n,s)