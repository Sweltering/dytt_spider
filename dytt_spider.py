# 爬取电影天堂2018新片电影数据
from lxml import etree
import requests

BASE_DOMAIN = 'http://www.dytt8.net'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
    'Referer': 'http://www.dytt8.net/html/gndy/dyzz/list_23_2.html'
}


# 爬取该页的电影的url
def get_detail_urls(url):
    response = requests.get(url=url, headers=HEADERS)  # 爬取第一页的html
    text = response.text

    html = etree.HTML(text)
    detail_urls = html.xpath('//table[@class="tbspan"]//a/@href')  # 获取该页每个电影的url
    detail_urls = map(lambda url: BASE_DOMAIN + url, detail_urls)  # 获取到的每个href加上http://www.dytt8.net得到一个完整url的列表
    return detail_urls


# 爬取电影的详情页面信息
def parse_detail_page(url):
    movie = {}  # 存放爬取到的数据

    response = requests.get(url, HEADERS)
    text = response.content.decode('gbk', 'ignore')
    html = etree.HTML(text)

    try:
        # 爬取数据
        title = html.xpath('//div[@class="title_all"]//font[@color="#07519a"]/text()')  # 爬取标题
        movie['title'] = title
        zoom = html.xpath('//div[@id="Zoom"]')[0]  # zoom标签，下面有好多数据
        imgs = zoom.xpath('.//img/@src')  # 列表中有海报和电影截图
        cover = imgs[0]  # 海报
        screenshot = imgs[1]  # 电影截图
        movie['cover'] = cover
        movie['screenshot'] = screenshot

        # 处理电影相关数据
        def parse_info(info, rule):
            return info.replace(rule, "").strip()

        infos = zoom.xpath('.//text()')  # 电影文本相关信息
        for index, info in enumerate(infos):
            if info.startswith('◎年　　代'):
                info = parse_info(info, "◎年　　代")  # 年代
                movie['year'] = info
            elif info.startswith('◎产　　地'):
                info = parse_info(info, '◎产　　地')  # 产地
                movie['country'] = info
            elif info.startswith('◎类　　别'):
                info = parse_info(info, '◎类　　别')  # 类别
                movie['category'] = info
            elif info.startswith("◎豆瓣评分"):
                info = parse_info(info, '◎豆瓣评分')  # ◎豆瓣评分
                movie['douban_rating'] = info
            elif info.startswith('◎片　　长'):
                info = parse_info(info, '◎片　　长')  # ◎片　　长
                movie['duration'] = info
            elif info.startswith('◎导　　演'):
                info = parse_info(info, '◎导　　演')  # ◎导　　演
                movie['director'] = info
            elif info.startswith('◎主　　演'):
                info = parse_info(info, '◎主　　演')
                actors = [info]  # 存放演员
                for x in range(index + 1, len(infos)):
                    actor = infos[x].strip()
                    if actor.startswith('◎简　　介'):
                        break
                    actors.append(actor)
                movie['actors'] = actors
            elif info.startswith('◎简　　介 '):  # ◎简　　介
                info = parse_info(info, '◎简　　介 ')  # ◎简　　介
                for x in range(index + 1, len(infos)):
                    profile = infos[x].strip()
                    if profile.startswith('【下载地址】'):
                        break
                    movie['profile'] = profile

        download_url = html.xpath('//td[@bgcolor="#fdfddf"]/a/@href')  # 下载地址
        movie['download_url'] = download_url
    except Exception as e:
        pass

    return movie


# 爬取前7页的url
def spider():
    base_url = 'http://www.dytt8.net/html/gndy/dyzz/list_23_{}.html'
    movies = []  # 存放爬取到的电影信息
    for x in range(1, 8):  # 爬取前7页url
        url = base_url.format(x)
        detail_urls = get_detail_urls(url)  # 爬取该页的电影的url
        for detail_url in detail_urls:  # 解析每个电影的详情
            movie = parse_detail_page(detail_url)
            movies.append(movie)
            print(movie)
    # print(movies)


if __name__ == '__main__':
    spider()
