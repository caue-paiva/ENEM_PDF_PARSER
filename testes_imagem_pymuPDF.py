import fitz, os

doc = fitz.open("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf")

for page_index in range(len(doc)):
    page = doc[page_index]
    image_list:list = page.get_images()

    if image_list:
        print(f" temos : {len(image_list)} imagens")
    else:
        print("zero imagens")

    for image_index,img in enumerate(image_list,start=1):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        # Create a Pixmap with the image bytes
        pix = fitz.Pixmap(image_bytes)

        # If the image has an alpha channel, drop the alpha channel
        if pix.alpha:
            try:
                pix = fitz.Pixmap(pix, 0)  # Drop the alpha channel if it's possible
            except ValueError as e:
                print(f"Error dropping alpha channel: {e}")
                continue  # Skip this image and move to the next one

        # If the image is CMYK, convert it to RGB
        if pix.n == 4:
            pix1 = fitz.Pixmap(fitz.csRGB, pix)
            pix = pix1  # Update pix to the new RGB pixmap

        output_filename = os.path.join("images_fitz", f"page{page_index}_image_{image_index}.png")

        pix.save(output_filename)
        print(f"Saved image as {output_filename}")
        pix = None