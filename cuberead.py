from HTMLParser import HTMLParser
import urllib
import re
import sys
import sqlite3

class card(object):
    def __init__(self, attr):
        lines = attr.split(u'\\n')
        title_re = re.compile(r"([^\(]+)\(([^\)]+)\)(.*)", flags=re.UNICODE)
        match = title_re.match(lines[0])
        self.title = match.group(1).strip()
        self.cost = match.group(2).strip()
        self.pt = match.group(3).strip()
        self.types = lines[1].strip()
        self.body = "".join(lines[2:-3])
        self.sets = lines[-3].strip()

global cards
cards = {}

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            for k,v in attrs:
                if k == 'title':
                    title = v
                    break
            the_card = card(title)
            cards[the_card.title] = the_card

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass

vintage = "/cygdrive/c/Users/Jason Sewall/Downloads/mtgo_vintage_cube_winter_20162017.txt"

if __name__ == '__main__':
    # instantiate the parser and fed it some HTML
    parser = MyHTMLParser()
    fi = ["file:///cygdrive/c/Users/Jason Sewall/Documents/mtgcube/proxies.htm",
          "file:///cygdrive/c/Users/Jason Sewall/Documents/mtgcube/proxies2.htm",
          "file:///cygdrive/c/Users/Jason Sewall/Documents/mtgcube/soi.htm",
          "file:///cygdrive/c/Users/Jason Sewall/Documents/mtgcube/enm-consp2-kld.htm",
          "file:///cygdrive/c/Users/Jason Sewall/Documents/mtgcube/commander.htm"]
    for f in fi:
        connection = urllib.urlopen(f)
        encoding = connection.headers.getparam('charset')
        page = connection.read().decode('utf-8')
        parser.feed(page)

    with open(vintage, "r") as f:
        vint = set(unicode(li.strip()) for li in f.readlines())

    cube = set(cards.iterkeys())

    # print vint
    # print cube
    diff = vint - cube
    for v in sorted(diff):
        print v

    # conn =sqlite3.connect("cube.db")
    # c = conn.cursor()

    # c.execute('''CREATE TABLE cards
    #              (date_added text, name text, mana text, power_toughness text, types text, body text, sets text)''')

    # for k,v in cards.iteritems():
    #     t = ('2015-11-30', v.title, v.cost, v.pt, v.types, v.body, v.sets)
    #     c.execute("INSERT INTO cards VALUES (?, ?, ?, ?, ?, ?, ?)", t)

    # conn.commit()
    # conn.close()
