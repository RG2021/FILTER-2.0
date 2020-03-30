
# coding: utf-8

# In[367]:


import pandas as pd
import numpy as np
import json
import nltk
from nltk import FreqDist
import re
import spacy
import textstat
import gensim
from gensim import corpora

import pyLDAvis
import pyLDAvis.gensim
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')


# In[368]:


path = "C:/Users/HP/Desktop/FILTER/amazon_reviews_scraping/reviews.json"


# In[369]:


df = pd.read_json(path, lines=True)

pos_path = "C:/Users/HP/Desktop/FILTER/amazon_reviews_scraping/positive-words.txt"
neg_path = "C:/Users/HP/Desktop/FILTER/amazon_reviews_scraping/negative-words.txt"

pos = pd.read_csv(pos_path, sep="\n", header=None, encoding='latin-1')
neg = pd.read_csv(neg_path, sep="\n", header=None, encoding='latin-1')

pos_words = np.array(pos[0]).tolist()
neg_words = np.array(neg[0]).tolist()


# In[370]:


df.helpful = df.helpful.str.split(" ").str.get(0)

df["helpful"] = df["helpful"].replace(to_replace="One", value="1")
df["helpful"] = df.helpful.astype(int)

df['postDate'] = df['postDate'].apply(lambda x: ' '.join(x.split(' ')[4:]))

df["postDate"] = pd.to_datetime(df["postDate"])

df["reviewerLink"] = df.reviewerLink.astype(str)
df["reviewerLink"] = "https://amazon.in" + df["reviewerLink"]


# In[371]:


df["nextPage"].iloc[0].split('/')

product_name = df.nextPage.iloc[0].split('/')[1]

print(product_name)


# In[372]:


df.nextPage = df.nextPage.str.split("&").str.get(0).str.get(-1)

df["starRating"] = df.starRating.str.split(" ").str.get(0)
df["starRating"] = df.starRating.astype(float)

df.loc[df["starRating"]>3.0, "sentiment"] = 1
df.loc[df["starRating"]<=3.0, "sentiment"] = 0

df["sentiment"] = df.sentiment.astype(int)

df.sort_values(by='postDate', inplace=True)

df.drop(["verifiedPurchase"], axis=1, inplace=True)

new_df = df


# In[373]:


review_titles = new_df.reviewTitles
review_body = new_df.reviewBody


# In[374]:


sample_df = new_df[["reviewBody", "reviewTitles"]]


# In[375]:


sample_df.head()


# In[376]:


def freq_words(x, terms = 30):
  all_words = ' '.join([text for text in x])
  all_words = all_words.split()

  fdist = FreqDist(all_words)
  words_df = pd.DataFrame({'word':list(fdist.keys()), 'count':list(fdist.values())})

  # selecting top 20 most frequent words
  d = words_df.nlargest(columns="count", n = terms) 
  plt.figure(figsize=(20,5))
  ax = sns.barplot(data=d, x= "word", y = "count")
  ax.set(ylabel = 'Count')
  plt.show()


# In[377]:


freq_words(sample_df['reviewBody'])


# In[378]:


sample_df['reviewBody'] = sample_df['reviewBody'].str.replace("[^a-zA-Z#]", " ")


# In[379]:


from nltk.corpus import stopwords
stop_words = stopwords.words('english')


# In[380]:


def remove_stopwords(rev):
    rev_new = " ".join([i for i in rev if i not in stop_words])
    return rev_new

# remove short words (length < 3)
sample_df['reviewBody'] = sample_df['reviewBody'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>2]))

# remove stopwords from the text
reviews = [remove_stopwords(r.split()) for r in sample_df['reviewBody']]

# make entire text lowercase
reviews = [r.lower() for r in reviews]


# In[381]:


freq_words(reviews, 35)


# In[382]:


nlp = spacy.load('en', disable=['parser', 'ner'])


# In[383]:


def lemmatization(texts, tags=['NOUN', 'ADJ']): # filter noun and adjective
    output = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        output.append([token.lemma_ for token in doc if token.pos_ in tags])
    return output


# In[384]:


tokenized_reviews = pd.Series(reviews).apply(lambda x: x.split())
print(tokenized_reviews[1])


# In[385]:


reviews_2 = lemmatization(tokenized_reviews)
print(reviews_2[1])


# In[386]:


reviews_2


# In[387]:


for i in range(0, len(reviews_2)):
    for j in range(0,len(reviews_2[i])-1):
        reviews_2[i][j] = reviews_2[i][j] + " " + reviews_2[i][j+1]


# In[388]:


reviews_2


# In[389]:


reviews_3 = []
for i in range(len(reviews_2)):
    reviews_3.append(' '.join(reviews_2[i]))

sample_df['reviews'] = reviews_3

