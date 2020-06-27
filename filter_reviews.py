from imp import reload

import pandas as pd
import numpy as np
import operator
import json
import nltk
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize, sent_tokenize
import stanfordnlp
import re
import spacy
import textstat
import gensim
from gensim import corpora

import pyLDAvis
import pyLDAvis.gensim
import matplotlib.pyplot as plt
import seaborn as sns


def get_data(data):

    df = pd.DataFrame.from_records(data)
    # path = "C:/Users/HP/Desktop/FILTER/amazon_reviews_scraping/reviews.json"
    #
    # df = pd.read_json(path, lines=True)

    pos_path = "amazon_reviews_scraping/positive-words.txt"
    neg_path = "amazon_reviews_scraping/negative-words.txt"

    pos = pd.read_csv(pos_path, sep="\n", header=None, encoding='latin-1')
    neg = pd.read_csv(neg_path, sep="\n", header=None, encoding='latin-1')

    pos_words = np.array(pos[0]).tolist()
    neg_words = np.array(neg[0]).tolist()

    return df, pos_words, neg_words


def data_preprocessing(df):
    df.helpful = df.helpful.str.split(" ").str.get(0)
    for i in range(0, len(df)):
        df["helpful"].iloc[i] = df["helpful"].iloc[i].replace(',', '')

    df["helpful"] = df["helpful"].replace(to_replace="One", value="1")
    df["helpful"] = df.helpful.astype(int)

    df['postDate'] = df['postDate'].apply(lambda x: ' '.join(x.split(' ')[4:]))

    df["postDate"] = pd.to_datetime(df["postDate"])

    df["reviewerLink"] = df.reviewerLink.astype(str)
    df["reviewerLink"] = "https://amazon.in" + df["reviewerLink"]

    df["nextPage"].iloc[0].split('/')

    product_name = df.nextPage.iloc[0].split('/')[1]

    df.nextPage = df.nextPage.str.split("&").str.get(0).str.get(-1)

    df["starRating"] = df.starRating.str.split(" ").str.get(0)
    df["starRating"] = df.starRating.astype(float)

    df.loc[df["starRating"]>3.0, "sentiment"] = 1
    df.loc[df["starRating"]<=3.0, "sentiment"] = 0

    df["sentiment"] = df.sentiment.astype(int)

    df.sort_values(by='postDate', inplace=True)

    df.drop(["verifiedPurchase"], axis=1, inplace=True)

    new_df = df

    return new_df, product_name


def remove_stopwords(rev):
    stop_words = stopwords.words('english')
    rev_new = " ".join([i for i in rev if i not in stop_words])
    return rev_new


def lemmatization(texts, tags=['NOUN', 'ADJ']): # filter noun and adjective
    output = []
    nl = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
    for sent in texts:
        doc = nl(" ".join(sent))
        output.append([token.lemma_ for token in doc if token.pos_ in tags])
    return output


def data_cleaning(new_df):
    review_titles = new_df.reviewTitles
    review_body = new_df.reviewBody

    sample_df = new_df[["reviewBody", "reviewTitles"]]
    sample_df['reviewBody'] = sample_df['reviewBody'].str.replace("[^a-zA-Z#]", " ")
    sample_df['reviewBody'] = sample_df['reviewBody'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>2]))

    # remove stopwords from the text
    reviews = [remove_stopwords(r.split()) for r in sample_df['reviewBody']]

    # make entire text lowercase
    reviews = [r.lower() for r in reviews]


    tokenized_reviews = pd.Series(reviews).apply(lambda x: x.split())

    reviews_2 = lemmatization(tokenized_reviews)

    for i in range(0, len(reviews_2)):
        for j in range(0,len(reviews_2[i])-1):
            reviews_2[i][j] = reviews_2[i][j] + " " + reviews_2[i][j+1]

    return reviews_2


def topics_list(reviews_2, pos_words, neg_words):
    dictionary = corpora.Dictionary(reviews_2)

    doc_term_matrix = [dictionary.doc2bow(rev) for rev in reviews_2]

    LDA = gensim.models.ldamodel.LdaModel

    lda_model = LDA(corpus=doc_term_matrix, id2word=dictionary, num_topics=12, random_state=100, chunksize=1000, passes=50)

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

    final_topics = []
    for i in topics:
        l = i.split(" ")
        if(len(l)>3):
            if((l[1] in pos_words) or (l[2] in pos_words) or (l[1] in neg_words) or (l[2] in neg_words)):
                continue
        if((l[1] in pos_words) or (l[1] in neg_words)):
            continue
        final_topics.append(i.strip())

    return final_topics



