from .abstract_extractor import AbstractExtractor
from ..article_candidate import ArticleCandidate
import logging
import lxml.html


class XpathExtractor(AbstractExtractor):
	"""This class implements xpath extractor. XpathExtractor is
	a subclass of ExtractorsInterface
	"""

	def __init__(self):
		self.log = logging.getLogger(__name__)
		self.name = "xpath"

	def theHinduExtractor(self, item):

		article_candidate = ArticleCandidate()
		article_candidate.extractor = self._name()
		doc = lxml.html.fromstring(item['spider_response'].body)

		article_candidate.language = "English"

		try:
			article_candidate.title = doc.xpath('//h1[@class= "title"]/text()')[0].strip()
		except Exception as e:
			article_candidate.title = None

		try:
			article_candidate.publish_date = doc.xpath("//span[contains(@class,'ksl-time-stamp')]/none/text()")[
				0].strip()
		except Exception as e:
			article_candidate.publish_date = None

		try:
			article_candidate.text = doc.xpath('//div[@class = " "]/div[contains(@id,"content-body")]/p//text()')
		except Exception as e:
			article_candidate.text = None

		'''
			If there isn't any image in article then xpath extractor will give null output
			but newsplease will give image url of the hindu cover photo like below
			https://www.thehindu.com/static/theme/default/base/img/og-image.jpg
		'''
		try:
			article_candidate.topimage = doc.xpath('//picture/source/@srcset')
		except Exception as e:
			article_candidate.topimage = None

		try:
			description = doc.xpath("//h2[@class = 'intro']/text()")
			article_candidate.description = "".join([str(e) for e in description])
		except Exception as e:
			article_candidate.description = None

		try:
			article_candidate.author = doc.xpath('//span[contains(@class,"author-img-name")]/a[2]/text()')[0]
		except Exception as e:
			article_candidate.author = None

		try:
			article_candidate.category = doc.xpath('//div[@class = "article-exclusive"]/a/text()')[0]
		except Exception as e:
			article_candidate.category = None

		# print(article_candidate.text)
		# print(article_candidate.publish_date)
		# print(article_candidate.title)
		# print(article_candidate.author)
		# print(article_candidate.description)
		# print(article_candidate.topimage)
		# print(article_candidate.category)

		return article_candidate

	def economicTimesExtractor(self, item):

		article_candidate = ArticleCandidate()
		article_candidate.extractor = self._name()
		doc = lxml.html.fromstring(item['spider_response'].body)

		article_candidate.language = "English"

		try:
			article_candidate.title = doc.xpath("//h1[@class= 'clearfix title']/text()")[0].strip()
		except Exception as e:
			article_candidate.title = None

		try:
			article_candidate.publish_date = doc.xpath('//meta[contains(@property,"article:published_time")]/@content')[
				0].strip()
		except Exception as e:
			article_candidate.publish_date = None

		try:
			article_candidate.text = doc.xpath("string(normalize-space(.//div[@class = 'Normal']))")
		except Exception as e:
			article_candidate.text = None

		'''
			If there isn't any image in article then xpath extractor will give null output
			but newsplease will give image url of the ET cover photo like below
			https://img.etimg.com/photo/65498029.cms
		'''
		try:
			article_candidate.topimage = doc.xpath("//figure/img/@src")
		except Exception as e:
			article_candidate.topimage = None

		try:
			article_candidate.description = doc.xpath("//h2[contains(@class ,'title2')]/text()")[0].strip()
		except Exception as e:
			article_candidate.description = None

		try:
			article_candidate.author = doc.xpath("//div[contains(@class, 'publisher')]//text()")[:-1]
		except Exception as e:
			article_candidate.author = None

		# print(article_candidate.text)
		# print(article_candidate.publish_date)
		# print(article_candidate.title)
		# print(article_candidate.author)
		# print(article_candidate.description)
		# print(article_candidate.topimage)

		return article_candidate

	# TODO: currently not working
	def timesOfIndiaExtractor(self, item):

		article_candidate = ArticleCandidate()
		article_candidate.extractor = self._name()
		doc = lxml.html.fromstring(item['spider_response'].body)

		article_candidate.language = "English"

		try:
			article_candidate.title = doc.xpath("//h1[@class= 'K55Ut']/text() | //arttitle/text()")[0].strip()
		except Exception as e:
			article_candidate.title = None

		try:
			article_candidate.publish_date = doc.xpath("//div[@class = '_3Mkg- byline']/text()").split('|')[1]
		except Exception as e:
			article_candidate.publish_date = None

		try:
			maintext = doc.xpath("//div[contains(@class,'_3WlLe clearfix')]//text()")
			article_candidate.text = ''.join(str(e) for e in maintext)
		except Exception as e:
			article_candidate.text = None

		try:
			article_candidate.topimage = doc.xpath("//div[contains(@class ,'coverimgIn')]/img/@src | //div[contains(@class,'image_wrapper')]/div/img/@src | //div[contains(@class,'2gIK')]/img/@src")
			# article_candidate.topimage = ''.join(str(e) for e in imageurl)
		except Exception as e:
			article_candidate.topimage = None
		#
		# try:
		#     article_candidate.description = doc.xpath("//h2[@class = 'intro']/text()")[0].strip()
		# except Exception as e:
		#     article_candidate.description = None

		try:
			article_candidate.author = doc.xpath('//a[@class="auth_detail"]/text() | //div[@class="_3Mkg- byline"]/span/a/text()')[0]
		except Exception as e:
			article_candidate.author = None

		# print(article_candidate.author)
		# print(article_candidate.text)
		# print(article_candidate.publish_date)
		# print(article_candidate.title)
		# print(article_candidate.topimage)

		return article_candidate

	def indianExpressExtractor(self, item):

		article_candidate = ArticleCandidate()
		article_candidate.extractor = self._name()
		doc = lxml.html.fromstring(item['spider_response'].body)

		article_candidate.language = "English"

		try:
			article_candidate.title = doc.xpath("(//div[@id = 'ie2013-content']/h1//text())")[0].strip()
		except Exception as e:
			article_candidate.title = None

		try:
			publish_date = doc.xpath("//div[@class = 'story-date']/text()")
			publish_date = max(publish_date, key=len)
			temp = publish_date.split(',')
			n = len(temp)
			article_candidate.publish_date = "".join([temp[n-2], temp[n-1]])
		except Exception as e:
			article_candidate.publish_date = None

		try:
			article_candidate.text = doc.xpath("//div[@class = 'ie2013-contentstory']//p//text()")
		except Exception as e:
			article_candidate.text = None

		# TODO: If there isn't any image in article then xpath extractor will give null output
		#  but newsplease will give image url of recommended article also
		try:
			article_candidate.topimage = doc.xpath("//div[contains(@class , 'storybigpic ssss')]/img/@src | //div[contains(@class , 'storybigpic')]/img/@src")
		except Exception as e:
			article_candidate.topimage = None

		# TODO: Write Xpath for description else news-please gives perfect result
		# try:
		#     article_candidate.description = doc.xpath()[0].strip()
		# except Exception as e:
		#     article_candidate.description = None

		try:
			article_candidate.author = doc.xpath("//div[@class = 'story-date']/a/text()")[0]
		except Exception as e:
			article_candidate.author = None

		# print(article_candidate.text)
		# print(article_candidate.publish_date)
		# print(article_candidate.title)
		# print(article_candidate.author)
		# print(article_candidate.description)
		# print(article_candidate.topimage)

		return article_candidate

	def oneIndiaExtractor(self, item):

		article_candidate = ArticleCandidate()
		article_candidate.extractor = self._name()
		doc = lxml.html.fromstring(item['spider_response'].body)

		article_candidate.language = "English"

		try:
			article_candidate.title = doc.xpath('//h1[@class="heading"]/text()')[0].strip()
		except Exception as e:
			article_candidate.title = None

		try:
			article_candidate.publish_date = doc.xpath('//div[contains(@class,"time-date date-time")]/span/time/@datetime | //div[contains(@class,"time-date")]/span/time/@datetime | //div[contains(@class,"date-time")]/span/time/@datetime')[
				0].strip()
		except Exception as e:
			article_candidate.publish_date = None

		try:
			article_candidate.text = doc.xpath('//div[@class="oi-article-lt"]/p//text()')
		except Exception as e:
			article_candidate.text = None

		# TODO: image url Every time gives gif as output
		#  like https://www.oneindia.com/img/loading.gif
		try:
			article_candidate.topimage = 'https://www.oneindia.com' + doc.xpath('//figure/strong/img/@src | //figure/img/@src')[0]
		except Exception as e:
			article_candidate.topimage = None

		# TODO: Add Xpath for description otherwise news-please gives good results
		# try:
		#     article_candidate.description = doc.xpath()[0].strip()
		# except Exception as e:
		#     article_candidate.description = None

		try:
			article_candidate.author = doc.xpath('//div[@class="posted-by"]//text()')
		except Exception as e:
			article_candidate.author = None

		# print(article_candidate.text)
		# print(article_candidate.publish_date)
		# print(article_candidate.title)
		# print(article_candidate.author)
		# print(article_candidate.description)
		# print(article_candidate.topimage)

		return article_candidate

	def ndtvExtractor(self, item):

		article_candidate = ArticleCandidate()
		article_candidate.extractor = self._name()
		doc = lxml.html.fromstring(item['spider_response'].body)

		article_url = item['url']
		category = article_url.split('.')[0][8:]
		# print(category)

		article_candidate.language = "English"

		if category == 'swachhindia':
			try:
				article_candidate.title = doc.xpath('//h1[@class="entry-title"]//text()')[0].strip()
			except Exception as e:
				article_candidate.title = None

			try:
				article_candidate.author = doc.xpath('//*[(@id = "post-header-bd")]//a[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//span /text()')
			except Exception as e:
				article_candidate.author = None

			try:
				article_candidate.topimage = doc.xpath('//div[@class="post-featured-image-bd"]/figure/a/@href')
			except Exception as e:
				article_candidate.topimage = None

			try:
				article_candidate.text = doc.xpath('//div[@class="post-content-bd"]/p//text() |  //div[@class="post-content-bd"]//strong//text() | //div[@class="post-content-bd"]/blockquote//text()')
			except Exception as e:
				article_candidate.text = None

			try:
				article_candidate.description = doc.xpath('//div[@class="excerpt_info"]//text()')
			except Exception as e:
				article_candidate.description = None

			article_candidate.category = category

		elif category == 'sports':
			try:
				article_candidate.title = doc.xpath("//h1[@class='sp-ttl']/text()")[0].strip()
			except Exception as e:
				article_candidate.title = None

			try:
				article_candidate.author = doc.xpath('//span[@itemprop="name"]/text()')
			except Exception as e:
				article_candidate.author = None

			try:
				article_candidate.topimage = doc.xpath('//div[@class="ins_instory_dv_cont"]/img/@srcset')
			except Exception as e:
				article_candidate.topimage = None

			try:
				article_candidate.text = doc.xpath('//div[@itemprop="articleBody"]//p//text()')
			except Exception as e:
				article_candidate.text = None

			try:
				article_candidate.description = doc.xpath('//div[@itemprop="description"]/h2/text()')
			except Exception as e:
				article_candidate.description = None

			article_candidate.category = 'Sports'

		elif category == 'gadgets':
			try:
				article_candidate.title = doc.xpath('//div[@class="lead_heading header_wrap"]/h1/text()')[0].strip()
			except Exception as e:
				article_candidate.title = None

			try:
				article_candidate.author = doc.xpath('//div[@class="content_section"]/div/div[@class = "dateline"]/a//text()')
			except Exception as e:
				article_candidate.author = None

			try:
				article_candidate.topimage = doc.xpath('//div[@class="fullstoryImage"]/picture/source/@srcset')
			except Exception as e:
				article_candidate.topimage = None

			try:
				article_candidate.text = doc.xpath('//div[@class="content_text row description"]//p[not(preceding-sibling::hr)]//text()')
			except Exception as e:
				article_candidate.text = None

			try:
				article_candidate.description = doc.xpath('//h2[@class="sdesc"]/text()')
			except Exception as e:
				article_candidate.description = None

			article_candidate.category = 'Technology'

		else:
			try:
				article_candidate.title = doc.xpath("//h1[@itemprop='headline']/text() | //h1[@class='sp-ttl']/text()")[0].strip()
			except Exception as e:
				article_candidate.title = None

			try:
				article_candidate.author = doc.xpath('//span[@itemprop="author"]/span/text() | //div[@class="postBy"]/span[2]/text()')
			except Exception as e:
				article_candidate.author = None

			try:
				article_candidate.topimage = doc.xpath('//div[@class="ins_instory_dv_cont lazyload"]/img/@data-src | //div[@class="ins_instory_dv_cont"]/img/@src | //div[@class="imgSection"]/img/@data-src')
			except Exception as e:
				article_candidate.topimage = None

			try:
				article_candidate.text = doc.xpath("//div[@itemprop = 'articleBody']/p//text() | //div[@class = 'artiLis-MainBlock']/p//text()")
			except Exception as e:
				article_candidate.text = None

			try:
				article_candidate.description = doc.xpath('//h2[@class="sp-descp"]/text()')
			except Exception as e:
				article_candidate.description = None

		# print(article_candidate.description)

		return article_candidate

	def dailyMailExtractor(self, item):

		article_candidate = ArticleCandidate()
		article_candidate.extractor = self._name()
		doc = lxml.html.fromstring(item['spider_response'].body)

		article_candidate.language = "English"

		try:
			article_candidate.title = doc.xpath("//div[contains(@id , 'js-article-text')]/h2/text() | //div[contains(@id , 'js-article-text')]/div/h2/text() | //div[contains(@itemprop , 'articleBody')]/h2/text()")[0].strip()
		except Exception as e:
			article_candidate.title = None

		try:
			article_candidate.publish_date = doc.xpath("//span[@class = 'article-timestamp article-timestamp-published']/time/text()")[
				0].strip()
		except Exception as e:
			article_candidate.publish_date = None

		try:
			article_candidate.text = doc.xpath("(//div[contains(@itemprop,'articleBody') ]/p[not(@class)]//text())")
		except Exception as e:
			article_candidate.text = None

		try:
			article_candidate.topimage = doc.xpath("//div[contains(@class , 'image-wrap') or contains(@class, 'artSplitter') or contains(@class, 'thinCenter') or contains(@class , 'fff-pic') or contains(@class, 'thinFloatRHS')]/img/@data-src")
		except Exception as e:
			article_candidate.topimage = None

		# TODO: write xpath for description otherwise nws-please gives good results
		# try:
		#     article_candidate.description = doc.xpath("//h2[@class = 'intro']/text()")[0].strip()
		# except Exception as e:
		#     article_candidate.description = None

		try:
			article_candidate.author = doc.xpath("//p[contains(@class, 'author-section')]//text()")
		except Exception as e:
			article_candidate.author = None

		# print(article_candidate.text)
		# print(article_candidate.publish_date)
		# print(article_candidate.title)
		# print(article_candidate.author)
		# print(article_candidate.description)
		# print(article_candidate.topimage)

		return article_candidate

	def extract(self, item, publisher):
		"""Creates an instance of Article without a Download and returns an ArticleCandidate with the results of
		parsing the HTML-Code.

		:param item: A NewscrawlerItem to parse.
		:param publisher: publisher
		:return: ArticleCandidate containing the recovered article data.
		"""
		article_candidate = ArticleCandidate()

		if publisher == "TheHindu":
			article_candidate = self.theHinduExtractor(item)

		elif publisher == "EconomicTimes":
			article_candidate = self.economicTimesExtractor(item)

		# TODO: complete extractor for TOI
		# elif publisher == "timesofindia":
		#     article_candidate = self.timesOfIndiaExtractor(item)

		elif publisher == "TheIndianExpress":
			article_candidate = self.indianExpressExtractor(item)

		elif publisher == "OneIndia":
			article_candidate = self.oneIndiaExtractor(item)

		elif publisher == "NDTV":
			article_candidate = self.ndtvExtractor(item)

		elif publisher == "DailyMail":
			article_candidate = self.dailyMailExtractor(item)

		return article_candidate
