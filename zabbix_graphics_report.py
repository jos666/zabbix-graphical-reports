#!/usr/bin/env python
#coding:utf8
#Author:Finy
#date 20131116
#fun get zabbix graphics send to mail.



import urllib2
import cookielib
import re
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class parameter:
    def __init__(self,**param):
        self.param = param
        self.user = self.param['user']
        self.passwd = self.param['passwd']
        self.zabbix_version = self.param['version']
        self.web = self.param['zabbix']
        self.header = [('User-agent','Mozilla/4.0 (compatible; MSIE 7.0; Windows NameError 5.1)')]
        self.Get_data = "/index.php?name=%s&password=%s&enter=Enter&login=1"%(self.user,self.passwd)
        self.sid = self.login()

class Report_Generation(parameter):
    def login(self):
        cj = cookielib.CookieJar()
        Opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        Opener.addheaders = self.header
        urllib2.install_opener(Opener)
        req = urllib2.Request(self.web+self.Get_data)
        html = urllib2.urlopen(req).read()
        sidre=re.compile('sid=(.*)">Dashboard')
        sid=re.findall(sidre,html)[0]
        return sid

    def download_image(self,Dict,directory):
        if os.path.exists(directory):
            pass
        else:
            os.popen('mkdir %s -p'%directory)
        #for key in Dict.keys():
        Image_Url=self.web+"/chart2.php?graphid=%s&&width=600&period=%s&stime=%s&sid=%s"%(Dict['graphid'],Dict['cycle'],Dict['date'],self.sid)
        Openfile=open(directory+'/'+Dict['name']+'.png','w')
        Openfile.write(urllib2.urlopen(Image_Url).read())
        Openfile.close()
        return directory + '/' + Dict['name'] + '.png'

class Mail_par:
    def __init__(self,**Mail):
        self.user = Mail['user']
        self.passwd = Mail['passwd']
        self.server = Mail['smtpserver']
        self.sender = self.user+'@'+self.server.split('.')[1]+'.'+self.server.split('.')[2]
        self.receiver = Mail['receiver']
        self.subject = Mail['subject']
        self.port = 25

class Mail(Mail_par):
    def login(self):
        smtp = smtplib.SMTP()
        try:
            smtp.connect(self.server)
        except Exception,err:
            print '[Error] Connect Smtp server fail error info:',err
            exit()
        try:
            smtp.login(self.user,self.passwd)
        except Exception,err1:
            print '[Error] Login Smtp server fail,placse check user and passord,error info:',err1
            exit()
        return smtp
    def Send(self,namelist,imagelist):
        smtp = self.login()
        Centent = ''
        for i in range(len(imagelist)):
            Centent = Centent + '<h1>%s</h1><br><img src="cid:image%s"><br>'%(namelist[i],str(i+1))
        print Centent
        msgRoot = MIMEMultipart('related')
        msgtext = MIMEText(Centent)
        msgRoot.attach(msgtext)
        images=[]
        for i in range(len(imagelist)):
            fp = open(imagelist[i], 'rb')
            msgImage = MIMEImage(fp.read())
            #images = MIMEImage(fp.read())
            #images.append(MIMEImage(fp.read()))
            fp.close()
            msgImage.add_header('Content-ID', '<image1>')
            msgRoot.attach(msgImage)
            #images.add_header('Content-ID', '<image%s>'%str(i+1))
            #images[i].add_header('Content-ID', '<image%s>'%str(i+1))
            #msgRoot.attach(images)
        msgRoot['Subject'] = self.subject
        msgRoot['To'] = self.receiver
        msgRoot['From'] = self.sender
        smtp.sendmail(self.sender, self.receiver, msgRoot.as_string())
        smtp.quit()
        return msgRoot





a=Report_Generation(user='admin',passwd='zabbix',version='1.8',zabbix='http://192.168.2.21')
Dict=[{'name':'cpu_load','graphid':'2','cycle':'86400','date':'20131116083111'}]
#{'name':'network_used','graphid':'4','cycle':'86400','date':'20131116083111'},
#{'name':'disk_used','graphid':'5','cycle':'86400','date':'20131116083111'},
#{'name':'cpu_used','graphid':'3','cycle':'86400','date':'20131116083111'}]
imagelist=[]
namelist=[]
for i in Dict:
    namelist.append(i['name'])
    imagelist.append(a.download_image(i,'/home/finy/zabbix'))
mail=Mail(user='860087477',passwd='findmy0606',smtpserver='smtp.qq.com',receiver='yyj@stucredit.com',subject='zabbix test')
aaa = mail.Send(namelist,imagelist)
print imagelist,namelist
#a=parameter(user='admin',passwd='zabbix',version='1.8',zabbix='http://zabbix.nginx.com')
