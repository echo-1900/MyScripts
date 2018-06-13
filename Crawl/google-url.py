# coding: utf-8
import requests,sys
from lxml import etree

def search(query,num):
	user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
	headers={"User-Agent":user_agent}
	url = r'http://www.google.com/search?q=' + query + '&num=' + str(num)
	return requests.get(url,headers=headers).text

def url_get(response):
	html  = etree.HTML(response)
	url   = html.xpath('//cite')
	return url


def main():
	assert(len(sys.argv)==3)
	query = sys.argv[1]
	num   = sys.argv[2]
	url   = url_get(search(query,num))
	with open(sys.argv[0].encode('base64').strip()+'.txt','w') as f:
		for i in url:
			#去tag
			f.write(i.xpath('string(.)').encode('utf-8')+'\n') 


main()
