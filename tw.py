# import twint
from paper import Story, Tweet, tweets
import os, subprocess
import urllib
from tqdm import tqdm
import json
from pprint import pprint
# # Configure
# c = twint.Config()
# c.Search = "https://www.nytimes.com/2018/01/02/world/asia/pakistan-trump-tweet.html"
# c.Format = '{"tweet_id": "{id}", "tweet": "{tweet}", "username":"{username}", "replies_count":"{replies_count}", "retweets_count":"{retweets_count}"}'

# # Run
# twint.run.Search(c)



au = Story.query.all()
for story in tqdm(au):
    url = story.url

    encurl = urllib.parse.quote_plus(url)
    jfile = "twitdata/"+encurl+".json"
    exists = os.path.isfile(jfile)

    if exists:
        with open(jfile) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            for line in tqdm(content):
                data = json.loads(line)
                username = data['username']
                text = data['tweet']
                likes =  data['likes_count']
                retweets =  data['retweets_count']
                replies =  data['replies_count']
                link = data['link']
                ex = Tweet.query.filter_by(link=link).all()
                if not ex:
                    t = Tweet(username=username, text=text, likes=likes, retweets=retweets, replies=replies, link=link)
                    story.tweets.append(t)
                    db.session.commit()
                    
    #subprocess.Popen(['twint', '-s', url, '-o', "twitdata/"+encurl+'.json', '--json'])