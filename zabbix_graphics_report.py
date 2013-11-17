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

zabbix='http://192.168.2.21'
zabbix_user='admin'
zabbix_passwd='zabbix'
zabbix_version='1.8'  #suport 1.8 and 2.03
smtpserver='smtp.qq.com'
smtpuser='hasdream'
smtppasswd='test'
receiver='test@qq.com'
subject='zabbix Graphics repost'
image_directory='/home/finy/zabbix'
date=os.popen('date +%Y%m%d%H%M%S').read().replace('\n','')


Cycle='86400'   #86400 is 1 day 

Dict=[{'name':'cpu_load','graphid':'2','cycle':Cycle,'date':date},
                {'name':'network_used','graphid':'4','cycle':Cycle,'date':date},
                {'name':'disk_used','graphid':'5','cycle':Cycle,'date':date},
                {'name':'cpu_used','graphid':'3','cycle':Cycle,'date':date}]







class parameter:
    def __init__(self,**param):
        self.param = param
        self.user = self.param['user']
        self.passwd = self.param['passwd']
        self.zabbix_version = self.param['version']
        self.web = self.param['zabbix']
        self.header = [('User-agent','Mozilla/4.0 (compatible; MSIE 7.0; Windows NameError 5.1)')]
        self.Get_data = "/index.php?name=%s&password=%s&enter=Enter&login=1"%(self.user,self.passwd)
        self.sid = self.login(self.zabbix_version)

class Report_Generation(parameter):
    def login(self,version):
        cj = cookielib.CookieJar()
        Opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        Opener.addheaders = self.header
        urllib2.install_opener(Opener)
        if '1.8' in version:
            req = urllib2.Request(self.web+self.Get_data)
            html = urllib2.urlopen(req)
            #print str(html.info())
            for i in str(html.info()).split('\n'):
                if 'Set-Cookie' in i:
                        sid=i.split('=')[1].split(";")[0][16:]
        elif '2.0' in version:
            post_data = urllib.urlencode({"autologin":"1","enter":"Sign in","name":self.user,"password":self.passwd})
            req = urllib2.Request(self.web,post_data)
            html = urllib2.urlopen(req)

            for i in str(html.info).split('\n'):
                if 'Set-Cookie' in i:
                    sid = i.split("=")[1].split(";")[0][16:]
                    break
        return sid

    def download_image(self,Dict,directory):
        if os.path.exists(directory):
            pass
        else:
            os.popen('mkdir %s -p'%directory)
        #for key in Dict.keys():
        Image_Url=self.web+"/chart2.php?graphid=%s&&width=600&period=%s&stime=%s&sid=%s"%(Dict['graphid'],Dict['cycle'],Dict['date'],self.sid)
        Openfile=open(directory+'/'+Dict['name']+'.png','w')
        try:
            Openfile.write(urllib2.urlopen(Image_Url).read())
        except Exception,err:
                print Image_Url
                print "download images error ,",err
                exit()
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
            Centent = Centent + '<h1>%s</h1><br><img src="cid:image%s"><br>'%(namelist[i],str(i))
        msgRoot = MIMEMultipart('related')
        msgtext = MIMEText(Centent,'html','utl8')
        msgRoot.attach(msgtext)
        #images=[]
        for i in range(len(imagelist)):
            fp = open(imagelist[i], 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
            msgImage.add_header('Content-ID', '<image%s>'%str(i))
            msgRoot.attach(msgImage)
        msgRoot['Subject'] = self.subject
        msgRoot['To'] = self.receiver
        msgRoot['From'] = self.sender
        smtp.sendmail(self.sender, self.receiver, msgRoot.as_string())
        smtp.quit()




if __name__ == '__main__':
    a=Report_Generation(user=zabbix_user,passwd=zabbix_passwd,version=zabbix_version,zabbix=zabbix)
    imagelist=[]
    namelist=[]
    for i in Dict:
       namelist.append(i['name'])
       imagelist.append(a.download_image(i,image_directory))
    mail=Mail(user=smtpuser,passwd=smtppasswd,smtpserver=smtpserver,receiver=receiver,subject=subject)
    mail.Send(namelist,imagelist)
