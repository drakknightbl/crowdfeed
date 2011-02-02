#!/usr/bin/python

import os
from twisted.internet import reactor
from twisted.web2 import server, http, resource, channel
from twisted.web2 import http_headers, responsecode
from twisted.web2 import iweb

SAVEDIR = "/tmp"
READSIZE=8192

class UploadFile(resource.PostableResource):
    def render(self, ctx):
        request = iweb.IRequest(ctx)
        filename = request.files['filename'][0][0]
        file = request.files['filename'][0][2]
        p = request.args['subscriber_id'][0]
        print 'subscriber_id : %s' % p

        dest = os.path.join(SAVEDIR, filename)
        destfile = open(dest, 'wb')
        tot = 0
        while True:
            buf = file.read(READSIZE)
            tot = tot + READSIZE
            if buf == '':
                break
            destfile.write(buf)
        destfile.close()
        file.close()

        msg = "saved %s to %s" % (filename, dest)
        print msg
        return http.Response(stream="%s" % msg)

class Toplevel(resource.Resource):
    addSlash = True
    def render(self, ctx):
        return http.Response(responsecode.OK,
                {'content-type':http_headers.MimeType('text', 'html')},
                "Hello")

    child_uploadfile = UploadFile()

if __name__ == "__main__":
    site = server.Site(Toplevel())
    reactor.listenTCP(1080, channel.HTTPFactory(site))
    reactor.run()

