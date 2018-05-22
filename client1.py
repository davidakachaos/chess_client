# Python TCP Client A
import socket
from socket import SHUT_RDWR
import pickle

host = "127.0.0.1" # socket.gethostname()
port = 2004
BUFFER_SIZE = 2000
MESSAGE = "uid" + input("Enter UID:")

tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClientA.connect((host, port))

# while MESSAGE != 'exit':
tcpClientA.send(MESSAGE.encode("utf8"))
data = tcpClientA.recv(BUFFER_SIZE)
player = pickle.loads(data)
print(" player?:", player)

# Close the connection to the server
# tcpClientA.send("exit".encode("utf8"))
tcpClientA.shutdown(SHUT_RDWR)
tcpClientA.close()
