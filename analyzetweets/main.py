import os
from TwitterSearch import *
from google.appengine.api import memcache, users
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import oauth

class TweetsText(db.Model):
    createdAt   = db.DateTimeProperty(auto_now_add=True)
    author      = db.UserProperty()
    companyName = db.StringProperty(required=False)
    tweetText   = db.TextProperty(required=False)

class MainHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        tweetstext = memcache.get('tweetstext')
        if not tweetstext:
            tweetstext = TweetsText.all().order('-createdAt').fetch(10)
            memcache.add('tweetstext', tweetstext)
        context = {
            'companyName': 'Tweets Analyzer',
            'user':      user,
            'tweetstext': tweetstext,
            'login':     users.create_login_url(self.request.uri),
            'logout':    users.create_logout_url(self.request.uri),
        }
        tmpl = os.path.join(os.path.dirname(__file__), 'top10tweets.html')
        self.response.out.write(render(tmpl, context))

class GetTweets(webapp.RequestHandler):
    def post(self):
      # Create object of DB
      data = TweetsText()
      # Get the company name
      companyName = 'Tweets Analyzer'
      data.companyName = companyName
      data.tweetText = self.request.get('companyName')
      # Now store the data into TweetsText DB Model
      data.put()

      #######
         #For time being
      ######
      # Get the Tweets from twitter API or From TwitterHandler
      companyName = self.request.get('companyName')
      THandler = TwitterHandler(companyName)
      tweetTextCotainer = THandler.getTweetsText()
      for tweetText in tweetTextCotainer:
        data.companyName = companyName
        data.tweetText = tweetText
        data.put()

      memcache.delete('tweetstext')
      self.redirect('/')

class TwitterHandler():
  def __init__(self, companyName):
    self.textTweet = []
    self.cName = companyName
    #access key for twitter api
    self.api_key = "RXJWocF9m1fMfQnlP2ua7rG8v"
    self.api_secret = "mCg63ep6GA35KU5lYmd0NOmgb6q1iEP9Ywg03DTuiEYZc32Cd6"
    self.access_token_key = "283141461-x1XViSBImLaHxx5L6CwNlUoV5gVEQ562rjGTyrEA"
    self.access_token_secret = "DfXbSTG8v3lFRsJlRwaRjYxdi7NVFiNmX8VS0uV4ydOHZ"

  # it's about time to create a TwitterSearch object with our secret tokens
  def getTweetsText(self):
    tso = TwitterSearchOrder() # create a TwitterSearchOrder object
    tso.setKeywords(['krishna']) # let's define all words we would like to have a look for
    tso.setLanguage('en') # we want to see German tweets only
    tso.setCount(7) # please dear Mr Twitter, only give us 7 results per page
    tso.setIncludeEntities(False) # and don't give us all those entity information

    ts = TwitterSearch(
      consumer_key = self.api_key,
      consumer_secret = self.api_secret,
      access_token = self.access_token_key,
      access_token_secret = self.access_token_secret
      )
    for tweet in ts.searchTweetsIterable(tso): # this is where the fun actually starts :)
      #print '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text']
      self.textTweet.append('@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )

    return self.textTweet

application = webapp.WSGIApplication([
    ( '/', MainHandler),
    ( '/gettweets', GetTweets),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
