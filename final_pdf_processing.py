from PyPDF2 import PdfReader 
import re #tentar parsear o arquivo das questoes, ver se existem questoes sem nada, ai compara a distancia entra a string (enem) e a (resposta), se ala for muito pequena, deleta tudo entre elas
import pdf_gabarito as gab
import functions as fn
from functions import yield_all_substrings
from functions import replace_code


#constantes baseadas na nomeclatura do INEP dos arquivos do enem, ex: 2022_GB_impresso_D1_CD1.pdf 
#utilizadas para identificar qual prova ou gabarito estamos lidando

YEAR_PATTERN = "20\d{2}"
DAY_ONE_SUBSTR = "D1"  #substr no nome do PDF que indica qual o dia da prova
TEST_IDENTIFIER = "PV"
ANSWER_PDF_IDENTIFIER = "GB"
NUM_PATTERN1 = r"\*\w{9}\*"  #esses padrões vem de um código de barras presente no topo de toda página, ele vai ser removido
NUM_PATTERN2 = r"\*\w{10}\*"
QUESTION_IDENTIFIER = "QUESTÃO"
QUESTION_TEMPLATE= "(Enem/{test_year})  {question_text} \n (RESPOSTA) sempre correta: {correct_answer} \n\n"

def __handle_day_one_tests__(pdf_reader:PdfReader,test_pdf_path:str, answers_pdf_path:str, test_year:int, num_pages:int)->None:
     total_question_number: int = 0
     english_questions: str = ""
     spanish_questions: str = ""
     humanities_questions: str = ""
     languages_arts_questions: str = ""
     
     past_eng_questions: bool = False
     topic_question_range:dict[str,tuple] = {"eng": (1,6), "spa":(1,6), "lang": (11,51), "huma":(51,96)} #ultima questão de humanas é a 96 pq tbm são contadas as de ingles e espanho,ambas entre 1-6

     for i in range(1,num_pages): #começamos da página numero um para não processar a capa 
         current_page = pdf_reader.pages[i]             
         
         try:
           num_images:int = len(current_page.images)
         except:
            print("exception")   #verifica se tem imagens na pagina
            num_images = 1
         
         if num_images != 0:
             continue  #caso tenha imagens na página vamos pular ela, já que não podemos extrair a imagem
         
         text:str = current_page.extract_text()
         first_question: int = next(yield_all_substrings(text,QUESTION_IDENTIFIER),-1) #acha a primeira questão da folha
        
         if first_question == -1:
             print("sem questões")
             continue # se não tiver questões na página (pagina de redação) pula a iteração
         
         text = text[first_question:]  #antes da primeira questão temos apenas um header inútil (ex: ENEM 2022, ENEM 2022....) do PDF
         
         text = re.sub(NUM_PATTERN1,"", text)  #remove os padrões numéricos do QR codes
         text = re.sub(NUM_PATTERN2,"",text)

         page_first_question: int = total_question_number #a primeira questão da prox página sera o numero total de questões processadas ate o momento
 
         for question in yield_all_substrings(text, 'QUESTÃO'):
            total_question_number += 1  #itera sobre o contador do numero de questões
            print(total_question_number)
        
        #eu ACHO que não precisa colocar o questao_index -= 1 pq eu n to colocando o QUESTÃO  no regex.sub
        
         question_start_index:int = 0
         answer_number: int = page_first_question
         for position in yield_all_substrings(text,QUESTION_IDENTIFIER): #yield na posição da substring que identifica as questoes
             
             correct_answer:str = (gab.find_answer(answer_number)).lower()
             unparsed_alternatives: str = text[question_start_index:position]
             parsed_question: str = fn.parse_alternatives(unparsed_alternatives)
             
             parsed_question = QUESTION_TEMPLATE.format(test_year = test_year, question_text = parsed_question, correct_answer = correct_answer)
             
             if answer_number in range(topic_question_range["eng"]) and not past_eng_questions:
                 english_questions += parsed_question
             
             elif answer_number in range(topic_question_range["spa"]):
                 spanish_questions += parsed_question
             
             elif answer_number in range(topic_question_range["lang"]):
                 languages_arts_questions += parsed_question
             
             elif answer_number in range(topic_question_range["huma"]):
                  humanities_questions += parsed_question
            
             if answer_number >= 5: #se ja passou da questão 5 então ja passou das de inglês
                 past_eng_questions = True
             
             question_start_index = position
             answer_number += 1
                 
                 
          
          

       

def extract_one_pdf(test_pdf_path:str, answers_pdf_path:str , output_text_path: str)->None: #extrai o texto dos PDF de um ano específico
    if TEST_IDENTIFIER not in test_pdf_path:
        raise Exception("nome do arquivo da prova está incorreto")
    
    if ANSWER_PDF_IDENTIFIER not in answers_pdf_path:
        raise Exception("nome do arquivo dr gabarito está incorreto")
      

    pdf_reader:PdfReader = PdfReader(test_pdf_path)
    
    test_year = re.findall(YEAR_PATTERN, "enem_1_dia_2022_azul.pdf")
    test_year:str = test_year[0]

    num_pages:int = len(pdf_reader.pages)    
    question_index: int = 0

    day_one_test: bool

    if DAY_ONE_SUBSTR in test_pdf_path:
        day_one_test = False # a prova não é do primeiro dia
    else:
        day_one_test = True
    



    passed_eng_questions: bool =  False #essa variável diz se na prova do primeiro dia, passamos da questão de ingles ou não
    pass

def extract_all_pdfs()->None: #extra o texto de todos os PDFs em um certo ditório, desde que ele esteja estruturado como ./pdfs_enem
    pass