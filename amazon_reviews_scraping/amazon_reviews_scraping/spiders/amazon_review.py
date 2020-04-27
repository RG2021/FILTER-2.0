from datetime import time

import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class MyItem(scrapy.Item):
    names = scrapy.Field()
    reviewerLink = scrapy.Field()
    reviewTitles = scrapy.Field()
    reviewBody = scrapy.Field()
    verifiedPurchase = scrapy.Field()
    postDate = scrapy.Field()
    starRating = scrapy.Field()
    helpful = scrapy.Field()
    nextPage = scrapy.Field(default = 'null')


class ReviewspiderSpider(scrapy.Spider):
    name = 'reviewspider'
    allowed_domains = ["amazon.in"]
    myBaseUrl=''
    start_urls = []

    def __init__(self, category='', **kwargs):
        self.myBaseUrl = category
        self.start_urls.append(self.myBaseUrl)
        #for i in range(1,20):
        #self.start_urls.append(self.myBaseUrl+"&pageNumber=1")
        super().__init__(**kwargs)

    custom_settings = {'FEED_URI': 'amazon_reviews_scraping/reviews.json', "CLOSESPIDER_TIMEOUT" : 10}
    #rules = [Rule(LinkExtractor(allow=(), restrict_xpaths=('//li[@class="a-last"]/a/@href',)), follow=True)]

    def parse(self, response):
        all_reviews = response.xpath('//div[@data-hook="reviews-medley-footer"]//a[@data-hook="see-all-reviews-link-foot"]/@href').extract_first()
        yield response.follow("https://www.amazon.in"+all_reviews, callback=self.parse_page)

    def parse_page(self, response):
        names=response.xpath('//div[@data-hook="review"]//span[@class="a-profile-name"]/text()').extract()
        reviewerLink=response.xpath('//div[@data-hook="review"]//a[@class="a-profile"]/@href').extract()
        reviewTitles=response.xpath('//a[@data-hook="review-title"]/span/text()').extract()
        reviewBody=response.xpath('//span[@data-hook="review-body"]/span').xpath('normalize-space()').getall()
        verifiedPurchase=response.xpath('//span[@data-hook="avp-badge"]/text()').extract()
        postDate=response.xpath('//span[@data-hook="review-date"]/text()').extract()
        starRating=response.xpath('//i[@data-hook="review-star-rating"]/span[@class="a-icon-alt"]/text()').extract()
        helpful = response.xpath('//span[@class="cr-vote"]//span[@data-hook="helpful-vote-statement"]/text()').extract()

        for (name, reviewLink, title, Review, Verified, date, rating, helpful_count) in zip(names, reviewerLink, reviewTitles, reviewBody, verifiedPurchase, postDate, starRating, helpful):
            next_urls = response.css('.a-last > a::attr(href)').extract_first()
            yield MyItem(names=name, reviewerLink = reviewLink, reviewTitles=title, reviewBody=Review, verifiedPurchase=Verified, postDate=date, starRating=rating, helpful=helpful_count, nextPage=next_urls)

        next_page = response.css('.a-last > a::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow("https://www.amazon.in"+next_page, callback=self.parse_page)

    # def profile_parse(self, response):
    #     vote = response.xpath('//div[@class="dashboard-desktop-stats-value"]/span/text()').extract_first()
    #     return votes
