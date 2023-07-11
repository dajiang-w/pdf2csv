from PDF2csv_wps import Pdf2txt
from datetime import datetime
import os
import sys

# # 读取一个pdf
# test = Pdf2txt(r'F:\工作\2022\05\lzk\test.pdf',r'F:\工作\2022\05\lzk\test3.csv')
# test.pdf2txt()
# test.writetext2csv()
starttime = datetime.now()
ii = 0
# rootpath = sys.argv[1]
# print(rootpath)
# rootpath = 'F:/pdfs/'
rootpath = sys.argv[1]
for root, ds, fs in os.walk(rootpath):
    for f in fs:
        if f.find('.pdf'):
            ii = ii + 1
            pdffile = os.path.join(root,f)
            csvfile = os.path.join(root,f.replace('.pdf','.csv'))
            print(pdffile)
            # 如果有csv就不执行，没有的话读取pdf，并转换
            if os.path.exists(csvfile):
                pass
            else:
                print(pdffile)
                tmp = Pdf2txt(pdfpath=pdffile,csvfile=csvfile)
                tmp.pdf2txt()
                tmp.writetext2csv()
endtime = datetime.now()
print("共处理了",ii,'个pdf文件,用时',( endtime - starttime ))