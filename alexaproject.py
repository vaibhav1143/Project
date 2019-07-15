#!/usr/bin/env python

import urllib
import json
import os
import re
import feedparser
from datetime import time
from datetime import datetime
from flask import Flask
from flask import request
from flask import make_response
import twitter
api = twitter.Api(consumer_key=' ',  consumer_secret=' ',    access_token_key=' ',    access_token_secret=' ')// twitter api

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    if req.get("queryResult").get("action") == "news":
        queryResult = req.get("queryResult")
        parameters = queryResult["parameters"]
        username = parameters["topic"]
        url ='http://news.yahoo.com/rss/'
        res= getHeadlines(url)
        return res
    elif req.get("queryResult").get("action")== "username":
        queryResult = req.get("queryResult")
        parameters = queryResult["parameters"]
        username = parameters["username"]
        number_to = parameters["number"]
        number_to_return = int(number_to)
        res = fetchTweets(username, number_to_return)
        return res
    else:
        {}

def getHeadlines(url):
    headlines = []
    feed = feedparser.parse(url)
    for newsitem in feed['items']:
        headlines.append(newsitem['title'])
    print(headlines)
    return{
               "fulfillmentText":str(headlines)
         }

def fetchTweets(username, number_to_return):
    statuses = api.GetUserTimeline(screen_name=username)
    timeline = [s.text for s in statuses]
    result =[]
    messages = []
    i = 0
    while i < number_to_return:
        messages.append( timeline[i] )
        result= re.sub(r"http\S+","",str(messages))
        msg= lambda result: re.compile('\#').sub('', re.compile('RT @').sub('@', result).strip())
        i += 1

    print(msg(result))

    return {
            "fulfillmentText":(msg(result))
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
