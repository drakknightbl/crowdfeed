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


class Pager(Resource):
    def render_GET(self, request):
        if state.count:
            return '<object width="640" height="385"><param name="movie" value="http://www.youtube.com/v/IQRWeZy-S8Q?fs=1&amp;hl=en_US"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/IQRWeZy-S8Q?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="640" height="385"></embed></object>'
        else:
            return 'some other none related ad'

class Activate(Resource):
    def render_GET(self,request):
        state.count+=1
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

factory = Site(root)
reactor.listenTCP(8083, factory)
print 'running...'
reactor.run()


