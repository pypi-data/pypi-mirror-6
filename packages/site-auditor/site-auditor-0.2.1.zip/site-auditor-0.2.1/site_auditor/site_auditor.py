# -*- coding: utf-8 -*-
import socket
from xml.dom.minidom import parseString
import random
import requests
from meta_parser import MetaHTMLParser
import re

# TODO strange work with http://www.rudn.ru/ & http://web-local.rudn.ru/


class SiteAuditor(object, MetaHTMLParser):
	def __init__(self, site):
		MetaHTMLParser.__init__(self)
		try:
			self.site = self.clear_site_name(site)
			self.headers = self.my_headers()
			self.ip = socket.gethostbyname(self.site)
			self.request = requests.get('http://%s' % self.site, headers=self.headers)
		except (socket.gaierror, requests.exceptions.ConnectionError):  # as error
			self.error = 'NO HOST AVAILABLE'
		else:
			self.error = None
			self.whois = self.who()
			self.web_server = self.inf_from_headers('server')
			self.powered_by = self.inf_from_headers('x-powered-by')
			self.content_lanuage = self.inf_from_headers('content-language')
			self.content_type = self.inf_from_headers('content-type')
			self.html = self.request.text
			self.feed(self.html)
			self.description = self.meta['description']
			self.key_words = self.meta['keywords']
			self.title = self.site_title()
			self.ya_metrica = self.analytics('yaCounter')
			self.google_an = self.analytics('google-analytics.com/ga.js')
			self.live_inet = self.analytics('counter.yadro.ru/hit')
			self.rambler_top = self.analytics('counter.rambler.ru/top100.jcn?')
			self.mail_rating = self.analytics('top.list.ru/counter?id=')
			self.yad = self.yandex()
			self.pr = self.page_rank()
			self.dmoz = self.dmoz_rank()
			self.alexa = self.alexa_rank()
			self.robots_txt = self.robots('robots.txt')
			self.sitemap_xml = self.robots('sitemap.xml')
			self.pro_index = self.index()
			self.mail_catalog = self.catalogs(u'Не найдено', 'http://search.list.mail.ru/?q=')
			self.yahoo_catalog = self.catalogs('We did not find', 'http://dir.search.yahoo.com/search?ei=UTF-8&h=c&p=')
			self.joomla = self.engine('administrator')
			self.word_press = self.engine('wp-login.php')
			self.umi = self.engine('admin/content/sitetree')
			self.ucoz = self.engine('panel')
			self.bitrix = self.engine('bitrix/admin')
			self.simple_login = self.engine('login')
			self.admin_login = self.engine('admin')
			self.modx = self.engine('manager')
			self.dle = self.engine('admin.php')
			self.drupal = self.engine('user')
			self.html_validator = self.html_valid()

	@staticmethod
	def clear_site_name(site):
		for i in ['http://', 'https://', '/', 'www.']:
			if i in site:
				site = site.replace(i, '')
		return site.strip()

	def my_headers(self):
		useragents = [
			'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3',
			'Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 \ '
			'(.NET CLR 3.5.30729)',
			'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 \ '
			'(.NET CLR 3.5.30729)',
			'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1',
			'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) \ '
			'Chrome/4.0.219.6 Safari/532.1',
			'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; \ '
			'.NET CLR 2.0.50727; InfoPath.2)',
			'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; \ '
			'.NET CLR 1.1.4322; .NET CLR 3.5.30729; .NET CLR 3.0.30729)',
			'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)',
			'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; .NET CLR 2.0.50727; InfoPath.2)',
			'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
			'Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)',
			'Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51',
			# new
			'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
			'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \ '
			'Chrome/32.0.1700.102 Safari/537.36',
			'Mozilla/5.0 (Linux; Android 4.2.2; ru-ru; SAMSUNG GT-19500 Build/JDQ39) AppleWebKit/535.19 \ '
			'(KHTML, like Gecko) Version/1.0 Chrome/18.0.1025.308 Mobile Safari/535.19',

		]
		refers = [
			'https://www.google.com/?q=',
			'https://www.google.ru/?q=',
			'http://yandex.ru/yandsearch?text=',
			'http://go.mail.ru/search?&q=',
			'http://nova.rambler.ru/search?query='
		]
		return {
			'User-Agent': random.choice(useragents),
			'Cache-Control': random.choice(['no-cache', 'cache']),
			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
			'Referer': '%s%s' % (random.choice(refers), self.site),
			'Keep-Alive': random.randint(110, 120),
			'Connection': 'keep-alive',
		}

	def inf_from_headers(self, string):
		try:
			return self.request.headers[string]
		except KeyError:
			return 'NO'

	def site_title(self):
		try:
			return self.html.split('<title>')[1].split('</title>')[0].strip()
		except IndexError:
			return 'NO'

	def analytics(self, string):
		return 'YES' if string in self.html else 'NO'

	def yandex(self):
		r = requests.get('http://bar-navig.yandex.ru/u?ver=2&url=http://%s&show=1' % self.site)
		xmldoc = parseString(r.text.encode('windows-1251'))
		tyc = xmldoc.getElementsByTagName('tcy')[0].attributes['value'].value
		if tyc == '-1':
			tyc = 0
		# TODO Yandex needs capcha
		r = requests.get('http://blogs.yandex.ru/search.xml?link=%s&noreask=1' % self.site, headers=self.headers).text
		try:
			blog_links = r.split(u' из <b>')[1].split(u'</b> найденных.')[0].strip()
		except IndexError:
			blog_links = 'NEED CAPTCHA'
		#r = requests.get('http://yandex.ru/yandsearch?text="*.%s"&noreask=1&lr=193' % (self.site),).text
		#r = r.split(u'Нашлось<br>')[1].split(u'ответов</strong>')[0].strip()
		#print r
		return {
				'tyc': tyc, 'blogs': blog_links,
				'cat': 'YES' if xmldoc.getElementsByTagName('textinfo')[0].childNodes[0].nodeValue.strip() else 'NO',
		}

	def dmoz_rank(self):
		try:
			r = requests.get('http://www.dmoz.org/search?q=%s' % self.site, headers=self.headers).text
			return 'YES, %s' % (r.split('Open Directory Sites</strong>')[1].split(')</small>')[0].split(' of ')[1])
		except IndexError:
			return 'NO'

	def alexa_rank(self):
		r = requests.get('http://data.alexa.com/data?cli=10&dat=snbamz&url=%s' % self.site, headers=self.headers)
		xmldoc = parseString(r.text.encode('utf-8'))
		try:
			alexa = {
				'all_world': xmldoc.getElementsByTagName('POPULARITY')[0].attributes['TEXT'].value,
				'country': xmldoc.getElementsByTagName('COUNTRY')[-1].attributes['NAME'].value,
				'rank_in_country': xmldoc.getElementsByTagName('COUNTRY')[-1].attributes['RANK'].value,
			}
		except IndexError:
			alexa = {'all_world': 0, 'country': None, 'rank_in_country': None}
		return alexa

	def page_rank(self):
		"""
		#   Desc    :   Get PageRank of a Website, for Python
		#   Author  :   iSayme
		#   E-Mail  :   isaymeorg@gmail.com
		#   Website :   http://www.isayme.org
		#   Date    :   2012-08-04
		https://github.com/isayme/google_pr/blob/master/GooglePr.py
		"""
		gpr_hash_seed = "Mining PageRank is AGAINST GOOGLE'S TERMS OF SERVICE. Yes, I'm talking to you, scammer."
		magic = 0x1020345
		for i in xrange(len(self.site)):
			magic ^= ord(gpr_hash_seed[i % len(gpr_hash_seed)]) ^ ord(self.site[i])
			magic = (magic >> 23 | magic << 9) & 0xFFFFFFFF
		url = "http://toolbarqueries.google.com/tbr?client=navclient-auto&features=Rank&ch=%s&q=info:%s" % \
				("8%08x" % (magic), self.site)
		data = requests.get(url, headers=self.headers).text
		data = data.split(":") if data else None
		return int(data[len(data) - 1]) if data else 0

	def robots(self, data):
		r = requests.get("http://%s/%s" % (self.site, data), allow_redirects=False)
		return 'EMPTY' if r.status_code in [404, 301, 302] or r.text == self.html else r.text

	def index(self):
		google = requests.get("https://www.google.ru/search?q=site:%s" % self.site, headers=self.headers).text
		if u'ничего не найдено' in google:
			google = 0
		else:
			#.replace(u'примерно', '')
			try:
				google = google.split(u'id="resultStats">Результатов: ')[1].split('<')[0].replace('&#160;', '')
			except IndexError:
				google = 'CANT DETECT'
		yad_session = requests.Session()
		yandex = yad_session.get("http://yandex.ru/yandsearch?text=&site=%s&ras=1" % self.site, headers=self.headers)
		try:
			yandex = yandex.text.split(u'Нашлось<br>')[1].split(u'ответов</strong>')[0].replace('&nbsp;', ' ').strip()
		except IndexError:
			# TODO Yandex needs capcha
			yandex = 'NEED CAPTCHA'
		yad_ind = requests.get("http://webmaster.yandex.ru/check.xml?hostname=%s" % self.site, headers=self.headers)
		mirror_text = u'Сайт является зеркалом</span> '
		if mirror_text in yad_ind.text:
			mirror = yad_ind.text.split(mirror_text)[1].split(', ')[0]
			yad_ind = requests.get("http://webmaster.yandex.ru/check.xml?hostname=%s" % mirror, headers=self.headers)
		try:
			yad_ind = yad_ind.text.split(u'Страницы: ')[1].split('</div>')[0]
		except IndexError:
			yad_ind = 0
		return {'google': google, 'yandex_standart': yandex, 'yandex_in_index': yad_ind}

	def catalogs(self, string, catalog):
		return 'NO' if string in requests.get("%s%s" % (catalog, self.site), headers=self.headers).text else 'YES'

	def engine(self, string):
		r = requests.get('http://%s/%s' % (self.site, string), headers=self.headers, allow_redirects=True)
		return 'YES' if r.status_code not in [404, 403, 503, 301, 302] \
				and r.text != self.html and '404' not in r.text else 'NO'

	def who(self):
		# Не юзается "встроенная" whois, тк на unix она встроенная, на винде, говорят, нет
		r = requests.post("http://www.ripn.net/nic/whois/whois.cgi", {'Whois': self.site, 'Host': 'whois.ripn.net'},
			headers=self.headers, allow_redirects=True,).text.split('(in English).\n')[1].split('</PRE>')[0].strip()
		# http://www.ripn.net/about/servpol.html
		if 'You have exceeded allowed connection rate.' in r:
			return u'Вы сделали больше 30 запросов в минуту (лимит). Попробуйте позже'
		elif 'You are not allowed to connect' in r:
			return u'Вы в течении 15 минут превышали лимит (30 запросов в минуту). Восстановление доступа будет ' \
										u'не менее, чем через час'
		else:
			return re.compile(r'<.*?>').sub('', r)  # Регулярки плохо, если есть иные предложения - жду

	def html_valid(self):
		r = requests.get('http://validator.w3.org/check?uri=%s' % self.site, headers=self.headers,).text
		r = r.split('valid">')[2].split('</td>')[0].strip()
		return re.compile(r'<.*?>').sub('', r) if '<' in r else r  # Регулярки плохо, если есть иные предложения - жду


