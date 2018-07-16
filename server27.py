# Servitor
# Lowell Crook, Billy McAllister
# FTP Project Fall 2016
# Server code

import socket
import os
import sys
import zlib
import base64

# set the default directory.
#os.chdir("C:\\")
os.chdir("C:\\Users\\Lowell\\Documents")

# Keep track of our sending and reciving formats
global isBinary
isBinary = True
global isCompress
isCompress = False
global isEncrypt
isEncrypt = False 

def ls(): # list the avalible directories
   data = os.listdir(os.getcwd())
   for item in data:
      c.send(item)
      c.recv(1024)
   c.send("\\last/")
   
def cd(changeTo): # change the currents working directory
   os.chdir(changeTo)
   c.send(os.getcwd())

def get(name): # Get file from sever and send to client
   message = ''
   with open(name, 'rb') as f:
      for data in f:
         message += str(data)
      f.close
   sendLong(message)
   return 'File sent successfully'

def put(name): # Put file from client on the sever
   fileName = name.split('\\')
   with open(fileName[-1], 'wb') as f:
      f.write(recvLong())
      f.close()        
   return 'Receive Successful'

def mget(fileNames): # Get multiple files from sever and send to client
   for n in fileNames:
      get(n)
   return 'Files sent Successfully'

def mput(fileNames): # Put mulitple files from client on to the sever
   for n in fileNames:
      put(n)
   return 'Files recived Successfully'

# send a long string in mulitple packets using stop and wait protocol
def sendLong(message): 
   message = comp_and_encrypt(message)
   mList = createPackets(message)
   c.send(str(len(mList)))
   for i in mList:
      c.send(i)
      c.recv(1024)

# revice a long string in mulitple packets using stop and wait protocol
def recvLong(): 
   num = int(c.recv(1024))
   message = ''
   for i in range(num):
      message += c.recv(1024)
      c.send('ack')
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
# We got this code for encryption and decryption from
# http://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
def encrypt(m): # encrypt a string 
   enc = []
   key = 'password'
   for i in range(len(m)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(m[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
   return base64.urlsafe_b64encode("".join(enc))
def decrypt(m): # decrypt a string
   dec = []
   key = 'password'
   m = base64.urlsafe_b64decode(m)
   for i in range(len(m)):
      key_c = key[i % len(key)]
      dec_c = chr((256 + ord(m[i]) - ord(key_c)) % 256)
      dec.append(dec_c)
   return "".join(dec)
#********************************************************************


#Main
s = socket.socket()
host = socket.gethostbyname(socket.gethostname())
port = 52
# Find next open port
while True: 
   try:
      s.bind((host, port))
      break
   except:
      port += 1
s.listen(1)
print 'Listening on host ', host, 'port', port
c, addr = s.accept()  # establish connection 
print 'connected to ', c.getpeername()

# Password entrie 
correct = False
while not correct:
   print 'waiting for password'
   password = c.recv(1024)
   if(password == "bjm1421@jagmail.southalabama.edu"):
      print 'password was correct'
      c.send('y')
      correct = True
   else:
      print 'password was incorrect'
      c.send('n')


# Start File Trasfer Protocol
done = False
while not done:
   m = c.recv(1024)
   print "Client input: ", m
   command = m.split(' ') # seperate components of the command
   if(command[0] == 'ls'):
      ls()
   elif(command[0] == 'dir'):
      ls()
   elif(command[0] == 'cd'):
      try:
         cd(command[1])
      except IndexError:
         c.send('invalid call to cd')
      except WindowsError:
         c.send('Directory not found')
   elif(command[0] == 'get'):
      try:
         print get(command[1])
      except IndexError:
         c.send('invalid call to get')
      except WindowsError:
         c.send('File not found')
   elif(command[0] == 'put'):
      try:
         print put(command[1])
      except IndexError:
         c.send('invalid call to put')
      except WindowsError:
         c.send('File not found')
   elif(command[0] == 'mget'):
      try:
         print mget(command[1:])
      except IndexError:
         c.send('invalid call to mget')
      except WindowsError:
         c.send('File not found')
   elif(command[0] == 'mput'):
      try:
         print mput(command[1:])
      except IndexError:
         c.send('invalid call to mput')
      except WindowsError:
         c.send('File not found')
        
   elif(command[0] == 'binary'):
      isBinary = True
      print 'Using Binary format'
   elif(command[0] == 'compress'):
      if isCompress:
         isCompress = False
         print 'Compression OFF'
      else:
         isCompress = True
         print 'Compression ON'
   elif(command[0] == 'encrypt'):
      if isEncrypt:
         isEncrypt = False
         print 'Encryption OFF'
      else:
         isEncrypt = True
         print 'Encryption ON'
   elif(command[0] == 'quit'):
      done = True
   else:
      print 'error invalid command'
      
print 'quitting...'
c.close()
