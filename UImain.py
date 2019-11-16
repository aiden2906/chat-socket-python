import tkinter as tk
from tkinter import *
from tkinter import messagebox
from socket import *
from threading import *
from _thread import *
from tkinter.scrolledtext import *
from PIL import Image, ImageTk
import peer
from tkinter import filedialog
from tkinter import ttk
import time

# GLOBAL VARIABLE ==================================
IPSERVER_GLOBAL = ""
APPSERVER_GLOBAL = None
LIST_GLOBAL=None
def reset_tabstop(event):
    event.widget.configure(tabs=(event.width-8, "right"))
def UploadAction(event=None):
    filename = filedialog.askopenfilename()
    print('Selected:', filename)


def raise_frame(frame):
    frame.tkraise()

def CheckIPServer(ipserver):
    global IPSERVER_GLOBAL          
    IPSERVER_GLOBAL = str(ipserver)     #Gán địa chỉ IP Server vào biến toàn cục
    result = peer.ConnectToServer(IPSERVER_GLOBAL,50000)
    if result==True:
        raise_frame(MAIN_SCREEN)
    else:
        messagebox.showerror("Connect to server", "The IP Address entered is not correct! Please again!")

def CheckRegister(loginname, loginpass, username):
    result = peer.Register(IPSERVER_GLOBAL, 50000, loginname, loginpass, username)
    if result==True:
        messagebox.showinfo("Register", "Register successful!")
        raise_frame(MAIN_SCREEN)
    else:
        messagebox.showerror("Register", "Register failed! Please again!")

def CheckLogin(loginname, loginpass):
    print(IPSERVER_GLOBAL)
    result = peer.Login(IPSERVER_GLOBAL, 50000, loginname, loginpass)
    print("UImain- CheckLogin(): result=",result)
    if result==True:
        ipfriend = peer.GetFriendIP(str(loginname))
        appServer = peer.App(FRIEND_SCREEN,ipfriend)
        appServer.start()
        raise_frame(FRIEND_SCREEN)
        print("UImain- CheckLogin(): ipfriend=", ipfriend)
        start_new_thread(request_list_friend,(1,))

    else:
        messagebox.showerror("Login", "Login failed! Please again!")

# nhận list sau mỗi 3 giây
def request_list_friend(en):
    global LIST_GLOBAL
    while True:
        list_temp=peer.RequestListFriend(IPSERVER_GLOBAL,50000)
        if list_temp!=LIST_GLOBAL:
            LIST_GLOBAL=list(list_temp)
            if list_temp!=None:
                for x in LIST_GLOBAL:
                    if x==entryname.get():
                        list_temp.remove(x)
                        break
                while (len(list_temp)<5):
                    list_temp=list_temp+[""]
                button1.config(text=list_temp[0])
                button2.config(text=list_temp[1])
                button3.config(text=list_temp[2])
                button4.config(text=list_temp[3])
                button5.config(text=list_temp[4])
                button1.config(command=lambda:CheckToFriend(button1['text']))
                button2.config(command=lambda:CheckToFriend(button2['text']))
                button3.config(command=lambda:CheckToFriend(button3['text']))
                button4.config(command=lambda:CheckToFriend(button4['text']))
                button5.config(command=lambda:CheckToFriend(button5['text']))
                button1.place(in_=bgLbl_Reg1, relx=0.5, rely=0.5, anchor=CENTER)
                button2.place(in_=bgLbl_Reg1, relx=0.5, rely=0.56, anchor=CENTER)
                button3.place(in_=bgLbl_Reg1, relx=0.5, rely=0.62, anchor=CENTER)
                button4.place(in_=bgLbl_Reg1, relx=0.5, rely=0.68, anchor=CENTER)
                button5.place(in_=bgLbl_Reg1, relx=0.5, rely=0.74, anchor=CENTER)
                for x in list_btn:
                    if x['text']=="":
                        x.place(in_=bgLbl_Reg1, relx=-0.5, rely=0.95, anchor=CENTER)
        time.sleep(1)

def exit_app(name):
    peer.request_exit_app(IPSERVER_GLOBAL,50000,name)
    raise_frame(LOGIN_SCREEN)


def ConnectToFriend(username):
    pass 

