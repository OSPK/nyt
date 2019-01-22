import os
import urllib
import json
from links import links
from newspaper import Article
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from textblob import TextBlob
import nltk.data
from tqdm import tqdm
from flask_migrate import Migrate
import pygal
from babel.dates import format_datetime
import datetime
from collections import Counter


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# db.create_all()
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]

app.config['APPLICATION_ROOT'] = '/labs/nyt-pakistan-coverage-2018'
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/labs/nyt-pakistan-coverage-2018')


def format_datetime2(value, format='medium'):
    if format == 'full':
        format="EEEE, d. MMMM y"
    elif format == 'medium':
        format="EE dd.MM.y"
    return format_datetime(value, format)

def date_to_nth_day(date, format='%Y%m%d'):
    new_year_day = datetime.datetime(year=date.year, month=1, day=1)
    return (date - new_year_day).days + 1

app.jinja_env.filters['datetime'] = format_datetime2
app.jinja_env.filters['day'] = date_to_nth_day

authors = db.Table('authors',
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True),
    db.Column('story_id', db.Integer, db.ForeignKey('story.id'), primary_key=True)
)

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('story_id', db.Integer, db.ForeignKey('story.id'), primary_key=True)
)

tweets = db.Table('tweets',
    db.Column('tweet_id', db.Integer, db.ForeignKey('tweet.id'), primary_key=True),
    db.Column('story_id', db.Integer, db.ForeignKey('story.id'), primary_key=True)
)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(280))
    title = db.Column(db.String(280))
    pub_date = db.Column(db.DateTime)
    body = db.Column(db.Text)
    entities = db.Column(db.Text)
    sentiment = db.Column(db.Numeric)
    sentiment2 = db.Column(db.Numeric)
    subjectivity = db.Column(db.Numeric)
    fb_shares =  db.Column(db.Integer)
    fb_comments =  db.Column(db.Integer)
    authors = db.relationship('Author', secondary=authors, lazy='subquery', backref=db.backref('story', lazy=True))
    tags = db.relationship('Tag', secondary=tags, lazy='subquery', backref=db.backref('story', lazy=True))
    tweets = db.relationship('Tweet', secondary=tweets, lazy='subquery', backref=db.backref('story', lazy=True))

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(120))

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(380))
    username =  db.Column(db.String(380))
    likes =  db.Column(db.Integer)
    retweets =  db.Column(db.Integer)
    replies =  db.Column(db.Integer)
    link = db.Column(db.String(980))
    sentiment =  db.Column(db.String(380))


# @app.route('/static/<path>')
# def static_file(path):
#     if path == "styles" or path == "awesomplete":
#         ff = path + ".css"
#     else:
#         ff = path + ".js"
#     print("working")
#     return app.send_static_file(ff)


@app.route("/")
def hello():
    stories = Story.query.all()
    tags = Tag.query.all()
    words = [tag.word for tag in tags]
    tagcounter = dict(Counter(words))
    badwords = ["one", "two", "three", "four", "first", "last year", "years", "Monday", "last week", "Thursday",\
                "2013","Agence France-Presse — Getty Images", "recent years", "2014", "One", "last month", \
                "this month", "second", "January", "Tuesday", "July", "2016", "dozens", "2015", "this week", \
                "thousands", "this year", "2008", "annual", "2011", "hundreds", "2012", "CreditAamir Qureshi", \
                "2010", "CreditDanial Shah", "months", "Credit", "Sunday", "Last year", "Friday", "Pakistan", "Pakistani", \
                "Pakistanis", "Wednesday", "Saturday", "The New York Times" \
            ]
    
    for word in badwords:
        del tagcounter[word]

    tagcounter =  [(k, tagcounter[k]) for k in sorted(tagcounter, key=tagcounter.get, reverse=True)]




    return render_template('home.html', stories=stories, tagcounter=tagcounter)

@app.route("/stories/")
def stories():
    stories = Story.query.all()

    return render_template('stories.html', stories=stories)


@app.route("/story/<id>")
def story(id):
    story = Story.query.get(id)

    return render_template('story.html', story=story)

@app.route("/search/", methods = ['GET', 'POST'])
def search():
    stories = Story.query.all()
    tags = Tag.query.all()
    words = [tag.word for tag in tags]
    words = list(set(words))
    searchterm = request.form.get("search")
    results = []
    if searchterm:
        for story in stories:
            if searchterm.lower() in story.body.lower():
                results.append(story.id)

    return render_template('search.html', stories=stories, words=words, results=results, searchterm=searchterm)

@app.route("/authors/")
def authors():
    authors = Author.query.all()

    austories = {}

    for author in authors:
        aid = author.id
        storiesa = Story.query.filter(Story.authors.any(id=aid)).all()
        austories[author.name] = storiesa

    return render_template('authors.html', authors=authors, austories=austories)

@app.route("/author/<id>")
def author(id):
    author = Author.query.get(id)
    stories = Story.query.filter(Story.authors.any(id=id)).all()

    return render_template('author.html', author=author, stories=stories)

# @app.route("/back")
# def back():
#     au = Story.query.all()
#     for story in tqdm(au):
#         url = story.url

#         encurl = urllib.parse.quote_plus(url)
#         jfile = "twitdata/"+encurl+".json"
#         exists = os.path.isfile(jfile)

#         if exists:
#             with open(jfile) as f:
#                 content = f.readlines()
#                 content = [x.strip() for x in content]
#                 for line in tqdm(content):
#                     data = json.loads(line)
#                     username = data['username']
#                     text = data['tweet']
#                     likes =  data['likes_count']
#                     retweets =  data['retweets_count']
#                     replies =  data['replies_count']
#                     link = data['link']
#                     ex = Tweet.query.filter_by(link=link).all()
#                     if not ex:
#                         t = Tweet(username=username, text=text, likes=likes, retweets=retweets, replies=replies, link=link)
#                         story.tweets.append(t)
#                         db.session.commit()
#     return "done"

# @app.route("/backend")
# def backend():
#     for link in tqdm(links):
#         article = Article(link)
#         article.download()
#         article.parse()

#         if "Pakistan" in article.title:
#             article.nlp()

#             url = link
#             title = article.title
#             pub_date = article.publish_date
#             authors = article.authors

#             story = Story(url=url, title=title, pub_date=pub_date, body="" )

#             for author in authors:
#                 au = Author.query.filter_by(name=author).first()
#                 if not au:
#                     p = Author(name=author)
#                     story.authors.append(p)
#                 else:
#                     au = Author.query.filter_by(name=author).all()
#                     for ass in au:
#                         story.authors.append(ass)

#             db.session.add(story)
#             db.session.commit()

            
            
            # sentences = tokenizer.tokenize(body)
            # print(sentences)
            # for sentence in sentences:
            #     blob = TextBlob(sentence)
            #     print(blob.sentiment.polarity)

            # break


    # return render_template('index.html', url=url, body=body)
    