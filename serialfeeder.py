import serial, sys
from colorama import Fore, Style, init

init()
ser = serial.Serial('COM10',9600)
sys.stdout.write(Style.BRIGHT+Fore.YELLOW+"\tSerialFeeder.py, for HackMelbourne CNC\n\n")
sys.stdout.write('\tClearing the input buffer\n')
sys.stdout.write(Fore.RED+'\t'+str(ser.inWaiting())+" chars waiting\n")
ser.flushInput()
sys.stdout.write(Fore.RED+"\tstill "+str(ser.inWaiting())+" chars waiting\n")
#ser.write(b'\rReady to send data!\r')
sys.stdout.write(Fore.BLUE+"\tReady to recieve.\n")
so_far = []
while True:
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
        #ser.close()
        #quit()
