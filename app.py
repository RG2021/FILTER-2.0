from imports import *

crochet.setup()

app = Flask(__name__)

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///final.db'
db = SQLAlchemy(app=app,metadata=MetaData(naming_convention=naming_convention))

migrate = Migrate(app, db, render_as_batch=True)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from model import Product

data = []
crawl_runner = CrawlerRunner()

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def submit():
    if request.method == 'POST':
        s = request.form['url']
        global baseURL
        baseURL = s
        global data
        data = []

        return redirect(url_for('scrape'))

@app.route("/scrape")
def scrape():

    global baseURL

    if(Product.query.filter_by(url=baseURL).first()):
        obj = Get(baseURL)
        output_data = obj.get_product_reviews_data()
        product_name, last_date, total_reviews = obj.get_product_details()
        top_pos_name, top_pos_review, top_neg_name, top_neg_review = obj.get_topPN()
        tag_ratings = obj.get_tag_ratings()
        reviews_count = obj.get_product_ratings()

    else:
        # scrape_with_crochet(baseURL=baseURL)
        # time.sleep(15)

        data = [{"postDate": "Reviewed in India on 5 September 2019", "names": "Chris", "verifiedPurchase": "Verified Purchase", "reviewTitles": "Read if you're considering whether to buy it or not.", "nextPage": "/Infinity-Glide-500-Headphones-Equalizer/product-reviews/B07W5MYRF4?pageNumber=2&reviewerType=all_reviews", "starRating": "5.0 out of 5 stars", "helpful": "339 people found this helpful", "reviewerLink": "/gp/profile/amzn1.account.AHJ52IRMRGY3OSUGM7PBMXIOKB6Q", "reviewBody": "First of all Thank You Harman for launching an affordable headphone. Now talking about the sound and build quality, the sound quality is awesome if you compare it with other headphone in this price segment. The Bass, Mids and High are equally balance thus giving you a warm and soothing sound. Most Indians like bass so if you are a bass lover you should know that it won't give you over your head bass but you'll get a smooth thumping bass, you can feel the vibration in your ears without any distortion. You get a dual EQ too, normal mode and bass mode. The sound does feel different but not that much. Impressive bass tho with the right EQ settings.If you want a very loud headphone then you won't be satisfied, I was surprised when I could still listen some songs even when both my phone and headphone volume was at 100%. I secretly wish they increase the loudness a little bit more but I'm equally satisfied.Now about the noise cancellation considering it is in the ear headphone and not over the ear it is quite impressive.The call quality is okay. Nothing impressive or nothing bad. The other side can hear me clearly and I too can hear the caller voice clearly.The build quality is normal it is made entirely out of plastic. Plastic material are quite good. Doesn't look or feel fragile.I tried putting this headphone on for 3 hours straight and I must say it is quite comfortable, you get a soft cushions and you shouldn't get any problem in 2 or 2.5 hours of wearing but at 3 or 3.5 hours you might want to rest your ears for a while.Now at this price segment this is the best headphone available. The sound quality beats all the others headphones and yes even boAts headphones. Now about the build quality, there are other headphones better than this but hey, the sound is what important. and this headphone isn't fragile at all plus you get a one year warranty.Well, what are you waiting for, go ahead a buy it. You won't regret afterall it is by HARMAN.#thelongestreview?"},
        {"postDate": "Reviewed in India on 3 September 2019", "names": "Janaki", "verifiedPurchase": "Verified Purchase", "reviewTitles": "Truly a light weight headphone with an excellent battery life", "nextPage": "/Infinity-Glide-500-Headphones-Equalizer/product-reviews/B07W5MYRF4?pageNumber=2&reviewerType=all_reviews", "starRating": "4.0 out of 5 stars", "helpful": "147 people found this helpful", "reviewerLink": "/gp/profile/amzn1.account.AFSK6MQ5NLOC6HWYAUYEFTBSNJ7Q", "reviewBody": "Would I recommend this product to others? Definitely yes.Pros:Light WeightBattery LifeCons:No 3.5 mm cable, only blue toothI was in search of a light weight wireless headphone that I can use for long hours. I have a Bose now but I cannot use it for longer than 2-3 hours as its heavy and ears and head start aching.This Infinity one wins there. I have used it for 6-7 hours without any aches or pains.The ear pieces do press a little on the ears unlike over-the-ear ones. This one is on-the-ear. But it is not uncomfortable and gives a good fit.The sound quality is good too. Noise cancellation is not big. With low volumes, you can hear surrounding noise.Battery does last for a long long time. I used it daily for 4-5 hours for about 3 days with one charge. Am truly impressed with it.And it folds, hence carrying it around is convenient too.And I got it in the lightning deal at 1500 Rs. Worth the price. I would definitely recommend this to anyone who is looking for a non-expensive wireless headphones with a decent sound quality.I am giving it a 4 because I am not sure of its durability. If it lasts foe 6 months at least, then I will come back and update the rating to a 5."},
        {"postDate": "Reviewed in India on 2 September 2019", "names": "Nagasi\tvakumar.Dosapati", "verifiedPurchase": "Verified Purchase", "reviewTitles": "Awesome product of JBL (harman)", "nextPage": "/Infinity-Glide-500-Headphones-Equalizer/product-reviews/B07W5MYRF4?pageNumber=2&reviewerType=all_reviews", "starRating": "5.0 out of 5 stars", "helpful": "144 people found this helpful", "reviewerLink": "/gp/profile/amzn1.account.AEY6FZXFVG3REFF7D7574OYIBWRA", "reviewBody": "Hi all,After a week rough usage i am sharing my opinion.i through that under 1499 INR i should not expect the headset with all features except sound,but this one made ,my through wrong.One of the best budget product it is. \"Infinity (JBL) Glide 500 Wireless On-Ear Dual EQ Deep Bass Headphones with Mic (Charcoal Black)\".Pros:--1.product quality is good on this price.2.sound quality is extraordinary,especially \"Gaana website songs\" are awesome,prime video streaming sound experience just like a theater.3. Battery backup ~20hrs is good is this product.Cons:--1.aux port not enabled in this version.2.No other reasons here."},
        {"postDate": "Reviewed in India on 4 September 2019", "names": "Amazon Customer", "verifiedPurchase": "Verified Purchase", "reviewTitles": "Worst product", "nextPage": "/Infinity-Glide-500-Headphones-Equalizer/product-reviews/B07W5MYRF4?pageNumber=2&reviewerType=all_reviews", "starRating": "1.0 out of 5 stars", "helpful": "43 people found this helpful", "reviewerLink": "/gp/profile/amzn1.account.AE2LNDESTZP3PKNULJZHQUTXWNRA", "reviewBody": "This is waste of money. Guys Don't go for this headset you will get lot of ear pain and you can't feel any Bass exist in it. Please don't buy it I had purchased later I found such a worst product and returned immediately."},
        {"postDate": "Reviewed in India on 5 September 2019", "names": "Krishna", "verifiedPurchase": "Verified Purchase", "reviewTitles": "Mimatch", "nextPage": "/Infinity-Glide-500-Headphones-Equalizer/product-reviews/B07W5MYRF4?pageNumber=2&reviewerType=all_reviews", "starRating": "1.0 out of 5 stars", "helpful": "42 people found this helpful", "reviewerLink": "/gp/profile/amzn1.account.AFCZGS72YPF6JNB2EKCNIRIFIL5A", "reviewBody": "Hello Amazon Team,In the Carton box it is mentioned as Manufactur \t\t ed in USA but in the product it mentioned as China . This is breach case , pls look into & Update."}]

        df, pos_words, neg_words = get_data(data)
        new_df, product_name = data_preprocessing(df)
        reviews_2 = data_cleaning(new_df)
        final_topics = topics_list(reviews_2, pos_words, neg_words)
        new2_df, total_reviews = categorizing_reviews(new_df, final_topics)
        tag_ratings, output_data, top_positive, top_negative = final_data_cleaning(new2_df, pos_words, neg_words, final_topics)
        reviews_count = review_count(new2_df)

        top_positive = json.loads(top_positive)
        top_negative = json.loads(top_negative)

        top_pos_name = top_positive["names"]
        top_pos_review = top_positive["reviewBody"]
        top_neg_name = top_negative["names"]
        top_neg_review = top_negative["reviewBody"]

        today = date.today()
        last_date = today.strftime("%B %d, %Y")

        obj = Put(baseURL, product_name, last_date, total_reviews)
        top_positive, top_negative = obj.add_reviewers_and_reviews(output_data)
        obj.add_product_ratings(reviews_count)
        obj.add_product_features(tag_ratings)
        obj.add_top_pos_and_neg(top_positive, top_negative)


    return render_template("newindex.html", reviews=output_data, product_name=product_name, total_reviews=total_reviews, reviews_count=json.dumps(reviews_count), tag_ratings =json.dumps(tag_ratings), top_pos_name=top_pos_name, top_pos_review=top_pos_review ,top_neg_name=top_neg_name, top_neg_review=top_neg_review, last_date=last_date)


@crochet.run_in_reactor
def scrape_with_crochet(baseURL):
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    eventual = crawl_runner.crawl(ReviewspiderSpider, category = baseURL)
    return eventual


def _crawler_result(item, response, spider):
    data.append(dict(item))


if __name__== "__main__":
    app.run(debug=True)
