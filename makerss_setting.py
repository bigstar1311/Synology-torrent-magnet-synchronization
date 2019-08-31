# -*- coding: utf-8 -*-
import sys, os
reload(sys)
sys.setdefaultencoding('utf-8')

import urllib, re
import json
import base64
import traceback, time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from makerss_main import download

############## 2018-10-24
# http://jaewook.net/archives/2613   
"""
SITE_LIST = [
	# 1.  Ʈ  
	{
		'TORRENT_SITE_TITLE': 'torrentboza',
		'TORRENT_SITE_URL': 'https://torrentboza.com',
		'BO_TABLE_LIST': ['drama', 'ent', 'daq'],
		'XPATH_LIST_TAG'      : '//*[@id="fboardlist"]/div[1]/ul/li[%s]/div[2]/a',
		'QUERY' : '&sca=&sfl=wr_subject&sop=and&stx=NEXT'
	},
	{
		'TORRENT_SITE_TITLE': 'torrentboza',
		'TORRENT_SITE_URL': 'https://torrentboza.com',
		'BO_TABLE_LIST': ['movie', 'ani'],
		'XPATH_LIST_TAG'      : '//*[@id="fboardlist"]/div[1]/ul/li[%s]/div[2]/a',
		'DOWNLOAD_FILE' : 'ON',
		#'DOWNLOAD_PATH' : 'D:\\work\\makerss\\sub'
	},
	{
		'TORRENT_SITE_TITLE': 'torrentboza',
		'TORRENT_SITE_URL': 'https://torrentboza.com',
		'BO_TABLE_LIST': ['ero_movie'],
		'XPATH_LIST_TAG'      : '//*[@id="fboardlist"]/div[1]/ul/li[%s]/div[2]/a',
	},
	# 4.  Ʈ   
	{
		'TORRENT_SITE_TITLE': 'torrenthaja',
		'TORRENT_SITE_URL': 'https://torrenthaja.com',
		'BO_TABLE_LIST': ['torrent_drama', 'torrent_ent', 'torrent_docu'],
		'XPATH_LIST_TAG'      : '//table[@class="table table-hover"]/tbody/tr[%s]/td[2]/div/a',
		'STEP' : 2,
		'HOW' : 'USING_MAGNET_REGAX',
		'MAGNET_REGAX' : "magnet_link\(\'(?P<magnet>.*?)\'\)",
		'MAGNET_MAKE_URL' : 'magnet:?xt=urn:btih:%s',
		'QUERY' : '&sca=&sop=and&sfl=wr_subject&stx=NEXT'
	},
	{
		'TORRENT_SITE_TITLE': 'torrenthaja',
		'TORRENT_SITE_URL': 'https://torrenthaja.com',
		'BO_TABLE_LIST': ['torrent_movie', 'torrent_kmovie'],
		'XPATH_LIST_TAG'      : '//table[@class="table table-hover"]/tbody/tr[%s]/td[2]/div/a',
		'STEP' : 2,
		'HOW' : 'USING_MAGNET_REGAX',
		'MAGNET_REGAX' : "magnet_link\(\'(?P<magnet>.*?)\'\)",
		'MAGNET_MAKE_URL' : 'magnet:?xt=urn:btih:%s',
		'DOWNLOAD_FILE' : 'ON'
	},
	# 7.  Ʈ .   Ʈ   QUERY     
	{
		'TORRENT_SITE_TITLE': 'torrentwal',
		'TORRENT_SITE_URL': 'https://torrentwal.net',
		'BO_TABLE_LIST': ['torrent_variety', 'torrent_tv', 'torrent_docu' ],
		'XPATH_LIST_TAG'      : '//*[@id="main_body"]/table/tbody/tr[%s]/td[1]/nobr/a',
		'HOW' : 'INCLUDE_MAGNET_IN_INPUT',
	},
	{
		'TORRENT_SITE_TITLE': 'torrentwal',
		'TORRENT_SITE_URL': 'https://torrentwal.net',
		'BO_TABLE_LIST': ['torrent_movie' ],
		'XPATH_LIST_TAG'      : '//*[@id="main_body"]/table/tbody/tr[%s]/td[1]/nobr/a',
		'HOW' : 'INCLUDE_MAGNET_IN_INPUT',
		'DOWNLOAD_FILE' : 'ON',
		'DOWNLOAD_REGEX' : "file_download\(\'(?P<url>.*?)\'\,\s?\'(?P<filename>.*?)\'",
		#'DOWNLOAD_PATH' : 'D:\\work\\makerss\\sub'
	}
]
"""
SITE_LIST = [
	{
		'TORRENT_SITE_TITLE': 'torrentwal',
		'TORRENT_SITE_URL': 'https://torrentwal.net',
		'BO_TABLE_LIST': ['torrent_movie' ],
		'XPATH_LIST_TAG'      : '//*[@id="main_body"]/table/tbody/tr[%s]/td[1]/nobr/a'		#'DOWNLOAD_PATH' : 'D:\\work\\makerss\\sub'
	},
]


