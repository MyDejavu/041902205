from lxml import etree
import asyncio
from pyppeteer import launch
import os
import time
import random


async def pyppeteer_main(url):
    # dumpio:是否将浏览器进城标准和标准管道输送到process.stdout和process.stderr
    browser = await launch({'dumpio': True})
    # newPage()相当于在浏览器中新建了一个选项卡
    page = await browser.newPage()
    # 绕过浏览器检测：evaluateOnNewDocument()，该方法是将一段 js 代码加载到页面文档中
    # 当发生页面导航、页面内嵌框架导航的时候加载的 js 代码会自动执行
    # 那么当页面刷新的时候该 js 也会执行，这样就保证了修改网站的属性持久化的目的
    await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'
                                     '{ webdriver:{ get: () => false } }) }')
    # UA验证
    await page.setUserAgent(
        'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36 Edg/105.0.1343.27')
    # 访问主页
    await page.goto(url)
    # await asyncio.sleep(10)
    await asyncio.wait([page.waitForNavigation()])
    # 获取网页源码
    str = await page.content()
    await browser.close()
    return str


# 设置获取每一页的的url
def get_urllist():
    url_list = []
    for page in range(1, 42):
        if page == 1:
            url_list.append('http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml')
        else:
            page_url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_' + str(page) + '.shtml'
            url_list.append(page_url)
    return url_list


# 获取每一页中的链接的文件名称
def get_filelist(html):
    file_list = []
    # 解析服务器响应文件
    html_tree = etree.HTML(html)
    li_list1 = html_tree.xpath("/html/body/div[3]/div[2]/ul/li")
    for li in li_list1:
        file = li.xpath("./a/text()")
        file = "".join(file)
        date = li.xpath('./span/text()')
        date = "".join(date)
        file_name = date + " " + file
        file_list.append(file_name)
    return file_list


#
def get_everydayhtml(html):
    day_urls = []
    html_tree = etree.HTML(html)
    li_list2 = html_tree.xpath("/html/body/div[3]/div[2]/ul/li")
    for li in li_list2:
        day_url = li.xpath('./a/@href')
        day_url = "http://www.nhc.gov.cn" + "".join(day_url[0])
        day_urls.append(day_url)
    return day_urls


# 获取文本内容
def get_content(html):
    html_tree = etree.HTML(html)
    text = html_tree.xpath('/html/body/div[3]/div[2]/div[3]//text()')
    day_text = "".join(text)
    return day_text


def save_file(path, filename, content):
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + filename + ".txt", 'w', encoding='utf-8') as f:
        f.write(content)


if "__main__" == __name__:
    start = time.time()
    for url in get_urllist():
        # 调用pyppeteer_fetchUrl()中await情况的方法
        s = asyncio.get_event_loop().run_until_complete(pyppeteer_main(url))
        time.sleep(random.randint(3, 6))
        filenames = get_filelist(s)
        links = get_everydayhtml(s)
        # 初始化索引
        index = 0
        for link in links:
            html = asyncio.get_event_loop().run_until_complete(pyppeteer_main(link))
            content = get_content(html)
            print(filenames[index] + " is successful")
            save_file('/Users/dejavu/Python/卫健委数据/', filenames[index], content)
            index = index + 1
    end = time.time()
    print(f"所有内容爬取完成，所用时间：{end - start}s")
