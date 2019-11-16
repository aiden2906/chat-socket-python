from tkinter import *
from socket import *
from threading import *
from tkinter.scrolledtext import*
from _thread import *
from tkinter import filedialog
import os
from PIL import Image, ImageTk

IPSERVER = ''
# nhận request lấy danh sách friend để hiển thị
def RequestListFriend(ipserver,serverPort):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((ipserver, serverPort))
    message = "GetListFriend()"+"#"
    clientSocket.sendall(message.encode('utf-8'))
    replyFromServer=clientSocket.recv(2048).decode('utf-8')
    clientSocket.close()
    listReply=replyFromServer.split('#')
    if listReply[0]=='OK,ListFriendIsReady!':
        return listReply[1:]
    else:
        return None

def request_exit_app(ipserver,serverPort,name):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((ipserver, serverPort))
    message = "ExitApp()"+"#"+name+"#"
    clientSocket.sendall(message.encode('utf-8'))
    replyFromServer=clientSocket.recv(2048).decode('utf-8')
    clientSocket.close()

def ConnectToServer(ipserver, serverPort):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((ipserver, serverPort))
    message = "ConnectToServer()"+"#"
    clientSocket.sendall(message.encode('utf-8'))
    replyFromServer = (clientSocket.recv(2048)).decode(
        'utf-8')  # Nhận từ server
    clientSocket.close()
    if replyFromServer == "OK,Connected!":
        return True
    else:
        return False


def Register(ipserver, serverPort, loginName, loginPass, userName):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((ipserver, serverPort))
    message = "Register()#"+str(loginName)+"#"+str(loginPass)+"#"+str(userName)+"#"
    clientSocket.sendall(message.encode('utf-8'))
    replyFromServer = (clientSocket.recv(2048)).decode(
        'utf-8')  # Nhận từ server
    clientSocket.close()
    print("replyFromServer: ", replyFromServer)
    if replyFromServer == "OK,Register!":
        return True
    else:
        return False


def Login(ipserver, serverPort, loginName, loginPass):
    global IPSERVER
    IPSERVER = ipserver
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((ipserver, serverPort))
    message = "Login()#"+str(loginName)+"#"+str(loginPass)+"#"
    clientSocket.sendall(message.encode('utf-8'))
    replyFromServer = (clientSocket.recv(2048)).decode(
        'utf-8')  # Nhận từ server
    clientSocket.close()
    print("replyFromServer: ", replyFromServer)
    print("peerloginName: ", loginName)
    print("peerloginPass: ", loginPass)
    if replyFromServer == "OK,Login!":
        return True
    else:
        return False


def FindFriend(ipserver, serverPort, friendlogname):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((ipserver, serverPort))
    message = "FindFriend()#"+friendlogname+"#"
    print(message)
    clientSocket.sendall(message.encode('utf-8'))
    replyFromServer = (clientSocket.recv(2048)).decode('utf-8')
    print(replyFromServer)  # Nhận từ server
    # phan giai message thanh 2 phan: message + ipfriend
    listReply = replyFromServer.split("#")
    clientSocket.close()
    print(replyFromServer)
    if listReply[0] == "OK,FriendOnline!":
        return str(listReply[1])   # return IPFRIEND
    elif listReply[0] == "OK,FriendOffline!":
        return False
    else:
        return None


def GetFriendName(ipfriend):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((IPSERVER, 50000))
    message = "GetFriendName()#"+str(ipfriend)+"#"
    print("PEER-GetFriendName() message:", message)
    clientSocket.sendall(message.encode('utf-8'))
    replyFromServer = (clientSocket.recv(2048)).decode(
        'utf-8')  # Nhận từ server
    clientSocket.close()
    print("PEER-GetFriendName() replyFromServer:", replyFromServer)
    if replyFromServer == "Fail,NotFound!":
        return None
    else:
        return str(replyFromServer)


def GetFriendIP(friendlogname):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((IPSERVER, 50000))
    message = "GetFriendIP()#"+str(friendlogname)+"#"
    clientSocket.sendall(message.encode('utf-8'))
    replyFromServer = clientSocket.recv(2048).decode('utf-8')  # Nhận từ server
    print("PEER-GetFriendIP() replyFromServer:", replyFromServer)
    clientSocket.close()
    if replyFromServer == "Fail,NotFound!":
        return None
    else:  # ipfriend
        return str(replyFromServer)


