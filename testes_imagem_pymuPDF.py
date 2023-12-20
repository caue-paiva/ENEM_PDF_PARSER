from encodings import utf_8
import fitz, os , re
from io import BytesIO
from PIL import Image, ExifTags

def __parse_alternatives_txt2__(question: str) -> str:

    first_pattern = r"([A-E])(\s{2,}|\n)"
    
    # Function to replace the match with the letter followed by a closing parenthesis
    def replace_match(match):
        return f"{match.group(1)})"

    # Replace using the pattern
    question = re.sub(first_pattern, replace_match, question)

    second_pattern = r"([A-E])\)\1"

    # Replace the matched pattern with just the first letter and parenthesis
    question = re.sub(second_pattern, r"\1)", question)

    # Check if all alternatives have been replaced
    if re.search(r"[A-E](\s{2,}|\n)", question):
        return "non-standard alternatives"

    return question


def __parse_alternatives_txt__(question:str)-> str:
        index:int = 0
        patterns_alternatives = [r"([A])",r"([B])",r"([C])",r"([D])",r"([E])"]
        non_standard:bool = False
        
        while index < 5 :   
            chosen_pattern = patterns_alternatives[index]   #para cada letra na lista de padrões, vamos aplicar a mudança  
            match = re.search(chosen_pattern, question)  
            if match:  #se existir algo similar ao padrão na string 
                print("one match")
                start_posi =  match.start() #pega a primeira letra da alternativa
                replacement = question[start_posi]
                repla_str = f"{replacement})" 
                question= re.sub(chosen_pattern, repla_str, question) #troca a substr (ex: A A) com apenas a primeira letra (ex: A)
                question.replace(repla_str,"", 1)
                index +=1  

                start_posi_str: str = question[start_posi:]
                newline_posi: int =  start_posi_str.find("\n")
                alternative_text_str: str =  question[start_posi+2: start_posi + newline_posi] # essa string contem o texto em si da alternativa depois da Letra e )
                
                if alternative_text_str.isspace(): #caso o texto da alternativa esteja vazia (Alternativas são imagens que não são checadas pelo PDF reader), retornamos um str de erro
                     non_standard = True
                     break
                     
            else:
                 non_standard = True
                 break #o padrão não existe, então não é o texto de uma alternativa  
       
        if non_standard:
            return "non-standard alternatives"
        
        return question

def fitz_get_text(page_index:int)->str:
    doc = fitz.open("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf")

    #for page_index in range(len(doc)):
    page = doc[page_index]
    return   __parse_alternatives_txt2__(page.get_text())


def fitz_get_images(page_index:int):
        doc = fitz.open("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf")

    #for page_index in range(len(doc)):
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
            if page_index == 2 or 3:
                image_metadata: tuple = doc.xref_get_keys(xref)
                print(f"image metadata { image_metadata}")

            for data in image_metadata:
             print( {doc.xref_get_key(xref, data)})

            #print(base_image["Name"])

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


def extract_image_and_metadata(pdf_path:str)->None:
    # Open the PDF
    doc = fitz.open(pdf_path)
    TAGS = ExifTags.TAGS

    # Loop through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # load the page
        image_list = page.get_images(full=True)
        
        # Loop through each image in the list
        for image_index, image_info in enumerate(image_list):
            xref = image_info[0]  # xref is the first item in the image_info tuple
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Now we have the image bytes, let's see if there's metadata
            image_stream = BytesIO(image_bytes)
            with Image.open(image_stream) as img:
                # Print image details
                print(f"Image {image_index + 1} on page {page_num + 1}:")
                print(f"  Format: {img.format}")
                print(f"  Size: {img.size}")
                print(f"  Mode: {img.mode}")
                
                # Check for and print EXIF data if available
                exif_data = img._getexif()
                if exif_data:
                    print("  EXIF Metadata:")
                    for tag, value in exif_data.items():
                        tag_name = TAGS.get(tag, tag)
                        print(f"    {tag_name}: {value}")
                else:
                    print("  No EXIF data found.")
                    
    # Close the document
    doc.close()

print(fitz_get_text(13))
#extract_image_and_metadata("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf")