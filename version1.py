import praw
import re
import json
import time
import warnings
import schedule
import datetime
import random
warnings.filterwarnings("ignore")
print("started", flush = True)

root = "C:/Users/Owner/Documents/projects/python/bot2/"

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

class Bot:
    def __init__(self, reddit, beat, subreddit, nonce, theme, winner, vote_count, submission_id, votes_id):
        self.reddit = reddit
        self.beat = beat
        self.subreddit = subreddit
        self.nonce = nonce
        self.submission_id = submission_id
        self.votes_id = votes_id
        self.theme = theme
        self.winner = winner
        self.vote_count = vote_count
        self.new_winner = None

    def get_submissions(self):
        data = {}
        sub = self.reddit.submission(id=self.submission_id).comments
        for top_comments in sub:
            body = top_comments.body
            print(body)
            author = top_comments.author
            match = re.findall("(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", body)
            if match:
                for i in match:
                    if "soundcloud.com" in i or "https://soundcloud.app.goo.gl" in i :
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

                        data[str(author)] = new


        return data

    def count_winner(self):
        all_votes = {}
        voters = self.get_submissions()
        time.sleep(1)
        sub = self.reddit.submission(id=str(self.votes_id)).comments
        for top_comments in sub:
            vote = set()
            for votes in top_comments.replies:
                if "vote" in votes.body.lower()  and str(votes.author) not in top_comments.body:
                    vote.add(str(votes.author))

            index = top_comments.body.find("[")
            index2 = top_comments.body.find("]")
            all_votes[str(top_comments.body)[index+1:index2]] = vote
        print(all_votes)

        max = [0,0]

        for i in all_votes:
            print(all_votes[i])


        new_vote_list = {}
        for i in all_votes:
            if all_votes[i] == set():
                print("ignore set")
            else:
                new_vote_list[i] = all_votes[i]
        print(new_vote_list)

        for i in new_vote_list:
            length = len(new_vote_list[i])
            print(i, length, max[1])
            if length > max[1]:
                max = [i, len(new_vote_list[i])]
                self.winner = i
                self.vote_count = length

                print(i, "this is winner")
                with open(root + "json/arg.json") as f:
                    arg = f.read()
                    arg = json.loads(arg)

                arg["winner"] = i
                with open(root + "/json/arg.json", "w") as f:
                    arg = f.write(json.dumps(arg))
                    print("new winner saved")

        print("trying to declear winner")
        decleared = False
        for top_comment in sub:
            if decleared == False:
                print(top_comment.body)
                if top_comment.body.find(max[0]) != -1:
                    with open(root + "text/declare_winner.txt", "r") as f:
                        text = f.read()
                    print(text.format(self.vote_count))
                    top_comment.reply(text.format(self.vote_count))
                    print("winner decleared")
                    decleared = True
        self.new_winner = max[0]
        return max[0]

    def create_voting_thread(self):
        with open(root + "text/voting.txt", "r") as f:
            text = f.read()
            text = text.replace("Beat", "[Beat]({})".format(self.beat)).format(self.theme)
        with open(root + "text/voting_title.txt", "r") as f:
            title = f.read().format(self.nonce)
        test = self.reddit.subreddit(self.subreddit)
        "e9a901a0-c9e3-11e9-87d6-0e2cbfdfe800", "696563b6-b1bd-11ec-a33b-e6cb802295fa"
        test.submit(title=title, selftext=text, flair_id="696563b6-b1bd-11ec-a33b-e6cb802295fa", flair_text="Weekly Cypher")
        print("voting thread created")

    def create_submission_thread(self):
        mes = self.reddit.inbox.unread()
        for i in mes:
            i.delete()
        here = "[**Here**]({})".format(self.beat)

        with open(root + "text/sub_thrd_title.txt", "rb") as f:
            title = f.read().decode('utf-8').format(self.nonce)
        with open(root + "text/sub_thrd_body.txt", "rb") as f:
            text = f.read().decode('utf-8').format(self.winner, self.winner, self.vote_count , here, self.theme)
        test = self.reddit.subreddit(self.subreddit)
        "e9a901a0-c9e3-11e9-87d6-0e2cbfdfe800", "696563b6-b1bd-11ec-a33b-e6cb802295fa"
        test.submit(title=title, selftext= text, flair_id="696563b6-b1bd-11ec-a33b-e6cb802295fa", flair_text="Weekly Cypher")
        print("submission thread created")

    def dm_winner(self):
        with open(root + "text/dm_winner.txt", "rb") as f:
            text = f.read().decode('utf-8')

        winner = self.new_winner
        print(winner)
        self.reddit.redditor(winner).message("Request for next week's beat", text)
        print("dm sent to winner")

    def check_on_winner(self):
        print("getting unread messages")
        winner = self.winner
        print("winner", winner)
        mes = self.reddit.inbox.unread()
        beat_c = False
        theme_c = False
        for i in mes:
            if str(i.author) == str(winner):
                print("winner found", i.body)
                if re.findall("(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", i.body) and "https://soundcloud.com/mhhofficialbeats" in i.body:
                    self.beat = re.findall("(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", i.body)[0]
                    print("new beat saved", self.beat)
                    i.mark_read()
                    beat_c = True
                index = i.body.lower().find("theme:")
                last = i.body.find("\n", index)
                if index != -1:
                    if last == -1:
                        theme = i.body[index+6:]
                        self.theme = theme
                        i.delete()
                        print("new theme saved" , theme)
                        theme_c = True
                    else:
                        theme = i.body[index+6:last]
                        self.theme = theme
                        i.delete()
                        print("new theme saved", theme)
                        theme_c = True
            i.delete()

        print(beat_c, "beat_c status")
        if beat_c == False:
            print("Picking from lists")
            with open(root + "text/themes.txt", "r") as f:
                theme_list = f.readlines()
                new_theme = random.choice(theme_list)
                self.theme = new_theme
                print("saving new theme from list", new_theme)

        print(theme_c, "theme_c status")
        if theme_c == False:
            with open(root + "text/beats.txt", "r") as f:
                beat_list = f.readlines()
                new_beat = random.choice(beat_list)
                self.beat = new_beat
                print("saving new beat from list", self.beat)


    def get_id_of_new_thread(self):
        sub = self.reddit.subreddit(self.subreddit)
        posts = sub.new()
        for i in posts:
            self.submission_id = i
            print("id of submission thread recovered as {}".format(self.submission_id))
            data = {
                "id": str(i)
            }

            with open(root + "json/sub.json", "w") as f:
                f.write(json.dumps(data))
            return i

    def get_id_of_vot_thread(self):
        sub = self.reddit.subreddit(self.subreddit)
        posts = sub.new()
        for i in posts:
            self.votes_id = i
            print("id of voting thread recovered as {}".format(self.votes_id))
            data = {
                "id": str(i)
            }

            with open(root + "json/vot.json", "w") as f:
                f.write(json.dumps(data))
            return i

    def comment_in_vot_thread(self):
        contesters = self.get_submissions()
        vot_sub = self.reddit.submission(str(self.votes_id))
        print(contesters)
        for i in contesters:
            reply = "[{}]({})".format(i, contesters[i])
            print(i)
            print(contesters[i])
            vot_sub.reply(reply)
            print("commented on voting thread")
            with open(root + "text/vote_dm_body.txt") as f:
                body = f.read()
            with open(root + "text/vote_dm_title.txt") as f:
                title = f.read()
            self.reddit.redditor(str(i)).message(title, body)
            print("voting reminder sent")
            time.sleep(2)

    def save_new_details(self, final = False):
        print("saving new details")
        if final == True:
            dict ={
                "beat": self.beat,
                "theme": self.theme,
                "winner": self.winner,
                "votes": self.vote_count,
                "nonce": self.nonce +1
            }
        else:
            dict ={
                "beat": self.beat,
                "theme": self.theme,
                "winner": self.winner,
                "votes": self.vote_count,
                "nonce": self.nonce
            }
        print(dict)
        with open(root + "json/arg.json", "w") as f:
            f.write(json.dumps(dict))

    def run(self):
        while True:
            self.create_submission_thread()
            time.sleep(1)
            self.get_id_of_new_thread()
            time.sleep(80)
            self.create_voting_thread()
            time.sleep(1)
            self.get_id_of_vot_thread()
            time.sleep(1)
            self.comment_in_vot_thread()
            time.sleep(60)
            self.count_winner()
            time.sleep(2)
            self.dm_winner()
            time.sleep(120)
            self.check_on_winner()
            self.nonce += 1
            time.sleep(15)
            self.save_new_details()