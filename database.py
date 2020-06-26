import json
import sqlite3 as sql
import time
from datetime import date

def check_review_table_exist(review_conn):
	x = review_conn.cursor()
	x.execute("SELECT count(name) FROM sqlite_master WHERE name='reviews' AND type='table' ")

	if x.fetchone()[0]==0:
		review_conn.execute('CREATE TABLE reviews (URL TEXT NOT NULL PRIMARY KEY, star_1 INT, star_2 INT, star_3 INT, star_4 INT, star_5 INT, total_count INT, product_name TEXT, top_positive_name, top_pos_review, top_negative_name, top_neg_review, last_analysed_date)')

def fetch_data(conn, review_conn, features_conn, table_name):

	conn.row_factory = sql.Row
	cur = conn.cursor()
	cur.execute("SELECT * from '%s'" %table_name)

	rows = cur.fetchall()

	output_data = json.dumps([dict(ix) for ix in rows])
	conn.close()

	review_conn.row_factory = sql.Row
	review_cur = review_conn.cursor()
	review_cur.execute('SELECT * from reviews WHERE URL="%s"'%table_name)

	review_rows = review_cur.fetchall()


	l = [dict(row) for row in review_rows]

	product_name = l[0]["product_name"]
	total_reviews = l[0]["total_count"]

	top_pos_name = l[0]["top_positive_name"]
	top_pos_review = l[0]["top_pos_review"]
	top_neg_name = l[0]["top_negative_name"]
	top_neg_review = l[0]["top_neg_review"]
	last_date = l[0]["last_analysed_date"]

	reviews_count = []
	reviews_count.append(["Review", "Count"])
	reviews_count.append(["1 Star", l[0]["star_1"]])
	reviews_count.append(["2 Star", l[0]["star_2"]])
	reviews_count.append(["3 Star", l[0]["star_3"]])
	reviews_count.append(["4 Star", l[0]["star_4"]])
	reviews_count.append(["5 Star", l[0]["star_5"]])

	review_conn.close()

	features_conn.row_factory = sql.Row

	features_cur = features_conn.cursor()
	features_cur.execute('SELECT * from "%s"'%table_name)

	features_rows = features_cur.fetchall()


	feature_l = [dict(row) for row in features_rows]

	tag_ratings = []
	tag_ratings.append(["Categories", "PositiveCount", "NegativeCount"])

	for i in feature_l:
	    tag_ratings.append([i["Categories"], i["PositiveCount"], i["NegativeCount"]])

	features_conn.close()

	return (output_data, reviews_count, tag_ratings, l)


def store_data(conn, features_conn, review_conn, c, features_cur, review_cur, output_data, tag_ratings, reviews_count, table_name, top_positive, top_negative, total_reviews, product_name):

	top_pos_name = top_positive["names"]
	top_pos_review = top_positive["reviewBody"]
	top_neg_name = top_negative["names"]
	top_neg_review = top_negative["reviewBody"]

	today = date.today()
	last_date = today.strftime("%B %d, %Y")

	conn.execute('''CREATE TABLE '%s' (names TEXT,  reviewerLink TEXT, reviewTitles TEXT, reviewBody TEXT, verifiedPurchase TEXT, postDate TEXT, starRating INT, helpful INT, Page INT)''' %table_name)

	features_conn.execute('''CREATE TABLE '%s' (Categories TEXT, PositiveCount INT, NegativeCount INT)'''%table_name)

	review_cur.execute('''REPLACE INTO reviews (URL, star_1, star_2, star_3, star_4, star_5, total_count, product_name, top_positive_name, top_pos_review, top_negative_name, top_neg_review, last_analysed_date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''' ,(table_name, reviews_count[1][1], reviews_count[2][1], reviews_count[3][1], reviews_count[4][1], reviews_count[5][1], total_reviews, product_name, top_pos_name, top_pos_review, top_neg_name, top_neg_review, last_date))

	new_output_data = eval(output_data)

	for i in range(0,len(new_output_data)):
	    new_output_data[i]["reviewerLink"] = str(new_output_data[i]["reviewerLink"]).encode('utf-8', 'replace').decode()
	    new_output_data[i]["reviewTitles"] = str(new_output_data[i]["reviewTitles"]).encode('utf-8', 'replace').decode()
	    new_output_data[i]["reviewBody"] = str(new_output_data[i]["reviewBody"]).encode('utf-8', 'replace').decode()


	for x in new_output_data:
	    c.execute('''INSERT INTO '%s' (names, reviewerLink, reviewTitles, reviewBody, postDate, starRating, helpful, Page) VALUES (?,?,?,?,?,?,?,?)''' %table_name ,(x["names"], x["reviewerLink"] , x["reviewTitles"], x["reviewBody"], x["postDate"], x["starRating"], x["helpful"], x["Page"]))

	for x in tag_ratings[1:]:
	    features_cur.execute('''INSERT INTO '%s' (Categories, PositiveCount, NegativeCount) VALUES (?,?,?)''' %table_name ,(x[0], x[1], x[2]))

	conn.commit()
	review_conn.commit()
	features_conn.commit()

	print("Records created successfully")