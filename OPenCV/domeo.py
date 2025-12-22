import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
import re

ImageCount = 0


def GetPageURL(URLStr):
    # 获取一个页面的所有图片的URL+下页的URL
    if not URLStr:
        print('现在是最后一页啦！爬取结束')
        return [], ''
    try:
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
        }
        response = requests.get(URLStr, headers=header)
        response.encoding = 'utf-8'
        html = response.text
    except Exception as e:
        print("err=", str(e))
        return [], ''

    # 使用正则表达式提取图片URL
    ImageURL = re.findall(r'"objURL":"(.*?)",', html, re.S)

    # 使用BeautifulSoup解析HTML，提取下一页的URL
    soup = BeautifulSoup(html, 'html.parser')
    NextPageURLS = soup.find('a', class_='n', text='下一页')
    if NextPageURLS:
        NextPageURL = 'http://image.baidu.com' + NextPageURLS['href']
    else:
        NextPageURL = ''

    return ImageURL, NextPageURL

def DownLoadImage(pic_urls, ImageFilePath):
    """给出图片链接列表, 下载所有图片"""
    global ImageCount
    for i, pic_url in enumerate(pic_urls):
        try:
            pic = requests.get(pic_url, timeout=15)
            ImageCount += 1
            string = os.path.join(ImageFilePath, f"{ImageCount}.jpg")
            with open(string, 'wb') as f:
                f.write(pic.content)
                print(f'已下载第{ImageCount}张图片: {pic_url}')
        except Exception as e:
            print(f'下载第{ImageCount}张图片失败: {e}')
            ImageCount -= 1
            continue

def CreateDirectory(path):
    """创建目录，如果不存在的话"""
    if not os.path.exists(path):
        os.makedirs(path)


def CrawlPicture(keyword):
    # 获取用户的桌面路径，并创建保存图片的目录
    desktop_path = os.path.join(os.path.expanduser("~"), 'Desktop')
    picture_path = os.path.join(desktop_path, 'picture')
    CreateDirectory(picture_path)

    # 创建以关键字命名的子文件夹
    keyword_path = os.path.join(picture_path, keyword)
    CreateDirectory(keyword_path)

    # 初始化爬取标志
    CrawlFlag = True
    NextPageURL = f"https://image.baidu.com/search/flip?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word={urllib.parse.quote(keyword, safe='/')}"

    while CrawlFlag:
        ImageURL, NextPageURL = GetPageURL(NextPageURL)
        if ImageURL:
            DownLoadImage(list(set(ImageURL)), keyword_path)
        if not NextPageURL:
            CrawlFlag = False


if __name__ == '__main__':
    keyword = input("请输入要爬取的关键词: ")
    CrawlPicture(keyword)