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

class YellowPagesProxy(Resource):
    def render_GET(self, request):
        try:
            q = cgi.escape(request.args['q'][0],None)
            callback = cgi.escape(request.args['callback'][0],None)
            try:
                results = cached_results[q]
                print 'returning cached results'
                return '%s(%s)' % (callback, cached_results[q])
            except KeyError:
                try:
                    print 'getting from yellowpages'
                    results = yp.find_business(q, 'Canada', uid='416.441.3594', page_len=100, sflag='flo')
                    content = json.loads(results)
                    listings = content['listings'][0:5]
                    
                    details_list = []
                    time.sleep(1)
                    for l in listings:
                        bus_name = YellowAPI.encode_business_name(l['name'])
                        listing_id = l['id']
                        print 'bus_name : %s' % bus_name
                        print 'listing_id : %s' % listing_id
                        detail_result = yp.get_business_details('Canada', bus_name, listing_id, '416.441.3594') 
                        dc = json.loads(detail_result)
                        bd = {}
                        bd['name'] = dc['name']
                        try:
                            bd['phone_number'] = dc['phones'][0]['dispNum']
                        except IndexError:
                            bd['phone_number'] = ''

                        try:
                            bd['thumb_url'] = dc['products']['dispAd'][0]['thmbUrl']
                            details_list.append(bd)
                        except IndexError:
                            pass

                        time.sleep(1)


                    results = json.dumps({'status': 'ok','results':details_list})
                    cached_results[q] = results
                    return '%s(%s)' % (callback, results)
                except urllib2.URLError:
                    return '%s(%s)' % (callback, json.dumps({'status':'failed','reason':'Could not pull data from yellow pages.'}))

        except KeyError:
            return json.dumps({'status':'failed','reason':'No q term specified.'})

root = Resource()
root.putChild('yellow_pages', YellowPagesProxy())
factory = Site(root)
reactor.listenTCP(8083, factory)
print 'running...'
reactor.run()


