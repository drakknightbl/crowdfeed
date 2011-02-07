import cgi, time

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor



import simplejson as json
import urllib2

API_KEY = 'x4ss4ypqaewteeqpkxzhr6xw' 
from yellowapi import YellowAPI
yp = YellowAPI(API_KEY, True, format='JSON')


cached_results = {}

import twillio
import state


class DadOnline(Resource):
    def __init__(self):
        state.dad_online = "offline"

    def render_GET(self, request):
        state.dad_online = "offline"
        return state.dad_online

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

class Pager(Resource):
    def render_GET(self, request):
        if state.count:
            return '1'
        else:
            return '0'

class Activate(Resource):
    def render_GET(self,request):
        state.count+=1
        return 'yeehaw %s' % state.count

class DeActivate(Resource):
    def render_GET(self,request):
        state.count=0
        return 'yeehaw %s' % state.count


class CallMyself(Resource):
    def render_GET(self, request):
        twillio.main()
        return 'yeehaw'

class YellowPagesDetails(Resource):
    def render_GET(self, request):
        try:
            callback = cgi.escape(request.args['callback'][0],None)
            bus_name = cgi.escape(request.args['encoded_bus_name'][0], None)
            listing_id = cgi.escape(request.args['id'][0], None)
            location = cgi.escape(request.args['location'][0], None)
            detail_result = yp.get_business_details(location, bus_name, listing_id, '416.441.3594') 
            dc = json.loads(detail_result)
            res = {}
            res['business_name'] = dc['name']
            try:
                phone = dc['phones'][0]
                try:
                    res['phone_number'] = phone['dispNum']
                except KeyError:
                    res['phone_number'] = ''

            except IndexError:
                res['phone_number'] = ''
            


            try:
                res['geocode'] = '%s,%s' % (dc['geoCode']['latitude'],dc['geoCode']['longitude'])
            except TypeError:
                res['geocode'] = ''

            res['thumb_urls'] = []
            try:
                disp_ads = dc['products']['dispAd']
                for ad in disp_ads:
                    res['thumb_urls'].append(ad['thmbUrl'])

            except KeyError:
                pass

            try:
                res['thumb_urls'][0]
            except (KeyError, IndexError):
                res['thumb_urls'].append('')

            try:
                res['thumb_urls'][1]
            except (KeyError, IndexError):
                res['thumb_urls'].append('')

            results = json.dumps({'status':'ok', 'results':res})
            return '%s(%s)' % (callback, results)                
        except KeyError:
            return json.dumps({'status':'failed', 'reason':'Not all paramaters specified.'})


class YellowPagesList(Resource):
    def render_GET(self, request):
        try:
            q = cgi.escape(request.args['q'][0],None)
            location = cgi.escape(request.args['location'][0],None)
            key = '%s%s' % (q,location)


            callback = cgi.escape(request.args['callback'][0],None)
            try:
                results = cached_results[key]
                return '%s(%s)' % (callback, cached_results[key])
            except KeyError:
                try:
                    results = yp.find_business(q, location, uid='416.441.3594', page_len=100)
                    content = json.loads(results)
                    listings = content['listings']
                    details_list = []


                    for l in listings:
                        d = {}
                        try:
                            d['encoded_business_name'] = YellowAPI.encode_business_name(l['name'])
                            d['business_name'] = l['name']
                            d['listing_id'] = l['id']
                            a = l['address']
                            if(a['street'] and a['city'] and a['prov'] and a['pcode']): 
                                d['address'] = '%s, %s, %s %s' % (a['street'], a['city'], a['prov'], a['pcode'])
                            else:
                                d['address'] = ''

                            try:
                                d['geocode'] = '%s,%s' % (l['geoCode']['latitude'],l['geoCode']['longitude'])
                            except TypeError:
                                d['geocode'] = ''

                            details_list.append(d)
                        except TypeError:
                            pass


                    results = json.dumps({'status': 'ok','results':details_list})
                    cached_results[key] = results
                    return '%s(%s)' % (callback, results)
                except urllib2.URLError:
                    return '%s(%s)' % (callback, json.dumps({'status':'failed','reason':'Could not pull data from yellow pages.'}))

        except KeyError:
            return json.dumps({'status':'failed','reason':'No q term specified.'})







root = Resource()
root.putChild('find_business', YellowPagesList())
root.putChild('get_business_details', YellowPagesDetails())
root.putChild('call_myself', CallMyself())
root.putChild('pager', Pager())
root.putChild('activate', Activate())
root.putChild('deactivate', DeActivate())
root.putChild('alice_command', AliceCommand())
root.putChild('alice_result', AliceResult())
root.putChild('dad_online', DadOnline())


factory = Site(root)
reactor.listenTCP(8083, factory)
print 'running...'
reactor.run()


