import socket as soc

# Connect to server.
size = 1024
recvData = 0
serverAddress = ('localhost', 9001)
sock = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
sock.connect(serverAddress)
sock.send('hello world')
recvData = sock.recv(size)

# except socket.error as error:
#     print(travelplan.name + ': error: ' + error.strerror)
#     sys.exit(1)
# else:
#     print('Connected to server %s at %s.' % serverAddress)
#     sock.close()
