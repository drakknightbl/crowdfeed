from twisted.internet import threads
import datetime, urllib, urllib2

class C2DMSender(object):
    _device_ids = []
    _token = False


    #_email = 'conversationboard@gmail.com'
    #_pwd = 'tApp3d0uT'
    _email = 'adriel.service@gmail.com'
    _pwd = 'gugugugu'
    _auth_url = 'https://www.google.com/accounts/ClientLogin'
    _last_time = datetime.datetime.now()

    def _get_token(self):
        if not self._token:
            params = urllib.urlencode({'Email':self._email, 'Passwd':self._pwd, 'accountType':'HOSTED_OR_GOOGLE', 'service':'ac2dm', 'source':'ConversationBoard'})

            req = urllib2.Request(self._auth_url, params)

            response = urllib2.urlopen(req)
            rS = response.read()
            rL = rS.split('\n')
            self._token = rL[2].split('=')[1]
            print 'got new token : %s' % self._token

        return self._token

    def new_device(self, id):
        if id not in self._device_ids:
            self._device_ids.append(id)

    def send_msg(self, msg):
        time_since_last = datetime.datetime.now() - self._last_time
        if time_since_last.seconds > 30:
            print 'send msg'
            self._last_time = datetime.datetime.now()
            for d in self._device_ids:
                params = urllib.urlencode({'registration_id':d, 'collapse_key':'conversation_board', 'data.message':msg})
                url = 'https://android.apis.google.com/c2dm/send'
                headers = {'Authorization':'GoogleLogin auth=%s' % self._get_token()}
                req = urllib2.Request(url, params, headers)
                threads.deferToThread(self._blocking_send_msg, req)
                print 'sent msg'
        else:
            print 'not sending because last time is : %s' % time_since_last.seconds

    def send_to_alu(self, subscriber_id, caller_id):
        print 'send to alu'
        params = urllib.urlencode({'subscriber_id':subscriber_id, 'caller_id':caller_id})
        try:
            #url = 'http://alusrv.demo.alcatel-lucent.com/alu/concierge/notify'
            url = 'http://aluserver.dyndns.org:18194/alu/concierge/notify'

            #url = 'http://127.0.0.1:18194/alu/concierge/notify'
                   
            req = urllib2.Request(url, params)
            threads.deferToThread(self._blocking_send_msg, req)
        except Exception:
            print 'fail alu_request silently'

    def _blocking_send_msg(self, req):
        response = urllib2.urlopen(req)
        try:
            content = response.read()
            print 'c2dm response : %s' % content
        except Exception:
            print 'an error occured while dispatching push message' 
