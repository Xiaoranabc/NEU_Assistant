FROM python:3.8

WORKDIR /app

RUN pip install scrapy ipython bs4 boto3

COPY . /app/neu_crawler

WORKDIR /app/neu_crawler

CMD ["scrapy", "crawl", "neuspider"]