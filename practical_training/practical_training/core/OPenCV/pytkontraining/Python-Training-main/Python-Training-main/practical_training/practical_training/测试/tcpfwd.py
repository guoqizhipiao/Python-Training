import socket
import threading
import time

def tcplink(sock,addr):
    print("已连接",addr)
    sock.send("已连接服务器".encode("utf-8"))
    while True:
        try:
            data = sock.recv(1024)
        except:
            break
        if not data:
            break
        if data.decode("utf-8") == "exit":
            sock.send("exit".encode("utf-8"))
            break
        elif data:
            print(data.decode("utf-8"))
            sock.send("已发送".encode("utf-8"))
    sock.close()
    print("已关闭",addr)

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("10.193.56.164",2000))
s.listen(5)
print("等待")
while True:
    sock, addr = s.accept()
    t = threading.Thread(target = tcplink,args = (sock, addr))
    t.start()