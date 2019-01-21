from textblob import TextBlob
from paper import Story, db, Tag, Tweet
import numpy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tqdm import tqdm
import spacy
from collections import Counter
import requests
import json

analyzer = SentimentIntensityAnalyzer()
nlp = spacy.load('en_core_web_sm')



# # Sentiments
# stories = Story.query.all()
# for story in tqdm(stories):
#     txbl = TextBlob(story.body)
#     sentp = []
#     if story.body:
#         for sentence in txbl.sentences:
#             vs = analyzer.polarity_scores(sentence)
#             sentp.append(vs.get("compound"))

#         story.sentiment = numpy.mean(sentp)
#         db.session.commit()

# # Entitites
# for story in tqdm(stories):
#     txbl = TextBlob(story.body)
#     entities = []
#     if story.body:
#         for sentence in txbl.sentences:
#             doc = nlp(str(sentence).strip())
#             for ent in doc.ents:
#                 tag = (ent.text).replace("\n", "")
#                 if tag:
#                     p = Tag(word=tag)
#                     story.tags.append(p)
#                     entities.append(tag)

#         story.entities = str(list(set(entities)))
#         db.session.commit()

# #Count Tags
# tags = Tag.query.all()
# words = [tag.word for tag in tags]
# counter = dict(Counter(words))
# for x, v in counter.items():
#     if v > 0:
#         print(v,x)

# # Tweet Sentiments
# tweets = Tweet.query.all()
# for tweet in tqdm(tweets):
#     text = tweet.text
#     if text:
#         vs = analyzer.polarity_scores(text)
#         tweet.sentiment = vs.get("compound")
#         db.session.commit()

# Objectivity
# stories = Story.query.all()
# for story in tqdm(stories):
#     txbl = TextBlob(story.body)
#     sentp = []
#     if story.body:
#         for sentence in txbl.sentences:
#             sentp.append(sentence.sentiment.subjectivity)

#         story.subjectivity = numpy.mean(sentp)
#         db.session.commit()

# Sentiment Blob
# stories = Story.query.all()
# for story in tqdm(stories):
#     txbl = TextBlob(story.body)
#     sentp = []
#     if story.body:
#         for sentence in txbl.sentences:
#             sentp.append(sentence.sentiment.polarity)

#         story.sentiment2 = numpy.mean(sentp)
#         db.session.commit()

# Facebook Count
stories = Story.query.all()
for story in tqdm(stories):
    if story.id > 85:
        endpoint = "https://graph.facebook.com/?id={}".format(story.url)
        resp = requests.get(endpoint)
        data = json.loads(resp.text)
        shares = data['share']['share_count']
        comments = data['share']['comment_count']
        story.fb_shares =  shares
        story.fb_comments = comments
        db.session.commit()