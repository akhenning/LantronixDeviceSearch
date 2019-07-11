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
# Only used in searchIPFromMac() to wait for search to finish
from time import sleep
# Used in graphics
from tkinter import Tk, Frame, Label, Button
# Used for lines in output
from tkinter.ttk import Separator
# Used to search and keep GUI running
from threading import Thread
# Also used to decode hex strings
from codecs import decode

# I did my best to import only what I need to try to speed up
# boot times

gridColor = "#20c0bb"
HEADER = "#FF69B4"

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

#--- IF CALLING THIS PROGRAM FROM ANOTHER PROGRAM, USE THIS METHOD
def searchIPFromMac(macAddress = "{)}`", print_when_done_searching = False, timeout = 2.0):
    ''' 
    General case method where the MAC address is given, and the IP address is returned.
    Broadcasts to all Lantronix devices, and looks for one with the correct MAC address.
    If no MAC address is given, returns the list of devices found in a list of lists in
    format [Device Name, MAC address, IP address]. Elements are as strings.

    It is not reccommended to change the second or third variables, but if you want:
    The second variable can be set to True if you wish it to print when it is done 
    searching. The third variable can be changed if you wish to increase the time before
    it stops searching.

    If calling from another program, use this method!
    '''
    # Global is used so you can check search across threads
    global output
    global timeoutTime
    global printMessages
    timeoutTime = timeout
    printMessages = print_when_done_searching

    macAddress = macAddress.upper()
    # Starts main method in main segment of program, which broadcasts and looks
    # for responses.
    listener = Thread(target=search, args=(), daemon=True)
    listener.start()

    # Anything the above thread finds will be added to the global output
    # variable.  So, we check for the MAC address in it.
    # I don't remember why I made the timeout counter slightly less than 2x.
    times = timeoutTime * 1.8
    while macAddress not in output:
        sleep(.5)
        if times < 0:
            # If times hits 0, then MAC address is not found in search.
            # If default mac address, then it should return the entire
            # output. If not, then search has failed.
            if macAddress == "{)}`":
                # It occured to me that I probably shouldn't return
                # this as a raw string. That'd probably be pretty
                # annoying to work with. So this bit splits it into
                # a list of lists.
                devices = output.split("\n")
                i = len(devices) - 1
                while i > -1:
                    devices[i] = devices[i].split("::")
                    if len(devices[i])==1:
                        del devices[i]
                    i -= 1
                return devices
            else:
                return -1
        times -= 1

    # Find IP address in the output string, since if it was not in output
    # string, it would not have exited loop.
    # See 'format of output string' above.
    lines = output.split('\n')
    for address in lines:
        if(address != ""):
            addresses = address.split('::')
            if macAddress.strip() in addresses[1]:
                return addresses[2]

    #Should not get here, but if it does, something went wrong
    return -1


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
    