# ==================== KẾT NỐI TỚI PEER KHÁC ==============================================

# ===================== NHẬN MESSAGE VÀ FILE TỪ PEER KHÁC ===================================


def reset_tabstop(event):
    event.widget.configure(tabs=(event.width-8, "right"))


class App(Thread):

    def __init__(self, master, ipaddress):
        Thread.__init__(self)
        self.root = master
        self.connecting(ipaddress)

    def connecting(self, ipaddress):
        self.server = socket(AF_INET, SOCK_STREAM)
        ######
        # + len(self.frlogname)  ############# de cho khac cong
        TEMP_PORT = 50001
        self.server.bind((ipaddress, TEMP_PORT))

    def create_frame(self, master, client, name):
        Frame_chat1(master, client, name)

    def close_server(self):
        self.server.shutdown(1)
        self.server.close()
        print("close")

    def run(self):
        self.server.listen(10)
        while True:
            client, addr = self.server.accept()
            print("APP(class): address=", addr[0])
            frlogname = GetFriendName(str(addr[0]))
            print("APP(class): peername=", frlogname)
            start_new_thread(self.create_frame,
                             (self.root, client, frlogname,))

# Frame chat hiển thị bên peer của mình


class App_client(Thread):
    def __init__(self, master, ipaddress, friendlogname):
        Thread.__init__(self)
        self.root = master
        self.frlogname = friendlogname
        self.connecting(ipaddress)

    def connecting(self, ipaddress):
        self.client = socket()
        # + len(self.frlogname)  ############# de cho khac cong
        TEMP_PORT = 50001
        self.client.connect((ipaddress, TEMP_PORT))

    def Send(self, args=None):
        self.gettext.configure(state='normal')
        text = "?"+self.sendtext.get()
        if text == "?":
            return
        self.gettext.insert(END, '\t%s\n\n' % text[1:])
        self.sendtext.delete(0, END)
        self.client.send(text.encode('utf-8'))
        self.sendtext.focus_set()
        self.gettext.configure(state='disabled')
        self.gettext.see(END)

    def send_file(self, event=None):
        filepath = filedialog.askopenfilename()
        filename = os.path.basename(filepath)
        lenname = len(filename)
        if lenname < 10:
            lenname = "!00"+str(lenname)
        else:
            lenname = "!0"+str(lenname)
        f = open(filepath, "r")
        l = lenname+filename
        while(l):
            self.client.send(l.encode('utf-8'))
            l = f.read(64000)
            if not l:
                break
        self.gettext.configure(state='normal')
        self.gettext.insert(END, '\tYou sent file %s to %s\n\n' %
                            (filename, self.frlogname))
        self.gettext.configure(state='disabled')
        f.close()

    def run(self):
        try:
            frame = Frame(self.root,bg="#363636")
            frame.master.title(self.frlogname.upper())
            frame.pack()
            self.gettext = ScrolledText(frame, height=18, width=55,bg="#363636",fg="white")
            self.gettext.bind("<Configure>", reset_tabstop)
            self.gettext.pack()
            self.gettext.configure(state='disabled')
            sframe = Frame(frame,bg='#363636')
            sframe.pack(anchor='w')
            self.pro = Label(sframe, text="  ",bg='#363636')
            self.pro1 = Label(sframe, text="  ",bg='#363636')
            self.sendtext = Entry(sframe, width=41)
            self.sendtext.focus_set()
            self.sendtext.bind(sequence="<Return>", func=self.Send)
            icon = ImageTk.PhotoImage(Image.open("clip1.png"))
            self.sendfile = Button(
                sframe, image=icon, width=35, height=35, command=self.send_file,bg="#363636")
            self.sendfile.pack(side=RIGHT)
            self.pro.pack(side=LEFT)
            self.sendtext.pack(side=LEFT)
            Label(sframe, text="  ",bg='#363636').pack(side=LEFT)
            icon1 = ImageTk.PhotoImage(Image.open("paper-plane.png"))
            self.sendmess = Button(
                sframe, image=icon1, width=35, height=35, command=self.Send,bg="#363636").pack(side=LEFT)
            self.pro1.pack(side=LEFT)
            Receive_client(self.client, self.gettext, self.frlogname)
        finally:
            print("closing socket")
            self.client.close()

