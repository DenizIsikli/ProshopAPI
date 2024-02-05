from flask import Flask, jsonify, request, g
from flask_restful import Api
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher
from scrapy import signals
from ProshopSpider.spiders.spider import ProshopSpider  # Adjust the import path as necessary
from ProshopSpider.pipelines import ProshopSpiderPipeline
import crochet

crochet.setup()


class ScrapyAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['DATABASE'] = 'Proshop.db'
        self.api = Api(self.app)
        self.crawl_runner = CrawlerRunner(get_project_settings())
        self.port = 5000
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

        try:
            self.db = ProshopSpiderPipeline()
        except Exception as e:
            print(f"Error connecting to the database: {e}")

        self.setup_routes()

    def setup_routes(self):
        @self.app.teardown_appcontext
        def close_db_connection(exception=None):
            db = g.pop('db', None)
            if db is not None:
                db.close_connection()

        @self.app.route('/crawl/<crawl_product_name>', methods=['GET'])
        def crawl_products(crawl_product_name):
            if not crawl_product_name:
                return jsonify({'error': 'Missing search term'}), 400
            self.scrape_with_crochet(crawl_product_name)
            return jsonify({'status': 'Spider started'}), 200

    @crochet.run_in_reactor
    def scrape_with_crochet(self, crawl_product_name):
        eventual = self.crawl_runner.crawl(ProshopSpider, product_name=crawl_product_name)
        eventual.addCallback(self.crawl_finished)

    def crawl_finished(self, _):
        print("Crawl finished.")

    def run(self):
        self.app.run(port=self.port, debug=True)

    def spider_closed(self, reason):
        if reason == 'finished':
            print('Spider finished successfully.')
        else:
            print(f'Spider closed with reason: {reason}')
