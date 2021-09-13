###############################################################################
#                   Henning
#                   SearchFunction.py
#                   A program that searches for Lantronix devices
#                   GridConnect, 6/3/19
###############################################################################
#                   Sources & Help
# https://stackoverflow.com/questions/27893804/udp-client-server-socket-in-python
# The code for using Sockets to conenct to UDP was on the internet, so I
# made good use of it.
# I also consulted with Andrew, but ended up not using his old code.
###############################################################################
# To build as executable (for my computer at least), in terminal type:
# py "C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python37_64\Scripts\pyinstaller.exe" --onefile SearchFunction.py
# I tried to get an icon to work because I have nothing to do, but I failed.
# --icon=SearchFunction.ico
###############################################################################
# I have nothing to do for the next hour, so you get unusually intimate and 
# sarcastic comments for this program.

import sys
# Needed to decode the hex strings the devices communicate with
from binascii import hexlify, unhexlify 
# Used to broadcast and receive messages
from socket import socket, SOL_SOCKET, SO_BROADCAST, timeout, AF_INET, SOCK_DGRAM
# Used to search and keep GUI running
from threading import Thread
# Also used to decode hex strings
from codecs import decode

# I did my best to import only what I need to try to speed up
# boot times

# Main output string variable that transfers information
output = []

# Global variables that determine some behavior in the thread that deals with
# sending and receiving messages
timeoutTime = 2.0
printMessages = False

def search():
    '''
    Broadcasts a message to all Lantronix devices, listens for responses, 
    and gets MAC and IP addresses from the responses. Outputs these values
    through the global variable output.
    '''
    global output
    global timeoutTime
    global printMessages
    output = []
    # Set port and destination that the devices are listening on
    port = 30718
    dest = '<broadcast>'
    if printMessages:
        print("BROADCASTING")
    # Make socket and set it to be able to broadcast
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.settimeout(timeoutTime)
    client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    # Make message that the devices will respond to
    message = unhexlify('000000F6')#.encode('utf-8')
    addr = (dest, port)
    
    # Send message, wait for responses until a timeout occurs
    client_socket.sendto(message, addr)
    try:
        while(1):
            # Wait for response
            data, server = client_socket.recvfrom(1024)
            
            # Decode MAC address from last 12 characters of data (shaved later)
            MAC = hexlify(data).decode('utf-8')

            # Decode id, and therefore name, of device
            id = decode(MAC[16:20], 'hex').decode('utf-8').upper()
            name = getType(id)

            MAC = MAC[-12:].upper()

            # Concatenate to global output variable, so other threads can see
            # Again, see 'format of output string' above.
            output.append((name, MAC, server[0]))
    except timeout:
        # Hey, this was the easiest way to terminate.
        if printMessages:
            print('done searching')
    

def getType(id):
    return {
        "X6": "xPico",
        "6X": "xPico110",
        "PA": "xPico-IAP",
        "Y1": "xPico Wi-Fi",
        "Y2": "xPico240",
        "Y3": "xPico250",
        "X2": "XPort-03/04",
        "XA": "XPort-IAP",
        "XM": "XPort-IAP",
        "YM": "XPort-IAP-05",
        "V2": "LTX110",
        "SC": "SecureLinx Console Manager",
        "S1": "SLC01 (Console Server)",
        "3Q": "UDS-10/Cobox 4.x",
        "X9": "XPort-05",
        "U4": "UDS2100",
        "U5": "XDirect",
        "X7": "XPort Direct",
        "X8": "XPort Direct+",
        "Y4": "XPort EDGE",
        "W1": "WiPort",
        "E5": "XPort Pro",
        "": ""}.get(id, "Not Recognized, " + str(id))


search()
if "--html" in sys.argv:
    for n in output:
        print('<p><a href="http://%s">%s, %s</a></p>' % (n[2], n[0], n[1]))
else:
    for n in output:
        print(n)
