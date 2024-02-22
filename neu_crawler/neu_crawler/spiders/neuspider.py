import scrapy
from bs4 import BeautifulSoup, Comment
import re
from datetime import datetime

class NeuspiderSpider(scrapy.Spider):
    name = 'neuspider'
    allowed_domains = ['northeastern.edu']
    start_urls = ['https://www.northeastern.edu/']
    visited_urls = set()
    skip_urls = ["archivesspace", "library", "news.northeastern", "_sei_"]
    
    def should_skip_url(self, url):
        for word in NeuspiderSpider.skip_urls:
            if word in url:
                return True
        return False
    
    def should_skip_year(self, url):
        year_pattern = re.compile(r'\/(\d{4})\/')
        match = year_pattern.search(url)
        if match:
            year = int(match.group(1))  
            current_year = datetime.now().year
            if year < current_year - 3:
                return True
        return False

    def parse(self, response):
        url = response.url

        if url not in NeuspiderSpider.visited_urls and not self.should_skip_url(url) and not self.should_skip_year(url):
            all_urls = response.css('a::attr(href)').getall()

            soup = BeautifulSoup(response.text, 'html.parser')
            comments = soup.findAll(text=lambda text: isinstance(text, Comment))
            [comment.extract() for comment in comments]
            for tag in soup(['head', 'style', 'script']):
                tag.decompose()

            item = {
                'url': url,
                'html_content': response.text,
            }

            yield item

            NeuspiderSpider.visited_urls.add(url)

            for next_url in all_urls:
                yield response.follow(next_url, callback=self.parse)

            self.log(f'HTML content for {url} has been sent to the configured feed')
            
        else:
            self.log(f'Skipping already visited URL: {url}')