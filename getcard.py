import json
import urllib.parse
import urllib.request
import time
import csv
import sys
import re
import sqlite3

baseurl = "https://api.scryfall.com"

def myint(x):
    return int(re.sub('[^0-9\-]', '', x))

def make_setmaps():
    url = baseurl + "/sets"
    resp = urllib.request.urlopen(url)
    if resp.getcode() == 200:
        res = {}
        rev_res = {}
        data = json.load(resp)['data']
        for s in data:
            res[s['name']] = s
            rev_res[s['code']] = s['name']
        return res, rev_res
    else:
        return None


setmap, rev_setmap = make_setmaps()

#sys.exit(1)

cardname = "/cards/named?"

homedir="/cygdrive/c/Users/Jason Sewall"

failed = []
# iko_gnr_war = homedir +"/Downloads/All-cards - All.csv"
# dom = homedir +"/Downloads/Dom.csv"
# m21 = homedir +"/Downloads/M21.csv"
cmr = homedir +"/Downloads/CMR.csv"
bxl2 = homedir +"/Downloads/Bxl2.csv"
rix =  homedir +"/Downloads/rix.csv"
rna =  homedir +"/Downloads/RNA.csv"
curt_trades = homedir + "/Downloads/curt-trades.csv"
curt_trades2 = homedir + "/Downloads/curt-trades-01-09-2021.csv"
sean_trades = homedir + "/Downloads/sean-trades.csv"
cmrc = homedir + "/Downloads/Cmr_coll.csv"
mh1 = homedir + "/Downloads/Mh1.csv"
myb = homedir + "/Downloads/Myb.csv"
twoxm = homedir + "/Downloads/2xm.csv"
eld = homedir + "/Downloads/Eld.csv"

tbd = homedir + "/Downloads/Tbd.csv"
m19 = homedir + "/Downloads/M19.csv"
kld = homedir + "/Downloads/Kld.csv"
xln = homedir + "/Downloads/Xln.csv"
m20 = homedir + "/Downloads/M20.csv"
khm = homedir + "/Downloads/Khm.csv"
tsr = homedir + "/Downloads/Tsr.csv"
znr = homedir + "/Downloads/Znr.csv"

# >>>> Skull Prophet for Intangible Virtue
# >>>> Unfriendly Fire for Pyroceratops
# >>>> Fire Shrine Keeper for Excavation Mole
# >>>> Hijack for Llanowar Visionary
# >>>> Jungle Delver for Imposing Vantosaur
#>>>> Jade Guardian for Armillary Sphere

#inputs = [bxl2, cmr, rna, curt_trades]

inputs = [znr]

#ref_csv = homedir +"/Downloads/boxing-league-12-25-2020.csv"
# trade_csv = homedir +"/Downloads/boxing-league-trade-12-18-2020.csv"
# export_csv = homedir +"/Downloads/boxing-league-ark-12-18-2020.csv"
# studio_csv = homedir +"/Downloads/boxing-league-studio-12-18-2020.csv"

#ref_of = open(ref_csv,"w")
# export_of = open(export_csv,"w")
# trade_of = open(trade_csv,"w")
# studio_of = open(studio_csv, "w")

#ref_csvw = csv.writer(ref_of)
# trade_csvw = csv.writer(trade_of)
# export_csvw = csv.writer(export_of)
# studio_csvw = csv.writer(studio_of)

#ref_csvw.writerow(["Name", "Non-foil quantity", "Foil quantity", "Set", "Coll. #", "Scryfall code"])
# trade_csvw.writerow(["Name", "Quantity", "Set", "Scryfall url"])
# export_csvw.writerow(["Name", "Quantity", "Scryfall code"])
# studio_csvw.writerow(["Card Name", "Set", "Qty", "Foil", "Price", "Condition",  "Notes"])

ref_db = homedir + "/Downloads/boxing-league.db"
print(ref_db)
conn = sqlite3.connect(ref_db)

c=  conn.cursor()
# c.execute("""DROP TABLE cards""")
# c.execute("""CREATE TABLE cards
#     (name text, nfq real, fq real, edition text, coll_no real, scryuri text, date_added text)""")
# conn.commit()
# conn.close()

# sys.exit(1)

date= "2021-04-10"

