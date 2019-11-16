from socket import *
import threading
from pyodbc import *
from flask import request, jsonify

# Global variables
USERNAME = ""               #
LOGIN_NAME = ""
PASSWORD = ""
IP = ""
CLIENTSTATUS = {}  # IP : 0|1
LIST_ONLINING = {}  # IP : {LoginName, UserName}
USERNAME_DICT = {}  # LoginName : {LoginPass , UserName, Status: 0}
USER_LOGIN = {}  # IP LoginName:Password

# @app.route("/get_my_ip", methods=["GET"])
# def get_my_ip():
# return jsonify({'ip': request.remote_addr}), 200

# def getMyIP():   # CÁI NÀY LÀ LẤY IP PUBLIC
#     try:
#         host_name = gethostname()
#         host_ip = gethostbyname(host_name)
#         return str(host_ip)
#     except:
#         print("Unable to get IP")
#         return


def getMyIP():
    s = socket(AF_INET, SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# def GetClient_Ip():
#     return str(jsonify({'ip': request.remote_addr}))


def SetStatus(loginName):
    global USERNAME_DICT
    USERNAME_DICT[loginName]["Status"] = 1


def LoadUser():
    global USERNAME_DICT
    #sqlquery = "SELECT LoginName, LoginPass, UserName FROM dbo.USERINFO"
    conn = connect("Driver={SQL Server Native Client 11.0};"
                   "Server=DESKTOP-29E9I02;"
                   "Database=Assignment1_Network;"
                   "Trusted_Connection=yes;")
    try:
        cursor = conn.cursor()
        # LoginName, LoginPass, UserName
        cursor.execute("SELECT * FROM dbo.USERINFO")
        records = cursor.fetchall()
        if records is not None:
            for row in records:
                logNameTemp = row[0]
                USERNAME_DICT[logNameTemp] = {
                    "LoginPass": row[1], "UserName": row[2], "Status": 0}
            cursor.close()
            print("LOAD USER(): Successful!")
        else:
            print("Nothing")
            cursor.close()
    except Error as error:
        print("LOAD USER(): Failed to read data from data table", error)
    finally:
        if (conn):
            conn.close()
            print("LOAD USER(): The pyodbc connection is closed!\n")


def Register(logName, logPass, userName):
    result = None
    global USERNAME_DICT
    conn = connect("Driver={SQL Server Native Client 11.0};"
                   "Server=DESKTOP-29E9I02;"
                   "Database=Assignment1_Network;"
                   "Trusted_Connection=yes;")
    try:
        cursor = conn.cursor()
        # LoginName, LoginPass, UserName
        cursor.execute(
            "SELECT * FROM dbo.USERINFO WHERE LoginName = '{0}' AND UserName = '{1}' ".format(logName, userName))

        records = cursor.fetchone()
        print("REGISTER() server: records = ", records)
        if records is not None:
            print("REGISTER(): Account existed!")
            result = False
        else:
            cursor.execute("INSERT INTO dbo.USERINFO (LoginName, LoginPass, UserName) VALUES ('{0}', '{1}', '{2}')".format(
                logName, logPass, userName))
            conn.commit()
            USERNAME_DICT[logName] = {
                "LoginPass": logPass, "UserName": userName, "Status": 0}
            print("REGISTER(): Successful!")
            result = True
        cursor.close()
    except Error as error:
        print("REGISTER(): Failed to read data from data table", error)
    finally:
        if (conn):
            conn.close()
            print("REGISTER(): The pyodbc connection is closed!\n")
    return result


def Login(logName, logPass, ip):
    result = None
    #sqlquery = "SELECT LoginName, LoginPass, UserName FROM dbo.USERINFO WHERE LoginName = {0} AND LoginPass =  {1}"
    global LIST_ONLINING
    print("LIST_ONLINING: ",LIST_ONLINING)
    print("USERNAME_DICT:", USERNAME_DICT)
    conn = connect("Driver={SQL Server Native Client 11.0};"
                   "Server=DESKTOP-29E9I02;"
                   "Database=Assignment1_Network;"
                   "Trusted_Connection=yes;")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM dbo.USERINFO WHERE LoginName = '{0}' AND LoginPass =  '{1}'".format(logName, logPass))

        records = cursor.fetchone()
        print("LOGIN() server: records = ", records)
        if records is not None:
            userName = records[2]
            print(userName)
            # cursor.execute("INSERT INTO dbo.LIST_ONLINING (LoginName, LoginPass, UserName, IP) VALUES ('{0}', '{1}', '{2}', '{3}')".format(logName, logPass, userName, str(ip)) )
            # conn.commit()
            LIST_ONLINING[str(ip)] = {"LoginName": logName,"UserName": userName}
            print("REGISTER(): Successful!")
            #LIST_ONLINING[str(ip)] = userName
            SetStatus(logName)
            print("LOGIN(): Successful!")
            result = True
        else:
            result = False
        cursor.close()
    except Error as error:
        print("LOGIN(): Failed to read data from data table", error)
    finally:
        if (conn):
            conn.close()
            print("LOGIN(): The pyodbc connection is closed!\n")
    return result


def FindFriend(friendlogname):
    for x in LIST_ONLINING:
        if LIST_ONLINING[x]["LoginName"] == friendlogname:
            return True
    for i in USERNAME_DICT:
        if i == friendlogname:
            return False
    return None


def getIPFriend(friendlogname):
    for x in LIST_ONLINING:
        if LIST_ONLINING[x]["LoginName"] == friendlogname:
            return str(x)
    return None

def getFriendName(ipfriend):
    print("getFriendName:",ipfriend)
    for x in LIST_ONLINING:
        if  x == ipfriend:
            return str(LIST_ONLINING[x]["LoginName"])
    return None

def getListFriend():
    result=''
    for x in LIST_ONLINING:
        result=result+str(LIST_ONLINING[x]["LoginName"])+"#"
    return result

def deleteUser(name):
    for x in LIST_ONLINING:
        if LIST_ONLINING[x]["LoginName"]==name:
            LIST_ONLINING.pop(x)
            return True
    return False



class ClientThread(threading.Thread):
    def __init__(self, clientAddress, connectionSoc):
        threading.Thread.__init__(self)
        self.clientAddr = clientAddress
        self.csocket = connectionSoc
        print("Connection from : " + str(self.clientAddr))

    def run(self):
        message = ''
        # while(True):
        data = self.csocket.recv(2048)
        message = data.decode('utf-8')
        messageCompile = message.split("#")
        print(message)
        if (messageCompile[0] == "ConnectToServer()"):
            replyFromServer = "OK,Connected!"
        elif (messageCompile[0] == "Register()"):
            logname = str(messageCompile[1])
            logpass = str(messageCompile[2])
            username = str(messageCompile[3])
            result = Register(logname, logpass, username)
            print("Da nhan duoc request REGISTER() tu peer: logname={0} logpass={1} username={2} address={3}".format(
                logname, logpass, username,  str(self.clientAddr[0])))
            print("ResultRegister = ", result)
            if result == True:
                replyFromServer = "OK,Register!"
            elif result == False:
                replyFromServer = "Fail,Register!"
            else:
                replyFromServer = "Result is None at REGISTER() server.py|"
        elif (messageCompile[0] == "Login()"):
            logname = str(messageCompile[1])
            logpass = str(messageCompile[2])
            result = Login(logname, logpass, str(self.clientAddr[0]))
            print("Da nhan duoc request LOGIN() tu peer: logname={0} logPass={1} address={2}".format(
                logname, logpass, str(self.clientAddr[0])))
            print("ResultLogin = ", result)
            if result == True:
                replyFromServer = "OK,Login!"
            elif result == False:
                replyFromServer = "Fail,Login!"
            else:
                replyFromServer = "Result is None at LOGIN() server.py|"
        elif (messageCompile[0] == "FindFriend()"):
            friendname = messageCompile[1]
            result = FindFriend(friendname)
            ipfriend = getIPFriend(friendname)
            print(
                "Da nhan duoc request FINDFRIEND() tu peer: friendname={0}".format(friendname))
            print("ResultFindFriend = ", result)
            if result == True:
                replyFromServer = "OK,FriendOnline!#"+ipfriend+"#"
            elif result == False:
                replyFromServer = "OK,FriendOffline!#"
            else:
                replyFromServer = "Fail,FriendNotFound!#"

        elif (messageCompile[0] == "GetFriendIP()"):
            friendIP = getIPFriend(str(messageCompile[1]))
            print("GetFriendIP(): friendIP=",friendIP)
            if friendIP is None:
                replyFromServer = "Fail,NotFound!"
            else:
                replyFromServer = friendIP
                
        elif (messageCompile[0] == "GetFriendName()"):
            print("GetFriendName(): messageCompile[1]=",messageCompile[1])
            friendname = getFriendName(str(messageCompile[1]))
            print("GetFriendName(): friendIP=",friendname)
            if friendname is None:
                replyFromServer = "Fail,NotFound!"
            else:
                replyFromServer = friendname

        elif (messageCompile[0] == "GetListFriend()"):
            listfriend=getListFriend()
            replyFromServer="OK,ListFriendIsReady!#"+str(listfriend)
        elif (messageCompile[0]=="ExitApp()"):
            check=deleteUser(messageCompile[1])
            if check==True:
                replyFromServer="DeleteUserSuccessful"
            else:
                replyFromServer="DeleteUserFailure"
            

        print("From client address: " + str(self.clientAddr) + " ||| Reply from server: " + str(replyFromServer))
        self.csocket.send(replyFromServer.encode('utf-8'))
        print("Client IP: " + str(self.clientAddr) + " disconnected!")
        print("_______________________________________________________________________________________________________________________________________________")
        print("_______________________________________________________________________________________________________________________________________________\n")


LoadUser()
print('.................................................................................')
ipserver2 = getMyIP()
ipserver = "0.0.0.0"
print("THE IP ADDRESS OF SERVER:", ipserver2)
serverPort = 50000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((ipserver, serverPort))
print('.............................. THE SERVER IS READY ..............................')
while True:
    serverSocket.listen(100)
    connectionSocket, addr = serverSocket.accept()
    newthread = ClientThread(addr, connectionSocket)
    newthread.start()
