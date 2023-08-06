#!/usr/bin/env python
from powerline.lib.threaded import ThreadedSegment, with_docstring
import requests

class BTCSegment(ThreadedSegment):
    interval = 300

    def set_state(self, exchange="bitstamp", currency="USD", **kwargs):
        self.exchange = exchange
        super(BTCSegment, self).set_state(**kwargs)

    def update(self, oldprice):
        price = None
        if self.exchange == "bitstamp":
            ticker = requests.get("https://www.bitstamp.net/api/ticker/").json()
            price = "$%s" % ticker['last']
        if price is not None:
            return price
        else:
            return "Unknown exchange \"%s\"" % exchange

    def render(self, price, **kwargs):
        return [{
            "contents": str(price),
            "hightlight_group": ["btc"]
            }]

btc = with_docstring(BTCSegment(),
"""Returns the current price of Bitcoin at the specified exchage
:param str exchange:
    The name of the exchange. Currently supported:

    * bitstamp (supported currencies: USD)

:param str currency:
    The currency being exchanged to. See above for available currencies for
    your exchange.
highlight groups: ``btc``
""")

class RedditMessageSegment(ThreadedSegment):
    interval = 60

    def set_state(self, username=None, password=None, **kwargs):
        self.headers = {"User-Agent": "Powerline Reddit Checker 0.1 (thefinn93@thefinn93.com)"}
        self.username = username
        self.password = password
        super(RedditMessageSegment, self).set_state(**kwargs)

    def dologin(self):
        login = requests.post("https://ssl.reddit.com/api/login", data = {
                "api_type": "json",
                "rem": "true",
                "user": self.username,
                "password": self.password}, headers = self.headers).json()
        errors = None
        cookies = None
        if "errors" in login:
            errors = login['errors']

        if "cookie" in login: # I'm hella ratelimited right now, can't test the actual value :(
            cookies = login['cookies']
        if "modhash" in login:
            self.headers['X-Modhash'] = login['modhash']

        return errors, cookies

    def update(self, oldstuff):
        errors = None
        olderrors = None
        cookies = None
        unread = None

        if oldstuff is None: # First run
            errors, cookies = self.dologin()
        else:
            olderrors, cookies, oldunread = oldstuff

            if cookies is None: # Not our first run, but no login cookies
                if olderrors[0][0] == "RATELIMIT": # we got ratelimited last time... try again
                    errors, cookies = self.dologin()
                elif olderrors[0][0] == "WRONG_PASSWORD": # Wrong password. Refuse to continue
                    return errors, cookies, None
        if cookies:
            unread = requests.get("https://ssl.reddit.com/message/unread.json",
                    params = {"mark": "false", "limit": 100},
                    cookies = cookies, headers = self.headers).json()

        return errors, cookies, unread

    def render(self, currentdata, **kwargs):
        errors, login, unread = currentdata
        ret = []
        if unread:
            if "data" in unread:
                if "children" in unread['data']:
                    if len(unread['data']['children']) > 0:
                        ret.append({
                            "contents": str(len(unread['data']['children'])),
                            "highlight_group": "reddit:messages"
                            })
                else:
                    raise Exception("UM WTF BRO", unread)
            else:
                raise Exception("UM WTF BRO", unread)

        if errors:
            ret.append({
                "contents": errors[0][1],
                "highlight_group": "reddit:messages"
                })
        return ret

redditmessages = with_docstring(RedditMessageSegment(),
        """Displays the number of unread reddit messages in your inbox.
:param str username
    Your reddit username

:param str password
    Your reddit password
""")
