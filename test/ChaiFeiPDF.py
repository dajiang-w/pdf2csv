import pdfplumber as pp

pdfpath = r'F:\工作\2022\05\lzk\pdfs\0001521477.pdf'
def chaifeipdf(pdfpath,first_pagenum,end_pagenum):
    pdf = pp.open(pdfpath)
    for page in pdf.pages:
        print(type(page))

if __name__=='__main__':
    chaifeipdf(pdfpath,12,18)