def CheckToFriend(friendLogName):
    result = peer.FindFriend(IPSERVER_GLOBAL, 50000, friendLogName)
    if result == None:
        messagebox.showerror("Check friends", "This name is not exist!")
    elif result == False:
        messagebox.showwarning("Check friends", "This friend is offline!")
    else:
        print(result)
        messagebox.showinfo("Check friends", "This friend is online!")
        rootclient=tk.Toplevel(FRIEND_SCREEN)
        app = peer.App_client(rootclient,result,friendLogName)
        app.start()


######  CHẠY CÁC FRAME =======================================================================================

root = tk.Tk()

IP_SCREEN = tk.Frame(root)
IP_SCREEN.master.title("Chatapp1.0")

MAIN_SCREEN = tk.Frame(root)
MAIN_SCREEN.master.title("Chatapp1.0")

REG_SCREEN = tk.Frame(root)
REG_SCREEN.master.title("Chatapp1.0")

LOGIN_SCREEN = tk.Frame(root)
LOGIN_SCREEN.master.title("Chatapp1.0")

FRIEND_SCREEN = tk.Frame(root)
FRIEND_SCREEN.master.title("Chatapp1.0")

for frame in (IP_SCREEN, MAIN_SCREEN, REG_SCREEN, LOGIN_SCREEN, FRIEND_SCREEN):
    frame.grid(row=0, column=0, sticky='news')


# IP_SCREEN
bg_img_ip = ImageTk.PhotoImage(Image.open("bg_IpScreen.png"))
w = bg_img_ip.width()
h = bg_img_ip.height()
bgLabel_IP = tk.Label(IP_SCREEN, image=bg_img_ip,justify=CENTER, width=w, height=h)
bgLabel_IP.pack(fill='both')
IP_SCREEN.master.minsize(w, h)
tk.Label(IP_SCREEN, text="ServerIP:", bg="#182B55", fg="white",font="18").place(in_=bgLabel_IP, relx=0.25, rely=0.45, anchor=CENTER)
entryServerIP = tk.Entry(IP_SCREEN, width=23, font=(18))
entryServerIP.place(in_=bgLabel_IP, relx=0.55, rely=0.45, anchor=CENTER)
tk.Button(IP_SCREEN, text="Connect", height="2", width="12", command= lambda: CheckIPServer(str(entryServerIP.get())), bg="#182B55", fg="white").place( relx=0.5, rely=0.55, anchor=CENTER)


# MAIN_SCREEN
bg_img = ImageTk.PhotoImage(Image.open("bgApp.png"))
w = bg_img.width()
h = bg_img.height()
bgLabel_Main = tk.Label(MAIN_SCREEN, image=bg_img, justify=CENTER, width=w, height=h)
bgLabel_Main.pack(fill='both')
MAIN_SCREEN.master.minsize(w, h)
tk.Button(MAIN_SCREEN, text="Login", height="2", width="12", command=lambda: raise_frame(LOGIN_SCREEN),bg="#182B55", fg="white").place(in_=bgLabel_Main, relx=0.5, rely=0.65, anchor=CENTER)
tk.Button(MAIN_SCREEN, text="Register", height="2", width="12", command=lambda: raise_frame(REG_SCREEN), bg="#182B55", fg="white").place(in_=bgLabel_Main, relx=0.5, rely=0.75, anchor=CENTER)


# LOGIN_SCREEN
bgLabel_Login = tk.Label(LOGIN_SCREEN, image=bg_img,justify=CENTER, width=w, height=h)
bgLabel_Login.pack(fill='both')
tk.Label(LOGIN_SCREEN, text="LoginName :", bg="#182B55", fg="white",font="18").place(in_=bgLabel_Login, relx=0.25, rely=0.62, anchor=CENTER)
entryname = tk.Entry(LOGIN_SCREEN, width=23, font=(18))
entryname.place(in_=bgLabel_Login, relx=0.65, rely=0.62, anchor=CENTER)
tk.Label(LOGIN_SCREEN, text="Password :", bg="#182B55", fg="white", font=(18)).place(in_=bgLabel_Login, relx=0.25, rely=0.68, anchor=CENTER)
entrypass = tk.Entry(LOGIN_SCREEN, width=23, show="*", font=(18))
entrypass.place(in_=bgLabel_Login, relx=0.65, rely=0.68, anchor=CENTER)
icon2 = ImageTk.PhotoImage(Image.open("house.png"))
icon1 = ImageTk.PhotoImage(Image.open("login.png"))
tk.Button(LOGIN_SCREEN, compound=LEFT, image=icon1, text="Log In", command=lambda: CheckLogin( entryname.get(), entrypass.get()), border="2",bg="#182B55", fg="white").place(in_=bgLabel_Login, relx=0.33, rely=0.77, anchor=CENTER)
tk.Button(LOGIN_SCREEN, compound=LEFT, image=icon2, text="Back", command=lambda: raise_frame(MAIN_SCREEN),border="2", bg="#182B55", fg="white").place(in_=bgLabel_Login, relx=0.67, rely=0.77, anchor=CENTER)


