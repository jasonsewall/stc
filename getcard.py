import json
import urllib.parse
import urllib.request
import time
import csv
import sys
import re

baseurl = "https://api.scryfall.com"

def myint(x):
    return int(re.sub('[^0-9]', '', x))

def make_setmaps():
    url = baseurl + "/sets"
    resp = urllib.request.urlopen(url)
    if resp.getcode() == 200:
        res = {}
        data = json.load(resp)['data']
        for s in data:
            res[s['name']] = s
        return res
    else:
        return None

setmap = make_setmaps()

#sys.exit(1)

cardname = "/cards/named?"

homedir="/mnt/c/Users/jsewall"

failed = []
# iko_gnr_war = homedir +"/Downloads/All-cards - All.csv"
# dom = homedir +"/Downloads/Dom.csv"
# m21 = homedir +"/Downloads/M21.csv"
# cmr = homedir +"/Downloads/CMR.csv"
# bxl2 = homedir +"/Downloads/Bxl2.csv"
# rix =  homedir +"/Downloads/rix.csv"
# rna =  homedir +"/Downloads/RNA.csv"

cmrc = homedir + "/Downloads/Cmr_coll.csv"
mh1 = homedir + "/Downloads/Mh1.csv"
myb = homedir + "/Downloads/Myb.csv"
twoxm = homedir + "/Downloads/2xm.csv"


# >>>> Skull Prophet for Intangible Virtue
# >>>> Unfriendly Fire for Pyroceratops
# >>>> Fire Shrine Keeper for Excavation Mole
# >>>> Hijack for Llanowar Visionary
# >>>> Jungle Delver for Imposing Vantosaur
#>>>> Jade Guardian for Armillary Sphere

#inputs = [bxl2, cmr, rix, rna]
inputs = [mh1, myb, twoxm]

ref_csv = homedir +"/Downloads/boxing-league-12-18-2020.csv"
trade_csv = homedir +"/Downloads/boxing-league-trade-12-18-2020.csv"
export_csv = homedir +"/Downloads/boxing-league-ark-12-18-2020.csv"
studio_csv = homedir +"/Downloads/boxing-league-studio-12-18-2020.csv"

ref_of = open(ref_csv,"w")
export_of = open(export_csv,"w")
trade_of = open(trade_csv,"w")
studio_of = open(studio_csv, "w")

ref_csvw = csv.writer(ref_of)
trade_csvw = csv.writer(trade_of)
export_csvw = csv.writer(export_of)
studio_csvw = csv.writer(studio_of)

ref_csvw.writerow(["Name", "Non-foil quantity", "Foil quantity", "Set", "Coll. #", "Scryfall code"])
trade_csvw.writerow(["Name", "Quantity", "Set", "Scryfall url"])
export_csvw.writerow(["Name", "Quantity", "Scryfall code"])
studio_csvw.writerow(["Card Name", "Set", "Qty", "Foil", "Price", "Condition",  "Notes"])

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

        unique = {}
        for c in csvreader:
            name,nfq,fq,ed,coll = c[iname],myint(c[infq]),myint(c[ifq]),c[ied],myint(c[icoll])
            set_code = setmap[ed]['code']

            url = f"{baseurl}/cards/{set_code}/{coll}"

            resp = urllib.request.urlopen(url)
            if resp.getcode() == 200:
                data = json.load(resp)
                sid=data['id']
                name=data['name']
                theircol = data['collector_number']
                theircol = int(re.sub('[^0-9]', '', theircol))
                if name in unique:
                    unique[name]['quantity'] += nfq + fq
                    if theircol < unique[name]['coll']:
                        unique[name]['coll'] = theircol
                        unique[name]['set'] = data['set']
                        unique[name]['url'] = data['scryfall_uri']
                else:
                    ent = {'name': name, 'coll': theircol, 'set' : data['set'], 'quantity' : nfq+fq, 'url' : data['scryfall_uri']}
                    unique[name] = ent
                scryfall_uri = data['scryfall_uri']
                ref_csvw.writerow([name,nfq,fq,set_code,coll,scryfall_uri])
                export_csvw.writerow([name,nfq+fq,sid])
                print(name)
            else:
                failed += (name, resp.getcode())

            time.sleep(0.5)

        for u in unique.values():
            studio_csvw.writerow([u['name'], u['set'], u['quantity'],0, 0, "NM", ""])
            trade_csvw.writerow([u["name"], u["quantity"], u["set"], u["url"]])
ref_of.close()
export_of.close()
trade_of.close()
studio_of.close()
print(failed)