def GetList(driver, site, cate):
	#   Ʈ   
	indexList = []
	max_page = site['MAX_PAGE'] if 'MAX_PAGE' in site else 1
	for page in range(1, max_page+1):
		print('PAGE : %s' % page)
		if 'SITE_TYPE' not in site: u = '%s/bbs/board.php?bo_table=%s&page=%s' % (site['TORRENT_SITE_URL'], cate, page)
		else: u = site['BO_TABLE_URL'] % cate;
		if 'QUERY' in site: u += site['QUERY']
		print('URL : %s' % u)
		driver.get(u)

		list_tag = site['XPATH_LIST_TAG'][:site['XPATH_LIST_TAG'].find('[%s]')]
		list = WebDriverWait(driver, 3).until(lambda driver: driver.find_elements_by_xpath(list_tag))
		step = 1 if 'STEP' not in site else site['STEP']
		start = 1 if 'START_INDEX' not in site else site['START_INDEX']
		for i in range(start, len(list)+1, step):
			try:
				a = WebDriverWait(driver, 3).until(lambda driver: driver.find_element_by_xpath(site['XPATH_LIST_TAG'] % i))
				if a.get_attribute('href').find(cate) == -1: continue
				item = {}
				item['title'] = a.text.strip()
				item['detail_url'] = a.get_attribute('href')
				indexList.append(item)
			except:
				print('NOT BBS : %s' % i)
				exc_info = sys.exc_info()
				traceback.print_exception(*exc_info)
	#           ũ   
	list = []
	for item in indexList:
		print ('URL : %s' % item['detail_url'])
		driver.get(item['detail_url'])
		if 'HOW' not in site or site['HOW'] != 'USING_MAGNET_REGAX':
			try:
				# TODO 
				if site['TORRENT_SITE_TITLE'] == 'tfreeca': driver.switch_to_frame("external-frame")
				if 'HOW' in site and site['HOW'] == 'INCLUDE_MAGNET_IN_INPUT': link_element = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_xpath("//input[starts-with(@value,'magnet')]"))
				else: link_element = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_xpath("//a[starts-with(@href,'magnet')]"))
				for magnet in link_element:
					if 'HOW' in site and site['HOW'] == 'INCLUDE_MAGNET_IN_LIST_AND_INCLUDE_LIST_ON_VIEW':
						if not magnet.text.startswith('magnet'): break
					if 'HOW' in site and site['HOW'] == 'INCLUDE_MAGNET_IN_INPUT':
						entity = {}
						entity['title'] = item['title']
						entity['link'] = magnet.get_attribute('value')
						print entity['link']
						list.append(entity)
						try: print('TITLE : %s\nLINK : %s' % (entity['title'], entity['link']))
						except: pass
						continue
					idx2 = 0
					# torrentao    magnet      
					while True:
						idx1 = magnet.get_attribute('href').find('magnet:?xt=urn', idx2)
						idx2 = magnet.get_attribute('href').find('magnet:?xt=urn', idx1+1)
						if idx2 == -1: idx2 = len(magnet.get_attribute('href'))
						#     
						entity = {}
						entity['title'] = item['title']
						entity['link'] = magnet.get_attribute('href')[idx1:idx2]
						flag = False
						for tmp in list:
							if tmp['link'] == entity['link']:
								flag = True
								break
						if flag == False:
							list.append(entity)
							try: print('TITLE : %s\nLINK : %s' % (entity['title'], entity['link']))
							except: pass
						if idx2 == len(magnet.get_attribute('href')): break
			except:
				exc_info = sys.exc_info()
				traceback.print_exception(*exc_info)

		elif site['HOW'] == 'USING_MAGNET_REGAX':
			try:
				regax = re.compile(site['MAGNET_REGAX'], re.IGNORECASE)
				#match = regax.search(driver.page_source)
				match = regax.findall(driver.page_source)
				for m in match:
					entity = {}
					entity['title'] = item['title']
					entity['link'] = site['MAGNET_MAKE_URL'] % m
					list.append(entity)
					try: print('TITLE : %s\nLINK : %s' % (entity['title'], entity['link']))
					except: pass
			except:
				exc_info = sys.exc_info()
				traceback.print_exception(*exc_info)
		
		# ÷        
		if 'DOWNLOAD_FILE' in site and site['DOWNLOAD_FILE'] is 'ON':
			try:
				if 'DOWNLOAD_REGEX' not in site:
					tmp = '%s/bbs/download.php' % site['TORRENT_SITE_URL']
					link_element = WebDriverWait(driver, 5).until(lambda driver: driver.find_elements_by_xpath("//a[starts-with(@href,'%s')]" % tmp))
				else:
					link_element = WebDriverWait(driver, 5).until(lambda driver: driver.find_elements_by_xpath("//a[contains(@href,'bbs/download.php')]"))

				for a_tag in link_element:
					flag = False
					filename = ''
					if 'DOWNLOAD_REGEX' not in site:
						tmp = a_tag.text.replace('\n', ' ').replace('\r', '')
						url = a_tag.get_attribute('href')
					else:
						regax = re.compile(site['DOWNLOAD_REGEX'], re.IGNORECASE)
						match = regax.search(a_tag.get_attribute('href'))
						if not match: continue
						tmp = match.group('filename')
						url = match.group('url')
						idx = url.find('bbs/download.php')
						url = site['TORRENT_SITE_URL'] + '/' + url[idx:]
					for ext in ['.torrent', '.smi', '.srt', '.ass']:
						idx = tmp.find(ext)
						if idx != -1:
							flag = True
							if ext != '.torrent': 
								filename = tmp[:idx + len(ext)]
								filename = filename.replace('\\', ' ').replace('/', ' ').replace(':', ' ').replace('*', ' ').replace('?', ' ').replace('"', ' ').replace('<', ' ').replace('>', ' ').replace('|', ' ')
							break
					if flag and filename is not '':
						print('DOWNLOAD : %s' % filename)
						download(driver, url, filename, site['DOWNLOAD_PATH'] if 'DOWNLOAD_PATH' in site else None)
			except:
				exc_info = sys.exc_info()
				traceback.print_exception(*exc_info)
				pass
		if 'SLEEP' in site: time.sleep(site['SLEEP'])
	return list
