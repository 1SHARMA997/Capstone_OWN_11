from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
import io


def pdfparser(file):
    """ Function that takes a path of a PDF file as input and extracts the text within the file as a string"""
    fp = open(file, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        pdf_text = retstr.getvalue()

    return pdf_text


def txtparser(ip1, ip2, res1, res2):
    try:
        f = open('Temp/Text_Input1.txt', 'w')
        f.write(res1)
        f.close()
        f = open('Temp/Text_Input2.txt', 'w')
        f.write(res2)
        f.close()
    except er:
        print("Error in txtparser()- {}".format(er))
