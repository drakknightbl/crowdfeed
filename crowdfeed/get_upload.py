#!/usr/bin/python

import os, time
from twisted.internet import reactor
from twisted.web2 import server, http, resource, channel
from twisted.web2 import http_headers, responsecode
from twisted.web2 import iweb
import shutil


SAVEDIR = "/tmp"
MEDIA_INDEX = '/u/media/facedetect/index.txt'
MEDIA_DIR = '/u/media/facedetect/'
READSIZE=8192

import state
from c2dm import C2DMSender

_c2dm = C2DMSender()

class RegisterDevice(resource.PostableResource):
    def render(self, ctx):
        print 'register'
        request = iweb.IRequest(ctx)
        device_id = request.args['device_id'][0]
        _c2dm.new_device(device_id) 
        return http.Response(responsecode.OK,
                {'content-type':http_headers.MimeType('text', 'html')},
                "Hello")


class SendMessage(resource.Resource):
    def render(self, ctx):
        print 'send msg'
        _c2dm.send_msg('Jake is at your door. %s' % time.time())
        return http.Response(responsecode.OK,
                {'content-type':http_headers.MimeType('text', 'html')},
                "Hello")


class UploadFile(resource.PostableResource):
    def render(self, ctx):
        request = iweb.IRequest(ctx)
        filename = request.files['filename'][0][0]
        file = request.files['filename'][0][2]
        p = request.args['subscriber_id'][0]
        c = request.args['caller_id'][0]

        try:
            native_dialer = request.args['native_dialer'][0]
        except (IndexError,ValueError):
            native_dialer = False

        print 'subscriber_id : %s' % p

        tmp = os.path.join(SAVEDIR, filename)
        destfile = open(tmp, 'wb')
        tot = 0
        while True:
            buf = file.read(READSIZE)
            tot = tot + READSIZE
            if buf == '':
                break
            destfile.write(buf)
        destfile.close()
        file.close()

        msg = "saved %s to %s" % (filename, tmp)
        
        if not native_dialer || native_dialer=='off':
            print 'sending notification'
            _c2dm.send_to_alu(p,c)
        else:
            print 'not sending notification'


        if not os.path.exists(MEDIA_DIR):
            os.makedirs(MEDIA_DIR)

        print 'opening : %s' % MEDIA_INDEX

        if not os.path.exists(MEDIA_INDEX):
            index = 0
        else:
            indexf = open(MEDIA_INDEX, 'r')
            c = indexf.read()
            if c:
                try:
                    index = int(c) + 1
                except ValueError:
                    index = 0
            else:
                index = 0

            indexf.close()

        indexf = open(MEDIA_INDEX, 'w')
        dest = os.path.join(MEDIA_DIR, '%s.jpg' % index)
        indexf.write('%s' % index)
        indexf.close()
        
        shutil.copy(tmp, dest)


        print msg
        return http.Response(stream="%s" % msg)

class Toplevel(resource.Resource):
    addSlash = True
    def render(self, ctx):
        return http.Response(responsecode.OK,
                {'content-type':http_headers.MimeType('text', 'html')},
                "Hello")

    child_uploadfile = UploadFile()
    child_send = SendMessage()
    child_register = RegisterDevice()

if __name__ == "__main__":
    # register with c2dm server
    site = server.Site(Toplevel())
    reactor.listenTCP(1080, channel.HTTPFactory(site))
    reactor.run()
