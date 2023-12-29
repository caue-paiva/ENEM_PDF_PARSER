import re, os ,json , fitz
from typing import Any 

"""

Performance da ferramenta nos PDFs do ENEM:

Boa funcionalidade de extração de textos e imagens:
    ENEM 2023/22

Extração de texto com problemas:
    ENEM 2020 (codificação não usual de caracteres impede a extração de texto)

"""

class EnemPDFextractor():
    """
    Classe para extração de conteúdo de PDFs do ENEM.
    
    A implementação dessa classe é baseada na nomeclatura dos PDFs do ENEM baixados do site do INEP, então para o funcionamento correto do código é necessário
    que os arquivos de input sejam dessa fonte.

    Caso a EXTRAÇÃO DE IMAGENS NÃO ESTEJA HABILITADA o código VAI PULAR PÁGINAS/QUESTÕES COM IMAGENS, isso é feito com o objetivo de filtrar. 
    questões de texto puro, que podem ser utilizadas facilmente sem se preocupar com falta de contexto devido à imagens associadas (Útil para várias tarefas de NLP)

    Mesmo com  extração de imagens habilitadas, a ferramenta não vai adicionar questões cujas alternativas estejam fora do comum (ex: alternativas são imagens)
    Isso pode levar à menos questões do que o total na prova em alguns casos

    Atributos:
        output_type (str) :  Tipos de arquivo de output do texto, são suportados outputs .TXT e .JSON. 
        -OBS:  arquivos JSON contem informações adicionais como lista de alternativas e lista de imagens associadas,caso imagens sejam extraidas.

        process_questions_with_images (bool) : Dita se textos e imagens de páginas com imagens serão processadas ou não.

    """

    #-------constantes baseadas na nomeclatura do INEP dos arquivos do enem, ex: 2022_GB_impresso_D1_CD1.pdf------- 
    
    #utilizadas para identificar qual prova ou gabarito estamos lidando
    __YEAR_PATTERN__ = "20\d{2}"
    __DAY_ONE_SUBSTR__ = "D1"  #substr no nome do PDF que indica qual o dia da prova
    __TEST_IDENTIFIER__ = "PV"
    __ANSWER_PDF_IDENTIFIER__ = "GB"
    __NUM_PATTERN1__ = r"\*\w{9}\*"  #esses padrões vem de um código de barras presente no topo de toda página, ele vai ser removido
    __NUM_PATTERN2__ = r"\*\w{10}\*"
    __QUESTION_IDENTIFIER__ = "QUESTÃO"
    __TXT_QUESTION_TEMPLATE__= "(Enem/{test_year})  {question_text}\n(RESPOSTA CORRETA): {correct_answer}\n\n"
    __SUPPORTED_OUTPUT_FILES__:tuple = ("txt", "json")
    __TEST_COLOR_PATTERN__ = "CD\d{1}"  #provas/cadernos e gabaritos  são separadas por cores, se as cores de ambos forem iguais, eles estão relacionados

    #-------variáveis específicas de cada classe-------
    test_pdf_path:str 
    answer_pdf_path: str
    extracted_data_path:str
    output_type:str 
    answer_pdf_text:str
    process_questions_with_images:bool 

    def __init__(self,output_type:str, process_questions_with_images:bool = True)->None:
        """
        Construtor para a classe EnemPDFextractor.
        
        Argumentos:
            output_type (str) :  Tipos de arquivo de output do texto, são suportados outputs .TXT e .JSON.
            -OBS:  arquivos JSON contem informações adicionais como lista de alternativas e lista de imagens associadas, caso imagens sejam extraidas.
            

            ignore_questions_with_images (bool) : Dita se textos e imagens de páginas com imagens serão processadas ou não.   
            -OBS: Caso a EXTRAÇÃO DE IMAGENS NÃO ESTEJA HABILITADA o código VAI PULAR PÁGINAS/QUESTÕES COM IMAGENS.
        """    
        output_type = output_type.lower()
        if output_type not in self.__SUPPORTED_OUTPUT_FILES__:
            raise IOError("tipo de arquivo de output não suportado")

        self.output_type =  output_type
        self.process_questions_with_images = process_questions_with_images
        
    #lida com erros de input/output, alertando sobre nomes não baseados na nomeclatura do INEP, assim como alerta sobre gabaritos e provas de cores diferentes
    
    def __handle_IO_errors__(self,test_pdf_path: str, answers_pdf_path:str)->None:
        if self.__TEST_IDENTIFIER__ not in test_pdf_path:
            raise IOError("nome do arquivo da prova não segue o padrão do INEP")
    
        if self.__ANSWER_PDF_IDENTIFIER__ not in answers_pdf_path:
            raise IOError("nome do arquivo do gabarito não segue o padrão do INEP")
            
        test_color_identifier = re.findall(self.__TEST_COLOR_PATTERN__, test_pdf_path)
        if not test_color_identifier:
            raise IOError("especificação da cor do caderno da prova não segue o padrão do INEP")
        
        answers_color_identifier= re.findall(self.__TEST_COLOR_PATTERN__, answers_pdf_path)
        if not answers_color_identifier:
            raise IOError("especificação da cor do gabarito não segue o padrão do INEP")
        
        test_color_identifier:str = test_color_identifier[0]
        answers_color_identifier:str = answers_color_identifier[0]
    
        if test_color_identifier[2] != answers_color_identifier[2]:  #terceiro char desse padrão é o numero referente à cor do caderno
            raise IOError("prova e gabarito são de cores diferentes") 

    #------abaixo funções de formatação do texto------

    #ao extrair o texto das alternativas do PDF, a letra da  alternativa é repetida 2 vezes, então essa função remove essa segunda repetição e formata as alternativas

    def __parse_alternatives__(self,question:str)-> str | tuple[str,list[str]]: #essa funcao retorna uma string caso o output é TXT e uma tuple (str,lista) caso o output seja JSON
        if self.output_type == "txt":
            return_val: str = "non-standard alternatives"
        else:
            return_val: tuple[str,list[str]] = "non-standard alternatives" , []
        pattern = r"([A-E])\s*\n\1\s*"
        
        single_letter_pattern = r"([A-E])\s{2}" #padrão de uma letra maiuscula com 2 espaços , pq o ENEM 2020 não repete as alternativas 2 vezes
        
        #troca a letra por ela mesmo com um ) depois
        def replace_match(match):
            return f"{match.group(1)})"
        number_substi: int 
        question, number_substi = re.subn(pattern, replace_match, question)
        if number_substi < 5:
           question , num = re.subn(single_letter_pattern,replace_match, question)
           if num < 5: #menos que 5 substituições no novo padrão
             return return_val
        #caso nos tenhamos realizado menos que 5 substituições (num de alternativas) então a estrutura da questão estava quebrada
        #provavelmente uma questão com imagem de alternativa 

        alternative_pattern = r"([A-E])\)"
        alternatives = {}
        #vamos ver se as alternativas contem texto vazio (então são imagens) e se for vamos pular a questão
        matches = list(re.finditer(alternative_pattern, question))
        for i, match in enumerate(matches):
            letter = match.group(1)
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(question)
            
            alternative_text = question[start_pos:end_pos]
            if not alternative_text:
                return return_val

            alternatives[letter] = alternative_text
       
        if isinstance(return_val,str):  #return_val depende do tipo de output, se for .txt retorna uma string, se for .json retorna uma tuple
            return_val = question
        elif isinstance(return_val,tuple):
            return_val = (question, self.__get_alternative_list__(question))
            
        return return_val  
    
    #retorna uma lista das alternativas da questão

    def __get_alternative_list__(self,question:str)->list[str]:
        regex_pattern = "[A-E]\)"
        alternatives_list: list[str] = []
        matches_list:list[int] = [match.start() for match in re.finditer(pattern=regex_pattern, string=question)]
       
        for i in  range(len(matches_list)):
            if i < len(matches_list)-1:
              alternative_text:str = question[matches_list[i]: matches_list[i+1]]
              alternatives_list.append(alternative_text)
            else:
              alternative_text:str = question[matches_list[i]: len(question)]
              alternatives_list.append(alternative_text)
    
        return alternatives_list
   
    #generator que itera sobre todas as substrings e retorna o index dela na string principal

    def __yield_all_substrings__(self, input_str: str, sub_str:str)->int:
     sub_str = sub_str or "*" 
     start = 0  
     while True:
        start:int = input_str.find(sub_str, start)
        if start == -1: return  
        yield start
        start += len(sub_str)  
    
    #acha a resposta correta dado o texto do gabarito (attbr de class) e o numero da questão, retorna a alternativa correta

    def __find_correct_answer__ (self, question_number:int,day_one: bool,is_spanish_question:bool = False )->str:          
        if day_one:    
            if question_number > 5:
                question_number = question_number -5
                
            question_string = str(question_number)
            question_num_pattern = r'\b' + question_string + r'\b'
        
            num_match =  re.search(question_num_pattern, self.answer_pdf_text)
            
            if num_match: # se achamos o número da questão isolado (não como parte de outro número)
                if question_number < 10 :
                    if is_spanish_question:
                        answer_index:int = (num_match.start() +4) #se o numero da questao de for de 1 digito, e ela for de espanhou, a resposta está a 4 espaços na direita
                    else:
                        answer_index = (num_match.start() +2) #se o numero da questao de for de 1 digito, e ela for de inglẽs, a resposta está a 2 espaços na direita
                
                else:  answer_index = (num_match.start() +3) #se tiver 2 digitos, a resposta está a 3 espaços na direita
                
            else: 
                return "não achou a questão"
            return self.answer_pdf_text[answer_index]
        else:
            question_number += 90  #gabarito do segundo dia começa da questão 91, mas a lógica do código conta as questões do 0 independente do dia, entao para achar é preciso somar +90

            question_string = str(question_number)
            question_num_pattern = r'\b' + question_string + r'\b'
            num_match =  re.search(question_num_pattern, self.answer_pdf_text)

            if num_match:
                if question_number < 100 :
                    answer_index = (num_match.start() +3) #se o numero da questao de for de 2 digitos (antes de subtrai 90), a resposta está a 3 espaços na direita
                else:  
                    answer_index = (num_match.start() +4) #se tiver 3 digitos, a resposta está a 4 espaços na direita

                return self.answer_pdf_text[answer_index]
            else:
                return "não achou a questão"
    
    #método para pre-processar o texto de uma página, retornando o texto processado, o num da primeira questão da página e pulando ela caso ela não tenha questões ou tenha imagens

    def __page_preprocessing__(self,pdf_reader:fitz.fitz.Document,page_index:int ,total_question_number:int)-> dict :
        text_processing_dict: dict = {"text": "", "page_first_question": 0, "total_question_number": 0 }
        
        current_page:fitz.fitz.Page = pdf_reader[page_index]    
                      
        page_text:str = current_page.get_text()
        page_text = page_text.replace("Questão", "QUESTÃO")
        first_question_str_index: int = next(self.__yield_all_substrings__(input_str = page_text, sub_str = self.__QUESTION_IDENTIFIER__) , -1 ) #acha a primeira questão da folha
        
        if first_question_str_index == -1:
            return {} # se não tiver questões na página (pagina de redação) pula a iteração
         
        page_text = page_text[first_question_str_index:]  #antes da primeira questão temos apenas um header inútil (ex: ENEM 2022, ENEM 2022....) do PDF
         
        page_text = re.sub(self.__NUM_PATTERN1__,"", page_text)  #remove os padrões numéricos do QR codes
        page_text = re.sub(self.__NUM_PATTERN2__,"",page_text)

        page_first_question: int = total_question_number + 1 #a primeira questão da prox página sera o numero total de questões processadas ate o momento + 1 (a primeira questão em si)  
      
        for _ in self.__yield_all_substrings__(page_text, self.__QUESTION_IDENTIFIER__):
            total_question_number += 1  #aumenta o numero de questoes ja processadas com todas daquela página
    
        
        image_list:list = current_page.get_images()

        if image_list:
            text_processing_dict.update({"text":"","page_first_question": page_first_question, "total_question_number": total_question_number})
            return text_processing_dict #retorna dict sem imagens
            
        #caso tenha imagens na página vamos pular ela, já que não podemos extrair a imagem   
        #não é possível fazer essa verificação no começo pois é preciso contar todas as questões da página para a variavel total_question_number, já que ela dita qual matéria esta sendo processada

        page_text += f" {self.__QUESTION_IDENTIFIER__}" #coloca isso no final do texto para ajudar no processamento, já que teremos uma substr de parada do algoritmo
        
        text_processing_dict.update({"text":page_text,"page_first_question": page_first_question, "total_question_number": total_question_number})
        return text_processing_dict
   
    #método para pre-processar o texto de uma página, retornando o texto processado, o num da primeira questão da página escrevendo as imagens da página no diretório de output

    def __page_preprocessing_images__(self,pdf_reader: fitz.fitz.Document,page_index:int ,total_question_number:int, test_year:int, day_one:bool)->dict:
        image_text_dict: dict = {"text": "", "page_first_question": 0, "total_question_number": 0 , "image_name_list": []}
        
        day_identifier:str = "D1" if day_one else "D2" #identificar do D1 para ser escrito no nome de arquivo das imagens
        image_name_list:list[str] = []
       
        current_page: fitz.fitz.Page = pdf_reader[page_index]                    
        page_text: str = current_page.get_text()
        page_text = page_text.replace("Questão", "QUESTÃO")
        first_question_str_index: int = next(self.__yield_all_substrings__(input_str = page_text, sub_str = self.__QUESTION_IDENTIFIER__) , -1 ) #acha a primeira questão da folha
        
        if first_question_str_index == -1:
            return {} # se não tiver questões na página (pagina de redação) pula a iteração
         
        page_text = page_text[first_question_str_index:]  #antes da primeira questão temos apenas um header inútil (ex: ENEM 2022, ENEM 2022....) do PDF
         
        page_text = re.sub(self.__NUM_PATTERN1__,"", page_text)  #remove os padrões numéricos do QR codes
        page_text = re.sub(self.__NUM_PATTERN2__,"", page_text)

        page_first_question: int = total_question_number + 1 #a primeira questão da prox página sera o numero total de questões processadas ate o momento + 1 (a primeira questão em si)  
      
        for _ in self.__yield_all_substrings__(page_text, self.__QUESTION_IDENTIFIER__):
            total_question_number += 1  #aumenta o numero de questoes ja processadas com todas daquela página

        page_text += f" {self.__QUESTION_IDENTIFIER__}" #coloca isso no final do texto para ajudar no processamento, já que teremos uma substr de parada do algoritmo
        image_text_dict.update({"text":page_text,"page_first_question": page_first_question, "total_question_number": total_question_number})

        image_list:list = current_page.get_images()

        if not image_list:
            return image_text_dict #retorna dict sem imagens
             
        if not os.path.isdir(os.path.join(self.extracted_data_path, "images")):  #caso não exista um dir para guardar as imagens, cria um
             print("diretorio de output de imagens não existe, criando um novo")
             os.makedirs(os.path.join(self.extracted_data_path, "images"), exist_ok=True)
        
        #loop sobre os indices da imagem e suas listas de conteúdo para extrair seu valor com a lib Fitz/PymuPDF
        for image_index,img in enumerate(image_list,start=1):
            xref = img[0] #pega o valor xref de cada imagem
            base_image = pdf_reader.extract_image(xref)
            image_bytes = base_image["image"]

            # Cria um Pixmap do fitz com os bytes da imagem
            pix = fitz.Pixmap(image_bytes)

            # se a imagem tem um canal alpha, remove ele
            if pix.alpha:
                try:
                    pix = fitz.Pixmap(pix, 0)  # tenta tirar o canal alfa

                except ValueError as e:
                    print(f"Erro ao tentar remover canal alfa da imagem: {e}")
                    continue  # não foi possível tirar o canal alfa, vai para a proxima imagem

            # se a imagem é CMYK, converte para RGB    
            if pix.n == 4:
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix = pix1  # atualiza o pix para o novo pixmap RGB

            output_filename:str = os.path.join(self.extracted_data_path ,"images", f"{test_year}_{day_identifier}_page{page_index}_{image_index}.png")
            pix.save(output_filename)
            image_name_list.append(output_filename)
            pix = None

        image_text_dict.update({"text":page_text,"page_first_question": page_first_question, "total_question_number": total_question_number, "image_name_list":image_name_list})
        return image_text_dict
        
        #retorna uma dict com informações sobre a questão, esse dict sera transformado num JSON

    def __get_json_from_question__(self, question:str, day_one: bool ,year: int, correct_answer:str, number:int, alternative_list:list[str] = [] , image_list = [None])->dict:
        day_identifier = "D1" if day_one else "D2"
        
        if day_one:
            number = number if number < 6 else number -5 #subtrair as 5 questões contadas na matéria de espanhol
        else:
            number += 90
        
        if alternative_list:
          if len(image_list) == 0 or  image_list[0] != None:
             json_dict = {
                "question_text": question,
                "correct_answer": correct_answer ,
                "alternatives": alternative_list,
                "page_images": image_list,
                "ID": f"{year}_{day_identifier}_N{number}",
                "year": year,
                "day": day_identifier,
                "question_num": number
            }
          else:
            json_dict = {
                "question_text": question,
                "correct_answer": correct_answer ,
                "alternatives": alternative_list,
                "ID": f"{year}_{day_identifier}_N{number}",
                "year": year,
                "day": day_identifier,
                "question_num": number
            }
        else:
            if image_list:
                json_dict = {
                    "question_text": question,
                    "correct_answer": correct_answer ,
                    "ID": f"{year}_{day_identifier}_N{number}",
                    "year": year,
                    "day": day_identifier,
                    "question_num": number
                }
            else:
                json_dict = {
                    "question_text": question,
                    "correct_answer": correct_answer ,
                    "page_images": image_list,
                    "ID": f"{year}_{day_identifier}_N{number}",
                    "year": year,
                    "day": day_identifier,
                    "question_num": number
                }
        return json_dict
   
    #-------abaixo funcoes que processam e salvam o texto num arquivo, funções diferentes para cada dia e se precisa salvar imagem ou não-------

    def __handle_day_one_with_images__(self, pdf_reader: fitz.fitz.Document, test_year:int)->None:
        
        total_question_number: int = 0 
        if self.output_type == "txt":
            english_questions: str = ""
            spanish_questions: str = ""
            humanities_questions: str = ""
            languages_arts_questions: str = ""
        else:
            english_questions: list[dict] = []
            spanish_questions: list[dict] = []
            humanities_questions: list[dict] = []
            languages_arts_questions: list[dict] = []
            
        num_pages: int = len(pdf_reader)
        topic_question_range:dict[str,tuple] = {"eng": (1,5), "spa":(6,10), "lang": (11,50), "huma":(51,95)} #ultima questão de humanas é a 96 pq tbm são contadas as de ingles e espanho,ambas entre 1-6

        for i in range(1,num_pages): #começamos da página numero um para não processar a capa 
            
            page_attributes: dict = self.__page_preprocessing_images__(
                pdf_reader=pdf_reader,
                page_index=i, 
                total_question_number=total_question_number,
                test_year= test_year,
                day_one= True
            )   
            if not page_attributes: #dict vazio, pagina não tem questões
             continue  

            page_first_question:int = page_attributes.get("page_first_question")
            total_question_number = page_attributes.get("total_question_number")
            text:str = page_attributes.get("text") 

            if self.output_type == "json": image_name_list:list[str] = page_attributes.get("image_name_list")

            question_start_index:int = 0
            answer_number: int = page_first_question
            in_spanish_question: bool = False
            if self.output_type== "json": alternative_list:list[str] = []

            for position in self.__yield_all_substrings__(text, self.__QUESTION_IDENTIFIER__): #yield na posição da substring que identifica as questoes     
                if position == 0: #se ele detectar a substr "QUESTÃO" no começo do texto, ele pula, caso contrário seria adicionado um string vazia
                    continue

                if answer_number > 5 and answer_number < 11:
                    in_spanish_question = True  #verifica se a questão é de espanhol
                else:
                    in_spanish_question = False
            
                # se a questão for de espanhol é necessário uma pequena mudança na parte de pegar a resposta
                correct_answer:str = self.__find_correct_answer__(
                    question_number= answer_number, 
                    is_spanish_question= in_spanish_question, 
                    day_one=True
                ) 
                unparsed_alternatives: str = text[question_start_index:position]
                
                parsed_question_vals: Any   = self.__parse_alternatives__(unparsed_alternatives)
                if isinstance(parsed_question_vals, tuple):
                    parsed_question:str = parsed_question_vals[0]
                    alternative_list = parsed_question_vals[1]
                elif isinstance(parsed_question_vals, str):
                    parsed_question:str = parsed_question_vals
                    
                if parsed_question == "non-standard alternatives": #caso a questão tenha alternativas de imagens (mas que o PDF não consegue detectar)     
                    question_start_index = position
                    answer_number += 1
                    continue

                if self.output_type == "txt":
                    parsed_question = self.__TXT_QUESTION_TEMPLATE__.format(test_year = test_year, question_text = parsed_question, correct_answer = correct_answer)
                else:
                    question_json:dict = self.__get_json_from_question__(
                        question= parsed_question,
                        day_one=True,
                        year= test_year,
                        correct_answer= correct_answer,
                        number= answer_number,
                        alternative_list= alternative_list,
                        image_list= image_name_list
                    )
                start_eng, end_eng = topic_question_range["eng"] #desempacotando a tuple de ranges de questões das matérias
                start_spa, end_spa = topic_question_range["spa"]
                start_lang, end_lang = topic_question_range["lang"]
                start_huma, end_huma = topic_question_range["huma"]

                if answer_number in range(start_eng, end_eng+1):
                    if self.output_type == "txt":
                        english_questions += parsed_question
                    else:
                        english_questions.append(question_json)

                elif answer_number in range(start_spa, end_spa+1): 
                    if self.output_type == "txt":
                        spanish_questions += parsed_question
                    else:
                        spanish_questions.append(question_json)

                elif answer_number in range(start_lang, end_lang+1):
                    if self.output_type == "txt":
                        languages_arts_questions += parsed_question
                    else:
                        languages_arts_questions.append(question_json)

                elif answer_number in range(start_huma, end_huma+1):
                    if self.output_type == "txt":
                        humanities_questions += parsed_question
                    else:
                        humanities_questions.append(question_json)

                question_start_index = position
                answer_number += 1
        
     #escrever as strings extraidas nos seus arquivos respectivos
        if self.output_type == "txt":   
            file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_eng_questions.txt" )
            with open(file_path, "w") as f_eng:
                f_eng.write(english_questions)
                
            file_path = os.path.join(self.extracted_data_path,f"{test_year}_spani_questions.txt" )
            with open(file_path, "w") as f_spani:
                    f_spani.write(spanish_questions)

            file_path = os.path.join(self.extracted_data_path,f"{test_year}_lang_questions.txt" )     
            with open(file_path, "w") as f_lang:
                f_lang.write(languages_arts_questions)
                
            file_path= os.path.join(self.extracted_data_path, f"{test_year}_huma_questions.txt" )
            with open(file_path, "w") as f_huma:
                f_huma.write(humanities_questions)
        else:
            file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_eng_questions.json" )
            with open(file_path, "w") as f_eng:
                json.dump(english_questions,f_eng, indent=4,  ensure_ascii=False)
                
            file_path = os.path.join(self.extracted_data_path,f"{test_year}_spani_questions.json" )
            with open(file_path, "w") as f_spani:
                    json.dump(spanish_questions,f_spani,  indent=4,  ensure_ascii=False)

            file_path = os.path.join(self.extracted_data_path,f"{test_year}_lang_questions.json" )     
            with open(file_path, "w") as f_lang:
                json.dump(languages_arts_questions,f_lang, indent=4,  ensure_ascii=False)
                
            file_path= os.path.join(self.extracted_data_path, f"{test_year}_huma_questions.json" )
            with open(file_path, "w") as f_huma:
                json.dump(humanities_questions,f_huma, indent=4,  ensure_ascii=False)

    def __handle_day_two_with_images__(self, pdf_reader: fitz.fitz.Document, test_year:int)->None: 
        total_question_number: int = 0 
        if self.output_type == "txt":
             math_questions: str = ""
             natural_sci_questions: str = ""
        else:
            math_questions: list[dict] = []
            natural_sci_questions: list[dict] = []

        num_pages: int = len(pdf_reader)
        topic_question_range:dict[str,tuple] = {"natu": (1,45), "math":(46,91)} 
        
        for i in range(1,num_pages): #começamos da página numero um para não processar a capa 
            page_attributes: dict = self.__page_preprocessing_images__(
                pdf_reader=pdf_reader,
                page_index=i, 
                total_question_number=total_question_number,
                test_year= test_year,
                day_one=False
            )   
            if not page_attributes: #dict vazio, pagina não tem questões
              continue  
            
            page_first_question:int = page_attributes.get("page_first_question")
            total_question_number = page_attributes.get("total_question_number")
            text:str = page_attributes.get("text") 
            if self.output_type == "json": image_name_list:list[str] = page_attributes.get("image_name_list")

            question_start_index:int = 0
            answer_number: int = page_first_question
            alternative_list:list[str] = []
            if self.output_type== "json": alternative_list:list[str] = []

            for position in self.__yield_all_substrings__(text, self.__QUESTION_IDENTIFIER__): #yield na posição da substring que identifica as questoes     
                if position == 0: #se ele detectar a substr "QUESTÃO" no começo do texto, ele pula, caso contrário seria adicionado um string vazia
                    continue
                
                # se a questão for de espanhol é necessário uma pequena mudança na parte de pegar a resposta
               
                correct_answer:str = self.__find_correct_answer__(
                    question_number= answer_number, 
                    is_spanish_question= False, 
                    day_one=False
                )  
                unparsed_alternatives: str = text[question_start_index:position]
                parsed_question_vals: Any   = self.__parse_alternatives__(unparsed_alternatives)
               
                if isinstance(parsed_question_vals, tuple):
                    parsed_question:str = parsed_question_vals[0]
                    alternative_list = parsed_question_vals[1]
                elif isinstance(parsed_question_vals, str):
                    parsed_question:str = parsed_question_vals

                if parsed_question == "non-standard alternatives": #caso a questão tenha alternativas de imagens (mas que o PDF não consegue detectar)     
                    question_start_index = position
                    answer_number += 1
                    continue

                if self.output_type == "txt":
                    parsed_question = self.__TXT_QUESTION_TEMPLATE__.format(test_year = test_year, question_text = parsed_question, correct_answer = correct_answer)
                else:
                    question_json:dict = self.__get_json_from_question__(  #retorna um dict com as informações da questão, para ser carregada num JSON
                        question= parsed_question,
                        day_one=False,
                        year= test_year,
                        correct_answer= correct_answer,
                        number= answer_number,
                        alternative_list= alternative_list,
                        image_list= image_name_list
                    )
                
                start_natu, end_natu = topic_question_range["natu"] #desempacotando a tuple de ranges de questões das matérias
                start_math, end_math = topic_question_range["math"]

                if answer_number in range(start_natu, end_natu+1):  #acha qual é a matéria da questão e adiciona a questão na variável associada
                    if self.output_type == "txt":
                       natural_sci_questions += parsed_question
                    else:
                        natural_sci_questions.append(question_json)

                elif answer_number in range(start_math, end_math+1):
                    if self.output_type == "txt":
                        math_questions += parsed_question
                    else:
                        math_questions.append(question_json)
                    
                question_start_index = position
                answer_number += 1
       
        #escrever as strings extraidas nos seus arquivos respectivos
        if self.output_type == "txt":   
             file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_natu_questions.txt" )
             with open(file_path, "w") as f_natu:
                f_natu.write(natural_sci_questions)
            
             file_path = os.path.join(self.extracted_data_path,f"{test_year}_math_questions.txt" )
             with open(file_path, "w") as f_math:
                  f_math.write(math_questions)
        else:
             file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_math_questions.json" )
             with open(file_path, "w") as f_math:
                json.dump(math_questions, f_math, indent=4,  ensure_ascii=False)
                
             file_path = os.path.join(self.extracted_data_path,f"{test_year}_natu_questions.json" )
             with open(file_path, "w") as f_natu:
                json.dump(natural_sci_questions,f_natu, indent=4,  ensure_ascii=False)

    def __handle_day_one_tests__(self, pdf_reader: fitz.fitz.Document, test_year:int)->None:

        total_question_number: int = 0 
        if self.output_type == "txt":
            english_questions: str = ""
            spanish_questions: str = ""
            humanities_questions: str = ""
            languages_arts_questions: str = ""
        else:
            english_questions: list[dict] = []
            spanish_questions: list[dict] = []
            humanities_questions: list[dict] = []
            languages_arts_questions: list[dict] = []
            
        num_pages: int = len(pdf_reader)
        topic_question_range:dict[str,tuple] = {"eng": (1,5), "spa":(6,10), "lang": (11,50), "huma":(51,95)} #ultima questão de humanas é a 96 pq tbm são contadas as de ingles e espanho,ambas entre 1-6

        for i in range(1,num_pages): #começamos da página numero um para não processar a capa  
            
            #função que realiza o pre-processamento do texto da página, incluindo decidindo se pula a página ou não (e de que forma pular)
            page_attributes: dict = self.__page_preprocessing__(
                    pdf_reader=pdf_reader,
                    page_index=i, 
                    total_question_number=total_question_number
            )      
            if not page_attributes: #dict vazio, pagina não tem questões
                 continue  

            page_first_question:int = page_attributes.get("page_first_question")
            total_question_number = page_attributes.get("total_question_number")
            text:str = page_attributes.get("text") 
            if not text: #dict com texto vazio (imagens na pagina), mas atualizando page_first question e total_question_number
                continue

            question_start_index:int = 0
            answer_number: int = page_first_question
            in_spanish_question: bool = False
            if self.output_type == "json": alternative_list:list[str] = []
            
            for position in self.__yield_all_substrings__(text, self.__QUESTION_IDENTIFIER__): #yield na posição da substring que identifica as questoes     
                if position == 0: #se ele detectar a substr "QUESTÃO" no começo do texto, ele pula, caso contrário seria adicionado um string vazia
                    continue
                
                if answer_number > 5 and answer_number < 11:
                    in_spanish_question = True  #verifica se a questão é de espanhol
                else:
                    in_spanish_question = False

                # se a questão for de espanhol é necessário uma pequena mudança na parte de pegar a resposta
                correct_answer:str = self.__find_correct_answer__(
                        question_number= answer_number, 
                        is_spanish_question= in_spanish_question, 
                        day_one=True
                ) 
                unparsed_alternatives: str = text[question_start_index:position]
                
                parsed_question_vals: Any   = self.__parse_alternatives__(unparsed_alternatives)
                if isinstance(parsed_question_vals, tuple):
                    parsed_question:str = parsed_question_vals[0]
                    alternative_list = parsed_question_vals[1]
                elif isinstance(parsed_question_vals, str):
                    parsed_question:str = parsed_question_vals
                
                
                if parsed_question == "non-standard alternatives": #caso a questão tenha alternativas de imagens (mas que o PDF não consegue detectar)     
                    question_start_index = position
                    answer_number += 1
                    continue
                
                if self.output_type == "txt":
                    parsed_question = self.__TXT_QUESTION_TEMPLATE__.format(test_year = test_year, question_text = parsed_question, correct_answer = correct_answer)
                else:
                    question_json:dict = self.__get_json_from_question__(
                        question= parsed_question,
                        day_one=True,
                        year= test_year,
                        correct_answer= correct_answer,
                        number= answer_number,
                        alternative_list= alternative_list
                    )
                    
                start_eng, end_eng = topic_question_range["eng"] #desempacotando a tuple de ranges de questões das matérias
                start_spa, end_spa = topic_question_range["spa"]
                start_lang, end_lang = topic_question_range["lang"]
                start_huma, end_huma = topic_question_range["huma"]

                if answer_number in range(start_eng, end_eng+1):
                    if self.output_type == "txt":
                        english_questions += parsed_question
                    else:
                        english_questions.append(question_json)

                elif answer_number in range(start_spa, end_spa+1):
                    if self.output_type == "txt":
                        spanish_questions += parsed_question
                    else:
                        spanish_questions.append(question_json)

                elif answer_number in range(start_lang, end_lang+1):
                    if self.output_type == "txt":
                        languages_arts_questions += parsed_question
                    else:
                        languages_arts_questions.append(question_json)

                elif answer_number in range(start_huma, end_huma+1):
                    if self.output_type == "txt":
                        humanities_questions += parsed_question
                    else:
                        humanities_questions.append(question_json)


                    
                question_start_index = position
                answer_number += 1
            
        
        #escrever as strings extraidas nos seus arquivos respectivos
        if self.output_type == "txt":   
            file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_eng_questions.txt" )
            with open(file_path, "w") as f_eng:
                f_eng.write(english_questions)
                
            file_path = os.path.join(self.extracted_data_path,f"{test_year}_spani_questions.txt" )
            with open(file_path, "w") as f_spani:
                    f_spani.write(spanish_questions)

            file_path = os.path.join(self.extracted_data_path,f"{test_year}_lang_questions.txt" )     
            with open(file_path, "w") as f_lang:
                f_lang.write(languages_arts_questions)
                
            file_path= os.path.join(self.extracted_data_path, f"{test_year}_huma_questions.txt" )
            with open(file_path, "w") as f_huma:
                f_huma.write(humanities_questions)
        else:
            file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_eng_questions.json" )
            with open(file_path, "w") as f_eng:
                json.dump(english_questions,f_eng, indent=4,  ensure_ascii=False)
                
            file_path = os.path.join(self.extracted_data_path,f"{test_year}_spani_questions.json" )
            with open(file_path, "w") as f_spani:
                    json.dump(spanish_questions,f_spani,  indent=4,  ensure_ascii=False)

            file_path = os.path.join(self.extracted_data_path,f"{test_year}_lang_questions.json" )     
            with open(file_path, "w") as f_lang:
                json.dump(languages_arts_questions,f_lang, indent=4,  ensure_ascii=False)
                
            file_path= os.path.join(self.extracted_data_path, f"{test_year}_huma_questions.json" )
            with open(file_path, "w") as f_huma:
                json.dump(humanities_questions,f_huma, indent=4,  ensure_ascii=False)

    def __handle_day_two_tests__(self, pdf_reader: fitz.fitz.Document, test_year:int)->None:
        
        total_question_number: int = 0 
        if self.output_type == "txt":  #a variavel para as questões de cada matéria depende do tipo de output, se for .txt é uma string, se for JSON é uma lista de dicts
             math_questions: str = ""
             natural_sci_questions: str = ""
        else:
            math_questions: list[dict] = []
            natural_sci_questions: list[dict] = []
            
        num_pages: int = len(pdf_reader)
        topic_question_range:dict[str,tuple] = {"natu": (1,45), "math":(46,91)} #dict com o range de questões para cada matéria, contando que cada dia começa na questão 1

        for i in range(1,num_pages): #começamos da página numero um para não processar a capa  
            
            #função que realiza o pre-processamento do texto da página, incluindo decidindo se pula a página ou não (e de que forma pular)
            page_attributes: dict = self.__page_preprocessing__(
                    pdf_reader=pdf_reader,
                    page_index=i, 
                    total_question_number=total_question_number
            )      
            if not page_attributes: #dict vazio, pagina não tem questões
                 continue  

            page_first_question:int = page_attributes.get("page_first_question")
            total_question_number = page_attributes.get("total_question_number")
            text:str = page_attributes.get("text") 
            
            if not text: #dict com texto vazio (imagens na pagina),pular página mas atualizando page_first question e total_question_number
                continue

            question_start_index:int = 0
            answer_number: int = page_first_question
            if self.output_type == "json": alternative_list:list[str] = []
            
            for position in self.__yield_all_substrings__(text, self.__QUESTION_IDENTIFIER__): #yield na posição da substring que identifica as questoes     
                if position == 0: #se ele detectar a substr "QUESTÃO" no começo do texto, ele pula, caso contrário seria adicionado um string vazia
                    continue
                
                correct_answer:str = self.__find_correct_answer__(
                        question_number= answer_number, 
                        is_spanish_question= False, 
                        day_one=False
                ) 
                unparsed_alternatives: str = text[question_start_index:position]
                parsed_question_vals: Any   = self.__parse_alternatives__(unparsed_alternatives) #retorna os valores da questão processada, pode ser uma string ou um tuple
               
                if isinstance(parsed_question_vals, tuple): #processa os valores baseado no tipo de retorno
                    parsed_question:str = parsed_question_vals[0]
                    alternative_list = parsed_question_vals[1]
                elif isinstance(parsed_question_vals, str):
                    parsed_question:str = parsed_question_vals
                
                if parsed_question == "non-standard alternatives": #caso a questão tenha alternativas de imagens (mas que o PDF não consegue detectar)     
                    question_start_index = position
                    answer_number += 1
                    continue
                
                if self.output_type == "txt":  #valor da questão depende do tipo de output
                    parsed_question = self.__TXT_QUESTION_TEMPLATE__.format(test_year = test_year, question_text = parsed_question, correct_answer = correct_answer)
                else:
                    question_json:dict = self.__get_json_from_question__(
                        question= parsed_question,
                        day_one=False,
                        year= test_year,
                        correct_answer= correct_answer,
                        number= answer_number,
                        alternative_list= alternative_list
                    )
                    
                start_natu, end_natu = topic_question_range["natu"] #desempacotando a tuple de ranges de questões das matérias
                start_math, end_math = topic_question_range["math"]

                if answer_number in range(start_natu, end_natu+1):
                    if self.output_type == "txt":
                       natural_sci_questions += parsed_question
                    else:
                        natural_sci_questions.append(question_json)

                elif answer_number in range(start_math,  end_math+1):
                    if self.output_type == "txt":
                        math_questions += parsed_question
                    else:
                        math_questions.append(question_json)
       
                question_start_index = position
                answer_number += 1
            
        #escrever as strings extraidas nos seus arquivos respectivos, dependendo do tipo de output
        if self.output_type == "txt":   
             file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_natu_questions.txt")
             with open(file_path, "w") as f_natu:
                f_natu.write(natural_sci_questions)
            
             file_path = os.path.join(self.extracted_data_path,f"{test_year}_math_questions.txt")
             with open(file_path, "w") as f_math:
                  f_math.write(math_questions)
        else:
             file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_math_questions.json")
             with open(file_path, "w") as f_math:
                json.dump(math_questions, f_math, indent=4,  ensure_ascii=False)
                
             file_path = os.path.join(self.extracted_data_path,f"{test_year}_natu_questions.json")
             with open(file_path, "w") as f_natu:
                json.dump(natural_sci_questions,f_natu, indent=4,  ensure_ascii=False)
   
    #-------método principal para o user extrair os contéudos de um PDF (dado o path dele e do gabarito relacionado) e escrever os contéudos em uma pasta específicada------- 
            
    def extract_pdf(self,test_pdf_path: str, answers_pdf_path:str, extracted_data_path:str)->None: #extrai o texto dos PDF de um ano específico
        """
        Método público para extrair os contéudos de um PDF do ENEM e escrever numa localização específica.

        Argumentos:
            test_pdf_path (str) : path para o PDF da prova do ENEM. 
            answers_pdf_path (str) : path para o gabarito da prova do ENEM.
            -OBS: ambos arquivos acima devem seguir a nomeclatura do PDF baixado do site do INEP.

            extracted_data_path (str) : path para o diretório onde os dados extraidos serão escritos.
        
        """
        self.__handle_IO_errors__(test_pdf_path= test_pdf_path, answers_pdf_path= answers_pdf_path)
        
        answer_pdf_reader: fitz.fitz.Document = fitz.open(answers_pdf_path)
        answer_page: fitz.fitz.Page = answer_pdf_reader[0]
        raw_answer_text :str = answer_page.get_text()
       
        answers_pattern = "^.{4,}$" #tira todas as linhas do gabarito com mais de 4 chars, ja que todas as respostas são formatadas com os numeros (max de 3 chars) em uma linha e a letra certa na prox
        modified_text = re.sub(answers_pattern, "", raw_answer_text, flags=re.MULTILINE)

        self.answer_pdf_text:str = modified_text #texto do gabarito, usado para a função que pega a resposta oficial
        self.answer_pdf_path:str = answers_pdf_path
        self.test_pdf_path:str = test_pdf_path
       
        absolute_path:str = os.path.abspath(extracted_data_path)   #cria path absoluto para o diretório de output com o argumento da função
        if not os.path.isdir(absolute_path):
            print("diretório não encontrado, criando um novo")
            os.makedirs(absolute_path)
        
        self.extracted_data_path:str = absolute_path

        test_pdf_reader: fitz.fitz.Document  = fitz.open(test_pdf_path) 
        regex_return:list = re.findall(self.__YEAR_PATTERN__, self.test_pdf_path)
        test_year:int = int(regex_return[0])   
    
        if self.__DAY_ONE_SUBSTR__ in test_pdf_path:     
              if not self.process_questions_with_images:
                 self.__handle_day_one_tests__(test_pdf_reader,test_year)
              else:
                  pdf_reader = fitz.open(self.test_pdf_path)
                  self.__handle_day_one_with_images__(pdf_reader,test_year=test_year)
        else:
              if not self.process_questions_with_images:
                 self.__handle_day_two_tests__(test_pdf_reader,test_year)
              else:
                 self.__handle_day_two_with_images__(test_pdf_reader,test_year)
