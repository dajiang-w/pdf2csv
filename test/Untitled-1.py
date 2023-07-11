import fitz
import re
import os


def save_pdf_img(path,save_path):
    '''
    path: pdf的路径
    save_path : 图片存储的路径
    '''
    # 使用正则表达式来查找图片
    checkXO = r"/Type(?= */XObject)" 
    checkIM = r"/Subtype(?= */Image)"  
    # 打开pdf
    doc = fitz.open(path)
    # 图片计数
    imgcount = 0
    # 获取对象数量长度
    lenXREF = doc.xref_length()
 
    # 打印PDF的信息
    print("文件名:{}, 页数: {}, 对象: {}".format(path, len(doc), lenXREF - 1))
    
    
    # 遍历每一个图片对象
    for i in range(1, lenXREF):
        # 定义对象字符串
        text = doc.xref_object(i)
#         print(i,text)
        isXObject = re.search(checkXO, text)
        # 使用正则表达式查看是否是图片
        isImage = re.search(checkIM, text)
        # 如果不是对象也不是图片，则continue
        if not isXObject or not isImage:
            continue
        imgcount += 1
        # 根据索引生成图像
        print(text)
        pix = fitz.Pixmap(doc, i)
        # 根据pdf的路径生成图片的名称  path.replace('\\', '_') + 
        new_name = "img{}.png".format(imgcount)
        # new_name = new_name.replace(':', '')
        # 如果pix.n<5,可以直接存为PNG
        if pix.n < 5:
            pix.pil_save(os.path.join(save_path, new_name))
        # 否则先转换CMYK
        else:
            pix0 = fitz.Pixmap(fitz.csRGB, pix)
            pix0.pil_save(os.path.join(save_path, new_name))
            pix0 = None
        # 释放资源
        pix = None
        print("提取了{}张图片".format(imgcount))


file_path = './tmp/0001186421.pdf' # PDF 文件路径
dir_path = './imgs/' # 存放图片的文件夹

save_pdf_img(file_path,dir_path)

