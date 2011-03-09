import cgi, time

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor



import simplejson as json
import urllib2, datetime

API_KEY = 'x4ss4ypqaewteeqpkxzhr6xw' 



cached_results = {}

import twillio
import state

class GameInvite(Resource):
    def __init__(self):
        state.friend_name = ""

    def render_GET(self, request):
        fn = state.friend_name
        state.friend_name = ""
        print 'game state : %s at : %s' % (fn, datetime.datetime.now())

        return fn

    def render_POST(self, request):
        friend_name = cgi.escape(request.args['friend_name'][0], None)
        if friend_name:
            state.friend_name = friend_name
            return 'ok'
        else:
            return "friend_name not specified"


class DadOnline(Resource):
    def __init__(self):
        state.dad_online = "offline"

    def render_GET(self, request):
        do = state.dad_online
        state.dad_online = "offline"
        print 'dad state : %s at : %s' % (do, datetime.datetime.now())
        return do

    def render_POST(self, request):
        status = cgi.escape(request.args['status'][0], None)
        if status:
            state.dad_online = status
            return 'ok'
        else:
            return 'message not specified'


class AliceCommand(Resource):
    def __init__(self):
        state.alice_message_creator = ""

    def render_GET(self, request):
        message = state.alice_message_creator
        state.alice_message_creator = ""
        return message

    def render_POST(self, request):
        message = cgi.escape(request.args['message'][0],None)
        if message:
            state.alice_message_creator = message
            return 'ok'
        else:
            return 'message not specified'


class AliceResult(Resource):

    def __init__(self):
        state.alice_message_guest = ""

    def render_GET(self, request):
        message = state.alice_message_guest
        state.alice_message_guest = ""
        return message

    def render_POST(self, request):
        message = cgi.escape(request.args['message'][0],None)
        if message:
            state.alice_message_guest = message
            return 'ok'
        else:
            return 'message not specified'









root = Resource()
root.putChild('alice_command', AliceCommand())
root.putChild('alice_result', AliceResult())
root.putChild('dad_online', DadOnline())
root.putChild('game_invite', GameInvite())


factory = Site(root)
reactor.listenTCP(8083, factory)
print 'running...'
reactor.run()


