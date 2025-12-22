import urllib.request
import re
import os


# 获取网页源代码
def getHtmlCode(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        page = urllib.request.urlopen(req, timeout=10).read()
        page = page.decode('utf-8', errors='ignore')
        return page
    except Exception as e:
        print(f"获取网页源代码失败：{e}")
        return None


# 解析图片链接并下载
def getImg(page, save_dir):
    if not page:
        print("网页源代码为空，无法解析图片！")
        return

    img_pattern = r'https?://tse\d+\.mimg\.com/[^\s\'"<>]*|https?://tse\d+-[a-z]\.mimg\.com/[^\s\'"<>]*'
    imgList = re.findall(img_pattern, page)
    # 提取链接，去掉元组的第二个元素
    print("imgList内容：", imgList)

    if not imgList:
        print("未匹配到任何图片链接！")
        return

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"创建保存目录：{save_dir}")

    x = 0
    success_count = 0
    fail_count = 0
    print('imgList内容：',imgList)


    for x, img_suffix in enumerate(imgList, 1):  # img_suffix 就是完整 URL
        try:
            print(f'正在下载[{x}]{img_suffix}')
            # 直接下载，别再 re.search
            urllib.request.urlretrieve(
                img_suffix,  # ← 直接用
                os.path.join(save_dir, f'{x}.{img_suffix.split(".")[-1].lower().split("?")[0]}')
            )
            success_count += 1
        except Exception as e:
            print(f'下载失败[{x}]{e}')
            fail_count += 1
            continue

    print(f"\n下载完成！总计匹配 {len(imgList)} 个图片链接")
    print(f"成功下载：{success_count} 张 | 下载失败：{fail_count} 张")
    print(f"图片保存路径：{save_dir}")


if __name__ == '__main__':
    # -------------------------- 核心修改：手动输入路径 --------------------------
    # 提示用户输入下载路径，支持绝对路径/相对路径
    while True:
        save_path = input("请输入图片下载位置（例如：E:/img/ 或 ./下载图片/）：").strip()
        # 允许直接回车使用默认路径
        if not save_path:
            save_path = r"./默认下载图片/"
            print(f"未输入路径，使用默认路径：{save_path}")
            break
        # 检查路径格式是否合法（简单校验）
        if save_path:
            break
    # ---------------------------------------------------------------------------

    # 必应图片搜索URL
    url = 'https://www.bing.com/search?q=%E8%B5%B5%E4%B8%BD%E9%A2%96%E5%86%99%E7%9C%9F%E5%9B%BE%E7%89%87&qs=UT&pq=%E8%B5%B5%E4%B8%BD%E9%A2%96%E5%86%99%E7%9C%9F&sk=HS1&sc=11-5&cvid=671A20D2564844AA8C914454089536AE&FORM=QBRE&sp=2&lq=0&ajf=60&mkt=zh-CN'
    print("开始获取网页源代码...")
    page = getHtmlCode(url)

    print("开始解析并下载图片...")
    getImg(page, save_path)