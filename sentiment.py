#Python Project : Twitter Sentiment Analysis
#Group Members :
#    1. Shraddha Dharmik
#    2. Sagar Vadsola
#    3. Vinod Sawant
#    4. Suyash Mudholkar


#Dependencies
from flask import Flask, render_template, request, redirect, url_for
from tweepy import OAuthHandler
import tweepy
import time
import pandas as pd
from textblob import TextBlob
import re


#For plotting
import cv2
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import os

#Class Sentiment
class Sentiment :
    
    #Initialize topic
    def __init__(self, topic) :
        self.topic = topic
    
    #Establish connection with 'TWEEPY API'
    def establish_connection(self) :
        #Access Keys and token
        access_token = "1142655619951804416-MeKfqh9c6jeaaAGIAqt2xGLpilyQt9"
        access_secret = "5oq2qbnqWt9UualX6UVHDxy0p8jJ9UXhxAk5vJnAneVxY"
        
        #Consumer key and secret
        consumer_key = "TeaEPSW9vmjBiki3F5v63luPL"
        consumer_secret = "WqWfUBQxA55JSywVa3faJ3Cc8FkCTCwKClLhfa3hS26FesvbFp"
        
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        
        self.api = tweepy.API(auth, wait_on_rate_limit= True, wait_on_rate_limit_notify= True)
        
    #Function to search tweets based on user search query
    def search_tweets(self) :
        
        self.is_invalidsearch = False
        #Function call to establish connection
        self.establish_connection();
        self.searchquery = self.topic
        
        #Get search results by calling the API
        self.users = tweepy.Cursor(self.api.search, q=self.searchquery).items()
        
        #Counters dictionary to keep the count of various parameters
        self.counters = {'count' : 0,  'waittime' : 2.0, 'totalnumber' : 20, 'waitquery' : 50, 'justincase' : 1,  'secondcount' : 0,  'errorcount' : 0 }
        
        #Lists to store tweets
        self.text = [0] * self.counters['totalnumber']
        #List to assign sentiment value
        self.sentiment_values = [0] * self.counters['totalnumber']
        self.retweet_count = [0] * self.counters['totalnumber']
        self.liked_count = [0] * self.counters['totalnumber']
        self.sensitive_count = [0] * self.counters['totalnumber']
        
        #Code to extract useful tweets based on Language and to not include Retweets
        while self.counters['secondcount'] < self.counters['totalnumber'] :
            try :
                self.user = next(self.users)
                self.counters['count'] += 1
                
                if (self.counters['count'] % self.counters['waitquery'] == 0) :
                    time.sleep(self.counters['waittime'])
            
            except tweepy.TweepError :
                print("Sleeping....")
                time.sleep(60*self.counters['justincase'])
                self.user = next(self.users)
                
            except StopIteration :
                break
            
            try :
                self.text_value = self.user._json['text']
                self.language = self.user._json['lang']
                
                if "RT" not in self.text_value :
                    if self.language == 'en' :
                        self.text[self.counters['secondcount']] = self.text_value
                        self.retweet_count[self.counters['secondcount']] = self.user._json['retweet_count']
                        self.liked_count[self.counters['secondcount']] = self.user._json['favorite_count']
                        self.counters['secondcount'] += 1
            except UnicodeEncodeError :
                self.counters['errorcount'] += 1
                print("UnicodeEncodeError, errorcount =", self.counters['errorcount'])
                
        self.d = {"text" : self.text, "sentiment " : self.sentiment_values, "retweets" : self.retweet_count, 
                  "likes" : self.liked_count, "sensitive" : self.sensitive_count}
        self.df = pd.DataFrame(data = self.d)
        
        if self.df['text'][0] == 0 :
            self.is_invalidsearch = True
        
    ################################ 2) CODE TO KNOW ABT % POS AND NEG ######################
    
    def sentiment_analysis(self) :
        self.user_sentiment = {}
        self.search_tweets()
