import urllib2
import json
import urllib
import random
from urlparse import urljoin

from pelican import signals


def add_hot_posts(generator):
    settings = generator.settings
    num_entries = settings.get('HOT_POSTS_MAX', 5)
    count_facebook = settings.get('HOT_POSTS_INCLUDE_FACEBOOK', True)
    count_twitter = settings.get('HOT_POSTS_INCLUDE_TWITTER', False)
    siteurl = settings.get('SITEURL')
    dummy = settings.get('HOT_POSTS_DUMMY', True)
    shuffle = settings.get('HOT_POSTS_SHUFFLE', True)

    if not dummy:
        hot_posts = []
        for article in generator.articles:
            encoded_url = urllib.quote_plus(urljoin(siteurl, article.url))

            weight = 0
            if count_facebook:
                facebook_api = 'http://graph.facebook.com/?id=%s' % encoded_url
                json_str = urllib2.urlopen(facebook_api).read()
                facebook_info = json.loads(json_str)
                weight += facebook_info.get('shares', 0)

            if count_twitter:
                twitter_api = 'http://urls.api.twitter.com/1/urls/count.json?url=%s' % encoded_url
                json_str = urllib2.urlopen(twitter_api).read()
                twitter_info = json.loads(json_str)
                weight += twitter_info.get('count', 0)

            hot_posts.append((weight, article))
    else:
        hot_posts = [(random.randint(0, 100), article) for article in generator.articles]

    hot_posts.sort(key=lambda v: v[0], reverse=True)
    hot_posts = hot_posts[:num_entries]
    if shuffle:
        random.shuffle(hot_posts)

    generator.context['hot_posts'] = hot_posts


def register():
    signals.article_generator_finalized.connect(add_hot_posts)
