'''
2022年6月4日16:41:09 wdj
'''

# 导入模块
import time
import pdfplumber as pp
from functools import reduce
from operator import add
from PIL import Image
import numpy as np
# import pytesseract # replace pytesseract module with paddleocr, to make identification faster.
from paddleocr import PaddleOCR, draw_ocr
import os



class Pdf2txt:
    
    # 初始化参数
    def __init__(self,pdfpath,csvfile):
        self.pdfpath = pdfpath
        self.csvfile = csvfile
        self.text = ''
        self.ocr = PaddleOCR(use_angle_cls = True, use_gpu = False) # replace with paddleocr
    
    # padding image, 给图像增加白边
    def pad_img(self,image, padding_num):    # image is an object of image, padding_num 就是要在图像边缘增加几个像素
        iw, ih = image.size # 原图像尺寸
        w,h = iw + 2 * padding_num, ih + 2 * padding_num
        # print('iw:',iw,'ih:',ih)
        # print('w:',w,'h',h,'padding:',padding_num)
        new_image = Image.new('RGB',(w,h),(256,256,256))
        new_image.paste(image,((w - iw)//2,(h - ih) // 2))
        return new_image

    def img2txt(self,pilimg,zoom,ob_i):  
        # pgimg: page.to_image(resolutino = 300), then pilimg = Image.open("./pgimg300.png")
        # ob_i is a dict of image in pdf
        croprect = (ob_i['x0']*zoom,ob_i['top']*zoom,ob_i['x1']*zoom,ob_i['bottom']*zoom)
        icrop = pilimg.crop(croprect)
        img = self.pad_img(icrop,20)
        img_np = np.array(img)
        if ob_i['width']>50:
            content = ''
        elif ob_i['height']>25:
            content = '\n'
        else:
            try:
                result = self.ocr.ocr(img_np,cls =True)
                content = result[0][1][0]
            except:
                content = 'ocrError'
        # print("img2txt:" + content)
        return content

    # 根据排序后的list结果，返回文本顺序
    def oblist2txt(self,oball):
        oba = oball
        oba.sort(key = lambda x:x['y0']+x['y1'], reverse = True)
        obtext = ''
        line = []
        ii = -1
        while(len(oba) > 0):
            ob0 = oba[0]
            # print(ob0['text'],end='')
            ii = ii + 1
            if ii ==0:
                line.append(ob0)
                # y0 = ob[0]['y0']
                oba.remove(ob0)
                
                # print('line:test')
            else:
                if(len(oba) > 1):
                    ob1 = oba[1]
                    ob0center = ob0['y1'] + ob0['y0']
                    ob1center = ob1['y1'] + ob1['y0']
                    if(ob0center - ob1center < 5):
                        line.append(ob0)
                        oba.remove(ob0)
                    else:
                        line.append(ob0)
                        oba.remove(ob0)
                        obtext = obtext + self.sortline(line)
                        ii = -1
                        line = []                    
                else:
                    break # 最后面一个元素是‘本结果仅对所做标本负责’ pass 
        return obtext


    # 将一行字典列表转成为文本，间隔远的字符间加逗号
    def sortline(self,line):
        # for ll in line:
        #     print(ll['text'],end = '')
        # print('\n')
        txt =''
        line.sort(key = lambda x:x['x0']+x['x1'], reverse = False)
        ii = 0
        while(len(line) >0):
            # print(line[0]['text'],end='')
            # if line[0]['text'] == '：':
            #     line[0]['text'] = '：,'
            if ii == 0:
                txt = line[0]['text']
                line.remove(line[0])
                ii = ii + 1
            else:
                if(len(line) > 1):
                    # 如果相距远，加逗号
                    if line[1]['x0'] - line[0]['x1'] > 1:
                        txt = txt + line[0]['text'] + ','
                        line.remove(line[0])
                    # 如果后一个字符盖着前一个字符一半，加逗号
                    elif line[0]['x1']-line[1]['x0']> 0.2:
                        txt = txt + line[0]['text'] + ','
                        line.remove(line[0])
                    else: # if line[1]['x0'] - line[0]['x1'] >= 0:
                        txt = txt + line[0]['text']
                        line.remove(line[0])
                    # elif line[1]['x0'] - line[0]['x1'] < 0:
                else:
                    txt = txt + line[0]['text']
                    break
        
        txt = txt + '\n' # 末尾加换行
        # print(txt)
        return txt

    def pdf2txt(self): 
        print(self.pdfpath)
        # 读取一个pdf, 获取image和char对象
        pdf = pp.open(self.pdfpath)  # 打开pdf
        pages =  pdf.pages  # 获取指定页面
        for page in pages:
            # try:
            ob = page.objects
            ob_char = ob['char']
            ob_image = ob['image']
            pgimg = page.to_image(resolution = 300)
            pgimg.save("./pgimg300.png",format = "PNG")
            pilimg = Image.open("./pgimg300.png")
            pw = page.width; ph = page.height
            iw = pilimg.size[0]; ih = pilimg.size[1]
            zoom = iw/pw
            # print(len(ob_image),'--',type(ob_image))
            # print(len(ob_char),'--',type(ob_char))

            ii = 0
            for ob in ob_image:
                try:
                    ob_image[ii]['text'] = self.img2txt(pilimg,zoom,ob)
                except:
                    logfile = open('F:/工作/2022/05/lzk/log.txt','a+',encoding='utf-8')
                    logcontent = self.pafpath + ',' + page.page_number
                    logfile.write(logcontent)
                    logfile.close
                # ob_image[ii]['text'] = 'test'
                # print(ob_image[ii]['text'])
                ii = ii + 1
            oba=[]
            oba.extend(ob_char)
            oba.extend(ob_image)
            # print(oba)
            # print(len(oba),'--',type(oba))
            self.text = self.text + self.oblist2txt(oba)
            # except:
            #     print("page analyse error!")


    def pdf2txt_advance(self,start_num,end_num): 
        print(self.pdfpath)
        # 读取一个pdf, 获取image和char对象
        pdf = pp.open(self.pdfpath)  # 打开pdf
        pages =  pdf.pages  # 获取指定页面
        ii = 0
        for page in pages:
            ii = ii + 1
            if((ii>=start_num) and (ii<end_num)):
                try:
                    ob = page.objects
                    ob_char = ob['char']
                    ob_image = ob['image']
                    pgimg = page.to_image(resolution = 300)
                    pgimg.save("./pgimg300.png",format = "PNG")
                    pilimg = Image.open("./pgimg300.png")
                    pw = page.width; ph = page.height
                    iw = pilimg.size[0]; ih = pilimg.size[1]
                    zoom = iw/pw
                    # print(len(ob_image),'--',type(ob_image))
                    # print(len(ob_char),'--',type(ob_char))

                    ii = 0
                    for ob in ob_image:
                        try:
                            ob_image[ii]['text'] = self.img2txt(pilimg,zoom,ob)
                        except:
                            logfile = open('F:/工作/2022/05/lzk/log.txt','a+',encoding='utf-8')
                            logcontent = self.pafpath + ',' + page.page_number
                            logfile.write(logcontent)
                            logfile.close
                        # ob_image[ii]['text'] = 'test'
                        # print(ob_image[ii]['text'])
                        ii = ii + 1
                    oba=[]
                    oba.extend(ob_char)
                    oba.extend(ob_image)
                    # print(oba)
                    # print(len(oba),'--',type(oba))
                    self.text = self.text + self.oblist2txt(oba)
                except:
                    print("page analyse error!")
    def pdftoimg_ocr(self):
        print(self.pdfpath)
        # 读取一个pdf, 获取image和char对象
        pdf = pp.open(self.pdfpath)  # 打开pdf
        pages =  pdf.pages  # 获取指定页面
        for page in pages:
            pgimg = page.to_image(resolution = 300)
            pgimg.save("./pgimg300.png",format = "PNG")
            pilimg = Image.open("./pgimg300.png")
            img_np = np.array(pilimg)
            try:
                tmp = self.ocr.ocr(img_np,cls = True)
                # result = tmp[0][1][0]
                result = ''
                for ii in range(len(tmp)):
                    result = result + tmp[ii][1][0] # 多行结果合并
                self.text = self.text + result
            except:
                print('ocrError--------------------')
                # plt.figure()
                # plt.imshow(imgn)
    
    def writetext2csv(self):
        file = open(self.csvfile,'a+',encoding='utf-8')
        file.write(self.text)
        file.close
        print("file is written.")

        
if __name__ == '__main__':
    pdfpath = r'F:\工作\2022\05\lzk\pdfs\0001521477.pdf'
    csvfile = r'F:\工作\2022\05\lzk\pdfs\0001521477.csv'
    test = Pdf2txt(pdfpath, csvfile)
    # test.pdf2txt_advance(12,18)
    test.pdftoimg_ocr()
    test.writetext2csv()