#        self.df = pd.read_excel('C:/Python/Twitter Sentiment Analysis/ML100.xlsx')
        if self.is_invalidsearch == False :
            #cleaning data
            self.cleanedtweet_list = []
            for i in range(0,self.df.shape[0]):
                text = self.df['text'][i]
                z = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text)
                self.cleanedtweet_list.append(z)
            
            #inserting cleaned tweets in dataframe
            self.df['cleaned tweets'] = self.cleanedtweet_list
            
            
            #sentiment variables
            self.sentiment_variables = {'positive' : 0, 'negative' : 0, 'neutral' : 0 }
            
            
            #taking out all types of sentiments
            for i in range(0,self.df.shape[0]):
                self.text = self.df['cleaned tweets'][i]
                self.blob = TextBlob(self.text)
                self.bsp = self.blob.sentiment.polarity   # bsp = blob sentiment polariry
                if self.bsp == 0:
                    self.sentiment_variables['neutral'] += 1
                elif self.bsp > 0:
                    self.sentiment_variables['positive'] += 1
                elif self.bsp < 0:
                    self.sentiment_variables['negative'] += 1
                  
            self.total = self.sentiment_variables['positive']+ self.sentiment_variables['negative'] + self.sentiment_variables['neutral']
            self.positive_percent = round((self.sentiment_variables['positive']/self.total)*100, 2)
            self.negative_percent = round((self.sentiment_variables['negative']/self.total)*100, 2)
            self.neutral_percent = round((self.sentiment_variables['neutral']/self.total)*100, 2)
            print('positive tweet percentage = ', self.positive_percent,'%',
                  '\nnegative tweet percentage = ', self.negative_percent,'%',
                  '\nneutral tweet percentage = ', self.neutral_percent,'%')
       
            max = -1
            self.sentiment = ''
            for k in self.sentiment_variables.keys():
                if max < self.sentiment_variables[k] :
                    max = self.sentiment_variables[k]
                    self.sentiment = k
                    
                  
            self.plot_wordcloud()
            self.plot_piechart()
            self.top_tweets()
            
            self.user_sentiment = {
                    'topic' : self.topic.title(),
                    'sentiment' : self.sentiment.capitalize(),
                    'tweets' : self.sentiment_variables['positive'] + self.sentiment_variables['negative'] + self.sentiment_variables['neutral'],
                    'likes' : self.df['likes'].sum(),
                    'retweets' : self.df['retweets'].sum(),
                    'positive' : {'number' : self.sentiment_variables['positive'], 'percent' : self.positive_percent },
                    'negative' : {'number' : self.sentiment_variables['negative'], 'percent' : self.negative_percent },
                    'neutral' : {'number' : self.sentiment_variables['neutral'], 'percent' : self.neutral_percent },
                    'top_tweets' : self.top_tweets,
                    'buttonwords' : self.button_word_list,
                    'buttoncomment' : self.button_comment
                    }
            return self.user_sentiment
        else :
            return False
       
    def fetch_keywords(self) :
        
        self.keywords = []
        self.positive_comments = []
        self.negative_comments = []
        self.polarity_values = [] 
        
        # Getting all words from df
        for i in range(0,self.df.shape[0]):
            text = self.df['cleaned tweets'][i]
            blob = TextBlob(text)
            self.keywords.extend(blob.words)
            self.polarity_values.append(blob.sentiment.polarity)
        self.df['polarity'] = self.polarity_values
        
   
        # Separating positive and negative words
        self.keywords_dict = {}

        for i in self.keywords:
            blob = TextBlob(i)
            self.keywords_dict[i] = blob.sentiment.polarity
            self.negative_words = []
            self.positive_words = []
            for k,v in self.keywords_dict.items():
                if v > 0.4:
                    self.positive_words.append(k)
                if v < -0.4:
                    self.negative_words.append(k)
                    
        self.button_word_list = self.positive_words[0:2] + self.negative_words[0:2]
        self.button_comment = []
        
        for b in self.button_word_list:   
            for i in range(0,self.df.shape[0]):
                text = self.df['cleaned tweets'][i]
                if b in text:
                    self.button_comment.append(text)
                    break

    def plot_wordcloud(self) :
        
        #Fetching keywords for Wordcloud
        self.fetch_keywords()
        self.allwords_string = ''
        # Concatenationg all positive and negative words into a single string
        if len(self.positive_words) == 0 and len(self.negative_words) == 0 :
            self.allwords_string = 'No-word'
        else :
            self.allwords_string = ' '.join(self.positive_words) + ' ' + ' '.join(self.negative_words)
        
        transformed_mask = cv2.imread('static//images//twitter_bird.png')
        self.wc = WordCloud(background_color="white", max_words=1000, mask=transformed_mask,
                       stopwords=STOPWORDS, contour_width=0.5, contour_color='black', width=300, height=100)
        
        # Generate a wordcloud
        self.wc.generate(self.allwords_string )
        
        # store to file
        self.wc.to_file("static//images//wordcloud.png")
        

    def plot_piechart(self) :
        labels = ['Positive', 'Negative', 'Neutral']
        sizes = [self.positive_percent, self.negative_percent, self.neutral_percent]
        col = [ '#58D68D', '#E74C3C', '#F39C12']
        plt.clf()
        patches, texts = plt.pie(sizes, labels=labels, colors=col, shadow=True)
        plt.legend(patches, labels, loc="best")
        plt.pie(sizes, labels=labels, colors=col, shadow=True, autopct='%1.0f%%')
        plt.title('Pie chart showing Sentiment Analysis')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        filepath = 'static//images//pie.png'
        if os.path.isfile(filepath):
           os.remove(filepath)   # Opt.: os.system("rm "+strFile)
        plt.savefig(filepath)
        
        
    def top_tweets(self) :
        
        self.polarity_list = []
        for i in range(0,self.df.shape[0]):
            text = self.cleanedtweet_list[i]
            blob = TextBlob(text)
            self.polarity_list.append(blob.sentiment.polarity)
        self.df['polarity'] = self.polarity_list
        self.polarity_df = self.df.sort_values(['polarity'])
        self.top_tweets = []
        self.top_tweets.extend(self.polarity_df['text'].iloc[0:3])
        self.top_tweets.extend(self.polarity_df['text'].iloc[-3:])
        print(self.top_tweets)
        
  

#z = Sentiment('trump')      
#z.sentiment_analysis()        
#z.allwords_string
#z.fetch_keywords()
#z.positive_words
#z.button_word_list

        
app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/', methods=['GET', 'POST'])
def index():
    user_sentiment = {}
    new_topic = 'Donald Trump'
    if request.method == 'POST':
        new_topic = request.form.get('topic')
    user = Sentiment(new_topic)
    user_sentiment = user.sentiment_analysis()
    if user_sentiment != False :
        return render_template('index.html', sentiment_data=user_sentiment)
    else :   
        return redirect(url_for('nodatafound'))
    
@app.route('/nodatafound', methods=['GET', 'POST'])
def nodatafound():
    if request.method == 'POST':
        return redirect(url_for('index'))
    else :   
        return render_template('nodatafound.html') 
    
        
    

