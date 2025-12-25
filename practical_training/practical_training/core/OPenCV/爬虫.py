import os
import requests
from bs4 import BeautifulSoup
import re
import urllib.request
import sqlite3

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


def DownLoadImage(pic_urls, ImageFilePath, keyword, db_conn, max_images):
    """给出图片链接列表, 下载所有图片"""
    global ImageCount
    for pic_url in pic_urls:
        # 如果已经达到最大下载数量，退出循环
        if ImageCount >= max_images:
            print(f"已达到最大下载数量 {max_images}，停止下载")
            break

        try:
            cursor = db_conn.cursor()
            cursor.execute("SELECT 1 FROM images WHERE original_url = ?", (pic_url,))
            if cursor.fetchone():
                print(f"跳过已存在的图片: {pic_url}")
                continue

            pic = requests.get(pic_url, timeout=15)
            ImageCount += 1
            local_filename = f"{ImageCount}.jpg"
            local_path = os.path.join(ImageFilePath, local_filename)

            with open(local_path, 'wb') as f:
                f.write(pic.content)

            # 插入数据库
            cursor.execute('''
                INSERT OR IGNORE INTO images 
                (keyword, original_url, local_path, source_page)
                VALUES (?, ?, ?, ?)
            ''', (keyword, pic_url, local_path, "https://image.baidu.com"))

            db_conn.commit()
            print(f'✅ 已下载第{ImageCount}张图片: {pic_url}')

        except Exception as e:
            print(f'❌ 下载失败: {pic_url}, 错误: {e}')
            continue


def CreateDirectory(path):
    """创建目录，如果不存在的话"""
    if not os.path.exists(path):
        os.makedirs(path)


def CrawlPicture(keyword, max_images):
    # 获取用户的桌面路径，并创建保存图片的目录
    desktop_path = os.path.join(os.path.expanduser("~"), 'Desktop')
    picture_path = os.path.join(desktop_path, 'picture')
    CreateDirectory(picture_path)

    # 创建以关键字命名的子文件夹
    keyword_path = os.path.join(picture_path, keyword)
    CreateDirectory(keyword_path)

    # === 新增：初始化数据库 ===
    db_path = os.path.join(picture_path, 'image_metadata.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            original_url TEXT UNIQUE NOT NULL,   -- 防止重复爬取
            local_path TEXT NOT NULL,
            source_page TEXT,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # 初始化爬取标志
    CrawlFlag = True
    NextPageURL = f"https://image.baidu.com/search/flip?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word={urllib.parse.quote(keyword, safe='/')}"

    while CrawlFlag:
        ImageURL, NextPageURL = GetPageURL(NextPageURL)
        if ImageURL:
            unique_urls = list(set(ImageURL))
            DownLoadImage(unique_urls, keyword_path, keyword, conn, max_images)
        if not NextPageURL or ImageCount >= max_images:
            CrawlFlag = False

    # 爬取结束，关闭数据库
    conn.close()
    print(f"🎉 爬取完成！共下载 {ImageCount} 张图片，元数据已保存至 {db_path}")


if __name__ == '__main__':
    keyword = input("请输入要爬取的关键词: ")
    max_images = int(input("请输入要下载的最大图片数量: "))
    CrawlPicture(keyword, max_images)