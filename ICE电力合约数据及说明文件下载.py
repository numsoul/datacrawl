# -*- coding: utf-8 -*-

from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import pandas as pd


#指定url获取BS对象实例
def parse_url(url):
	try:
		html=urlopen(url)
	except HTTPError as e:
		return None
	else:
		return BeautifulSoup(html.read(),"lxml")

#返回合约名称及其链接的词典，名称：合约详情网址
def get_ice_el_list(url):
	d=dict()
	el_soup=parse_url(url)
	try:
		ta=el_soup.find("table",{"class":"table table-data"})
		t=ta.thead.next_sibling.next_sibling#找到表格开始
		for sibling in t.tr.next_siblings:
			link_tag=sibling.td.next_sibling.next_sibling.find("a")
			contract_name=link_tag.get_text()
			contract_link="https://www.theice.com"+link_tag.attrs['href']
			d[contract_name]=contract_link
	except AttributeError as e:
		return None
		print("Tag was not found")
	else:
		return d

#输入合约链接字典，返回合约大小
def get_contract_size(d):
	ct_size=dict()
	i=0
	try:	
		for k in d:
			print(i)
			i=i+1
			url=d.get(k)
			bs=parse_url(url)
			des=bs.find('p',{"itemprop":"description"}).parent.next_sibling.find('dl')
			size=des.find('dt',text='Contract Size').next_sibling.get_text()
			ct_size[k]=size
	except AttributeError as e:
		print(e)
		return None
	else:
		return ct_size


#输入合约链接字典，返回合约详情pdf文件地址字典
def getfileurl(d):
	url_dict=dict()
	for k in d:
		url_dict[k]="https://www.theice.com/api/productguide/spec/"+d[k][32:d[k].find('/',32)]+"/pdf"
	return url_dict



url="https://www.theice.com/products/Futures-Options/Energy/Electricity"
merged=dict() #把8页的合约列表合并为一个
for i in range(8):
	if i==0:
		urli=url
	else:
		urli=url+'/page'+str(i+1)
	d=get_ice_el_list(urli)
	merged=dict(merged,**d)


#下载文件
file_dict=getfileurl(merged)
for k in file_dict:
	u=urlopen(file_dict[k])
	f=open(k+".pdf","wb")
	buffer=u.read()
	f.write(buffer)
	f.close()
	u.close()
