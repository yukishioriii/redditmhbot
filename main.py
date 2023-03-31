"""
# bot to scrape entire monster hunter mhrise subreddit, figure out if there's
  trend going on

"""

import requests
import json
from tqdm import tqdm
import re
import time
import os
from collections import Counter
import math

HEADERS = {
    "User-Agent": "python:com.example.trendseeker:v0.0.1 (by /u/No_Musician_4234)"
}

WEAPONS = [
    ("ls", "longsword"),
    ("sns", "swordandshield", "swordnshield"),
    ("db", "dualblade"),
    ("ham", "hammer"),
    ("hh", "huntinghorn"),
    ("lance", "lance"),
    ("gl", "gunlance"),
    ("swax", "switchaxe"),
    ("cb", "chargeblade"),
    ("ig", "insectglaive"),
    ("lbg", "lightbowgun"),
    ("hbg", "heavybowgun"),
    ("bow", "bow"),
    ("gs", "greatsword"),

]


def getWeaponType(string):
    for nicknames in WEAPONS:
        if any([name in re.sub("[^0-9a-zA-Z]+", "", string).lower() for name in nicknames]):
            return nicknames[0]
    return None


class Scraper:
    subreddits = ["MHRise"]

    def _getUserMetadata(self, child, filtered):
        user_id = child.get("author")
        if user_id not in filtered["users"]:
            filtered["users"][user_id] = {}
            for attr in child:
                if "author" in attr.lower():
                    filtered["users"][user_id][attr] = child[attr]

    def _getParentMetadata(self, child, filtered):
        parent_id = child.get("link_id")  # parent's id
        title = child.get("link_title")
        if parent_id not in filtered["parents"]:
            filtered["parents"][parent_id] = title

    def _getCommentMetadata(self, child, filtered):
        name = child.get("name")  # post's id
        body = child.get("body")  # actual comment
        author = child.get("author")
        parent_id = child.get("link_id")

        filtered["comments"].append({
            "name": name,
            "body": body,
            "author": author,
            "parent_id": parent_id
        })

    def scrapeAllComments(self, total=100):
        after = "="
        limit = 100

        for name in self.subreddits:
            filtered = {
                "parents": {},
                "comments": [],
                "users": {}
            }
            url = f"https://dm.reddit.com/r/{name}/comments.json?limit={limit}&count=100&after=="
            now = int(time.time())
            os.makedirs(f"./raw/{now}")
            for _ in tqdm(range(0, total, limit)):
                try:
                    res = requests.get(url, headers=HEADERS)
                    data = res.json()
                    url = url[:-len(after)] + data.get("data").get("after")
                    after = data.get("data").get("after")
                    for child in data["data"].get("children"):
                        child = child.get("data")
                        self._getCommentMetadata(child, filtered)
                        self._getParentMetadata(child, filtered)
                        self._getUserMetadata(child, filtered)

                    with open(f"./raw/{now}/{after}.json", "w+") as f:
                        f.write(json.dumps(data))

                except Exception as e:
                    print(f"ERROR: something happened {e}")
                    break

            with open(f"./filtered/{int(time.time())}_{name}.json", "w+") as f:
                f.write(json.dumps(filtered))


# a = Scraper()
# a.scrapeAllComments(10000)

def tokenize(sentence):
    return [word.lower().strip() for word in sentence.split(" ")]


class Stuff:

    def tf(self, document):
        pass

    def idf(self, documents):

        df = {}
        for doc in documents:
            ws = set(tokenize(doc))
            for w in ws:
                if w in df:
                    df[w] += 1
                else:
                    df[w] = 1
        len_doc = len(documents)
        idf = {i: math.log(len_doc / df[i]) for i in df}
        sorted_idf = {k: v for k, v in sorted(idf.items(), key=lambda item: -item[1])}
        return sorted_idf

    def tf_idf(self, wat):
        pass

    def wac(self):
        with open("/Users/ando/work/baking/redditbot/filtered/1680231634_MHRise.json", "r") as f:
            data = json.load(f)
            comments = data["comments"]
            comments = [re.sub("[^'a-zA-Z\\d:]", " ", a["body"]) for a in comments]
            idf = self.idf(comments)

            print()


a = Stuff()
a.wac()
