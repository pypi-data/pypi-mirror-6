import re

date = u'(?:(?<!\:)(?<!\:\d)[0-3]?\d(?:st|nd|rd|th)?\s+(?:of\s+)?(?:jan\.?|january|feb\.?|february|mar\.?|march|apr\.?|april|may|jun\.?|june|jul\.?|july|aug\.?|august|sep\.?|september|oct\.?|october|nov\.?|november|dec\.?|december)|(?:jan\.?|january|feb\.?|february|mar\.?|march|apr\.?|april|may|jun\.?|june|jul\.?|july|aug\.?|august|sep\.?|september|oct\.?|october|nov\.?|november|dec\.?|december)\s+(?<!\:)(?<!\:\d)[0-3]?\d(?:st|nd|rd|th)?)(?:\,)?\s*(?:\d{4})?|[0-3]?\d[-/][0-3]?\d[-/]\d{2,4}'
time = u'\d{1,2}:\d{2} ?(?:[ap]\.?m\.?)?|\d[ap]\.?m\.?'
phone = u'(\d?\W*(?:\(?\d{3}\)?\W*)?\d{3}\W*\d{4})'
link = u'(?i)((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\))+(?:\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))'
email = u"([a-z0-9!#$%&'*+\/=?^_`{|.}~-]+@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"
ip = u'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
money = u"\$\s?[+-]?[0-9]{1,3}(?:,?[0-9])*(?:\.[0-9]{1,2})?"
hex_color = u'(#(?:[0-9a-fA-F]{8})|#(?:[0-9a-fA-F]{3}){1,2})\\b'

class CommonRegex:

    def __init__(self, text=""):
        self.text = text

        if text:
            self.dates    = self.dates()
            self.times    = self.times()
            self.phones   = self.phones()
            self.links    = self.links()
            self.emails   = self.emails()
            self.ip       = self.ip()
            self.money    = self.money()
            self.hex_color = self.hex_color()

    def _opt(self, regex):
        return u'(?:' + regex + u')?'

    def _group(self, regex):
        return u'(?:' + regex + ')'

    def _any(self, *regexes):
        return u'|'.join(regexes)

    def _strip(fn, *args, **kwargs):
        def new_fn(*args, **kwargs):
          return [x.strip() for x in fn(*args, **kwargs)]
        return new_fn

    @_strip
    def dates(self, text=None):
        global date
        text = text or self.text
        return re.findall(date, text, re.IGNORECASE)

    @_strip
    def times(self, text=None):
        global time
        text = text or self.text
        return re.findall(time, text, re.IGNORECASE)

    @_strip
    def phones(self, text=None):
        global phone
        text = text or self.text
        return re.findall(phone, text)

    @_strip
    def links(self, text=None):
        global link
        text = text or self.text
        return re.findall(link, text, re.IGNORECASE)

    @_strip
    def emails(self, text=None):
        global email
        text = text or self.text
        return re.findall(email, text, re.IGNORECASE)

    @_strip
    def ip(self, text=None):
        global ip
        text = text or self.text
        return re.findall(ip, text)

    @_strip
    def money(self, text=None):
        global money
        text = text or self.text
        return re.findall(money, text)

    @_strip
    def hex_color(self, text=None):
        global hex_color
        text = text or self.text
        return re.findall(hex_color, text)

if __name__ == "__main__":
    parse = CommonRegex("8:00 5:00AM Jan 9th 2012 8/23/12 www.google.com $4891.75 http://hotmail.com (520) 820 7123, 1-230-241-2422 john_smith@gmail.com 127.0.0.1 #e9be4fff ")
    print(parse.dates)
    print(parse.times)
    print(parse.phones)
    print(parse.links)
    print(parse.emails)
    print(parse.ip)
    print(parse.money)
    print(parse.hex_color)
