# coding: utf-8
import base64
import cv2
import requests

# 图像处理标准库
from PIL import Image
# 进行图片的截取拼凑
imgu = Image.open("./2u.png")
imgd = Image.open("./2d.png")
img_temp = imgu.crop((0, 0, imgu.width, imgu.height/2))
img_temp.show()
imgd.paste(img_temp, (0, 0))
imgd.save("1m.png")


def show(name):
    '''展示圈出来的位置'''
    cv2.imshow('Show', name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def _tran_canny(image):
    """消除噪声"""
    image = cv2.GaussianBlur(image, (3, 3), 0)
    return cv2.Canny(image, 50, 150)


def detect_displacement(img_slider_path, image_background_path):
    """detect displacement"""
    # # 参数0是灰度模式
    image = cv2.imread(img_slider_path, 0)
    template = cv2.imread(image_background_path, 0)

    # 寻找最佳匹配
    res = cv2.matchTemplate(_tran_canny(image), _tran_canny(template), cv2.TM_CCOEFF_NORMED)
    # 最小值，最大值，并得到最小值, 最大值的索引
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc[0]  # 横坐标
    # 展示圈出来的区域
    x, y = max_loc  # 获取x,y位置坐标
    w, h = image.shape[::-1]  # 宽高
    cv2.rectangle(template, (x, y), (x + w, y + h), (7, 249, 151), 2)
    # show(template)
    print(max_loc)
    return top_left


# 均值哈希算法
def aHash(img):
    # 缩放为8*8
    img = cv2.resize(img, (8, 8), interpolation=cv2.INTER_CUBIC)
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # s为像素和初值为0，hash_str为hash值初值为''
    s = 0
    hash_str = ''
    # 遍历累加求像素和
    for i in range(8):
        for j in range(8):
            s = s+gray[i, j]
    # 求平均灰度
    avg = s/64
    # 灰度大于平均值为1相反为0生成图片的hash值
    for i in range(8):
        for j in range(8):
            if gray[i, j] > avg:
                hash_str = hash_str+'1'
            else:
                hash_str = hash_str+'0'
    return hash_str


# Hash值对比
def cmpHash(hash1, hash2):
    n=0
    # hash长度不同则返回-1代表传参出错
    if len(hash1) != len(hash2):
        return -1
    # 遍历判断
    for i in range(len(hash1)):
        # 不相等则n计数+1，n最终为相似度
        if hash1[i] != hash2[i]:
            n = n+1
    return n


# 对比图片的相似度
def compare_picture(pic):
    img0 = cv2.imread(pic)
    img1 = cv2.imread(f'./background1.png')
    img2 = cv2.imread(f'./background2.png')
    hash_1 = aHash(img1)
    hash_2 = aHash(img2)
    hash_0 = aHash(img0)
    n1 = cmpHash(hash_1, hash_0)
    n2 = cmpHash(hash_2, hash_0)
    if n1 < n2:
        return "1"
    else:
        return "2"


if __name__ == '__main__':
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }
    # 获取cookie值
    cookie_url = "http://gcxm.hunanjs.gov.cn/AjaxHandler/PersonHandler.ashx?method=GetListPage&type=1&corptype_1=&corpname_1=&licensenum_1=&Province_1=430000&City_1=&county_1=&persontype=&persontype_2=&personname_2=&idcard_2=&certnum_2=&corpname_2=&prjname_3=&corpname_3=&prjtype_3=&cityname_3=&year_4=&jidu_4=3&corpname_4=&corpname_5=&corpcode_5=&legalman_5=&cityname_5=&SafeNum_6=&corpname_6=&corpname_7=&piciname_7=&corptype_7=&corpname_8=&corpcode_8=&legalman_8=&cityname_8=&pageSize=30&pageIndex=1&xypjcorptype=3"
    resp = requests.get(cookie_url, headers=headers)
    print("cookie request", resp.status_code)
    cookies = dict(resp.cookies.items())
    print(cookies)
    # Setp: 2 获取网页上的图片,与本地图片做对比
    url_pic = "http://gcxm.hunanjs.gov.cn/AjaxHandler/PersonHandler.ashx?method=GetVerifyImg"

    resp = requests.get(url=url_pic, headers=headers, cookies=cookies)
    print(resp.status_code)
    param = eval(resp.text)

    data = base64.b64decode(param[0])
    with open("./target.png", mode="wb") as f:
        f.write(data)

    data_b = base64.b64decode(param[1])
    with open("./background.png", mode="wb") as f:
        f.write(data_b)

    # 对比图片
    pic_num = compare_picture("./background.png")
    print("pic_num", pic_num)

    # 获取到图片的偏移位置
    top_left = detect_displacement("./target.png", f"./background{pic_num}.png")
    print("top_left", top_left)

    print(param[2], param[-1])
    url_data = f"http://gcxm.hunanjs.gov.cn/AjaxHandler/PersonHandler.ashx?method=GetListPage&type=1&corptype_1=&corpname_1=&licensenum_1=&Province_1=430000&City_1=&county_1=&persontype=&persontype_2=&personname_2=&idcard_2=&certnum_2=&corpname_2=&prjname_3=&corpname_3=&prjtype_3=&cityname_3=&year_4=&jidu_4=2&corpname_4=&corpname_5=&corpcode_5=&legalman_5=&cityname_5=&SafeNum_6=&corpname_6=&corpname_7=&piciname_7=&corptype_7=&corpname_8=&corpcode_8=&legalman_8=&cityname_8=&pageSize=30&pageIndex=1&xypjcorptype=3&moveX={top_left}&verifyid={param[2]}"

    resp = requests.get(url_data, headers=headers, cookies=cookies)

    print(resp.status_code)
    print(resp.text)







