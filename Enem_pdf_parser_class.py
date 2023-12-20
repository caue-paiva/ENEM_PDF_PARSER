from PyPDF2 import PdfReader 
import re, os ,json #tentar parsear o arquivo das questoes, ver se existem questoes sem nada, ai compara a distancia entra a string (enem) e a (resposta), se ala for muito pequena, deleta tudo entre elas

""" A melhorar:
1) Lidar com casos de questão anulada (atualmente ele pega essas questões e fala que o gabarito é A)

2) fazer com que o JSON da questão inclua as alternativas em uma lista separada

3) refatorar a função que pega o texto e escreve em um TXT em funções menores para acabar com menos funções repetidas

"""



class EnemPDFextractor():
    #constantes baseadas na nomeclatura do INEP dos arquivos do enem, ex: 2022_GB_impresso_D1_CD1.pdf 
    #utilizadas para identificar qual prova ou gabarito estamos lidando
    __YEAR_PATTERN__ = "20\d{2}"
    DAY_ONE_SUBSTR = "D1"  #substr no nome do PDF que indica qual o dia da prova
    TEST_IDENTIFIER = "PV"
    ANSWER_PDF_IDENTIFIER = "GB"
    NUM_PATTERN1 = r"\*\w{9}\*"  #esses padrões vem de um código de barras presente no topo de toda página, ele vai ser removido
    NUM_PATTERN2 = r"\*\w{10}\*"
    QUESTION_IDENTIFIER = "QUESTÃO"
    TXT_QUESTION_TEMPLATE= "(Enem/{test_year})  {question_text}\n(RESPOSTA CORRETA): {correct_answer}\n\n"
    SUPPORTED_OUTPUT_FILES:tuple = ("txt", "json")
    TEST_COLOR_PATTERN = "CD\d{1}"  #provas/cadernos e gabaritos  são separadas por cores, se as cores de ambos forem iguais, eles estão relacionados

    test_pdf_path:str 
    answer_pdf_path: str
    extracted_data_path:str
    output_type:str 
    answer_pdf_text:str

    def __init__(self, output_type:str = "txt")-> None:
        if output_type not in self.SUPPORTED_OUTPUT_FILES:
            raise IOError("tipo de arquivo de output não suportado")

        self.output_type =  output_type
        
    #ao extrair o texto das alternativas do PDF, a letra da  alternativa é repetida 2 vezes, então essa função remove essa segunda repetição
    
    def __handle_IO_errors__(self,test_pdf_path: str, answers_pdf_path:str)->None:
        if self.TEST_IDENTIFIER not in test_pdf_path:
            raise IOError("nome do arquivo da prova não segue o padrão do INEP")
    
        if self.ANSWER_PDF_IDENTIFIER not in answers_pdf_path:
            raise IOError("nome do arquivo do gabarito não segue o padrão do INEP")
            
        test_color_identifier = re.findall(self.TEST_COLOR_PATTERN, test_pdf_path)
        if not test_color_identifier:
            raise IOError("especificação da cor do caderno da prova não segue o padrão do INEP")
        
        answers_color_identifier= re.findall(self.TEST_COLOR_PATTERN, answers_pdf_path)
        if not answers_color_identifier:
            raise IOError("especificação da cor do gabarito não segue o padrão do INEP")
        
        test_color_identifier:str = test_color_identifier[0]
        answers_color_identifier:str = answers_color_identifier[0]
    
        if test_color_identifier[2] != answers_color_identifier[2]:  #terceiro char desse padrão é o numero referente à cor do caderno
            raise IOError("prova e gabarito são de cores diferentes") 

    def __parse_alternatives__(self,question:str)->str:
        index:int = 0
        patterns_alternatives = [r"([A]) ([A])",r"([B]) ([B])",r"([C]) ([C])",r"([D]) ([D])",r"([E]) ([E])"]
    
        while index < 5 :   
            chosen_pattern = patterns_alternatives[index]   #para cada letra na lista de padrões, vamos aplicar a mudança  
            match = re.search(chosen_pattern, question)  
            if match:  #se existir algo similar ao padrão na string 
                start_posi =  match.start() #pega a primeira letra da alternativa
                replacement = question[start_posi]
                repla_str = f"{replacement})" 
                question= re.sub(chosen_pattern, repla_str, question) #troca a substr (ex: A A) com apenas a primeira letra (ex: A)
                index +=1  

                start_posi_str: str = question[start_posi:]
                newline_posi: int =  start_posi_str.find("\n")
                alternative_text_str: str =  question[start_posi+2: start_posi + newline_posi] # essa string contem o texto em si da alternativa depois da Letra e )
                
                if alternative_text_str.isspace(): #caso o texto da alternativa esteja vazia (Alternativas são imagens que não são checadas pelo PDF reader), retornamos um str de erro
                     return "non-standard alternatives"   
            else:
                return "non-standard alternatives" #o padrão não existe, então não é o texto de uma alternativa  
        return question

    def __yield_all_substrings__(self, input_str: str, sub_str:str)->int:
     sub_str = sub_str or "*"
     start = 0  
     while True:
        start:int = input_str.find(sub_str, start)
        if start == -1: return  
        yield start
        start += len(sub_str) 
    
    def __find_correct_answer__ (self, question_number:int,day_one: bool,is_spanish_question:bool = False, )->str:          
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
            #print(self.answer_pdf_text[answer_index])
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
    
    def __txt_handle_day_two_tests__(self, pdf_reader:PdfReader, test_year:int)->None: 
              
     total_question_number: int = 0 
     math_questions: str = ""
     natural_sci_questions: str = ""
     
     topic_question_range:dict[str,tuple] = {"natu": (1,45), "math":(46,91)} 
     num_pages: int = len(pdf_reader.pages)
     for i in range(1,num_pages): #começamos da página numero um para não processar a capa 
        current_page = pdf_reader.pages[i]             
             
        text:str = current_page.extract_text()

        first_question_str_index: int = next(self.__yield_all_substrings__(input_str = text, sub_str = self.QUESTION_IDENTIFIER) , -1 ) #acha a primeira questão da folha
        
        if first_question_str_index == -1:
            print("sem questões")
            continue # se não tiver questões na página (pagina de redação) pula a iteração
         
        text = text[first_question_str_index:]  #antes da primeira questão temos apenas um header inútil (ex: ENEM 2022, ENEM 2022....) do PDF
         
        text = re.sub(self.NUM_PATTERN1,"", text)  #remove os padrões numéricos do QR codes
        text = re.sub(self.NUM_PATTERN2,"",text)

        page_first_question: int = total_question_number + 1 #a primeira questão da prox página sera o numero total de questões processadas ate o momento + 1 (a primeira questão em si)
        
        for _ in self.__yield_all_substrings__(text, self.QUESTION_IDENTIFIER):
            total_question_number += 1  #aumenta o numero de questoes ja processadas com todas daquela página
            #print(total_question_number)
                  
        try:
           num_images:int = len(current_page.images)
        except:
            print("exception")   #verifica se tem imagens na pagina
            num_images = 1
         
        if num_images != 0:  #caso tenha imagens na página vamos pular ela, já que não podemos extrair a imagem 
             print("tem imagens, pula")
             continue   
        #não é possível fazer essa verificação no começo pois é preciso contar todas as questões da página para a variavel total_question_number, já que ela dita qual matéria esta sendo processada
        
        text += f" {self.QUESTION_IDENTIFIER}" #coloca isso no final do texto para ajudar no processamento, já que teremos uma substr de parada do algoritmo
        question_start_index:int = 0
        answer_number: int = page_first_question
        
        for position in self.__yield_all_substrings__(text, self.QUESTION_IDENTIFIER): #yield na posição da substring que identifica as questoes     
            
             if position == 0: #se ele detectar a substr "QUESTÃO" no começo do texto, ele pula, caso contrário seria adicionado um string vazia
                 continue
             # se a questão for de espanhol é necessário uma pequena mudança na parte de pegar a resposta
             correct_answer:str = self.__find_correct_answer__(question_number = answer_number, is_spanish_question= False, day_one= False) 
             unparsed_alternatives: str = text[question_start_index:position]
             parsed_question: str = self.__parse_alternatives__(unparsed_alternatives)
             
             if parsed_question == "non-standard alternatives": #caso a questão tenha alternativas de imagens (mas que o PDF não consegue detectar)     
                 question_start_index = position
                 answer_number += 1
                 continue
             
             parsed_question = self.TXT_QUESTION_TEMPLATE.format(test_year = test_year, question_text = parsed_question, correct_answer = correct_answer)
             
             start_natu, end_natu = topic_question_range["natu"] #desempacotando a tuple de ranges de questões das matérias
             start_math, end_math = topic_question_range["math"]

             if answer_number in range(start_natu,  end_natu+1): #precisamos incluir a ultima questão do range de cada matéria
                natural_sci_questions += parsed_question

             elif answer_number in range( start_math, end_math+1):
                math_questions += parsed_question

             question_start_index = position
             answer_number += 1
        
     #escrever as strings extraidas nos seus arquivos respectivos
     file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_natu_questions.txt" )
     with open(file_path, "w") as f_natu:
             f_natu.write(natural_sci_questions)
        
     file_path = os.path.join(self.extracted_data_path,f"{test_year}_math_questions.txt" )
     with open(file_path, "w") as f_math:
             f_math.write(math_questions)

    def __txt_handle_day_one_tests__(self, pdf_reader:PdfReader, test_year:int)->None:
      
     total_question_number: int = 0 
     english_questions: str = ""
     spanish_questions: str = ""
     humanities_questions: str = ""
     languages_arts_questions: str = ""
     num_pages: int = len(pdf_reader.pages)
     topic_question_range:dict[str,tuple] = {"eng": (1,5), "spa":(6,10), "lang": (11,50), "huma":(51,95)} #ultima questão de humanas é a 96 pq tbm são contadas as de ingles e espanho,ambas entre 1-6

     for i in range(1,num_pages): #começamos da página numero um para não processar a capa 
        current_page = pdf_reader.pages[i]             
             
        text:str = current_page.extract_text()

        first_question_str_index: int = next(self.__yield_all_substrings__(input_str = text, sub_str = self.QUESTION_IDENTIFIER) , -1 ) #acha a primeira questão da folha
        
        if first_question_str_index == -1:
            print("sem questões")
            continue # se não tiver questões na página (pagina de redação) pula a iteração
         
        text = text[first_question_str_index:]  #antes da primeira questão temos apenas um header inútil (ex: ENEM 2022, ENEM 2022....) do PDF
         
        text = re.sub(self.NUM_PATTERN1,"", text)  #remove os padrões numéricos do QR codes
        text = re.sub(self.NUM_PATTERN2,"",text)

        page_first_question: int = total_question_number + 1 #a primeira questão da prox página sera o numero total de questões processadas ate o momento + 1 (a primeira questão em si)
        
        for _ in self.__yield_all_substrings__(text, self.QUESTION_IDENTIFIER):
            total_question_number += 1  #aumenta o numero de questoes ja processadas com todas daquela página
            #print(total_question_number)
                  
        try:
           num_images:int = len(current_page.images)
        except:
            print("exception")   #verifica se tem imagens na pagina
            num_images = 1
         
        if num_images != 0:
             print("tem imagens, pula")
             continue  #caso tenha imagens na página vamos pular ela, já que não podemos extrair a imagem   
        #não é possível fazer essa verificação no começo pois é preciso contar todas as questões da página para a variavel total_question_number, já que ela dita qual matéria esta sendo processada
        
        text += f" {self.QUESTION_IDENTIFIER}" #coloca isso no final do texto para ajudar no processamento, já que teremos uma substr de parada do algoritmo
        question_start_index:int = 0
        answer_number: int = page_first_question
        in_spanish_question: bool = False
        
        for position in self.__yield_all_substrings__(text, self.QUESTION_IDENTIFIER): #yield na posição da substring que identifica as questoes     
             if position == 0: #se ele detectar a substr "QUESTÃO" no começo do texto, ele pula, caso contrário seria adicionado um string vazia
                 continue
             
             if answer_number > 5 and answer_number < 11:
                 in_spanish_question = True  #verifica se a questão é de espanhol
             else:
                 in_spanish_question = False

             # se a questão for de espanhol é necessário uma pequena mudança na parte de pegar a resposta
             correct_answer:str = self.__find_correct_answer__(question_number= answer_number, is_spanish_question= in_spanish_question, day_one=True,) 
             unparsed_alternatives: str = text[question_start_index:position]
             parsed_question: str = self.__parse_alternatives__(unparsed_alternatives)
                
             if parsed_question == "non-standard alternatives": #caso a questão tenha alternativas de imagens (mas que o PDF não consegue detectar)     
                 question_start_index = position
                 answer_number += 1
                 continue

             parsed_question = self.TXT_QUESTION_TEMPLATE.format(test_year = test_year, question_text = parsed_question, correct_answer = correct_answer)
             
             start_eng, end_eng = topic_question_range["eng"] #desempacotando a tuple de ranges de questões das matérias
             start_spa, end_spa = topic_question_range["spa"]
             start_lang, end_lang = topic_question_range["lang"]
             start_huma, end_huma = topic_question_range["huma"]

             if answer_number in range(start_eng, end_eng+1): #precisamos incluir a ultima questão do range de cada matéria
                english_questions += parsed_question

             elif answer_number in range(start_spa, end_spa+1):
                spanish_questions += parsed_question

             elif answer_number in range(start_lang, end_lang+1):
                languages_arts_questions += parsed_question

             elif answer_number in range(start_huma, end_huma+1):
                humanities_questions += parsed_question
                   
             question_start_index = position
             answer_number += 1
        
     #escrever as strings extraidas nos seus arquivos respectivos
     file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_eng_questions.txt" )
     with open(file_path, "a") as f_eng:
        f_eng.write(english_questions)
        
     file_path = os.path.join(self.extracted_data_path,f"{test_year}_spani_questions.txt" )
     with open(file_path, "a") as f_spani:
             f_spani.write(spanish_questions)

     file_path = os.path.join(self.extracted_data_path,f"{test_year}_lang_questions.txt" )     
     with open(file_path, "a") as f_lang:
        f_lang.write(languages_arts_questions)
        
     file_path= os.path.join(self.extracted_data_path, f"{test_year}_huma_questions.txt" )
     with open(file_path, "a") as f_huma:
        f_huma.write(humanities_questions)
     
    def __get_json_from_question__(self, question:str, day_one: bool ,year: int, correc_answer:str, number:int)->dict:
        day_identifier = "D1" if day_one else "D2"
        
        if day_one:
            number = number if number < 6 else number -5 #subtrair as 5 questões contadas na matéria de espanhol
        else:
            number += 90
        
        json_dict = {
           "question_text": question,
           "correct_answer": correc_answer ,
           "ID": f"{year}_{day_identifier}_N{number}",
           "year": year,
           "day": day_identifier,
           "question_num": number
        }
        return json_dict

    def __json_handle_day_one_tests__(self, pdf_reader: PdfReader, test_year:int)->None:
        total_question_number: int = 0 
        english_questions: list[dict] = []
        spanish_questions: list[dict] = []
        humanities_questions: list[dict] = []
        languages_arts_questions: list[dict] = []

        num_pages: int = len(pdf_reader.pages)
        topic_question_range:dict[str,tuple] = {"eng": (1,5), "spa":(6,10), "lang": (11,50), "huma":(51,95)} #ultima questão de humanas é a 96 pq tbm são contadas as de ingles e espanho,ambas entre 1-6

        for i in range(1,num_pages): #começamos da página numero um para não processar a capa 
            current_page = pdf_reader.pages[i]             
                
            text:str = current_page.extract_text()

            first_question_str_index: int = next(self.__yield_all_substrings__(input_str = text, sub_str = self.QUESTION_IDENTIFIER) , -1 ) #acha a primeira questão da folha
            
            if first_question_str_index == -1:
                print("sem questões")
                continue # se não tiver questões na página (pagina de redação) pula a iteração
            
            text = text[first_question_str_index:]  #antes da primeira questão temos apenas um header inútil (ex: ENEM 2022, ENEM 2022....) do PDF
            
            text = re.sub(self.NUM_PATTERN1,"", text)  #remove os padrões numéricos do QR codes
            text = re.sub(self.NUM_PATTERN2,"",text)

            page_first_question: int = total_question_number + 1 #a primeira questão da prox página sera o numero total de questões processadas ate o momento + 1 (a primeira questão em si)
            
            for _ in self.__yield_all_substrings__(text, self.QUESTION_IDENTIFIER):
                total_question_number += 1  #aumenta o numero de questoes ja processadas com todas daquela página
                #print(total_question_number)
                    
            try:
             num_images:int = len(current_page.images)
            except:
                print("exception")   #verifica se tem imagens na pagina
                num_images = 1
            
            if num_images != 0:
                print("tem imagens, pula")
                continue  #caso tenha imagens na página vamos pular ela, já que não podemos extrair a imagem   
            #não é possível fazer essa verificação no começo pois é preciso contar todas as questões da página para a variavel total_question_number, já que ela dita qual matéria esta sendo processada
            
            text += f" {self.QUESTION_IDENTIFIER}" #coloca isso no final do texto para ajudar no processamento, já que teremos uma substr de parada do algoritmo
            question_start_index:int = 0
            answer_number: int = page_first_question
            in_spanish_question: bool = False
            
            for position in self.__yield_all_substrings__(text, self.QUESTION_IDENTIFIER): #yield na posição da substring que identifica as questoes     
                if position == 0: #se ele detectar a substr "QUESTÃO" no começo do texto, ele pula, caso contrário seria adicionado um string vazia
                    continue
                
                if answer_number > 5 and answer_number < 11:
                    in_spanish_question = True  #verifica se a questão é de espanhol
                else:
                    in_spanish_question = False

                # se a questão for de espanhol é necessário uma pequena mudança na parte de pegar a resposta
                correct_answer:str = self.__find_correct_answer__(question_number= answer_number, is_spanish_question= in_spanish_question, day_one=True,) 
                unparsed_alternatives: str = text[question_start_index:position]
                parsed_question: str = self.__parse_alternatives__(unparsed_alternatives)
                    
                if parsed_question == "non-standard alternatives": #caso a questão tenha alternativas de imagens (mas que o PDF não consegue detectar)     
                    question_start_index = position
                    answer_number += 1
                    continue

                question_json:dict = self.__get_json_from_question__(
                      question= parsed_question,
                      day_one=True,
                      year= test_year,
                      correc_answer= correct_answer,
                      number= answer_number
                )
                
                start_eng, end_eng = topic_question_range["eng"] #desempacotando a tuple de ranges de questões das matérias
                start_spa, end_spa = topic_question_range["spa"]
                start_lang, end_lang = topic_question_range["lang"]
                start_huma, end_huma = topic_question_range["huma"]

                if answer_number in range(start_eng, end_eng+1): #precisamos incluir a ultima questão do range de cada matéria
                    english_questions.append(question_json)

                elif answer_number in range(start_spa, end_spa+1):
                    spanish_questions.append(question_json)

                elif answer_number in range(start_lang, end_lang+1):
                    languages_arts_questions.append(question_json)

                elif answer_number in range(start_huma, end_huma+1):
                    humanities_questions.append(question_json)
                    
                question_start_index = position
                answer_number += 1
        
     #escrever as strings extraidas nos seus arquivos respectivos
        file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_eng_questions.json" )
        with open(file_path, "a") as f_eng:
            json.dump(english_questions,f_eng, indent=4,  ensure_ascii=False)
            
        file_path = os.path.join(self.extracted_data_path,f"{test_year}_spani_questions.json" )
        with open(file_path, "a") as f_spani:
                json.dump(spanish_questions,f_spani,  indent=4,  ensure_ascii=False)

        file_path = os.path.join(self.extracted_data_path,f"{test_year}_lang_questions.json" )     
        with open(file_path, "a") as f_lang:
            json.dump(languages_arts_questions,f_lang, indent=4,  ensure_ascii=False)
            
        file_path= os.path.join(self.extracted_data_path, f"{test_year}_huma_questions.json" )
        with open(file_path, "a") as f_huma:
            json.dump(humanities_questions,f_huma, indent=4,  ensure_ascii=False)

    def __json_handle_day_two_tests__(self, pdf_reader: PdfReader, test_year:int)->None:
        
        total_question_number: int = 0 
        math_questions: list[dict] = []
        natural_sci_questions: list[dict] = []
        num_pages: int = len(pdf_reader.pages)
        topic_question_range:dict[str,tuple] = {"natu": (1,45), "math":(46,91)} 
       
        for i in range(1,num_pages): #começamos da página numero um para não processar a capa 
            current_page = pdf_reader.pages[i]             
                
            text:str = current_page.extract_text()

            first_question_str_index: int = next(self.__yield_all_substrings__(input_str = text, sub_str = self.QUESTION_IDENTIFIER) , -1 ) #acha a primeira questão da folha
            
            if first_question_str_index == -1:
                print("sem questões")
                continue # se não tiver questões na página (pagina de redação) pula a iteração
            
            text = text[first_question_str_index:]  #antes da primeira questão temos apenas um header inútil (ex: ENEM 2022, ENEM 2022....) do PDF
            
            text = re.sub(self.NUM_PATTERN1,"", text)  #remove os padrões numéricos do QR codes
            text = re.sub(self.NUM_PATTERN2,"",text)

            page_first_question: int = total_question_number + 1 #a primeira questão da prox página sera o numero total de questões processadas ate o momento + 1 (a primeira questão em si)
            
            for _ in self.__yield_all_substrings__(text, self.QUESTION_IDENTIFIER):
                total_question_number += 1  #aumenta o numero de questoes ja processadas com todas daquela página
                #print(total_question_number)
                    
            try:
             num_images:int = len(current_page.images)
            except:
                print("exception")   #verifica se tem imagens na pagina
                num_images = 1
            
            if num_images != 0:
                print("tem imagens, pula")
                continue  #caso tenha imagens na página vamos pular ela, já que não podemos extrair a imagem   
            #não é possível fazer essa verificação no começo pois é preciso contar todas as questões da página para a variavel total_question_number, já que ela dita qual matéria esta sendo processada
            
            text += f" {self.QUESTION_IDENTIFIER}" #coloca isso no final do texto para ajudar no processamento, já que teremos uma substr de parada do algoritmo
            question_start_index:int = 0
            answer_number: int = page_first_question
            
            for position in self.__yield_all_substrings__(text, self.QUESTION_IDENTIFIER): #yield na posição da substring que identifica as questoes     
                if position == 0: #se ele detectar a substr "QUESTÃO" no começo do texto, ele pula, caso contrário seria adicionado um string vazia
                    continue
                
                # se a questão for de espanhol é necessário uma pequena mudança na parte de pegar a resposta
                correct_answer:str = self.__find_correct_answer__(question_number= answer_number, is_spanish_question= False, day_one=False,) 
                unparsed_alternatives: str = text[question_start_index:position]
                parsed_question: str = self.__parse_alternatives__(unparsed_alternatives)
                    
                if parsed_question == "non-standard alternatives": #caso a questão tenha alternativas de imagens (mas que o PDF não consegue detectar)     
                    question_start_index = position
                    answer_number += 1
                    continue

                question_json:dict = self.__get_json_from_question__(
                      question= parsed_question,
                      day_one=False,
                      year= test_year,
                      correc_answer= correct_answer,
                      number= answer_number
                )
                
                start_natu, end_natu = topic_question_range["natu"] #desempacotando a tuple de ranges de questões das matérias
                start_math, end_math = topic_question_range["math"]

                if answer_number in range(start_natu,  end_natu+1): #precisamos incluir a ultima questão do range de cada matéria
                  natural_sci_questions.append(question_json)

                elif answer_number in range( start_math, end_math+1):
                  math_questions.append(question_json)
                    
                question_start_index = position
                answer_number += 1
        
     #escrever as strings extraidas nos seus arquivos respectivos
        file_path:str = os.path.join(self.extracted_data_path,f"{test_year}_math_questions.json" )
        with open(file_path, "a") as f_math:
            json.dump(math_questions, f_math, indent=4,  ensure_ascii=False)
            
        file_path = os.path.join(self.extracted_data_path,f"{test_year}_natu_questions.json" )
        with open(file_path, "a") as f_natu:
            json.dump(natural_sci_questions,f_natu, indent=4,  ensure_ascii=False)

    def extract_pdf(self,test_pdf_path: str, answers_pdf_path:str, extracted_data_path:str)->None: #extrai o texto dos PDF de um ano específico
        self.__handle_IO_errors__( test_pdf_path= test_pdf_path, answers_pdf_path= answers_pdf_path)
        
        answer_pdf_reader = PdfReader(answers_pdf_path)
        answer_page = answer_pdf_reader.pages[0]
        
        self.answer_pdf_text = answer_page.extract_text() #texto do gabarito, usado para a função que pega a resposta oficial
        self.answer_pdf_path = answers_pdf_path
        self.test_pdf_path = test_pdf_path
        self.extracted_data_path = extracted_data_path

        if not os.path.isdir(extracted_data_path):
             print("diretorio de output não existe, criando um novo")
             os.makedirs(extracted_data_path, exist_ok=True)

        test_pdf_reader:PdfReader = PdfReader(test_pdf_path) 
        regex_return = re.findall(self.__YEAR_PATTERN__, self.test_pdf_path)
        test_year:int = int(regex_return[0])   
        print(type(regex_return[0]))
    
        if self.DAY_ONE_SUBSTR in test_pdf_path:
            if self.output_type == "txt":
              self.__txt_handle_day_one_tests__(test_pdf_reader,test_year)
            else:
              self.__json_handle_day_one_tests__(test_pdf_reader,test_year)
        else:
            if self.output_type == "txt":
              self.__txt_handle_day_two_tests__(test_pdf_reader,test_year)
            else:
              self.__json_handle_day_two_tests__(test_pdf_reader,test_year)
        