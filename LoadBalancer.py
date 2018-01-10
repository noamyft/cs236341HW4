import socket
import select

openConnections = {}

serversIP = ["192.168.0.101", "192.168.0.102", "192.168.0.103"]

serversSockets = []

# connectiong to servers
for ip in serversIP:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, 80)
    print('connecting to %s port %s' % server_address)
    sock.connect(server_address)
    serversSockets.append(sock)

# wait for clients
# Create a TCP/IP socket
clientsSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('10.0.0.1', 80)
print ('starting up on %s port %s' % server_address)
clientsSock.bind(server_address)

# Listen for incoming connections
clientsSock.listen(1)

while True:
    # Wait for a connection
    print ( 'waiting for a connection')
    connectionToClient, client_address = clientsSock.accept()

    # print('connection from', client_address)
    data = connectionToClient.recv(2)
    # print('received "%s"' % data)
    readable, writable, _ = select.select(serversSockets, serversSockets, [])


    if not writable:
        # need to choose wisely the server to send to
        connectionToServer = writable[0]

        # send request to server
        # print ('sending "%s" to %s' % (data, connectionToServer.getpeername()))
        connectionToServer.setblocking(0)
        connectionToServer.send(data)

        openConnections[connectionToServer] = connectionToClient

    # transfer response to clients
    for readServer in readable:
        dataResponse = readServer.recv(2)
        returnTo = openConnections[readServer]
        returnTo.setblocking(0)
        returnTo.send(dataResponse)

        print ("forward ", data, " from: ", returnTo.getpeername(), " to server: ", readServer.getpeername())

        returnTo.close()
