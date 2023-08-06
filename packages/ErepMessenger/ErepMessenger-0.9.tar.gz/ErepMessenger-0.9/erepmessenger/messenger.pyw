from Tkinter import *
import tkMessageBox
import requests
from bs4 import BeautifulSoup
import ConfigParser

#------------------------------------------------------------------------------------------------

def showLogin():
    global mLogin
    if eToken is not None:
        if mmToken == '1':
            tkMessageBox.showinfo("Attention!", "You are already logged into both Erepublik and the Messenger!")
        else:
            showMMLogin()
    else:
        mLogin=Toplevel()
        mLogin.title("Login to Erepublik")
        mLogin.geometry('225x125+600+400')
        mLogin.lift()
        Label(mLogin,text='Email:').grid(row=0,column=0,sticky=E)
        Label(mLogin,text='Password:').grid(row=1,column=0,sticky=E)
        Entry(mLogin,textvariable=eEmail).grid(row=0,column=1,sticky=W)
        Entry(mLogin,textvariable=ePassword).grid(row=1,column=1,sticky=W)
        Button(mLogin,text="Login to Erepublik",command=eLogin).grid(row=2,column=1,sticky=W)

#------------------------------------------------------------------------------------------------

def showMMLogin():
    global mMMLogin
    mMMLogin=Toplevel()
    mMMLogin.title("Messenger Account")
    mMMLogin.geometry('300x125+600+400')
    mMMLogin.lift()
    if eToken is None:
        Label(mMMLogin,text='Log into Erepublik first!').grid(row=0,column=0,sticky=W)
    else:
        Label(mMMLogin,text='ID:').grid(row=0,column=0,sticky=E)
        Label(mMMLogin,text='Password:').grid(row=1,column=0,sticky=E)
        Entry(mMMLogin,textvariable=mmID).grid(row=0,column=1,sticky=W)
        Entry(mMMLogin,textvariable=mmPass).grid(row=1,column=1,sticky=W)
        Button(mMMLogin,text="Register",command=mmRegister).grid(row=2,column=0,sticky=W)
        Button(mMMLogin,text="Retrieve",command=mmRetrieve).grid(row=2,column=1)
        Button(mMMLogin,text="Login",command=mmLogin).grid(row=2,column=2,sticky=W)
        
#------------------------------------------------------------------------------------------------
        
def eLogin():
    global mLogin
    global eToken
    global eRep
    formdata = {'citizen_email': eEmail.get(), 'citizen_password': ePassword.get(), "remember": '1', 'commit': 'Login'}
    erepLogin = eRep.post('http://www.erepublik.com/en/login',data=formdata,allow_redirects=False)
    if erepLogin.status_code==302:
        mLogin.destroy()
        r = eRep.get('http://www.erepublik.com/en')        
        soup = BeautifulSoup(r.text)
        hidden = soup.find_all(type="hidden")
        eToken = hidden[0]['value']
        showMMLogin()
    else:
        tkMessageBox.showerror("Attention!", "Login Failed!", parent=mLogin)
        return
        
#------------------------------------------------------------------------------------------------
        
def sendPM(citizen,subject,message):
    global eRep
    eHeaders = {
        'Referer': 'http://www.erepublik.com/en/main/messages-compose/'+citizen,
        'X-Requested-With': 'XMLHttpRequest'}

    sendmessage = {
        '_token': eToken,
        'citizen_name': citizen,
        'citizen_subject': subject,
        'citizen_message': message}
    
    erepMess = eRep.post('http://www.erepublik.com/en/main/messages-compose/'+citizen,data=sendmessage,headers=eHeaders,allow_redirects=False)
    return
    
#------------------------------------------------------------------------------------------------
    
def mmRegister():
    global eMes
    eMesData = {'register': 1, 'id': mmID.get()}
    eMesRetrieve = eMes.post('http://ereptools.tk/messenger/control.php',data=eMesData)
    if eMesRetrieve.text == '1':
        tkMessageBox.showinfo("Attention!", "Check your inbox for your password!", parent=mMMLogin)
    if eMesRetrieve.text == '2':
        tkMessageBox.showerror("Attention!", "You are already registered! Try recovering your password if you forgot it.", parent=mMMLogin)
    if eMesRetrieve.text == '0':
        tkMessageBox.showerror("Attention!", "Make sure you are entering the correct profile ID!", parent=mMMLogin)
        
#------------------------------------------------------------------------------------------------
    
