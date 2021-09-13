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
output = ""
# Format of output string
# In hindsight, maybe I should have made this a list... 
# oh well, this works fine.
'''
NAME::MAC_ADDRESS1::IP_ADDRESS1\n
NAME::MAC_ADDRESS2::IP_ADDRESS2\n
'''

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
    output = ""
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
            output += name + "::" + MAC + "::" + server[0] + "\n"
    except timeout:
        # Hey, this was the easiest way to terminate.
        if printMessages:
            print('done searching')
    

def getType(id):
    ''' Matches a device's ID to its name.
    Does not cover every possible option, because there are so, so many.
    '''
    # what, no switch statement?
    if id == "X6":
        return "xPico"
    if id == "6X":
        return "xPico110"
    if id == "PA":
        return "xPico-IAP"
    if id == "Y1":
        return "xPico Wi-Fi"
    if id == "Y2":
        return "xPico240"
    if id == "Y3":
        return "xPico250"
    if id == "X2":
        return "XPort-03/04"
    if id == "XA":
        return "XPort-IAP"
    if id == "XM":
        return "XPort-IAP"
    if id == "YM":
        return "XPort-IAP-05"
    if id == "V2":
        return "LTX110"
    if id == "SC":
        return "SecureLinx Console Manager"
    if id == "S1":
        return "SLC01 (Console Server)"
    if id == "3Q":
        return "UDS-10/Cobox 4.x"
    if id == "X9":
        return "XPort-05"
    if id == "U4":
        return "UDS2100"
    if id == "U5":
        return "XDirect"
    if id == "X7":
        return "XPort Direct"
    if id == "X8":
        return "XPort Direct+"
    if id == "Y4":
        return "XPort EDGE"
    if id == "W1":
        return "WiPort"
    if id == "E5":
        return "XPort Pro"
    if id == "":
        return ""
    return "Not Reconized, " + str(id)


search()
print(output)
