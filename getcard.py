import json
import urllib.parse
import urllib.request
import time

baseurl = "https://api.scryfall.com"

cardname = "/cards/named?"

vintage = "mtgo_vintage_cube_winter_20162017.txt"
vintage2 = "mtgo_vintage_cube_winter_201718.txt"

with open(vintage, "r") as f:
    vint = set(li.strip() for li in f.readlines())

with open(vintage2, "r") as f:
    vint2 = set(li.strip() for li in f.readlines())


fn = "cards.db"
failed = []
with open(fn, "a") as fot:
    for card in list(vint.union(vint2)):
        print(card)
        url = baseurl + cardname + urllib.parse.urlencode({"exact": card})
        resp = urllib.request.urlopen(url)
        if resp.getcode() == 200:
            data = json.load(resp)
            s = json.dumps(data)
            fot.write(s)
        else:
            failed += (card, resp.getcode())

        time.sleep(0.1)
    print(failed)
