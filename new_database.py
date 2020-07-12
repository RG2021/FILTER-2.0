# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import MetaData
# from flask_script import Manager
# from flask_migrate import Migrate, MigrateCommand

# app = Flask(__name__)

# naming_convention = {
#     "ix": 'ix_%(column_0_label)s',
#     "uq": "uq_%(table_name)s_%(column_0_name)s",
#     "ck": "ck_%(table_name)s_%(column_0_name)s",
#     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#     "pk": "pk_%(table_name)s"
# }

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///final.db'
# db = SQLAlchemy(app=app,metadata=MetaData(naming_convention=naming_convention))

# migrate = Migrate(app, db, render_as_batch=True)
# manager = Manager(app)

# manager.add_command('db', MigrateCommand)

from app import db
import json

reviewed = db.Table('reviewed',
	db.Column('reviewer_id', db.Integer, db.ForeignKey('reviewer.id')),
	db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
)

class Product(db.Model):
	__tablename__ = 'product'
	id = db.Column('id', db.Integer, primary_key=True) #
	url = db.Column('url', db.String) #
	name = db.Column('name', db.String) #
	last_date = db.Column('last_date', db.Integer) #
	total_reviews = db.Column('total_reviews', db.Integer) #
	reviews = db.relationship('Reviews', backref='product') #
	reviewers = db.relationship('Reviewer', secondary=reviewed, backref=db.backref('products'), lazy='dynamic') #
	ratings = db.relationship('Ratings', backref='product', uselist=False)
	features = db.relationship('Features', backref='product')
	top_pn = db.relationship('TopPN', backref='product', uselist=False)

class Reviewer(db.Model):
	__tablename__ = 'reviewer'
	id = db.Column('id', db.Integer, primary_key=True) #
	name = db.Column('name', db.String) #
	url = db.Column('url', db.String) #
	reviews = db.relationship('Reviews', backref='reviewer') #


class Reviews(db.Model):
	__tablename__ = 'reviews'
	id = db.Column('id', db.Integer, primary_key=True) #
	rid = db.Column('rid', db.Integer, db.ForeignKey('reviewer.id')) #
	pid = db.Column('pid', db.Integer, db.ForeignKey('product.id')) #
	title = db.Column('title', db.String) #
	review = db.Column('review', db.String) #
	post_date = db.Column('post_date', db.String) #
	rating = db.Column('rating', db.Integer) #
	helpful = db.Column('helpful', db.Integer) #
	page = db.Column('page', db.Integer) #
	score = db.Column('score', db.Float) #
	top_positive = db.relationship('TopPN', backref='top_pos_review', foreign_keys = 'TopPN.pos_review_id')
	top_negative = db.relationship('TopPN', backref='top_neg_review', foreign_keys = 'TopPN.neg_review_id')


class Ratings(db.Model):
	__tablename__ = 'ratings'
	id = db.Column('id', db.Integer, primary_key=True) #
	pid = db.Column('pid', db.Integer, db.ForeignKey('product.id'), unique=True) #
	star_1 = db.Column('star_1', db.Integer) #
	star_2 = db.Column('star_2', db.Integer) #
	star_3 = db.Column('star_3', db.Integer) #
	star_4 = db.Column('star_4', db.Integer) #
	star_5 = db.Column('star_5', db.Integer) #

class Features(db.Model):
	__tablename__ = 'features'
	id = db.Column('id', db.Integer, primary_key=True) #
	pid = db.Column('pid', db.Integer, db.ForeignKey('product.id')) #
	feature = db.Column('feature', db.String) #
	pos_count = db.Column('pos_count', db.Integer) #
	neg_count = db.Column('neg_count', db.Integer) #

class TopPN(db.Model):
	__tablename__ = 'TopPN'
	id = db.Column('id', db.Integer, primary_key=True)
	pid = db.Column('pid', db.Integer, db.ForeignKey('product.id'), unique=True)
	pos_review_id = db.Column('pos_review_id', db.Integer, db.ForeignKey('reviews.id'))
	neg_review_id = db.Column('neg_review_id', db.Integer, db.ForeignKey('reviews.id'))


#####################################################  Adding Data  ##########################################################


def add_product(url, name, last_date, total_reviews):
	product = Product(url=url, name=name, last_date=last_date, total_reviews=total_reviews)
	db.session.add(product)
	db.session.commit()

	return product


def add_reviewers_and_reviews(output_data, product):
	max_pos_score = 0
	max_neg_score = 0

	new_output_data = eval(output_data)

	for i in range(0,len(new_output_data)):
	    new_output_data[i]["reviewerLink"] = str(new_output_data[i]["reviewerLink"]).encode('utf-8', 'replace').decode()
	    new_output_data[i]["reviewTitles"] = str(new_output_data[i]["reviewTitles"]).encode('utf-8', 'replace').decode()
	    new_output_data[i]["reviewBody"] = str(new_output_data[i]["reviewBody"]).encode('utf-8', 'replace').decode()

	for data in new_output_data:
		reviewer = Reviewer(products=[product], name=data["names"], url=data["reviewerLink"])
		db.session.add(reviewer)

		review = Reviews(product=product, 
			reviewer=reviewer, 
			title=data["reviewTitles"], 
			review=data["reviewBody"], 
			post_date=data["postDate"], 
			rating=data["starRating"], 
			helpful=data["helpful"], 
			page=data["Page"], 
			score=data["finalScore"])

		if(review.score>max_pos_score and review.rating>3):
			max_pos_score = review.score
			top_pos_review = review
		if(review.score>max_neg_score and review.rating<=3):
			max_neg_score = review.score
			top_neg_review = review

		db.session.add(review)

	db.session.commit()

	return(top_pos_review, top_neg_review)


