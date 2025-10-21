import scrapy
from scrapy.http import Response


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response):
        books = response.css("article.product_pod h3 a::attr(href)").getall()
        for book_url in books:
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response):
        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        title = extract_with_css("div.product_main h1::text")
        price = extract_with_css("p.price_color::text")
        amount_in_stock = extract_with_css("p.instock.availability::text")
        amount_in_stock = amount_in_stock.replace("\n", "").strip()

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating = (
            rating_class.replace("star-rating", "").strip() if rating_class else None
        )

        category = response.css("ul.breadcrumb li a::text").getall()[-1].strip()

        description = response.css("#product_description ~ p::text").get()
        description = description.strip() if description else ""

        upc = response.xpath('//th[text()="UPC"]/following-sibling::td/text()').get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
