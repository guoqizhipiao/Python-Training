import socket
import threading

def jiesou(sock):
    while True:
        data = sock.recv(1024)
        if data.decode("utf-8") == "exit":
            break
        elif data:
            print(data.decode("utf-8"))
    print("接收已退出")

def fashong(sock):
    while True:
        sstr = input()
        if sstr == "exit":
            sock.send(sstr.encode("utf-8"))
            break
        sock.send(sstr.encode("utf-8"))
    print("发送已退出")

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect((("10.193.56.164",2000)))
i = threading.Thread(target = fashong, args=(sock,))
o = threading.Thread(target = jiesou, args=(sock,))
i.start()
o.start()