class Application(Frame):
    '''Holds GUI for selecting an IP address from a list'''
    def __init__(self,master):
        '''Initalizes frame'''
        Frame.__init__(self,master)
        self.grid()
        self.root = master
        self.menu()
        
    def menu(self):
        '''The main place the buttons and found devices are displayed.'''
        self.searching = 0
        # Set window size and first few descriptive labels.
        # ...I probably should have collapsed these into one label, in
        # hindsight. I didn't know you could make multiline labels at first. 
        self.root.geometry("500x600")
        self.label1 = Label(self,text="\n\tWelcome to the GridConnect Simple Lantronix Device Search!\n" + 
                            "\n\tClick the 'Find Devices' button to recieve a list of all Lantronix devices.\n" + 
                            "\tYou can copy any IP address to clipboard by clicking the button with the IP.", justify="left")
        self.label1.grid(columnspan=16,sticky='w')
        self.label4 = Label(self,text="\t\t\t")
        self.label4.grid()

        # Label that displays the spinner.
        self.spin = Label(self,text="",font=('TkDefaultFont', 24))
        self.spin.grid(column = 0, row = 14, sticky = 'e')

        # Make the buttons
        self.new = Button(self,text="Find Devices",command=self.search,bg="white")
        self.new.grid(column=1,row=14)
        self.new2 = Button(self,text="Exit",command=self.exitgame,bg="red")
        self.new2.grid(column=3,row=14,sticky='e')

        # Final output label
        self.outputL = Label(self,text="\t")
        self.outputL.grid(column=0,row=17,columnspan=16,sticky='w')

        # Make empty list that will hold the widgets that contain the output 
        # of the program
        self.seriesOfLabels = []
        # Make variable that saves cycles if nothing has changed since it
        # last checked
        self.lastOutput = ""

        # Variables that handle the spinning of the spinner
        self.counter = 0
        self.spinner = ['◐','◓','◑','◒']#["◜ ", " ◝", " ◞", "◟ "]
        self.spinlength = len(self.spinner)

        # Start loop that updates output
        self.updateOutput()
    def exitgame(self):
        '''closes window.'''
        self.root.destroy() # is this how you do this?  This seems barbaric in hindsight
    def updateOutput(self):
        ''' Reads from output variable to update GUI. Rather contrived in how it does it.
        The grid might look a bit ugly, but it took me a stupid amount of time, so it means a lot to me.
        '''
        global output
        # Only edit if something has changed
        if self.lastOutput != output:
            # Clear previous display (dynamically adding/removing is not worth the effort)
            for tupl in self.seriesOfLabels:
                tupl[0].grid_forget()
                tupl[0].destroy()
                # In try block because the last one only has 3 elements, and 
                # it wasn't worth trying to find a way to do this without a 
                # try block since the None will always be the last element.
                try:
                    tupl[1].grid_forget()
                    tupl[1].destroy()
                    tupl[2].grid_forget()
                    tupl[2].destroy()
                    tupl[3].grid_forget()
                    tupl[3].destroy()
                except:
                    pass
            self.seriesOfLabels = []
            # This prevents it from rendering grid if no output
            if output != "":
                self.outputL['text'] = "\t"
                lines = output.split('\n')

                # This variable helps the loop tell where to place objects
                grid = 19
                # Make topmost line
                line1 = Separator(self)
                line1.grid(row = 18, column = 1, columnspan=2, sticky="ew")
                # Sequentially make labels for each of the devices found
                for address in lines:
                    if(address != ""):
                        addresses = address.split('::')
                        #self.seriesOfIPA.append(addresses[2])

                        name = Label(self,text=addresses[0] + " ")
                        mac = Label(self,text=addresses[1])
                        ip = Label(self, text=addresses[2], cursor = "hand2", highlightthickness = 2, relief = 'raised')
                        # Make it so you can click on the IP addresses to copy 
                        # them to clipboard
                        ip.bind("<Button-1>", self.copy)  
                        name.grid(column = 0, row = grid, sticky = 'e')
                        mac.grid(column = 1, row = grid)
                        ip.grid(column = 2, row = grid)

                        # Add line that separates elements
                        line = Separator(self)
                        line.grid(row = grid + 1, column = 1, columnspan = 2, sticky="ew")

                        # Basic iteration stuff
                        grid += 2
                        self.seriesOfLabels.append((name, mac, ip, line))
                        if grid > 32:
                            self.root.geometry("500x1000")
                # Fill out the grid with things that go on the side
                span = grid - 19
                if span < 1:
                    span = 1
                line2 = Separator(self, orient='vertical').grid(column=0, row=19, rowspan=span, sticky='nse')
                line3 = Separator(self, orient='vertical').grid(column=3, row=19, rowspan=span, sticky='nsw')
                self.seriesOfLabels.append((line1, line2, line3, None))

                self.lastOutput = output
        # Call itself soon to update any changes while searching for
        # devices.
        if(self.searching > 0): # 5 times a second
            self.after(200, self.updateOutput)
            self.searching -= 1
            if self.searching == 0:
                self.spin['text'] = ""
                if output == "":
                    self.outputL['text'] = "\t[None Found]"
            else:
                self.spin['text'] = self.spinner[self.counter] 
                self.counter += 1
                if self.counter == self.spinlength:
                    self.counter = 0
    def copy(self, event):
        ''' Simple method to copy button's contents to clipboard.'''
        cpy = event.widget.cget("text")
        self.root.clipboard_clear()
 
        self.root.clipboard_append(cpy)
        self.root.update()
    def search(self):
        ''' Starts another thread to search for devices.'''
        # The self.searching variable prevents you from starting another 
        # search before the previous one has ended
        if self.searching <= 0:
            self.searching = (timeoutTime * 5) + 6
            # Wow, did I really name the method 'search' as well? Uh, so it
            # targets the global method Search which sends and recieves 
            # the messages.
            listener = Thread(target=search, args=(), daemon=True)
            listener.start()
        # Calls the update output method, which will continue to run 5 times
        # a second until self.searching hits zero.
        self.updateOutput()


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
    if id == "U5":
        return "XDirect"
    if id == "X7":
        return "XPort Direct"
    if id == "X8":
        return "XPort Direct+"
    if id == "W1":
        return "WiPort"
    if id == "E5":
        return "XPort Pro"
    if id == "":
        return ""
    return "Not Reconized, " + str(id)


def main():
    ''' Basic main method to set up GUI.'''
    #subprocess.call('pyinstaller -h')# SearchFunction.py')

    root = Tk()
    root.title("Lantronix Device Searcher")

    app = Application(root)
    root.mainloop()

def main2():
    print("Answer: "+ str(searchIPFromMac())) #Ex: "0080A3CFEE24"
main()
#main2()