if __name__ == '__main__':
	my_site = SiteAuditor(raw_input('Enter site, please: '))
	if not my_site.error:
		# WhoIS
		print '='*50
		print my_site.whois
		print '='*50
		# Base site information
		print 'Site ip - %s' % my_site.ip
		print 'Web Server - %s' % my_site.web_server
		print 'Powered by - %s' % my_site.powered_by
		print 'Content Language - %s' % my_site.content_lanuage
		print 'Content Type - %s' % my_site.content_type
		print 'Site title - %s' % my_site.title
		print 'Description - %s' % my_site.description
		print 'Key words - %s' % my_site.key_words
		print 'W3C HTML validator - %s' % my_site.html_validator
		#print 'W3C CSS validator - %s' % my_site.css_validator
		# Ranks
		print 'Yandex TYC - %s' % my_site.yad['tyc']
		print 'Google Page Rank - %s' % my_site.pr
		print 'Alexa Rank in all world - %s' % my_site.alexa['all_world']
		print 'Alexa Rank in %s - %s' % (my_site.alexa['country'], my_site.alexa['rank_in_country'])
		# Catalogs
		print 'Yandex Catalog - %s' % my_site.yad['cat']
		print 'Mail Catalog - %s' % my_site.mail_catalog
		print 'Yahoo Catalog - %s' % my_site.yahoo_catalog
		print 'DMOZ Catalog - %s' % my_site.dmoz
		# Links
		print 'Yandex Blog links - %s' % my_site.yad['blogs']
		print 'Proindexirovano v Google - %s' % my_site.pro_index['google']
		print 'Proindexirovano v Yandex - %s' % my_site.pro_index['yandex_standart']
		print 'Popavshie v index Yandex - %s' % my_site.pro_index['yandex_in_index']
		# Stats
		print 'Yandex Metrika - %s' % my_site.ya_metrica
		print 'Google Analytics - %s' % my_site.google_an
		print 'Live Internet - %s' % my_site.live_inet
		print 'Rambler TOP100 - %s' % my_site.rambler_top
		print 'Mail Rating - %s' % my_site.mail_rating
		# Admins
		print 'Joomla Admin Directory - %s' % my_site.joomla
		print 'WordPress Admin Directory - %s' % my_site.word_press
		print 'UMI.CMS Admin Directory - %s' % my_site.umi
		print 'Ucoz Admin Directory - %s' % my_site.ucoz
		print 'Bitrix Admin Directory - %s' % my_site.bitrix
		print 'Simple Login Page - %s' % my_site.simple_login
		print 'Simple Admin Login Page - %s' % my_site.admin_login
		print 'MODX Admin Directory or ISP Manager - %s' % my_site.modx
		print 'DLE Admin Directory - %s' % my_site.dle
		print 'Drupal Login page - %s' % my_site.drupal
		# Files
		print 'Robots.txt: '
		print my_site.robots_txt
		print 'SiteMap XML: '
		print my_site.sitemap_xml
	else:
		print my_site.error