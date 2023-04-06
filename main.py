"""
# bot to scrape entire monster hunter mhrise subreddit, figure out if there's a trend going on

"""

import sys
import requests
import json
import re
import time
import os
from collections import Counter
import math
import concurrent.futures
import nltk
lemma = nltk.wordnet.WordNetLemmatizer()

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
WPN_SHORT = set([i for j in WEAPONS for i in j])


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

        created = child.get("created")
        score = child.get("score")
        controversiality = child.get("controversiality")

        filtered["comments"].append({
            "name": name,
            "body": body,
            "author": author,
            "parent_id": parent_id,
            
            "created": created,
            "score": score,
            "controversiality": controversiality
        })

    def scrape(self, total, name, limit, now):
        after = "="
        filtered = {
            "parents": {},
            "comments": [],
            "users": {}
        }
        url = f"https://dm.reddit.com/r/{name}/comments.json?limit={limit}&count=100&after=="
        for _ in range(0, total, limit):
            try:
                print(url)
                res = requests.get(url, headers=HEADERS)
                data = res.json()
                url = url[:-len(after)] + data.get("data").get("after")
                after = data.get("data").get("after")
                for child in data["data"].get("children"):
                    child = child.get("data")
                    self._getCommentMetadata(child, filtered)
                    self._getParentMetadata(child, filtered)
                    self._getUserMetadata(child, filtered)

                with open(f"./raw/{now}/{name}_{after}.json", "w+") as f:
                    f.write(json.dumps(data))

            except Exception as e:
                print(f"ERROR: something happened {e}")
                break

        with open(f"./filtered/{int(time.time())}_{name}.json", "w+") as f:
            f.write(json.dumps(filtered))

    def scrapeAllComments(self, total=100):
        limit = 100
        now = int(time.time())
        os.makedirs(f"./raw/{now}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            for name in self.subreddits:
                executor.submit(self.scrape, total, name, limit, now)

            # a = Scraper()
            # a.scrapeAllComments(10000)


def clean(sentence):
    return re.sub("[^'a-zA-Zd: ]", "", sentence)


stopwords = set()
with open("stopwords.txt", "r") as f:
    stopwords = set(f.read().splitlines())


def tokenize(sentence):
    n1 = [word.lower().strip() for word in clean(sentence).split(" ") if word.lower().strip() not in stopwords]
    n1 = [lemma.lemmatize(word) if word not in WPN_SHORT else word for word in n1]
    n2 = [f"{n1[i]} {n1[i+1]}" for i in range(len(n1) - 2 + 1) if n1[i] and n1[i+1]]
    return n2


def tokenizeSentences(a):
    return [w for i in a for w in tokenize(i)]


class corpus

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
        path = "/Users/ando/work/baking/redditbot/filtered/"
        filenames = os.listdir(path)
        curr = int(time.time())
        wac = sorted([(int(i[:10]), i)
                      for i in filenames], key=lambda x: curr - x[0])

        corpus = {
            "MonsterHunter": {},
            "MHRise": {},
            "MonsterHunterMeta": {}
        }
        for _, name in wac:
            a = {}
            with open(path + name, "r") as f:
                category = name.split("_")[1].split(".")[0]

                data = json.load(f)
                for i in data["parents"]:
                    a[i] = [data["parents"][i]]

                for comment in data["comments"]:
                    a[comment["parent_id"]].append(comment["body"])
                corpus[category] = {**corpus[category], **a}

        for cat in corpus:
            print(f"______{cat}_____")
            sorted_tf_idf, tf = self.tf_idf([corpus[cat][i] for i in corpus[cat]])
            print([i for i in sorted_tf_idf][:30])



def call_scrape():
    a = Scraper()
    a.scrapeAllComments(900)

def cal_idf():
    b = Stuff()
    b.wac()

if __name__ == '__main__':
    try:
        action = sys.argv[1]
        if action == "scrape":
            a = Scraper()
            a.scrapeAllComments(900)
        elif action == "idf":
            a = Stuff()
            a.wac()
        elif action == "all":
            a = Scraper()
            a.scrapeAllComments(900)
            b = Stuff()
            b.wac()
    except IndexError:
        call_scrape()
        # a = Stuff()
        # a.wac()
        # print(stopwords)
        # print("what's up dude")
# a = Stuff()
# a.wac()














