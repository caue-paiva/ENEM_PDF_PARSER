from encodings import utf_8
import fitz, os , re
from io import BytesIO
from PIL import Image, ExifTags

question_str = """
QUESTÃO 29 
Esaú e Jacó
Bárbara entrou, enquanto o pai pegou da viola e 
passou ao patamar de pedra, à porta da esquerda. 
Era uma criaturinha leve e breve, saia bordada, chinelinha 
no pé. Não se lhe podia negar um corpo airoso. Os cabelos, 
apanhados no alto da cabeça por um pedaço de fita 
enxovalhada, faziam-lhe um solidéu natural, cuja borla era 
suprida por um raminho de arruda. Já vai nisto um pouco 
de sacerdotisa. O mistério estava nos olhos. Estes eram 
opacos, não sempre nem tanto que não fossem também 
lúcidos e agudos, e neste último estado eram igualmente 
compridos; tão compridos e tão agudos que entravam 
pela gente abaixo, revolviam o coração e tornavam cá 
fora, prontos para nova entrada e outro revolvimento. 
Não te minto dizendo que as duas sentiram tal ou qual 
fascinação. Bárbara interrogou-as; Natividade disse 
ao que vinha e entregou-lhe os retratos dos filhos e os 
cabelos cortados, por lhe haverem dito que bastava.
— Basta, confirmou Bárbara. Os meninos são seus filhos?
— São.
ASSIS, M. Obra completa. Rio de Janeiro: Nova Aguilar, 1994.
No relato da visita de duas mulheres ricas a uma vidente 
no Morro do Castelo, a ironia — um dos traços mais 
representativos da narrativa machadiana — consiste no
A 
A modo de vestir dos moradores do morro carioca.
B 
B senso prático em relação às oportunidades de renda.
C 
C mistério que cerca as clientes de práticas de 
vidência.
D 
D misto de singeleza e astúcia dos gestos da 
personagem.
E 
E interesse do narrador pelas figuras femininas 
ambíguas.
QUESTÃO 30 
A senhora manifestava-se por atos, por gestos, 
e sobretudo por um certo silêncio, que amargava, que esfolava. 
Porém desmoralizar escancaradamente o marido, não era 
com ela. [...]
As negras receberam ordem para meter no serviço a gente 
do tal compadre Silveira: as cunhadas, ao fuso; os cunhados, 
ao campo, tratar do gado com os vaqueiros; a mulher e as 
irmãs, que se ocupassem da ninhada. Margarida não tivera 
filhos, e como os desejasse com a força de suas vontades, 
tratava sempre bem aos pequenitos e às mães que os estavam 
criando. Não era isso uma sentimentalidade cristã, uma ternura, 
era o egoísta e cru instinto da maternidade, obrando por mera 
simpatia carnal. Quanto ao pai do lote (referia-se ao Antônio), 
esse que fosse ajudar ao vaqueiro das bestas.
Ordens dadas, o Quinquim referendava. Cada um 
moralizava o outro, para moralizar-se.
PAIVA, M. O. Dona Guidinha do Poço. Rio de Janeiro: Tecnoprint, s/d.
No trecho do romance naturalista, a forma como 
o narrador julga comportamentos e emoções das 
personagens femininas revela influência do pensamento
A 
A capitalista, marcado pela distribuição funcional do 
trabalho.
B 
B liberal, buscando a igualdade entre pessoas 
escravizadas e livres.
C 
C científico, considerando o ser humano como um 
fenômeno biológico.
D 
D religioso, fundamentado na fé e na aceitação dos 
dogmas do cristianismo.
E 
E afetivo, manifesto na determinação de acolher 
familiares e no respeito mútuo.
QUESTÃO 31 
Era o êxodo da seca de 1898. Uma ressurreição de 
cemitérios antigos — esqueletos redivivos, com o aspecto 
terroso e o fedor das covas podres. 
Os fantasmas estropiados como que iam dançando, 
de tão trôpegos e trêmulos, num passo arrastado de 
quem leva as pernas, em vez de ser levado por elas. 
Andavam devagar, olhando para trás, como quem 
quer voltar. Não tinham pressa em chegar, porque não 
sabiam aonde iam. Expulsos de seu paraíso por espadas 
de fogo, iam, ao acaso, em descaminhos, no arrastão dos 
maus fados. 
Fugiam do sol e o sol guiava-os nesse forçado 
nomadismo.
Adelgaçados na magreira cômica, cresciam, como se 
o vento os levantasse. E os braços afinados desciam-lhes 
aos joelhos, de mãos abanando.
Vinham escoteiros. Menos os hidrópicos — de ascite 
consecutiva à alimentação tóxica — com os fardos das 
barrigas alarmantes.
Não tinham sexo, nem idade, nem condição nenhuma. 
Eram os retirantes. Nada mais.
ALMEIDA, J. A. A bagaceira. Rio de Janeiro: J. Olympio, 1978.
Os recursos composicionais que inserem a obra no 
chamado “Romance de 30” da literatura brasileira 
manifestam-se aqui no(a)
A 
A desenho cru da realidade dramática dos retirantes.
B 
B indefinição dos espaços para efeito de generalização.
C 
C análise psicológica da reação dos personagens à seca.
D 
D engajamento político do narrador ante as desigualdades.
E 
E contemplação lírica da paisagem transformada em 
alegoria.
*010175AZ14*"""

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

def format_multiple_choice(question: str) -> str:
    # Pattern to match 'Letter\nLetter'
    pattern = r"([A-E])\s*\n\1\s*"

    # Replacement function
    def replace_pattern(match):
        return f"{match.group(1)}) "

    # Perform the replacement
    formatted_question = re.sub(pattern, replace_pattern, question)

    return formatted_question

def fitz_get_text(page_index:int)->str:
    doc = fitz.open("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf")

    #for page_index in range(len(doc)):
    page = doc[page_index]
    print(page.get_text() + "\n\n")
    return   format_multiple_choice(page.get_text())


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

print(format_multiple_choice(question_str))
#extract_image_and_metadata("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf")