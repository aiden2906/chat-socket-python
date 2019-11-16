from tkinter import *
from socket import *
from threading import *
from tkinter.scrolledtext import*
from tkinter import filedialog
import os 
# import mysql.connectorr
from PIL import Image, ImageTk

class Receive():
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
          gettext.insert(END,'%s >> %s\n\n'%(name,text.decode()))
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
          gettext.insert(END,'You receive file %s from %s\n\n'%(filename.decode(),name))
          gettext.configure(state='disabled')
          f.close()
        except:
          return

def reset_tabstop(event):
  event.widget.configure(tabs=(event.width-8, "right"))

class App(Thread):
  def connecting(self,ipaddress):
    self.client = socket()
    self.client.connect((ipaddress, 10101))
    
  def __init__(self, master,ipaddress):
    Thread.__init__(self)
    self.root=master
    # self.connecting(ipaddress)
    # mydb = mysql.connector.connect(
    #   host="localhost",
    #   user="root",
    #   passwd="",
    #   database="ChatAppDB"
    # )
    # mycursor = mydb.cursor()
    # mycursor.execute("SELECT * FROM user")
    # myresult = mycursor.fetchall()
    # for x in myresult:
    #   if x[0]==ipaddress:
    #     self.name=x[1]
    #     break

  def Send(self,args=None):
    self.gettext.configure(state='normal')
    text = "?"+self.sendtext.get()
    if text=="?": return
    self.gettext.insert(END,'\t%s\n\n'%text[1:])
    self.sendtext.delete(0,END)
    self.client.send(text.encode())
    self.sendtext.focus_set()
    self.gettext.configure(state='disabled')
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
      self.client.send(l.encode())
      l=f.read(64000)
      if not l:
        break
    self.gettext.configure(state='normal')
    self.gettext.insert(END,'\tYou sent file %s to %s\n\n'%(filename,self.name))
    self.gettext.configure(state='disabled')
    f.close()

  def run(self):
    try:
      frame = Frame(self.root)
      frame.pack()
      self.gettext = ScrolledText(frame, height=18,width=55)
      self.gettext.bind("<Configure>",reset_tabstop)
      self.gettext.pack()
      self.gettext.configure(state='disabled')
      sframe = Frame(frame)
      sframe.pack(anchor='w')
      self.pro = Label(sframe, text="  ")
      self.pro1 = Label(sframe, text="  ")
      self.sendtext = Entry(sframe,width=41)
      self.sendtext.focus_set()
      self.sendtext.bind(sequence="<Return>", func=self.Send)
      icon=ImageTk.PhotoImage(Image.open("clip1.png"))
      self.sendfile = Button(sframe,image=icon,width=35,height=35,command=self.send_file)
      self.sendfile.pack(side=RIGHT)
      self.pro.pack(side=LEFT)
      self.sendtext.pack(side=LEFT)
      Label(sframe,text="  ").pack(side=LEFT)
      icon1=ImageTk.PhotoImage(Image.open("paper-plane.png"))
      self.sendmess = Button(sframe,image=icon1,width=35,height=35,command=self.Send).pack(side=LEFT)
      self.pro1.pack(side=LEFT)
      Receive(self.client, self.gettext,self.name)

    finally:
      print("closing socket")
      self.client.close()
