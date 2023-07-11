import os
from PIL import Image
from PIL import ImageEnhance
import matplotlib.pyplot as plt
from paddleocr import PaddleOCR, draw_ocr
import numpy as np
# import shutil


ocr= PaddleOCR(use_angle_cls = True, use_gpu = False)
def rectocr(filepath,img,rect,mc):
    resizenum = 6
    img = img.resize((img.width * resizenum, img.height * resizenum), Image.ANTIALIAS)
    rectn = (rect[0]  * resizenum, rect[1] * resizenum, rect[2] * resizenum, rect[3] * resizenum)
    icrop = img.crop(rectn)
    imgn = pad_img(icrop,20)
    imgen = ImageEnhance.Contrast(imgn)
    imgen = imgen.enhance(factor = 1.6)
    img_np = np.array(imgen)
    # plt.figure()
    # plt.imshow(imgen)
    # plt.xlabel(rect)
    try:
        
        tmp = ocr.ocr(img_np,cls = True)
        # result = tmp[0][1][0]
        result = ''
        for ii in range(len(tmp)):
            result = result + tmp[ii][1][0] # 多行结果合并
        result = result.replace('\n','|')
        result = result.replace(' ','')
        result = result.replace(';','。')
        result = result + ';'
        print(rect,'ocr result:',result)
        return result
    except:
        print('ocrError--------------------',rect)
        # plt.figure()
        # plt.imshow(imgn)
        logfile = open("C:/I/files/UCGs/logfile.txt","a+",enconding='utf-8')
        logfile.write(filepath + " " + mc + " ocrError!")
        logfile.close()
        return 'ocrError;'
    
def pad_img(image, padding_num):    # image is an object of image, padding_num 就是要在图像边缘增加几个像素
    iw, ih = image.size # 原图像尺寸
    w,h = iw + 2 * padding_num, ih + 2 * padding_num
    # print('iw:',iw,'ih:',ih)
    # print('w:',w,'h',h,'padding:',padding_num)
    new_image = Image.new('RGB',(w,h),(256,256,256))
    new_image.paste(image,((w - iw)//2,(h - ih) // 2))
    return new_image

def getUCG700data(filepath,img):
    pname = rectocr(filepath,img,(58,73,97,91),'patient name')
    pid = rectocr(filepath,img,(485,72,551,91),'patient id')
    reportdate = rectocr(filepath,img,(530,943,666,962),'report time')
    aao = rectocr(filepath,img,(116,138,182,150),'AAO')
    la = rectocr(filepath,img,(116,153,182,166),'LA')
    lv = rectocr(filepath,img,(116,169,182,183),'LV')
    ivs = rectocr(filepath,img,(116,186,182,200),'IVS')
    lvpw = rectocr(filepath,img,(116,203,182,214),'LVPW')
    ra = rectocr(filepath,img,(116,217,182,228),'RA')
    rv = rectocr(filepath,img,(116,233,182,246),'RV')
    pa = rectocr(filepath,img,(116,250,182,262),'PA')
    fs = rectocr(filepath,img,(116,265,182,275),'FS')
    ef = rectocr(filepath,img,(116,280,182,293),'EF')
    mve = rectocr(filepath,img,(368,138,428,149),'MVE')
    aa = rectocr(filepath,img,(368,153,428,166),'AA')
    ea = rectocr(filepath,img,(368,169,428,183),'EA')
    lvot = rectocr(filepath,img,(368,217,428,228),'LVOT')
    av = rectocr(filepath,img,(368,233,428,246),'AV')
    pv = rectocr(filepath,img,(368,265,428,277),'PV')
    # csms = rectocr(filepath,img,(39,562,693,793)) # 超声描述
    # csts = rectocr(filepath,img,(30,813,531,933)) # 超声提示
    
    content = pname + pid + reportdate + aao + la + lv + ivs + lvpw + ra \
    + rv + pa + fs + ef + mve + aa + ea + lvot + av + pv + ' ;' + ' ;' + ' ;' + ' ;' + '\n' # + csms + csts + '\n'
    
    txtfile = 'C:/I/files/UCGs/t2/700.txt'
    ff = open(txtfile,'a+',encoding='utf-8')
    ff.write(content)
    print("file is writen")
    
   
    
if __name__ =='__main__':
    rootpath = r'C:\I\files\UCGs\t2\700'
    for root, ds, fs in os.walk(rootpath):
        for f in fs:
            print(os.path.join(root,f))
            filepath = os.path.join(root,f)
            img = Image.open(filepath)
            getUCG700data(filepath,img)
            # shutil.move(os.path.join(root,f),os.path.join('C:/I/files/UCGs/finish',f))
            print('-'*70)
            