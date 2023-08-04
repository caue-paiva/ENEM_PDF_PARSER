from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import io

laparams = LAParams()

with open('PDF_3_PAGINAS.pdf', 'rb') as fp, open('document.html', 'wb') as outfp:
    extract_text_to_fp(fp, outfp, output_type='html', laparams=laparams)

       
    

