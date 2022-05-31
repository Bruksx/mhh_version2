from version1 import Bot
import random
import time
import json
import praw
import re
import schedule
from datetime import datetime, timedelta

class TeamBot(Bot):
    def get_id(self, file):
        with open(root + file, "r") as f:
            id = json.loads(f.read())
        return id.get("id")

    def get_value(self, key, file):
        with open(root + file, "r") as f:
            data = json.loads(f.read())
        value = data.get(key)
        return value

    def get_teams(self):
        id = self.get_id("json/col.json")
        all_comments = self.reddit.submission(id=id).comments
        producer_list = []
        emc_list = []

        for comment in all_comments:
            if comment.body.lower().strip() == "emcee":
                emc_list.append(str(comment.author))
            if comment.body.lower().strip() == "producer":
                producer_list.append(str(comment.author))
        shorter = min(producer_list, emc_list, key=len)
        longer = max(producer_list, emc_list, key=len)
        longer = longer[:len(shorter)]
        #print("Original list")
        #print("producer list",producer_list)
        #print("emc list", emc_list)
        producer_list = producer_list[: len(shorter)]
        emc_list = emc_list[: len(shorter)]
        #print("After slicing")
        #print("producer list",producer_list)
        #print("emc list", emc_list)
        random.shuffle(producer_list)
        random.shuffle(emc_list)
        #print("after shuffle")
        #print(producer_list, emc_list)
        teams = {}
        for a,b in zip(producer_list, emc_list):
            teams[f"{str(a)} {str(b)}"] = [a, b]
        #print(teams)
        with open(root + "json/teams.json", "w") as f:
            f.write(json.dumps(teams))
        return teams


    def post_collection_thread(self):
        with open(root+ "text/sign_up_title.txt") as f:
            title = f.read().format(self.nonce)
        with open(root+ "text/sign_up_thread.txt") as f:
            text = f.read()
        sub = self.reddit.subreddit(self.subreddit)
        thrd = sub.submit(title=title, selftext=text, flair_id="696563b6-b1bd-11ec-a33b-e6cb802295fa", flair_text="MHH TEAMS")
        print(self.save_id(thrd, "json/col.json"))
        return thrd

    def create_submission_thread(self):
        print("create sub thread")
        with open(root+ "text/sub_thrd_title.txt") as f:
            title = f.read().format(self.nonce)
        with open(root+ "text/sub_thrd_body.txt") as f:
            text = f.read().format(self.theme)
        sub = self.reddit.subreddit(self.subreddit)
        thrd = sub.submit(title=title, selftext=text, flair_id="696563b6-b1bd-11ec-a33b-e6cb802295fa", flair_text="MHH TEAMS")
        print(self.save_id(thrd, "json/sub.json"))
        return thrd

    def save_id(self, id, file):
        data = {
            "id": str(id)
        }
        with open(root + file, "w") as f:
            f.write(json.dumps(data))
        return f"saved id to {file}"

    def save_key(self, key, file, new_value):
        with open(root + file, "r") as f:
            data = json.loads(f.read())
            data[key] = new_value
        with open(root + file, "w") as f:
            f.write(json.dumps(data))
            print(f"saved new {key} to {file}")

    def comment_on_sub_thread(self):
        id = self.get_id("json/sub.json")
        thrd = self.reddit.submission(id=id)
        teams = self.get_teams()
        with open(root+ "text/submission_comment.txt", "r") as f:
            reply = f.read()
        number = 1
        for i in teams:
            list = i.split(" ")
            producer = list[0]
            emc = list[1]
            thrd.reply(reply.format(number, producer, emc))
            print("commented on submission thread")
            number += 1

    def create_voting_thread(self):
        print("create vot thread")
        with open(root+ "text/voting_title.txt") as f:
            title = f.read().format(self.nonce)
        with open(root+ "text/voting.txt") as f:
            text = f.read()
        sub = self.reddit.subreddit(self.subreddit)
        thrd = sub.submit(title=title, selftext=text, flair_id="696563b6-b1bd-11ec-a33b-e6cb802295fa", flair_text="MHH TEAMS")
        print(self.save_id(thrd, "json/vot.json"))
        return thrd

    def comment_in_vot_thread(self):
        id = self.get_id("json/vot.json")
        thrd = self.reddit.submission(id=id)
        beats = self.get_beats()
        print(beats)
        with open(root+ "text/submission_comment2.txt", "r") as f:
            reply = f.read()
        number = 1
        for i in beats:
            list = i.split(" ")
            producer = list[0]
            emc = list[1]
            beat = beats[i][2]
            thrd.reply(reply.format(number, producer, emc, beat))
            print("commented on voting thread")
            number += 1
        self.save_id(id, "json/vot.json")

    def get_beats(self):
        id = self.get_id("json/sub.json")
        all_comments = self.reddit.submission(id=id).comments
        with open (root + "json/teams.json", "r") as f:
            teams = json.loads(f.read())
        for comment in all_comments:
            for reply in comment.replies:
                print(reply.body)
                match = re.findall("(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", reply.body)
                if match:
                    for i in match:
                        if "soundcloud.com" in i or "https://soundcloud.app.goo.gl" in i:
                            first = i.find(")")
                            if first != -1:
                                new = i[:first]
                            else:
                                new = i
                            first = new.find("]")
                            if first != -1:
                                new = new[:first]
                            else:
                                new = new
                            for key in teams:
                                if str(reply.author) in teams[key]:
                                    teams[key].append(new)
                                    teams[key].append(reply.created_utc)
        return teams

    def count_winner(self):
        id = self.get_id("json/vot.json")
        thrd = self.reddit.submission(id=id)
        data = {}
        for comment in thrd.comments:
            text = comment.body
            text_list = text.split("\n")
            producer_text = text_list[2]
            emc_text = text_list[4]
            producer = producer_text[14:]
            emc = emc_text[11:]
            team = f"{producer} {emc}"
            votes = set()
            count = 0
            for reply in comment.replies:
                if reply.body.strip().lower() == "vote":
                    print("vote seen")
                    votes.add(reply.author)
                    count += 1
            if count == 0:
                pass
            else:
                data[team] = votes
        maxValue = max(data.values())
        num_of_votes = len(maxValue)
        print("max",num_of_votes)
        self.save_key("votes", "json/arg.json", num_of_votes)
        result = [k for k, v in data.items() if v == maxValue]
        print(result)
        if len(result) > 1:
            submissions = self.get_beats()
            print(submissions)
            data = {}
            for team in result:
                data[team] = submissions[team][3]
            print(data)
            winner = min(data.values())
            for key in data:
                if data[key] == winner:
                    winning_team = key
            self.save_key("winner", "json/arg.json", key)
            return [[winning_team],num_of_votes]
        else:
            self.save_key("winner", "json/arg.json", result[0])
            return [result, num_of_votes]

    def declare_winner(self):
        winners = self.get_value("winner", "json/arg.json")
        vote_count = self.vote_count
        id = self.get_id("json/vot.json")
        thrd = self.reddit.submission(id=id)
        for comment in thrd.comments:
            text = comment.body
            text_list = text.split("\n")
            producer_text = text_list[2]
            emc_text = text_list[4]
            producer = producer_text[14:]
            emc = emc_text[11:]
            team = f"{producer} {emc}"
            if team == winners:
                print("winner found")
                with open(root + "text/declare_winner.txt", "r") as f:
                    text = f.read()
                    comment.reply(text.format(vote_count, producer))
                    print("winner decleared")
                with open(root + "text/dm_winner.txt", "rb") as f:
                    text = f.read().decode('utf-8')
                producer = winners.split()[0]
                print(producer)
                self.reddit.redditor(producer).message("Request for next week's theme", text)
                print("dm sent to winner")

    def check_on_winner(self):
        winners = self.get_value("winner", "json/arg.json")
        producer = winners.split()[0]
        mes = self.reddit.inbox.all(limit = 5)
        theme_c = None
        for dm in mes:
            print(dm.author)
            if str(dm.author) == producer and "#" in dm.body:
                new_theme = dm.body[1:]
                theme_c = True
                print("new theme found", new_theme)
                self.save_key("theme", "json/arg.json", new_theme)
                break
        if not theme_c:
            with open(root + "text/themes.txt", "r") as f:
                beat_list = f.readlines()
                new_beat = random.choice(beat_list)
                self.beat = new_beat
                print(f"saving new theme from list '{self.beat}'")
        self.save_key("nonce", "json/arg.json", self.nonce + 1)

    def get_today(self):
        d = datetime.today()
        return d.day

    def get_future(self):
        d = datetime.today()
        span = timedelta(days = +4)
        new = d + span
        return new.day

    def run(self):
        #self.post_collection_thread()
        #time.sleep(180)
        #self.create_submission_thread()
        #self.comment_on_sub_thread()
        #time.sleep(150)
        #self.create_voting_thread()
        #self.comment_in_vot_thread()
        #time.sleep(180)
        #self.count_winner()
        #self.declare_winner()
        #time.sleep(150)
        self.check_on_winner()

