import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import ErstebankmeItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.erstebank.me/bin/erstegroup/gemesgapi/feature/gem_site_me_www-erstebank-me-me-es7/,"

base_payload = "{\"filter\":[{\"key\":\"path\",\"value\":\"/content/sites/me/ebmn/www_erstebank_me/sr_ME/saopstenja\"}]," \
        "\"page\":%s,\"query\":\"*\",\"items\":5,\"sort\":\"DATE_RELEVANCE\",\"requiredFields\":[{\"fields\":[" \
        "\"teasers.NEWS_DEFAULT\",\"teasers.NEWS_ARCHIVE\",\"teasers.newsArchive\"]}]} "
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
  'Content-Type': 'application/json',
  'Accept': '*/*',
  'Origin': 'https://www.erstebank.me',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.erstebank.me/sr_ME/saopstenja',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': '_fbp=fb.1.1614003878094.1943964085; _gid=GA1.2.1230981758.1615534837; 3cf5c10c8e62ed6f6f7394262fadd5c2=ffb311b6d6c2f7e071b7c1a53fef5c06; _ga_LY0YT9KJ9C=GS1.1.1615534836.1.1.1615535008.0; _ga=GA1.2.1822492609.1614003877; _gat=1'
}


class ErstebankmeSpider(scrapy.Spider):
	name = 'erstebankme'
	start_urls = ['https://www.erstebank.me/sr_ME/saopstenja']
	page = 0

	def parse(self, response):
		payload = base_payload % self.page
		data = requests.request("POST", url, headers=headers, data=payload)
		raw_data = json.loads(data.text)
		for post in raw_data['hits']['hits']:
			link = post['_source']['url']
			date = post['_source']['date']
			title = post['_source']['title']
			yield response.follow(link, self.parse_post, cb_kwargs={'date': date, 'title': title})
		if self.page < raw_data['hits']['total'] // 5:
			self.page += 1
			yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response, date, title):
		description = response.xpath(
			'//div[@class="w-auto mw-full rte"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=ErstebankmeItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
