import os

def checkq(path,limit):
    queue_num = os.popen("ls %s | wc -l" % path).read().strip()
    if int(queue_num) > limit:
        print "do something"

def mailer():
    print "mail_adm"
