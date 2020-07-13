from typing import List, Any
import json
from flask import Flask , render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from filter_reviews import get_data, data_preprocessing, data_cleaning, final_data_cleaning, categorizing_reviews, remove_stopwords, lemmatization, topics_list, review_count
from twisted.internet import reactor
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
from amazon_reviews_scraping.amazon_reviews_scraping.spiders.amazon_review import ReviewspiderSpider
import time
from datetime import date
import os
import sqlite3 as sql
import crochet