root = "/home/MHHOfficialBot/mhh_version2/"

with open(root + "json/arg.json") as f:
    arg = f.read()
arg = json.loads(arg)

beat = arg["beat"]
theme = arg["theme"]
winner = arg["winner"]
votes = arg["votes"]
nonce = arg["nonce"]

with open(root + "json/sub.json", "r") as f:
    sub = json.loads(f.read())
with open(root + "json/vot.json", "r") as f:
    vot = json.loads(f.read())
with open(root + "json/var.json") as f:
    var = f.read()
var = json.loads(var)

reddit = praw.Reddit(
    client_id = var["id"],
    client_secret = var["secret"],
    user_agent = "teast sa",
    username = var["username"],
    password = var["password"],
)

"makinghiphop"
test_bot = TeamBot(reddit, beat, "test_bruks_bot", nonce, theme , winner, votes,sub.get("id"), vot.get("id"))
#print(test_bot.get_future())

def job():
    if test_bot.get_today() == test_bot.get_value("signup", "json/schedule.json"):
        test_bot.post_collection_thread()
        new = test_bot.get_future()
        test_bot.save_key("signup", "json/schedule.json", new)
    else:
        print("not today")
        exit()

def job2():
    if test_bot.get_today() == test_bot.get_value("submission", "json/schedule.json"):
        test_bot.create_submission_thread()
        test_bot.comment_on_sub_thread()
        new = test_bot.get_future()
        test_bot.save_key("submission", "json/schedule.json", new)
    else:
        print("not today")
        exit()

def job3():
    if test_bot.get_today() == test_bot.get_value("voting", "json/schedule.json"):
        test_bot.create_voting_thread()
        test_bot.comment_in_vot_thread()
        new = test_bot.get_future()
        test_bot.save_key("voting", "json/schedule.json", new)
    else:
        print("not today")
        exit()

def job4():
    if test_bot.get_today() == test_bot.get_value("declare", "json/schedule.json"):
        test_bot.count_winner()
        test_bot.declare_winner()
        new = test_bot.get_future()
        test_bot.save_key("declare", "json/schedule.json", new)
    else:
        print("not today")
        exit()

def job5():
    if test_bot.get_today() == test_bot.get_value("checkon", "json/schedule.json"):
        test_bot.check_on_winner()
        new = test_bot.get_future()
        test_bot.save_key("checkon", "json/schedule.json", new)
    else:
        print("not today")
        exit()

#job()

schedule.every().day.at("17:25").do(job)
schedule.every().day.at("17:26").do(job2)
schedule.every().day.at("17:27").do(job3)
schedule.every().day.at("17:28").do(job4)
schedule.every().day.at("15:30").do(job5)
while True:
    schedule.run_pending()
