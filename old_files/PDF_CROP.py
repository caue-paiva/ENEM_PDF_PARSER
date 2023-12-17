from PyPDF2 import PdfWriter, PdfReader

reader = PdfReader("enem_1_dia_2022_azul.pdf")
writer = PdfWriter()


writer.add_page(reader.pages[5])

with open("PDF_PAGINA6.pdf", "wb") as pF:
    writer.write(pF)