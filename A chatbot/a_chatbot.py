# -*- coding: utf-8 -*-
"""A_Chatbot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1V6cHPtmBEXoWb4UCV_pvfc0Al8Lcm82E

# A CHAT BOT
"""

!pip install nlp_utils

import nltk
import numpy as np
import pandas as pd
import random
import string
import nlp_utils as nu
import matplotlib.pyplot as plt

f = open('dialogs.txt','r')
print(f.read())

df = pd.read_csv('dialogs.txt', names = ('Query', 'Response'), sep = ('\t'))

df

"""## Data Understanding

"""

df.shape

df.info()

df.columns

df.nunique()

df.describe()

df.isnull().sum()

df.duplicated().sum()

df['Response'].value_counts()

df['Query'].value_counts()

"""## Data Visualization"""

from nltk.sentiment.vader import SentimentIntensityAnalyzer

Test = df['Query']

nltk.download('vader_lexicon')

sid = SentimentIntensityAnalyzer()
for sentence in Test:
    print(sentence)
    ss = sid.polarity_scores(sentence)
    for k in sorted(ss):
        print('{0}: {1}, '.format(k, ss[k]), end='')
    print()

analyzer = SentimentIntensityAnalyzer()
df['rating'] = Test.apply(analyzer.polarity_scores)
df=pd.concat([df.drop(['rating'], axis=1), df['rating'].apply(pd.Series)], axis=1)
### Creating a dataframe.

from wordcloud import WordCloud

def wordcloud(df, label):

    subset=df[df[label]==1]
    text=df.Query.values
    wc= WordCloud(background_color="black",max_words=1000)

    wc.generate(" ".join(text))

    plt.figure(figsize=(20,20))
    plt.subplot(221)
    plt.axis("off")
    plt.title("Words frequented in {}".format(label), fontsize=20)
    plt.imshow(wc.recolor(colormap= 'gist_earth' , random_state=244), alpha=0.98)
# visualising wordcloud

wordcloud(df,'Query')

wordcloud(df,'Response')

"""##Text Normalization"""

#Removinf special character
import re

punc_lower = lambda x: re.sub('[%s]' % re.escape(string.punctuation),'',x.lower())

# removing \n and replacing them with empty value
remove_n = lambda x: re.sub('\n',' ',x)

from os import remove
# removing asci character
remove_non_ascii = lambda x: re.sub(r'[^\x00-\x7f]',r' ',x)

# removing alpha numeric values
alphanumeric = lambda x: re.sub('\w*\d\w*', ' ', x)

df['Query'] = df['Query'].map(alphanumeric).map(punc_lower).map(remove_n).map(remove_non_ascii )

df['Response'] = df['Response'].map(alphanumeric).map(punc_lower).map(remove_n).map(remove_non_ascii )

df

pd.set_option('display.max_colwidth', 3000)

df

"""##Importance Sentence"""

imp_sent=df.sort_values(by='compound', ascending=False)

imp_sent.head()

"""##Top Positive Sentence"""

pos_sent = df.sort_values(by='pos', ascending=False)

pos_sent.head()

"""##Top Negative Sentence"""

neg_sent = df.sort_values(by='neg', ascending=False)

neg_sent.head()

"""##Top Netural Sentence"""

neu_sort = df.sort_values(by='neu', ascending=False)

neu_sort.head()

from sklearn.feature_extraction.text import TfidfVectorizer

# importing tfidf vectorizer

tfidf = TfidfVectorizer()
# Word Embedding - TF-IDF

factors = tfidf.fit_transform(df['Query']).toarray()
# changing column into array

feature_names = tfidf.get_feature_names_out()

"""##Application"""

from sklearn.metrics.pairwise import cosine_distances

import nltk
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')

query = 'who are you ?'
def chatbot(query):
    # step:-1 clean
    lemmatizer = WordNetLemmatizer()
    query = lemmatizer.lemmatize(query)
    # step:-2 word embedding - transform
    query_vector = tfidf.transform([query]).toarray()
    # step-3: cosine similarity
    similar_score = 1 -cosine_distances(factors,query_vector)
    index = similar_score.argmax() # take max index position
    # searching or matching question
    matching_question = df.loc[index]['Query']
    response = df.loc[index]['Response']
    pos_score = df.loc[index]['pos']
    neg_score = df.loc[index]['neg']
    neu_score = df.loc[index]['neu']
    confidence = similar_score[index][0]
    chat_dict = {'match':matching_question,
                'response':response,
                'score':confidence,
                'pos':pos_score,
                'neg':neg_score,
                'neu':neu_score}
    return chat_dict

while True:
    query = input('USER: ')
    if query == 'exit':
        break

    response = chatbot(query)
    if response['score'] <= 0.2: #
        print('BOT: Please rephrase your Question.')

    else:
        print('='*80)
        print('logs:\n Matched Question: %r\n Confidence Score: %0.2f \n PositiveScore: %r \n NegativeScore: %r\n NeutralScore: %r'%(
            response['match'],response['score']*100,response['pos'],response['neg'],response['neu']))
        print('='*80)
        print('BOT: ',response['response'])