def mmRetrieve():
    global eMes
    eMesData = {'recover': 1, 'id': mmID.get()}
    eMesRetrieve = eMes.post('http://ereptools.tk/messenger/control.php',data=eMesData)
    if eMesRetrieve.text == '1':
        tkMessageBox.showinfo("Attention!", "Check your inbox for your password!", parent=mMMLogin)
    if eMesRetrieve.text == '2':
        tkMessageBox.showerror("Attention!", "You may only recover your password 1 time every 24 hours!", parent=mMMLogin)
    if eMesRetrieve.text == '3':
        tkMessageBox.showinfo("Attention!", "You are not registered!", parent=mMMLogin)
    if eMesRetrieve.text == '0':
        tkMessageBox.showerror("Attention!", "Make sure you are entering the correct profile ID!", parent=mMMLogin)    
    
#------------------------------------------------------------------------------------------------    
    
def mmLogin():
    global eMes
    global mmToken
    eMesData = {'login': 1, 'id': mmID.get(), 'pass': mmPass.get()}
    eMesLogin = eMes.post('http://ereptools.tk/messenger/control.php',data=eMesData)
    mmToken=eMesLogin.text
    if mmToken == '1':
        mMMLogin.destroy()
    else:
        tkMessageBox.showerror("Attention!", "Login Failed!", parent=mMMLogin)

#------------------------------------------------------------------------------------------------

def mmSend():
    global eMes
    error = 0
    if mmToken == "1":
        eProcdata = {'process': 1, 'ids': idList.get(1.0,END), 'subject': sub.get(), 'message': mess.get(1.0,END)}
        eMesproc = eMes.post('http://ereptools.tk/messenger/control.php',data=eProcdata)
        response = eMesproc.text.split('\n')
        if response[0] == 'error':
            tkMessageBox.showerror("Attention!", "Make sure all info is complete before trying to send your messages!", parent=mGui)
            error = 1
        if response[0] == 'long':
            tkMessageBox.showerror("Attention!", "Your message cannot be more than 2000 characters long! It is currently "+response[1]+" characters long.", parent=mGui)
            error = 1
        if error == 0:
            response = eMesproc.text.split('\n')[:-1]
            for mId in response:
                sendPM(mId,sub.get(),mess.get(1.0,END))
            tkMessageBox.showinfo("Attention!", "Messages sent!\n"+eMesproc.text, parent=mGui)
    else:
        tkMessageBox.showerror("Attention!", "Press \"Start\" to login before using the messenger!", parent=mGui)

#------------------------------------------------------------------------------------------------

global eToken
global mmToken
global eRep
global eMes
global idList
global sub
global mess
#citList = StringVar()
#subject = StringVar()
#message = StringVar()
eRep = requests.Session()
eMes = requests.Session()
defHeaders = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/31.0.1650.63 Chrome/31.0.1650.63 Safari/537.36'}
eRep.headers=defHeaders
mesHeaders = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip,deflate,sdch', 'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive', 'User-Agent': 'eMes/MO'}
eMes.headers=mesHeaders
mGui = Tk()
eToken = None
eEmail = StringVar()
ePassword = StringVar()
mmToken = '0'
mmID = StringVar()
mmPass = StringVar()
config = ConfigParser.ConfigParser()

config.readfp(open('config.cfg'))
eEmail.set(config.get('User','erepEmail'))
ePassword.set(config.get('User','erepPass'))
mmID.set(config.get('User','mesId'))
mmPass.set(config.get('User','mesPass'))

menubar = Menu(mGui)
menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=menu)
menu.add_command(label="Start", command=showLogin)
menu.add_command(label="Exit", command=mGui.quit)
mGui.config(menu=menubar)
leftFrame = Frame(mGui)
leftFrame.grid(row=0, column=0)
rightFrame = Frame(mGui)
rightFrame.grid(row=0, column=1)
#ID List box
Label(leftFrame, text="Citizen IDs:").pack(side="top")
scrollid = Scrollbar(leftFrame)
scrollid.pack(side="right", fill="y", expand=False)
idList = Text(leftFrame, height=28, width=15, wrap=WORD, yscrollcommand=scrollid.set)
idList.pack(side="left", fill="both", expand=True)
scrollid.config(command=idList.yview)
#Subject box
Label(rightFrame, text="Subject:").grid(row=0,column=0, sticky=W)
sub = Entry(rightFrame, width=39)
sub.grid(row=1,column=0)
#Message box
Label(rightFrame, text="Message:").grid(row=2,column=0, sticky=W)
scrollMes = Scrollbar(rightFrame)
scrollMes.grid(row=3,column=1,sticky="N,S,W")
mess = Text(rightFrame, height=23,width=44, wrap=WORD, yscrollcommand=scrollMes.set)
mess.grid(row=3,column=0, sticky=W)
scrollMes.config(command=mess.yview)
#Send button
Button(rightFrame, text="Send",command=mmSend).grid(row=4,column=0, sticky=E)

mGui.geometry('525x500+200+100')
mGui.minsize(525,500)
mGui.title("Erepublik Messenger")
icon = PhotoImage(file="messenger.gif")
mGui.tk.call('wm', 'iconphoto', mGui._w, icon)
mGui.mainloop()
