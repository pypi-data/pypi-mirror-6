
from datetime import datetime

from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.web.client import ResponseDone
from twisted.trial.unittest import TestCase


def skipTest(reason):
    def deco(func):
        func.skip = reason
        return func
    return deco


class TestTwitterTransportRealIntertrons(TestCase):
    timeout = 15

    def setUp(self):
        from txtwitter import twitter
        self.TwitterClient = twitter.TwitterClient

        self.config = {
            'consumer_key': 'MBRx2eTDZu1Eu2VHiGSLw',
            'consumer_secret': '9jxvZdCwLyXSvrrWibgzjbtOdRjLWdl3TobUrvpo9Js',
            'token_key':
                '2258763672-JXsurIhVkdsuZdikIq0xiUPlPSj4X65zjP257Nx',
            'token_secret':
                'jcy7U9PuBmWuKtGzdxOyE2aw05y6SBMY2GuAxb4FYmIgf',
        }

    @skipTest("Don't hit the real API for now.")
    @inlineCallbacks
    def test_statuses_show(self):
        client = self.TwitterClient(**self.config)
        resp = yield client.statuses_show("415184968248487936", trim_user=True)
        print "\n-----"
        print resp
        print "-----"

    @skipTest("Don't hit the real API for now.")
    @inlineCallbacks
    def test_show_bad_id(self):
        client = self.TwitterClient(**self.config)
        d = client.show("badtweet")
        d.addErrback(lambda f: f.value)
        err = yield d
        print "\n-----"
        print repr(err)
        print "-----"

    @skipTest("Don't hit the real API for now.")
    @inlineCallbacks
    def test_statuses_update(self):
        client = self.TwitterClient(**self.config)
        resp = yield client.statuses_update(
            "new test: %s" % (datetime.utcnow(),))
        print "\n-----"
        print resp
        print "-----"

    @skipTest("Don't hit the real API for now.")
    @inlineCallbacks
    def test_statuses_update_mentions(self):
        client = self.TwitterClient(**self.config)
        resp = yield client.statuses_update(
            ".@jerithtest @E5BB1EF8_6EB9 @jerithtest2 %s" % (
                datetime.utcnow(),))
        print "\n-----"
        print resp
        print "-----"

    @skipTest("Don't hit the real API for now.")
    @inlineCallbacks
    def test_stream_filter(self):

        class LimitedDelegate(object):
            def __init__(self, max_count):
                self.count = 0
                self.max_count = max_count

            def __call__(self, tweet):
                self.count += 1
                print "\n-- v %s v ---" % self.count
                print tweet
                import json
                print "=== %s ===" % len(json.dumps(tweet))
                print "-- ^ %s ^ ---" % self.count
                if self.count >= self.max_count:
                    self.svc.stopService()

        client = self.TwitterClient(**self.config)
        delegate = LimitedDelegate(5)
        svc = client.stream_filter(delegate, track=["twitter"])
        d = Deferred()
        svc.set_disconnect_callback(lambda s, r: d.callback(r))
        delegate.svc = svc
        yield d.addErrback(lambda f: f.trap(ResponseDone))

    @skipTest("Don't hit the real API for now.")
    @inlineCallbacks
    def test_userstream_user(self):

        class LimitedDelegate(object):
            def __init__(self, max_count):
                self.count = 0
                self.max_count = max_count

            def __call__(self, tweet):
                self.count += 1
                print "\n-- v %s v ---" % self.count
                print tweet
                import json
                print "=== %s ===" % len(json.dumps(tweet))
                print "-- ^ %s ^ ---" % self.count
                if self.count >= self.max_count:
                    self.svc.stopService()

        client = self.TwitterClient(**self.config)
        delegate = LimitedDelegate(5)
        svc = client.userstream_user(delegate, with_='user')
        d = Deferred()
        svc.set_disconnect_callback(lambda s, r: d.callback(r))
        delegate.svc = svc
        yield d.addErrback(lambda f: f.trap(ResponseDone))
