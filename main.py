import bottle, pprint
from bottle import route, post, run, request, template
from instagram import client, subscriptions

bottle.debug(True)

CONFIG = {
    'client_id': '<CLIENTID>',
    'client_secret': '<SECRET>',
    'redirect_uri': 'http://localhost:8515/oauth_callback'
}

unauthenticated_api = client.InstagramAPI(**CONFIG)

def process_tag_update(update):
    print update

reactor = subscriptions.SubscriptionsReactor()
reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)

@route('/')
def home():
    try:
        url = unauthenticated_api.get_authorize_url(scope=["likes","comments"])
        return '<a href="%s">Connect with Instagram</a>' % url
    except Exception, e:
        print e

@route('/oauth_callback')
def on_callback():
	f = open('index.html', 'r')
	feed, next = get_feed(code = request.GET.get("code"))
	return template(f.read(), feed = feed, next = next)

@post('/get_feed')
def get_feed(code = ''):
    if not code:
        code = request.POST['code']
        
    if not code:
        return 'Missing code'
    
    max_id = ''
    if 'next' in request.POST:
        return '278488500469360147_325120'
    
    try:
        access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
        if not access_token:
            return 'Could not get access token'
        
        api = client.InstagramAPI(access_token=access_token)
        if not max_id:
            recent_media, next = api.user_media_feed()
        else:
            recent_media, next = api.user_media_feed_next(max_id = max_id)
        photos = []
        for media in recent_media:
            photos.append('{ "feed_url": "' + media.images['standard_resolution'].url + '", "username": "' + media.user.username + '", "profile_img_url": "' + media.user.profile_picture + '" }')
        return  '['+','.join(photos)+']', next
    except Exception, e:
        print e

run(host='localhost', port=8515, reloader=True)