class Frame_chat1():
    def __init__(self, master, client, name):
        self.client = client
        self.name = name
        root = Toplevel(master)
        frame = Frame(root,bg="#363636")
        frame.master.title(name.upper())
        frame.pack()
        self.gettext = ScrolledText(frame, height=18, width=55,bg="#363636",fg="white", state=NORMAL)
        self.gettext.bind("<Configure>", reset_tabstop)
        self.gettext.pack()
        sframe = Frame(frame,bg="#363636")
        sframe.pack(anchor='w')
        self.pro = Label(sframe, text="  ",bg="#363636")
        self.sendtext = Entry(sframe, width=41)
        self.sendtext.focus_set()
        self.sendtext.bind(sequence="<Return>", func=self.Send)
        self.pro1 = Label(sframe, text="  ",bg="#363636")
        icon = ImageTk.PhotoImage(Image.open("clip1.png"))
        self.sendfile = Button(sframe, image=icon, width=35,
                               height=35, command=self.send_file,bg="#363636")
        icon1 = ImageTk.PhotoImage(Image.open("paper-plane.png"))
        self.sendmess = Button(sframe, image=icon1,
                               width=35, height=35, command=self.Send,bg="#363636")
        self.sendfile.pack(side=RIGHT)
        self.pro.pack(side=LEFT)
        self.sendtext.pack(side=LEFT)
        self.pro1.pack(side=LEFT)
        self.sendmess.pack(side=LEFT)
        Label(sframe, text=" ",bg="#363636").pack(side=LEFT)
        self.gettext.configure(state=DISABLED)
        Receive_client(self.client, self.gettext, self.name)

    def Send(self, args=None):
        self.gettext.configure(state=NORMAL)
        text = "?"+self.sendtext.get()
        if text == "?":
            return
        self.gettext.insert(END, '\t%s\n\n' % text[1:])
        self.sendtext.delete(0, END)
        self.client.send(text.encode('utf-8'))
        self.sendtext.focus_set()
        self.gettext.configure(state=DISABLED)
        self.gettext.see(END)

    def send_file(self, event=None):
        filepath = filedialog.askopenfilename()
        filename = os.path.basename(filepath)
        lenname = len(filename)
        if lenname < 10:
            lenname = "!00"+str(lenname)
        else:
            lenname = "!0"+str(lenname)
        f = open(filepath, "r")
        l = lenname+filename
        while(l):
            self.client.send(l.encode('utf-8'))
            l = f.read(64000)
            if not l:
                break
        self.gettext.configure(state='normal')
        self.gettext.insert(END, '\tYou sent file %s to %s\n\n' %
                            (filename, self.name))
        self.gettext.configure(state='disabled')
        f.close()


class Receive_client():
    def __init__(self, server, gettext, name):
        self.server = server
        self.gettext = gettext
        self.name = name
        while 1:
            temp = self.server.recv(1).decode('utf-8')
            if temp == "?":
                try:
                    text = self.server.recv(1024)
                    if not text:
                        break
                    self.gettext.configure(state='normal')
                    self.gettext.insert(END, '%s\n\n' %
                                        (text.decode('utf-8')))
                    self.gettext.configure(state='disabled')
                    self.gettext.see(END)
                except:
                    return
            else:
                try:
                    dir_path = os.path.dirname(os.path.realpath(__file__))
                    lenname = self.server.recv(3)
                    filename = self.server.recv(int(lenname))
                    print(filename.decode('utf-8'))
                    f = open(dir_path+"/"+filename.decode('utf-8'), "w")
                    text = self.server.recv(64000)
                    f.write(text.decode('utf-8'))
                    self.gettext.configure(state='normal')
                    self.gettext.insert(END, 'You receive file %s from %s\n\n' % (
                        filename.decode('utf-8'), self.name))
                    self.gettext.configure(state='disabled')
                    f.close()
                except:
                    return