def aspect_sentiment_analysis(txt, stop_words, nlp, final_topics):
	
    txt = txt.lower()
    sentList = nltk.sent_tokenize(txt)

    fcluster = []
    totalfeatureList = []
    finalcluster = []
    dic = {}

    for line in sentList:
        txt_list = nltk.word_tokenize(line)
        taggedList = nltk.pos_tag(txt_list)

        newwordList = []
        flag = 0
        for i in range(0,len(taggedList)-1):
            if(taggedList[i][1]=="NN" and taggedList[i+1][1]=="NN"):
                newwordList.append(taggedList[i][0]+taggedList[i+1][0])
                flag=1
            else:
                if(flag==1):
                    flag=0
                    continue
                newwordList.append(taggedList[i][0])
                if(i==len(taggedList)-2):
                    newwordList.append(taggedList[i+1][0])

        finaltxt = ' '.join(word for word in newwordList)
        new_txt_list = nltk.word_tokenize(finaltxt)
        wordsList = [w for w in new_txt_list if not w in stop_words]
        taggedList = nltk.pos_tag(wordsList)

        if(len(finaltxt)==0):
            continue

        doc = nlp(finaltxt)

        dep_node = []
        for dep_edge in doc.sentences[0].dependencies:
            dep_node.append([dep_edge[2].text, dep_edge[0].index, dep_edge[1]])

        for i in range(0, len(dep_node)):
            if (int(dep_node[i][1]) != 0):
                dep_node[i][1] = dep_node[(int(dep_node[i][1]) - 1)][0]

        featureList = []
        for i in taggedList:
            if(i[1]=='JJ' or i[1]=='NN' or i[1]=='JJR' or i[1]=='NNS' or i[1]=='RB'):
                featureList.append(list(i))
                totalfeatureList.append(list(i))

        categories = []
        for i in featureList:
            categories.append(i[0])

        for i in featureList:
            filist = []
            for j in dep_node:
                if((j[0]==i[0] or j[1]==i[0]) and (j[2] in ["nsubj", "acl:relcl", "obj", "dobj", "agent", "advmod", "amod", "neg", "prep_of", "acomp", "xcomp", "compound"])):
                    if(j[0]==i[0]):
                        filist.append(j[1])
                    else:
                        filist.append(j[0])
            fcluster.append([i[0], filist])


        for i in totalfeatureList:
            dic[i[0]] = i[1]

        for i in fcluster:
            if(dic[i[0]]=="NN"):
                finalcluster.append(i)


    return(finalcluster)


def tagging(new_df, pos_words, neg_words, final_topics):
    
    nlp = stanfordnlp.Pipeline()
    stop_words = set(stopwords.words('english'))
    
    countlist = {}
    countposlist = {}
    countneglist = {}
    finallist = {}
    for i in range(0, len(new_df)):
        txt = new_df["reviewBody"].iloc[i]
        l = aspect_sentiment_analysis(txt, stop_words, nlp, final_topics)
        for j in l:
            if(j[0] not in finallist):
                for k in j[1]:
                    if(k in pos_words):
                        finallist[j[0]] = 5
                        countlist[j[0]] = 1
                        countposlist[j[0]] = 1
                        countneglist[j[0]] = 0
                    elif(k in neg_words):
                        finallist[j[0]] = 1
                        countlist[j[0]] = 1
                        countneglist[j[0]] = 1
                        countposlist[j[0]] = 0
                        
            else:
                for k in j[1]:
                    if(k in pos_words):
                        finallist[j[0]] = finallist[j[0]]+5
                        countlist[j[0]] = countlist[j[0]] + 1
                        countposlist[j[0]] = countposlist[j[0]] + 1
                    elif(k in neg_words):
                        finallist[j[0]] = finallist[j[0]]+1
                        countlist[j[0]] = countlist[j[0]] + 1
                        countneglist[j[0]] = countneglist[j[0]] + 1


    return (countlist, countposlist, countneglist)


