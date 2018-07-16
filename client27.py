# Servitor
# Lowell Crook, Billy McAllister
# FTP Project Fall 2016
# Client code

import socket
import os
import sys
import zlib
import getpass
import base64

# set the default place for file to be saved from the sever.
#os.chdir("C:\Users\sol_s\Desktop\FTP")
os.chdir("C:\Users\sol_s\Desktop\FTP")

# Keep track of our sending and reciving formats
global isBinary
isBinary = True
global isCompress
isCompress = False
global isEncrypt
isEncrypt = False

def ls(): # list the avalible directories
    data = ''
    done = False
    while not done:
        m = s.recv(1024)
        if(m == "\\last/"):
            done = True
        else:
            s.send('got it')
            data += m + '\n'
            
    return data

def cd(): # change the currents working directory
   return s.recv(1024)

def get(name): # Get file from sever and send to client
    name_of_file= name.split('\\')
    with open(name_of_file[-1], 'wb') as f:
        f.write(recvLong())
        f.close()
    return 'Receive Successful'

def put(name): # Put file from client on the sever
    message = ''
    with open(name, 'rb') as f:
        for data in f:
            message += str(data)
        f.close()
    sendLong(message) 
    return 'Put Successful'

def mget(filenames): # Get multiple files from sever and send to client
    for i in filenames:
        get(i)
    return 'Files Sent Successfully'

def mput(filenames): # Put mulitple files from client on to the sever
    for i in filenames:
        put(i)
    return 'Files Retrieved Successfully'

# send a long string in mulitple packets using stop and wait protocol
def sendLong(message): 
    message = comp_and_encrypt(message)
    mList = createPackets(message)
    s.send(str(len(mList)))
    for i in mList:
        s.send(i)
        s.recv(1024)

# revice a long string in mulitple packets using stop and wait protocol
def recvLong(): 
    num = int(s.recv(1024))
    message = ''
    for i in range(num):
        message += s.recv(1024)
        s.send('ack')
    message = decomp_and_unencrypt(message)
    return message

def createPackets(m): # Split a long string into equal length smaller strings
    packets = []
    pack = ''
    count = 0
    for i in m:
        if count < 1022:
            count += 1
            pack += i
        else:
            packets.append(pack)
            pack = i
            count = 0
    packets.append(pack)
    return packets

def comp_and_encrypt(m): # compress and/or encrypt the string as needed
    if(isCompress):
        m = str(zlib.compress(m))
    if(isEncrypt):
        m = str(encrypt(m))
    return m

def decomp_and_unencrypt(m): # decompress and/or decrypt the string as needed
    if(isEncrypt):
        m = str(decrypt(m))
    if(isCompress):
        m = str(zlib.decompress(m))
    return m

#code ffor encrypt and decrypt comes from the below URL
#http://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
def encrypt(m): # encrypt a string
    key = 'password'
    enc = []
    for i in range(len(m)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(m[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))

def decrypt( m): # decrypt a string
    key = 'password'
    dec = []
    m = base64.urlsafe_b64decode(m)
    for i in range(len(m)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(m[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

# Type in the password but only show ***** as you are typing
# This code is not ours, it is from
# http://stackoverflow.com/questions/7838564/how-to-read-password-with-echo-in-python-console-program
def win_getpass(prompt='Password: ', stream=None):
    """Prompt for password with echo off, using Windows getch()."""
    if sys.stdin is not sys.__stdin__:
        return fallback_getpass(prompt, stream)
    import msvcrt
    for c in prompt:
        msvcrt.putch(c)
    pw = ""
    while 1:
        c = msvcrt.getwch()
        if c == '\r' or c == '\n':
            break
        if c == '\003':
            raise KeyboardInterrupt
        if c == '\b':
            if pw == '':
                pass
            else:
                pw = pw[:-1]
                msvcrt.putch('\b')
                msvcrt.putch(" ")
                msvcrt.putch('\b')
        else:
            pw = pw + c
            msvcrt.putch("*")
    msvcrt.putch('\r')
    msvcrt.putch('\n')
    return pw
#********************************************************************


#Main
s = socket.socket()        
#host = socket.gethostbyname(socket.gethostname())
port = 0
while True: # user must enter the correct port number and IP Addres
   try:
      host = str(raw_input('Enter the IP Address: '))
      port = int(raw_input('Enter Port: '))
      break
   except ValueError:
      print 'You Must enter an integer'

s.connect((host, port)) # establish connection 
print 'Connection achieved on host ', host, 'port', port

# Password entrie
password = False
while not password:
    #command works!!! but only in the command line
    #http://stackoverflow.com/questions/7838564/how-to-read-password-with-echo-in-python-console-program
    command = win_getpass()
    #command = raw_input("Please enter the password for the server: ")
    s.sendall(command)
    p = s.recv(1024)
        
    if p == 'y':
        password = True
    else:
        print 'Password was incorrect please try again.'

# Start File Trasfer Protocol
print 'For help type the command \'help\''
done = False
while not done:
    
    command = raw_input(">>> ") # input command
                
    lsCom = command.split(' ') # seperate components of the command
    # Don't send the command until it is verified
            #this way we don't waste time sending incorrect commands
    if(lsCom[0] == 'ls'):
        s.send(command)
        print ls()
    elif(lsCom[0] == 'dir'):
        s.send(command)
        print ls()
    elif(lsCom[0] == 'cd'):
        s.send(command)
        print cd()
    elif(lsCom[0] == 'get'):
        s.send(command)
        print get(lsCom[1])
    elif(lsCom[0] == 'put'):
        if len(lsCom) == 2:
            s.send(command)
            print put(lsCom[1])
        else:
            print "Invalid call to ls"
    elif(lsCom[0] == 'mget'):
        s.send(command)
        print mget(lsCom[1:])
    elif(lsCom[0] == 'mput'):
        s.send(command)
        print mput(lsCom[1:])
    elif(lsCom[0] == 'binary'):
        s.send(command)
        isBinary = True
        print 'Using Binary format'
    elif(lsCom[0] == 'compress'):
        s.send(command)
        if isCompress:
            isCompress = False
            print 'Compression OFF'
        else:
            isCompress = True
            print 'Compression ON'
    elif(lsCom[0] == 'encrypt'):
        s.send(command)
        if isEncrypt:
            isEncrypt = False
            print 'Encryption OFF'
        else:
            isEncrypt = True
            print 'Encryption ON'
    elif(lsCom[0] == 'help'):
        print '*************HELP MENU*************'
        print 'Avalible commands:'
        print 'ls\t- List all of the objects in the current directory'
        print 'dir\t- List all of the objects in the current directory.'
        print 'cd\t- Change the directory to the specified.'
        print 'get\t- Copy a file from the server and place it on your computer.'
        print 'put\t- Copy a file from your computer and give it to the server.'
        print 'mget\t- Copy multiple files from the server and place them on your computer.'
        print 'mput\t- Copy multiple files from your computer and give them to the server.'
        print 'binary\t- Change the file format to binary.'
        print 'compress- Toggle the use of compression when sending the files.'
        print 'encrypt\t- Toggle the use of encryption when sending files.'
        print 'help\t- Open this help menu'
        print 'quit\t- Quit this program'
        print '***********************************'
    elif(lsCom[0] == 'quit'):
        s.send(command)
        done = True
    else:
        print 'Error: Invalid command'
print 'quitting...'
s.close()