# REGISTER_SCREEN
bgLbl_Reg = tk.Label(REG_SCREEN, image=bg_img, justify=CENTER, width=w, height=h)
bgLbl_Reg.pack(fill='both')
tk.Label(REG_SCREEN, text="Please enter details below", bg="#182B55", fg="white",font=(19)).place(in_=bgLbl_Reg, relx=0.5, rely=0.6, anchor=CENTER)
tk.Label(REG_SCREEN, text="UserName * ", bg="#182B55", fg="white", font=(18)).place(in_=bgLbl_Reg, relx=0.25, rely=0.65, anchor=CENTER)
entryUserName = tk.Entry(REG_SCREEN, width=23, font=(18))
entryUserName.place(in_=bgLbl_Reg,relx=0.65, rely=0.65, anchor=CENTER)
tk.Label(REG_SCREEN, text="LoginName * ", bg="#182B55", fg="white", font=(18)).place(in_=bgLbl_Reg, relx=0.25, rely=0.7, anchor=CENTER)
entryLoginName = tk.Entry(REG_SCREEN, width=23, font=(18))
entryLoginName.place(in_=bgLbl_Reg,relx=0.65, rely=0.7, anchor=CENTER)
tk.Label(REG_SCREEN, text="Password * ", bg="#182B55", fg="white", font=(18) ).place(in_=bgLbl_Reg, relx=0.25, rely=0.75, anchor=CENTER)
entryLoginPass = tk.Entry(REG_SCREEN, width=23, show="*", font=(18))
entryLoginPass.place(in_=bgLbl_Reg, relx=0.65, rely=0.75, anchor=CENTER)
icon3 = ImageTk.PhotoImage(Image.open("notes.png"))
tk.Button(REG_SCREEN, compound=LEFT, image=icon3, text="Register", command=lambda: CheckRegister(entryLoginName.get(), entryLoginPass.get(),entryUserName.get()), bg="#182B55", fg="white").place(in_=bgLbl_Reg, relx=0.33, rely=0.82, anchor=CENTER)
tk.Button(REG_SCREEN, compound=LEFT, image=icon2, text="Back", command=lambda: raise_frame(MAIN_SCREEN), bg="#182B55", fg="white").place(in_=bgLbl_Reg, relx=0.67, rely=0.82, anchor=CENTER)

# FRIEND_SCREEN

UI_friendscreen= ImageTk.PhotoImage(Image.open('bg_frscreen.png'))
bgLbl_Reg1 = tk.Label(FRIEND_SCREEN, image=UI_friendscreen, justify=CENTER, width=w, height=h)
bgLbl_Reg1.pack(fill='both')
back_icon=ImageTk.PhotoImage(Image.open("back.png"))
chat_icon=ImageTk.PhotoImage(Image.open("bubble.png"))
tk.Button(FRIEND_SCREEN,compound=LEFT,image=back_icon,text="back",command=lambda:exit_app(entryname.get()),bg="#182B55",fg="white").place(in_=bgLbl_Reg1, relx=0.5, rely=0.95, anchor=CENTER)
button1=tk.Button(FRIEND_SCREEN,width=150,bg="#182B55",fg="white",compound=RIGHT,image=chat_icon)
button2=tk.Button(FRIEND_SCREEN,width=150,bg="#182B55",fg="white",compound=RIGHT,image=chat_icon)
button3=tk.Button(FRIEND_SCREEN,width=150,bg="#182B55",fg="white",compound=RIGHT,image=chat_icon)
button4=tk.Button(FRIEND_SCREEN,width=150,bg="#182B55",fg="white",compound=RIGHT,image=chat_icon)
button5=tk.Button(FRIEND_SCREEN,width=150,bg="#182B55",fg="white",compound=RIGHT,image=chat_icon)
list_btn=[button1,button2,button3,button4,button5]
raise_frame(IP_SCREEN)
root.mainloop()
FRIEND_SCREEN.mainloop()
