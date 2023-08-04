from pdf2docx import Converter

pdf_file = "enem_1_dia_2022_azul.pdf"
html_file = "html_pagina6"

cv = Converter(pdf_file)

cv.convert(html_file, start=5, end=5)
cv.close()