for fn in inputs:
    with open(fn) as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        print(header)
        iname = header.index("Name")
        infq = header.index("Non-foil quantity")
        ifq = header.index("Foil quantity")
        ied = header.index("Edition")
        icoll = header.index("Collector's number")

        for row in csvreader:
            name,nfq,fq,ed,coll = row[iname],myint(row[infq]),myint(row[ifq]),row[ied],myint(row[icoll])
            set_code = setmap[ed]['code']

            url = f"{baseurl}/cards/{set_code}/{coll}"

            resp = urllib.request.urlopen(url)
            if resp.getcode() == 200:
                data = json.load(resp)
                sid=data['id']
                name=data['name']
                theset=data['set']
                theircol = data['collector_number']
                theircol = int(re.sub('[^0-9]', '', theircol))
                uri = data['scryfall_uri']

                c.execute("SELECT * FROM cards WHERE scryuri=?", (uri,))
                dbres = c.fetchone()
                if dbres is not None:
                    c.execute("UPDATE cards SET nfq = nfq+?, fq = fq+? WHERE scryuri=?", (nfq, fq, uri))
                else:
                    c.execute("INSERT into cards values (?, ?, ?, ?, ?, ?, ?, ?)", (name, nfq, fq, theset, theircol, uri, date, sid))
                print(name)
            else:
                failed += (name, resp.getcode())

            time.sleep(0.5)

print(failed)

def updatecode(c):
    c.execute("SELECT * FROM cards WHERE scrycode IS NULL")
    allres = c.fetchall()
    failed = []
    for res in allres:
        (name, nfq, fq, theset, col, uri, date, scrycode) = res
        print(name, col)
        query = f"{name} set:{theset}"
        url = f"{baseurl}/cards/search?{urllib.parse.urlencode({'q': query, 'unique': 'prints'})}"
        print(url)
        try:
            resp = urllib.request.urlopen(url)
            if resp.getcode() == 200:
                parsed = json.load(resp)
                assert not parsed['has_more']
                pick = None
                for pt in parsed['data']:
                    theircol=int(re.sub('[^0-9]', '', pt['collector_number']))
                    if theircol == col:
                        pick = pt
                if not pick:
                    pick = parsed['data'][0]
                theircol=int(re.sub('[^0-9]', '', pick['collector_number']))

                c.execute("UPDATE cards SET scrycode = ?, scryuri = ?, coll_no = ? WHERE name = ? and edition = ? and coll_no = ?", (pick['id'], pick['scryfall_uri'], theircol, name, theset, col))
            else:
                failed.append((name, theset))
            time.sleep(0.5)
        except:
            pass
    return failed


def write_archidekt(c):
    out = homedir + "/Downloads/boxing-league-04-10-2021-archidekt.csv"
    with open(out, "w") as of:
        writer = csv.writer(of)
        writer.writerow(["Quantity", "Name", "Scryfall Id"])
        c.execute("SELECT nfq+fq, name, scrycode FROM cards WHERE date_added = '2021-01-09' ")
        res = c.fetchall()
        for r in res:
            writer.writerow([int(r[0]), r[1], r[2]])


def write_decked(c):
    out_decked = homedir + "/Downloads/boxing-league-04-10-2021-decked.csv"
    with open(out_decked, "w") as of:
        writer = csv.writer(of)
        writer.writerow(["Set", "Card", "Regular", "Foil"])
        c.execute("SELECT * FROM cards")
        res = c.fetchone()
        while res is not None:
            writer.writerow([rev_setmap[res[3]], res[0], int(res[1]), int(res[2])])
            res = c.fetchone()

def write_deckstats(c):
    out_decked = homedir + "/Downloads/boxing-league-04-10-2021-deckstats.csv"
    with open(out_decked, "w") as of:
        writer = csv.writer(of)
        writer.writerow(["card_name", "set_name", "collector_number", "Reg Qty", "Foil Qty"])
        c.execute("SELECT name, edition, coll_no, nfq, fq FROM cards")
        res = c.fetchone()
        while res is not None:
            writer.writerow(res)
            res = c.fetchone()

def write_trades(c):
    out_trades = homedir + "/Downloads/boxing-league-04-10-2021-trades.csv"
    with open(out_trades, "w") as of:
        writer = csv.writer(of)
        writer.writerow(["Card", "Qty", "URI"])
        #c.execute("SELECT name, SUM(nfq), SUM(fq),  FROM (SELECT DISTINCT name, nfq, fq, scryuri FROM cards)")
        c.execute("SELECT name, num, uri FROM ( SELECT name, SUM(nfq+fq) as num, GROUP_CONCAT(scryuri) as uri FROM cards group by name) ORDER BY num DESC, name ASC")
        res = c.fetchone()
        while res is not None:
            writer.writerow([res[0], int(res[1]), res[2]])
            res = c.fetchone()

write_trades(c)

write_deckstats(c)
# write_archidekt(c)
# write_decked(c)
# failed = updatecode(c)
# print(failed)


conn.commit()
conn.close()