def add_product_ratings(product, reviews_count):
	rating = Ratings(product=product, 
		star_1=reviews_count[1][1], 
		star_2=reviews_count[2][1], 
		star_3=reviews_count[3][1], 
		star_4=reviews_count[4][1], 
		star_5=reviews_count[5][1])

	db.session.add(rating)
	db.session.commit()


def add_product_features(product, tag_ratings):
	for x in tag_ratings:
		feature = Features(product=product, feature=x[0], pos_count=x[1], neg_count=x[2])
		db.session.add(feature)
	db.session.commit()

def add_top_pos_and_neg(product, top_pos_review, top_neg_review):
	pn_review = TopPN(product=product, top_pos_review=top_pos_review, top_neg_review=top_neg_review)
	db.session.add(pn_review)
	db.session.commit()


######################################################## GET DATA ################################################################



# product = Product.query.filter_by(name=name).first()

def get_product_ratings(product):
	rating = product.ratings

	reviews_count = []
	reviews_count.append(["Review", "Count"])
	reviews_count.append(["1 Star", rating.star_1])
	reviews_count.append(["2 Star", rating.star_2])
	reviews_count.append(["3 Star", rating.star_3])
	reviews_count.append(["4 Star", rating.star_4])
	reviews_count.append(["5 Star", rating.star_5])

	return reviews_count

def get_tag_ratings(product):
	pfeature = product.features

	tag_ratings = []
	tag_ratings.append(["Categories", "PositiveCount", "NegativeCount"])

	for i in pfeature[1:]:
		tag_ratings.append([i.feature, i.pos_count, i.neg_count])

	return tag_ratings

def get_topPN(product):
	top_pn = product.top_pn
	top_pos_review_id = top_pn.pos_review_id
	top_neg_review_id = top_pn.neg_review_id

	top_pos_review = Reviews.query.filter_by(id = top_pos_review_id).first()
	top_neg_review = Reviews.query.filter_by(id = top_neg_review_id).first()

	top_pos_name = top_pos_review.reviewer.name
	top_pos_text = top_pos_review.review

	top_neg_name = top_neg_review.reviewer.name
	top_neg_text = top_neg_review.review

	return(top_pos_name, top_pos_text, top_neg_name, top_neg_text)

def get_product_details(product):
	name = product.name
	last_analyzed_date = product.last_date
	total_count = product.total_reviews

	return(name, last_analyzed_date, total_count)

def get_product_reviews_data(product):
	output_data = []
	data = product.reviews
	for x in data:
		temp = dict(x.__dict__.items())
		temp.pop("_sa_instance_state")
		temp["names"] = x.reviewer.name
		output_data.append(temp)

	return(json.dumps(output_data))

#################################################################################################################################



# db.create_all()
# user1 = Reviewer(name="user1", url="http")
# user2 = Reviewer(name="user2", url="http")
# user3 = Reviewer(name="user3", url="http")
# user4 = Reviewer(name="user4", url="http")
# user5 = Reviewer(name="user5", url="http")
# db.session.add(user1)
# db.session.add(user2)
# db.session.add(user3)
# db.session.add(user4)
# db.session.add(user5)
# db.session.commit()
# product1 = Product(url="http", name="product1", last_date=10, total_reviews=10)
# product2 = Product(url="http", name="product2", last_date=10, total_reviews=10)
# product3 = Product(url="http", name="product3", last_date=10, total_reviews=10)
# db.session.add(product1)
# db.session.add(product2)
# db.session.add(product3)
# db.session.commit()


# review1 = Reviews(reviewer=user1, product=product1, title="hello", review="hello world", post_date="10", rating=5, h
# review2 = Reviews(reviewer=user2, product=product1, title="hello", review="hello world", post_date="10", rating=5, h
# review2 = Reviews(reviewer=user3, product=product1, title="hello", review="hello world", post_date="10", rating=5, h
# review3 = Reviews(reviewer=user4, product=product2, title="hello", review="hello world", post_date="10", rating=5, h
# review4 = Reviews(reviewer=user2, product=product2, title="hello", review="hello world", post_date="10", rating=5, h
# review5 = Reviews(reviewer=user5, product=product3, title="hello", review="hello world", post_date="10", rating=5, h
# db.session.add(review1)
# db.session.add(review2)
# db.session.add(review3)
# db.session.add(review4)
# db.session.add(review5)
# db.seesion.commit()

# product1.reviewers.append(user3)
# product3.reviewers.append(user1)
# product3.reviewers.append(user1)
# product2.reviewers.append(user5)
# product2.reviewers.append(user4)
# product2.reviewers.append(user6)