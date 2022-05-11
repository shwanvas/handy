import feedparser
from flask import Flask, render_template, request
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from newspaper import Article
import nltk
nltk.download('punkt')
from flask_paginate import Pagination, get_page_args


def get_bbc_text(url):
    """Parse bbc article and return text in list of string"""
    article=Article(url, language="en")
    article.download()
    article.parse()
    article.nlp()
    return article.title,article.text,article.top_image


app = Flask(__name__)

RSS_FEEDS = [
    'https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms',
    'https://www.indiatoday.in/rss/home'
]


@app.route("/")
@app.route("/home")
def index():
    page = int(request.args.get('page', 1))
    per_page = 9
    offset = (page - 1) * per_page
    pagination_articles = get_articles(offset=offset, per_page=per_page)
    keys = feed[0][0].keys()
    source=feed[1]
    pagination = Pagination(page=page, total=len(feed[0]), per_page=per_page, record_name='articles', css_framework='bootstrap5')
    return render_template("index.html", keys=keys, articles=pagination_articles, pagination=pagination, page=page, per_page=int(per_page),source=source)


@app.route("/extract")
def extract():
    feedid = request.args.get('feedId')
    parsed = get_bbc_text(feedid)
    return render_template("handyextract.html", body=parsed[1], title=parsed[0], image=parsed[2])


@app.route("/travel")
def travel():
    url = "http://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    publication = "Travel"
    paginate = paginat(url)
    return render_template("publication.html", publication=publication, articles=paginate[1][1], pagination=paginate[0], page=paginate[2], per_page=int(paginate[3]),source=feed[1])

@app.route("/india")
def india():
    url = "http://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms"
    publication = "India"
    paginate = paginat(url)
    return render_template("publication.html", publication=publication, articles=paginate[1][1], pagination=paginate[0], page=paginate[2], per_page=int(paginate[3]),source=feed[1])


@app.route("/world")
def world():
    url = "http://timesofindia.indiatimes.com/rssfeeds/296589292.cms"
    publication = "World"
    paginate = paginat(url)
    return render_template("publication.html", publication=publication, articles=paginate[1][1], pagination=paginate[0], page=paginate[2], per_page=int(paginate[3]),source=feed[1])


@app.route("/sports")
def sports():
    url = "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms"
    publication = "Sports"
    paginate = paginat(url)
    return render_template("publication.html", publication=publication, articles=paginate[1][1], pagination=paginate[0], page=paginate[2], per_page=int(paginate[3]),source=feed[1])


@app.route("/political")
def political():
    url = "https://www.news18.com/rss/politics.xml"
    publication = "Political"
    paginate = paginat(url)
    articles = paginate[1][1]
    

    return render_template("publication.html", publication=publication, articles=articles, pagination=paginate[0], page=paginate[2], per_page=int(paginate[3]),source=paginate[1])


def paginat(url):
    page = int(request.args.get('page', 1))
    per_page = 12
    offset = (page - 1) * per_page
    pagination_articles = get_feed_specific(
        url, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, total=len(
        pagination_articles[1]), per_page=per_page, record_name='articles', css_framework='bootstrap5')
    return pagination, pagination_articles, page, per_page


def get_feed_specific(url, offset=0, per_page=5):
    posts = []
    feed = feedparser.parse(url)
    for post in feed.entries:
        posts.append((post))
    return [posts[offset:offset+per_page], posts,feed.feed.title]

import html
def get_feed():
    posts = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for post in feed.entries:
            posts.append((post))
    

    return posts,feed.feed.title


feed = get_feed()
# pagination


def get_articles(offset=0, per_page=5):
    return feed[0][offset:offset+per_page]


if __name__ == "__main__":
    app.run(port=5000, debug=False)