def dictionairy(dic, countposlist, countneglist, final_topics):
    newdic = sorted(dic.items(), key = lambda kv:(kv[1], kv[0]))
    l = []
    temp = []
    for i in range(0, len(final_topics)):
        final_topics[i] = final_topics[i].replace('  ', '   ')[::2]

    l.append(["Categories", "PositiveCount", "NegativeCount"])
    for i in newdic:
        if((i[0] in countposlist.keys()) and (i[0] in countneglist.keys())):
            for j in range (0,len(final_topics)):
                if((i[0] in final_topics[j].lower().split(" ")) and (final_topics[j] not in temp)):
                    l.append([final_topics[j], countposlist[i[0]], countneglist[i[0]]])
                    temp.append(final_topics[j])
                    break

    return l


def categorizing_reviews(new_df, final_topics):
    new_df["Categories"] = np.nan
    new_df["Categories"] = new_df["Categories"].astype(object)

    for j in range(0, len(new_df)):
        l = []
        for i in final_topics:
            if(i.split()[0] not in new_df["reviewBody"].iloc[j].lower()):
                continue
            l.append(i)

        new_df["Categories"].iloc[j] = l

    return new_df, len(new_df)


def readibility_score(txt):
    return textstat.dale_chall_readability_score(txt)


def final_data_cleaning(new_df, pos_words, neg_words, final_topics):
    new_df["reviewLength"] = np.nan

    for i in range(0, len(new_df)):
        new_df["reviewLength"].iloc[i] = len(new_df["reviewBody"].iloc[i].split(" "))

    new_df["reviewLength"] = new_df["reviewLength"].astype(int)

    new2_df = new_df

    new2_df = new2_df.drop(new2_df[(len(new2_df["Categories"])==0) or (new2_df["reviewLength"]<15)].index)

    new2_df.sort_values("helpful", axis = 0, ascending = False, inplace = True, na_position ='last')

    new2_df["noOfCategories"] = np.nan

    for i in range(0, len(new2_df)):
        new2_df["noOfCategories"].iloc[i] = len(new2_df["Categories"].iloc[i])

    new2_df["noOfCategories"] = new2_df.noOfCategories.astype(int)
    new2_df.sort_values(by="noOfCategories", axis = 0, ascending = False, inplace = True, na_position ='last')

    new2_df["Page"] = np.nan
    new2_df["nextPage"] = new2_df.nextPage.astype(int)
    for i in range(0, len(new2_df)):
        new2_df["Page"].iloc[i] = new2_df["nextPage"].iloc[i] - 1
    new2_df["Page"] = new2_df.Page.astype(int)
    new2_df.drop(['nextPage'], axis = 1, inplace=True)

    new2_df["readingScore"] = np.nan
    new2_df["readingScore"] = new2_df["readingScore"].astype(float)

    for i in range(0,len(new2_df)):
        txt = new2_df["reviewBody"].iloc[i]
        new2_df.readingScore.iloc[i] = readibility_score(txt)

    new2_df["finalScore"] = np.nan
    new2_df["finalScore"] = new2_df["finalScore"].astype(float)

    for i in range(0, len(new2_df)):
        new2_df.finalScore.iloc[i] = ((0.40*new2_df["reviewLength"].iloc[i]) + (0.40*new2_df["noOfCategories"].iloc[i]) + (0.05*new2_df["readingScore"].iloc[i]) + (0.15*new2_df["helpful"].iloc[i]))

    new2_df.sort_values("finalScore", axis = 0, ascending = False, inplace = True, na_position ='last')

    new3_df = new2_df.head(50)


    p=0
    n=0
    for i in range(0, len(new3_df)):
        if(p==1 and n==1):
            break
        elif(int(new3_df["starRating"].iloc[i]) in [3, 4, 5] and p==0):
            top_positive = new3_df.iloc[i]
            p=1
        elif(int(new3_df["starRating"].iloc[i]) in [1, 2] and n==0):
            top_negative = new3_df.iloc[i]
            n=1

    countList, countposList, countnegList = tagging(new2_df, pos_words, neg_words, final_topics)

    tag_rating = dictionairy(countList, countposList, countnegList, final_topics)
    return (tag_rating, new3_df.to_json(orient='records', date_format='iso'), top_positive.to_json(), top_negative.to_json())

def review_count(new_df):
    review_dic = [["Review", "Count"], ["1 Star", 0], ["2 Star", 0], ["3 Star", 0], ["4 Star", 0], ["5 Star", 0]]
    for i in range(0,len(new_df)):
        x = new_df["starRating"].iloc[i]
        review_dic[int(x)][1] = review_dic[int(x)][1] + 1
    return review_dic
