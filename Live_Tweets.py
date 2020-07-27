#!/usr/bin/env python
# coding: utf-8
# In[1]:
# Import packages
import tweepy, json, re, time, string
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read in the Twitter API login credentials
login = pd.read_csv('twitter_login.csv')

# Store OAuth authentication credentials in relevant variables
consumer_key = login['keys'][0]
consumer_secret = login['keys'][1]
access_token = login['keys'][2]
access_token_secret = login['keys'][3]

#%%
# Pass OAuth details to tweepy's OAuth handler
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token,access_token_secret)

#Listener Class to store tweets to .txt file
class MyStreamListener(tweepy.StreamListener):
    def __init__(self, api=None):
        super(MyStreamListener, self).__init__()
        self.num_tweets = 0
        self.file = open("tweets.txt", "w")
        self.start = time.time()

    def on_status(self, status):
        tweet = status._json
        self.file.write( json.dumps(tweet) + '\n' )
        self.num_tweets += 1
        
        if(time.time()-self.start<180):
            if(self.num_tweets%500==0):
                print('Tweets Recorded: '+str(self.num_tweets))
                print('Time Elapsed: '+str(round(time.time()-self.start))+'s')
        #if self.num_tweets < 500:
            return True
        else:
            return False
        self.file.close()

    def on_error(self, status):
        print(status)

        
# clean tweets
def clean_tweets(tweet):
    #tweet = re.sub(r'@\S+','',tweet)            #remove mentions
    tweet = re.sub(r'#','',tweet)               #remove hashtags
    tweet = re.sub(r'RT\s+','',tweet)           #remove RT 
    #tweet = re.sub(r'https?:\/\/\S+','',tweet)  #remove hyperlinks
    tweet = re.sub(r'\'','',tweet)               #remove quotes
    tweet = re.sub(r'\’','',tweet)
    tweet = re.sub(r"’",'',tweet)
    return tweet

#Function to match a word in a tweet        
def word_in_text(word, text):
    word = word.lower()
    text = text.lower()
    match = re.search(word, text)

    if match:
        return True
    return False


def track_tweets(*args):
    
    tracking_list=[]
    for arg in args:
        tracking_list.append(arg)

    # Initialize Stream listener
    l = MyStreamListener()

    # Create your Stream object with authentication
    stream = tweepy.Stream(auth, l)

    # Filter Twitter Streams to capture data by the keywords:
    stream.filter(track=tracking_list, languages=['en'])

    # String of path to file: tweets_data_path
    tweets_data_path='tweets.txt'

    # Initialize empty list to store tweets: tweets_data
    tweets_data=[]

    # Open connection to file
    tweets_file = open(tweets_data_path, "r")

    # Read in tweets and store in list: tweets_data
    for line in tweets_file:
        tweet=json.loads(line)
        tweets_data.append(tweet)

    # Close connection to file
    tweets_file.close()

    # "If max_cols is exceeded, switch to truncate view"
    pd.set_option('display.max_columns', 5400)
    # "The maximum width in characters of a column"
    pd.set_option('display.max_colwidth', 500)

    # Build DataFrame of tweet texts and languages
    df = pd.DataFrame(tweets_data, columns=['text','lang'])

    # Initialize list to store tweet counts
    length=len(tracking_list) 
    arr=[0]*(length)

    df['text'] = df['text'].apply(clean_tweets)

    # Print head of DataFrame
    print(df.head())

    for string in df['text']:
        for m,n in enumerate(tracking_list):
            if word_in_text(n,string):
                arr[m]+=1
    sns.set(color_codes=True)

    # Plot the bar chart
    # %matplotlib inline
    ax = sns.barplot(tracking_list, arr)
    ax.set(ylabel="Count")
    ax.set(title="Live Twitter Traffic (3 min Interval)")
    plt.show()
    #print('Total Tweets Plotted :'+str(sum(arr)))
    return df

df=track_tweets('Facebook','Instagram','Amazon','Apple')


# %%
