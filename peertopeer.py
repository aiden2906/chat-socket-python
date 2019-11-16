from tkinter import *
from socket import *
from threading import *
from tkinter.scrolledtext import*
from _thread import *
from tkinter import filedialog
import os 
# import mysql.connector
from PIL import Image, ImageTk

class Receive_client():
  def __init__(self, server, gettext,name):
    #self.server = server
    #self.gettext = gettext
    while 1:
      temp=server.recv(1).decode()
      if temp=="?":
        try:
          text = server.recv(1024)
          if not text: break
          gettext.configure(state='normal')
          gettext.insert(END,'%s >> %s\n\n'%(name,text.decode('utf-8')))
          gettext.configure(state='disabled')
          gettext.see(END)
        except:
          return
      else:
        try:
          dir_path= os.path.dirname(os.path.realpath(__file__))
          lenname=server.recv(3)
          filename=server.recv(int(lenname))
          print(filename.decode())
          f=open(dir_path+"/"+filename.decode(),"w")
          text=server.recv(64000)
          f.write(text.decode())
          gettext.configure(state='normal')
          gettext.insert(END,'You receive file %s from %s\n\n'%(filename.decode('utf-8'),name))
          gettext.configure(state='disabled')
          f.close()
        except:
          return


def reset_tabstop(event):
  event.widget.configure(tabs=(event.width-8, "right"))



def reset_tabstop(event):
  event.widget.configure(tabs=(event.width-8, "right"))


class App_server(Thread):
  def connecting(self,ipaddress):
    self.server = socket(AF_INET,SOCK_STREAM)
    self.server.bind((ipaddress,10101))

  def __init__(self, master,ipaddress):
    Thread.__init__(self)
    self.root=master
    self.connecting(ipaddress)

  def create_frame(self,master,client,name):
    Frame_chat1(master,client,name)

  def close_server(self):
    self.server.shutdown(1)
    self.server.close()
    print("close")

  def run(self):
    self.server.listen(10)
    while True:
        client,addr=self.server.accept()
        print(addr[0])
        mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          passwd="",
          database="ChatAppDB"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM user")
        myresult = mycursor.fetchall()
        for x in myresult:
          if x[0]==addr[0]:
            start_new_thread(self.create_frame,(self.root,client,x[1],))
            break


class Frame_chat1():
  def __init__(self,master,client,name):
    self.client=client
    self.name=name
    root=Toplevel(master)
    frame = Frame(root)
    frame.pack()
    self.gettext = ScrolledText(frame, height=18,width=55, state=NORMAL)
    self.gettext.bind("<Configure>",reset_tabstop)
    self.gettext.pack()
    sframe = Frame(frame)
    sframe.pack(anchor='w')
    self.pro = Label(sframe, text="  ")
    self.sendtext = Entry(sframe,width=41)
    self.sendtext.focus_set()
    self.sendtext.bind(sequence="<Return>", func=self.Send)
    self.pro1 = Label(sframe, text="  ")
    icon=ImageTk.PhotoImage(Image.open("clip1.png"))
    self.sendfile = Button(sframe,image=icon,width=35,height=35,command=self.send_file)
    icon1=ImageTk.PhotoImage(Image.open("paper-plane.png"))
    self.sendmess = Button(sframe,image=icon1,width=35,height=35,command=self.Send)
    self.sendfile.pack(side=RIGHT)
    self.pro.pack(side=LEFT)
    self.sendtext.pack(side=LEFT)
    self.pro1.pack(side=LEFT)
    self.sendmess.pack(side=LEFT)
    Label(sframe,text=" ").pack(side=LEFT)
    self.gettext.configure(state=DISABLED)
    Receive_server(self.client, self.gettext,self.name)

  def Send(self, args=None):
    self.gettext.configure(state=NORMAL)
    text = "?"+self.sendtext.get()
    if text=="?": return
    self.gettext.insert(END,'\t%s\n\n'%text[1:])
    self.sendtext.delete(0,END)
    self.client.send(text.encode('utf-8'))
    self.sendtext.focus_set()
    self.gettext.configure(state=DISABLED)
    self.gettext.see(END)

  def send_file(self,event=None):
    filepath=filedialog.askopenfilename()
    filename=os.path.basename(filepath)
    lenname=len(filename)
    if lenname<10:
      lenname="!00"+str(lenname)
    else:
      lenname="!0"+str(lenname)
    f=open(filepath,"r")
    l=lenname+filename
    while(l):
      self.client.send(l.encode('utf-8'))
      l=f.read(64000)
      if not l:
        break
    self.gettext.configure(state='normal')
    self.gettext.insert(END,'\tYou sent file %s to %s\n\n'%(filename,self.name))
    self.gettext.configure(state='disabled')
    f.close()


class Receive_server():
  def __init__(self, server, gettext,name):
    self.server = server
    self.gettext = gettext
    self.name=name
    while True:
      temp=self.server.recv(1).decode()
      if temp=="?":
        try:
          text = self.server.recv(1024)
          if not text: 
            break
          self.gettext.configure(state=NORMAL)
          self.gettext.insert(END,'%s >> %s\n\n'%(self.name,text.decode('utf-8')))
          self.gettext.configure(state=DISABLED)
          self.gettext.see(END)
        except:
          return
      else:
        try:
          dir_path = os.path.dirname(os.path.realpath(__file__))
          lenname=self.server.recv(3)
          filename=self.server.recv(int(lenname))
          print(filename.decode())
          f=open(dir_path+"/"+filename.decode(),"w")
          text=self.server.recv(64000)
          f.write(text.decode())
          self.gettext.configure(state='normal')
          self.gettext.insert(END,'You receive file %s from %s\n\n'%(filename.decode('utf-8'),self.name))
          self.gettext.configure(state='disabled')
          f.close()
        except:
          return
