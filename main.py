"""
# bot to scrape entire monster hunter mhrise subreddit, figure out if there's
  trend going on

"""

import sys
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
    subreddits = [
        "MonsterHunter",
        "MHRise",
        "MonsterHunterMeta"
    ]

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
        limit = 100
        for name in self.subreddits:
            after = "="
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
def clean(sentence):
    return re.sub("[^'a-zA-Z\\d:]", " ", sentence)


def tokenize(sentence):
    n1 = [word.lower().strip() for word in clean(sentence).split(" ")]
    n2 = [f"{n1[i]} {n1[i+1]}" for i in range(len(n1) - 2 + 1)]
    return n2


def tokenizeSentences(a):
    return [w for i in a for w in tokenize(i)]


class Stuff:

    def tf_idf(self, corpus):
        tf = Counter(
            [w for documents in corpus for w in tokenizeSentences(documents)])
        df = {}
        for documents in corpus:
            ws = set(tokenizeSentences(documents))
            for w in ws:
                if w in df:
                    df[w].append(documents)
                else:
                    df[w] = [documents]
        len_doc = len(corpus)
        idf = {i: math.log(len_doc / len(df[i])) for i in df}
        tf_idf = {i: math.log(tf[i]) * idf[i] for i in idf}
        sorted_tf_idf = {k: v for k, v in sorted(
            tf_idf.items(), key=lambda x: -x[1])}
        return sorted_tf_idf, tf

    def wac(self):
        path = "/mnt/SSDee/work/baking/redditmhbot/filtered/"
        filenames = os.listdir(path)
        curr = int(time.time())
        wac = sorted([(int(i[:10]), i)
                      for i in filenames], key=lambda x: curr - x[0])

        a = {}
        for _, name in wac:
            with open(path + name, "r") as f:
                data = json.load(f)
                for i in data["parents"]:
                    a[i] = [data["parents"][i]]

                for comment in data["comments"]:
                    a[comment["parent_id"]].append(comment["body"])

                sorted_tf_idf, tf = self.tf_idf([a[i] for i in a])


if __name__ == '__main__':
    try:
        action = sys.argv[1]
        if action == "scrape":
            a = Scraper()
            a.scrapeAllComments(10000)
        elif action == "idf":
            a = Stuff()
            a.wac()
    except IndexError:
        a = Stuff()
        a.wac()
        # print("what's up dude")
# a = Stuff()
# a.wac()
