from PyPDF2 import PdfReader 


reader = PdfReader("enem_1_dia_2022_azul.pdf")
#print(type(reader)) 
page = reader.pages[1]
count = 0

print(page.extract_text())

for image_file_object in page.images: # tentar ver se paginas sem imagens na questão ainda tem outras imagens na pagina
    print("Indirect Reference ID: ", image_file_object.indirectRef.idnum)
    print("Indirect Reference Generation: ", image_file_object.indirectRef.generation)
    print(image_file_object.indirectRef)
    with open(str(count) + image_file_object.name, "wb") as fp:
        fp.write(image_file_object.data)
        count += 1

