import serial, sys, time
from colorama import Fore, Style, init

def GetNew():
    so_far = []
    currentchar = ser.read(1)
    if(currentchar != b"\n" and currentchar != b"\r"):
        so_far.append(currentchar.decode('utf-8'))
    else:
        entire_line = "".join(so_far)
        if(entire_line == "quit" or entire_line == "exit"):
            ser.close()
            quit()
        elif(entire_line == "ok"):
            sys.stdout.write(Fore.YELLOW)
            print("\tRecieved an OKAY signal from controller")
            so_far = []
        else:
            sys.stdout.write(Fore.GREEN)
            print("\t\t",entire_line)
            #sys.stdout.write(str(entire_line),"\n")
            so_far = []

init()
ser = serial.Serial('COM10',9600,8,'N',1,0.5)
sys.stdout.write(Style.BRIGHT+Fore.YELLOW+"\tSerialFeeder.py, for HackMelbourne CNC\n\n")
sys.stdout.write('\tClearing the input buffer\n')
sys.stdout.write(Fore.RED+'\t'+str(ser.inWaiting())+" chars waiting\n")
ser.flushInput()
sys.stdout.write(Fore.RED+"\tstill "+str(ser.inWaiting())+" chars waiting\n")
sys.stdout.write(Fore.BLUE+"\tReady to recieve.\n")

while True:
    input("Press ENTER to exit")
    GetNew()


