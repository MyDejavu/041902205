import asyncio
from pyppeteer import launch
import os
from lxml import etree
import random
import time
import random


# def screen_size():
#     # 使用tkinter获取屏幕大小
#     import tkinter
#     tk = tkinter.Tk()
#     width = tk.winfo_screenwidth()
#     height = tk.winfo_screenheight()
#     tk.quit()
#     return width, height


async def pyppteer_fetchUrl(url):
    browser = await launch({'headless': True, 'dumpio': True, 'autoClose': True})
    page = await browser.newPage()
    # 绕过浏览器检测
    await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'
                                     '{ webdriver:{ get: () => false } }) }')
    # 设置页面视图大小
    # width, height = screen_size()
    # await page.setViewport(viewport={'width': width, 'height': height})
    await page.setUserAgent(
        'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36 Edg/105.0.1343.27')
    await page.goto(url)
    # await asyncio.sleep(10)
    await asyncio.wait([page.waitForNavigation()])
    str = await page.content()
    await browser.close()
    return str


# 获取每一个有防控数据页面的内容（页面源代码）
def Get_Pagesouce(url):
    return asyncio.get_event_loop().run_until_complete(pyppteer_fetchUrl(url))


# 获取每一页的24条url
def getPageUrl():
    url_list = []
    for page in range(1, 42):
        if page == 1:
            url_list.append('http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml')
        else:
            page_url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_' + str(page) +'.shtml'
            url_list.append(page_url)
    return url_list


# 通过 getDateUrl发布日期。
def getFiles(html):
    file_list =[]
    html_tree = etree.HTML(html)
    li_lsit = html_tree.xpath("/html/body/div[3]/div[2]/ul/li")
    for li in li_lsit:
        file = li.xpath("./a/text()")
        file = "".join(file)
        date = li.xpath('./span/text()')
        date = "".join(date)
        file_name = date + "-" + file
        # print(file_name)
        file_list.append(file_name)
    return file_list


def getLinkUrl(html):
    day_urls = []
    html_tree = etree.HTML(html)
    li_list = html_tree.xpath("/html/body/div[3]/div[2]/ul/li")
    for li in li_list:
        day_url = li.xpath('./a/@href')
        day_url = "http://www.nhc.gov.cn" + "".join(day_url[0])
        day_urls.append(day_url)
    return day_urls


def getContent(html):
    html_tree = etree.HTML(html)
    text = html_tree.xpath('/html/body/div[3]/div[2]/div[3]//text()')
    day_text = "".join(text)
    return day_text


def saveFile(path, filename, content):
    if not os.path.exists(path):
        os.makedirs(path)
    # 保存文件
    with open(path + filename + ".txt", 'w', encoding='utf-8') as f:
        f.write(content)


if "__main__" == __name__:
    start = time.time()
    for url in getPageUrl():
        s = Get_Pagesouce(url)
        time.sleep(1)
        filenames = getFiles(s)
        # print("文件名列表：", filenames)
        index = 0
        links = getLinkUrl(s)
        # print("收集到的所有链接：", links)
        for link in links:
            html = Get_Pagesouce(link)
            content = getContent(html)
            print(filenames[index] + "爬取成功")
            saveFile('C:/Users/OSHMK/Desktop/wjwData/', filenames[index], content)
            index = index + 1
        print("-----"*20)
    end = time.time()
    print(f"所有内容爬取完成，所用时间：{end-start}s")
