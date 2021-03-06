import socket
import select




serversIP = ["192.168.0.101", "192.168.0.102", "192.168.0.103"]

serversSockets = []
clientsOpenedSockets = []

requestsQueue = []

isServerAvailable = {}
handledConnections = {}


def peekServer(serversList, msg):
    if msg[0] == "P" or msg[0] == "V":
        for s in serversList[0:2]:
            if isServerAvailable[s]:
                # print(msg, " to ", s.getpeername())
                return s

    if (msg[0] == "M"):
        if isServerAvailable[serversList[2]]:
            # print(msg, " to ", serversList[2].getpeername())
            return serversList[2]

    # default case - choose someone
    for s in serversList:
        if isServerAvailable[s]:
            # print(msg, " to ", s.getpeername())
            return s

    # all servers are busy
    return None


# connectiong to servers
for ip in serversIP:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, 80)
    print('connecting to %s port %s' % server_address)
    sock.connect(server_address)
    serversSockets.append(sock)
    isServerAvailable[sock] = True

# wait for clients
# Create a TCP/IP socket
listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
server_address = ('10.0.0.1', 80)
print ('starting up on %s port %s' % server_address)
listeningSock.bind(server_address)
# Listen for incoming connections
listeningSock.listen(1)

while True:

    readable, writable, _ = select.select(serversSockets + clientsOpenedSockets + [listeningSock], serversSockets, [])

    # transfer response to clients
    for read in readable:
        if read is listeningSock:
            # add new connection to list
            connectionToClient, client_address = listeningSock.accept()
            # connectionToClient.setblocking(0)
            clientsOpenedSockets.append(connectionToClient)
        elif read in clientsOpenedSockets:
            # recieve request and store it in queue
            data = connectionToClient.recv(2)
            if data:
                requestsQueue.append((read, data))
            # else:
            #     if s in outputs:
            #         outputs.remove(s)
            #     inputs.remove(s)
            #     s.close()
            #     del message_queues[s]
        else: #server socket
            # send response to client
            dataResponse = read.recv(2)
            returnTo = handledConnections[read]
            returnTo.send(dataResponse)

            # print("server ", read.getpeername(), " free")
            # notify that server is enable
            isServerAvailable[read] = True
            # remove connection and close it
            clientsOpenedSockets.remove(returnTo)
            returnTo.close()

    if (writable):
        if (requestsQueue):
            # get next request
            connection, msg = requestsQueue[0]

            # need to choose wisely the server to send to
            connectionToServer = peekServer(serversSockets, msg)

            #send meassage from queue
            if (connectionToServer is not None):
                # remove next request from queue
                requestsQueue.remove((connection, msg))

                print("forward %s from: %s to server: %s" % (msg, connection.getpeername(), connectionToServer.getpeername()))

                # handle request
                handledConnections[connectionToServer] = connection
                isServerAvailable[connectionToServer] = False
                connectionToServer.send(msg)