freq_words(sample_df['reviews'], 35)


# In[390]:


dictionary = corpora.Dictionary(reviews_2)

doc_term_matrix = [dictionary.doc2bow(rev) for rev in reviews_2]

LDA = gensim.models.ldamodel.LdaModel

lda_model = LDA(corpus=doc_term_matrix, id2word=dictionary, num_topics=12, random_state=100, chunksize=1000, passes=50)

lda_model.print_topics()


# In[391]:


pyLDAvis.enable_notebook()
vis = pyLDAvis.gensim.prepare(lda_model, doc_term_matrix, dictionary)
vis


# In[392]:


topic_list = lda_model.print_topics()

l = []
for i in topic_list:
    l.append(i[1])

lst = []
for i in l:
    x = i.split("+")
    for j in x:
        y = j.split("*")
        lst.append(y)

dic = {}
for i in lst:
    topic = " ".join(re.split("[^a-zA-Z]*", i[1]))
    if(topic not in dic):
        dic[topic] = 1
        continue
    dic[topic] = dic[topic] + 1

topics = []
for i in dic:
    if(dic[i]>1):
        topics.append(i)

print(topics)


# In[393]:


print(dic)


# In[394]:


final_topics = []
for i in topics:
    l = i.split(" ")
    if(len(l)>3):
        if((l[1] in pos_words) or (l[2] in pos_words) or (l[1] in neg_words) or (l[2] in neg_words)):
            continue
    if((l[1] in pos_words) or (l[1] in neg_words)):
        continue
    final_topics.append(i.strip())


# In[395]:


final_topics


# In[396]:


new_df.head(20)


# In[397]:


new_df["Categories"] = np.nan

reviewers_link = new_df["reviewerLink"]

new_df["Categories"] = new_df["Categories"].astype(object)

for j in range(0, len(new_df)):
    l = []
    for i in final_topics:
        if(i not in new_df["reviewBody"].iloc[j].lower()):
            continue
        l.append(i)
    new_df["Categories"].iloc[j] = l


# In[398]:


new_df.head(20)


# In[399]:


print(new_df["Categories"].iloc[1])

print(new_df["reviewBody"].iloc[1])


# In[400]:


new_df.Categories


# In[401]:


sns.countplot(x = new_df.starRating)


# In[402]:


new_df["reviewLength"] = np.nan

for i in range(0, len(new_df)):
    new_df["reviewLength"].iloc[i] = len(new_df["reviewBody"].iloc[i].split(" "))

new_df["reviewLength"] = new_df["reviewLength"].astype(int)


# In[403]:


new_df.describe()


# In[404]:


new2_df = new_df

new2_df = new2_df.drop(new2_df[(len(new2_df["Categories"])==0) or (new2_df["reviewLength"]<15)].index)

new2_df.sort_values("helpful", axis = 0, ascending = False, inplace = True, na_position ='last') 


# In[405]:


def readibility_score(txt):
    return textstat.dale_chall_readability_score(txt)

new2_df["reviewBody"].iloc[1]

new2_df["readingScore"] = np.nan
new2_df["readingScore"] = new2_df["readingScore"].astype(float)

for i in range(0,len(new2_df)):
    txt = new2_df["reviewBody"].iloc[i]
    new2_df.readingScore.iloc[i] = readibility_score(txt)


# In[406]:


new2_df.head(20)


# In[407]:


new2_df["reviewBody"].iloc[11]


# In[408]:


new2_df["Categories"].iloc[11]


# In[409]:


new2_df["noOfCategories"] = np.nan

for i in range(0, len(new2_df)):
    new2_df["noOfCategories"].iloc[i] = len(new2_df["Categories"].iloc[i])

new2_df["noOfCategories"] = new2_df.noOfCategories.astype(int)


# In[410]:


new2_df.head(20)


# In[411]:


new2_df.sort_values(by="noOfCategories", axis = 0, ascending = False, inplace = True, na_position ='last')


# In[412]:


new2_df.head(20)


# In[413]:


print(new2_df["reviewBody"].iloc[0])

print(new2_df["reviewBody"].iloc[1])


# In[414]:


print(new2_df["Categories"].iloc[0])


# In[415]:


print(new2_df["Categories"].iloc[8])


# In[416]:


print(dic)


# In[417]:


print(final_topics)


# In[419]:


new2_df.head(20)


# In[421]:


new2_df["Page"] = np.nan
new2_df["nextPage"] = new2_df.nextPage.astype(int)
for i in range(0, len(new2_df)):
    new2_df["Page"].iloc[i] = new2_df["nextPage"].iloc[i] - 1
new2_df["Page"] = new2_df.Page.astype(int)
new2_df.drop(['nextPage'], axis = 1, inplace=True)


# In[422]:


new2_df.head(20)

