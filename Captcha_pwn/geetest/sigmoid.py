#!/usr/bin/env python
# encoding: utf-8

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from PIL import Image as image
from PIL import ImageChops
from math import exp
import time,re,cStringIO,urllib2,random


def merge_image(in_image,location_list):
	
	# 将图片流打开并转换色彩模式和大小
	old_im 	= image.open(in_image)
	new_im  = image.new("RGB",(260,116))

	# 以y值为标准将每张小图片分为两类
	# 分别为-58和0，参见url
	im_list_upper = []
	im_list_down  = []
	for location in location_list:
		if location['y']  == -58:
			im_list_upper.append(old_im.crop((abs(location['x']),58,abs(location['x'])+10,166))) # 可能有报错
		if location['y']  ==   0:
			im_list_down.append(old_im.crop((abs(location['x']),0,abs(location['x'])+10,58)))
	# 拼接图片
	x_offset = 0
	for im in im_list_upper:
		new_im.paste(im, (x_offset,0))
		x_offset += im.size[0]

	x_offset = 0
	for im in im_list_down:
		new_im.paste(im, (x_offset,58))
		x_offset += im.size[0]

	# 返回图片
	return new_im



def get_image(driver,div):

	# 初始化
	background_images  =   driver.find_elements_by_xpath(div)
	location_list      =   []
	imageurl           =   ''

	# 将所有小图片的url解析出来
	# 可以观察到url是固定的，因此只要提取一次就可以
	# 将每张小图片的位置提取出来，每张小图片需要分别提取其坐标x及y的值，定义在一个字典里

	for background_image in background_images:
		location={}
		location['x']=int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][1])
		location['y']=int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][2])
		imageurl=re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][0]
		location_list.append(location)
	imageurl=imageurl.replace("webp","jpg")
    # 将图片获取后写入内存，避免了先写入磁盘再都出来的繁琐步骤
	jpgfile = cStringIO.StringIO(urllib2.urlopen(imageurl).read())
    # 重新拼接图片
	image = merge_image(jpgfile,location_list)

    # 返回图片
	return image



def is_similar(iamge1,image2,x,y):
	# 取像素点对比RGB值，选定一个阈值
	# 若RGB三个值任一个大于阈值则认定此处为不同
	# 返回此处的横坐标值
	threshold = 50
	pixel_1 = iamge1.getpixel((x,y))
	pixel_2 = image2.getpixel((x,y))
	for i in range(0,3):
		if abs(pixel_1[i]-pixel_2[i]) >= threshold:
			return False
	return True



def get_diff_X(iamge1,image2):
	for i in range(0,260):
		for j in range(0,116):
			if is_similar(iamge1,image2,i,j) == False:
				return i


def get_track(X_length):
	track_list = [0:X_length:1]
	# 为了防止鼠标轨迹识别，采用sigmoid函数模拟轨迹
	tmp_list = map(lambda x: 1.0/(1+exp(-1*x)),[0,1,2,3,4,5,6])
	track_list = [0.265*X_length,0.235*X_length]
	for i in range(1,len(tmp_list)):
		track_list.append((tmp_list[i] - tmp_list[i-1])*X_length)
	return track_list


def main():
	# 打开网页
	driver = webdriver.Firefox()
	driver.get('http://127.0.0.1:8000/')


	# 确保元素被加载出来，每500ms刷新一次，直至返回结果为真或达到指定时间并抛出错误
	try:
		WebDriverWait(driver, 30).until(lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']").is_displayed())
		WebDriverWait(driver, 30).until(lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_cut_bg gt_show']").is_displayed())
		WebDriverWait(driver, 30).until(lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_cut_fullbg gt_show']").is_displayed())
	except NoSuchElementException:
		print "[!] Fail to initialize the element."



	# 下载图片
	image1 = get_image(driver,"//div[@class='gt_cut_bg gt_show']/div") 
	image2 = get_image(driver,"//div[@class='gt_cut_fullbg gt_show']/div")

	# 计算滑动截止位置X
	loc = get_diff_X(image1,image2)

	# 生成移动轨迹
	track_list = get_track(loc)

	# 定位滑动拼图时所操作的元素
	try:
		element=driver.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
		y = element.location['y']
	except NoSuchElementException:
		print "[!] Fail to find the virtual ball"


	# 开始模拟滑动过程
	print "Step 1: Click the ball."
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	ActionChains(driver).click_and_hold(on_element=element).perform()
	time.sleep(0.1)

	print "Step 2: Move the ball."
	for track in track_list:
		# 加减值是因为轨迹为圆球中心轨迹，而参考点为圆球左上角
		ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=track+22, yoffset=y-600).perform()
		time.sleep(random.randint(1,5)/1000)

	print "Step 3: Release the ball."
	ActionChains(driver).release(on_element=element).perform()
	time.sleep(5)


main()
