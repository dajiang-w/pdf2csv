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

    def img2txt(self,i_tmp):  # i_tmp is a dict of image in pdf
        # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        imgstream = i_tmp['stream']
        if i_tmp['height']<19:
            data = imgstream.get_data()
            # imgrawdata = imgstream.rawdata
            # print(imgrawdata)
            size = (imgstream.attrs['Width'], imgstream.attrs['Height'])
            if imgstream.attrs['ColorSpace'].name == 'DeviceRGB':
                mode = 'RGB'
            else:
                mode = 'P'
            # img_pre = "C:/I/imgs2/" + str(int(time.time()*1000))# i_tmp['name']
            # print(imgstream.attrs['Filter'].name)
            FilterName = imgstream.attrs['Filter'].name
            if 'Filter' in imgstream.attrs:
                if FilterName == 'FlateDecode':
                    # print("Flate")
                    img = Image.frombytes(mode, size, data)
                    img = self.pad_img(img,20)
                    # content = pytesseract.image_to_string(img, lang='eng+chi_sim')
                    img_np = np.array(img)
                    try:
                        result = self.ocr.ocr(img_np,cls = True)
                        content = result[0][1][0]
                    except:
                        content = 'ocrError'
                    content = content.replace(' ','') # 去掉空格
                    content = content.replace('\n','') # 去掉换行符
                    content = content + ''
                    if content == '':
                        return ""
                    else:
                        return content
                    # img.save(img_pre + ".png", dpi=(300,300))
                elif FilterName == 'DCTDecode':
                    # # print("DCT")
                    # img = open(img_pre + ".jpg", "wb")
                    # img.write(data)
                    # img.close()
                    return ""
                elif FilterName == 'JPXDecode':
                    # img = open(img_pre + ".jp2", "wb")
                    # img.write(data)
                    # img.close()
                    return ""
                elif FilterName == 'CCITTFaxDecode':
                    # img = open(img_pre + ".tiff", "wb")
                    # img.write(data)
                    # img.close()
                    return ""
            else:
                return   ""
        else:
            return '\n'

    # 根据排序后的list结果，返回文本顺序
    def oblist2txt(self,oball):
        oba = oball
        oba.sort(key = lambda x:x['y0']+x['y1'], reverse = True)
        obtext = ''
        line = []
        ii = -1
        while(len(oba) > 0):
            ob0 = oba[0]
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
        txt =''
        line.sort(key = lambda x:x['x0']+x['x1'], reverse = False)
        ii = 0
        while(len(line) >0):
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
        return txt

    def pdf2txt(self): 
        print(self.pdfpath)
        # 读取一个pdf, 获取image和char对象
        pdf = pp.open(self.pdfpath)  # 打开pdf
        pages =  pdf.pages  # 获取指定页面
        for page in pages:
            ob = page.objects
            ob_char = ob['char']
            ob_image = ob['image']
            # print(len(ob_image),'--',type(ob_image))
            # print(len(ob_char),'--',type(ob_char))

            ii = 0
            for ob in ob_image:
                ob_image[ii]['text'] = self.img2txt(ob)
                ii = ii + 1
            oba=[]
            oba.extend(ob_char)
            oba.extend(ob_image)
            # print(len(oba),'--',type(oba))
            self.text = self.text + self.oblist2txt(oba)
    
    def writetext2csv(self):
        file = open(self.csvfile,'a+',encoding='utf-8')
        file.write(self.text)
        file.close
        print("file is written.")

