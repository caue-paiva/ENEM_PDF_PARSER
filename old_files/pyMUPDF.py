import fitz


doc = fitz.open("enem_1_dia_2022_azul.pdf")
page = doc.load_page(5)

images = page.get_images(full=True)

d = page.get_text("dict")
blocks = d["blocks"]  # the list of block dictionaries
imgblocks = [b for b in blocks if b["type"] == 1]
print(imgblocks[0]["bbox"])
print(imgblocks[0]["width"])
print(imgblocks[0]["height"])

print(imgblocks[1]["bbox"])
print(imgblocks[1]["width"])
print(imgblocks[1]["height"])


# for img in images:
#     img_tuple =img
#     x0 = img_tuple[0]-850
#     print(img)
#     xref= img[0]
#     base_image=doc.extract_image(xref)
    
   
#     image_data= base_image["image"]
#     with open(f"image_{xref}.png", "wb") as img_file:
#         img_file.write(image_data)


# print(f"Image {xref}")