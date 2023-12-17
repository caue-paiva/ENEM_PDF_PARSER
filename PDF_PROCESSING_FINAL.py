from PyPDF2 import PdfReader 
import re #tentar parsear o arquivo das questoes, ver se existem questoes sem nada, ai compara a distancia entra a string (enem) e a (resposta), se ala for muito pequena, deleta tudo entre elas
import pdf_gabarito as gab
import functions as fn
from functions import yield_all_substrings
from functions import replace_code


reader = PdfReader("enem_1_dia_2022_azul.pdf") #achar o ano das questões
year_pattern = "20\d{2}"
test_year = re.findall(year_pattern, "enem_1_dia_2022_azul.pdf")
test_year = test_year[0]
num_pags= len(reader.pages)
 
replacement = "QUESTÃO"

questao_index = 0   #conta o numero da questão e se ja passou das questões de ingles
eng_quest_passed = False

for i in range(1,num_pags): 
    
    page = reader.pages[i]  #loop sobre todas as paginas do PDF, extraindo o texto de cada uma
    num_images = 0
    texto = page.extract_text() 
    
    try:              
     inicio_quest = next(yield_all_substrings(texto, 'QUESTÃO')) #itera sobre todas as questões da pagina
    except:
        print("sem questões")
        continue 
        
    texto_sem_header = texto[inicio_quest:]
    texto_sem_header = replace_code(texto_sem_header, replacement)
    quest_string_start  = 0
    start_quest_index = questao_index


    for position in yield_all_substrings(texto_sem_header, 'QUESTÃO'):
        questao_index += 1  #itera sobre o contador do numero de questões
        print(questao_index)
        

    questao_index -= 1 

  
    try:
        num_images = len(page.images)
    except:
        print("exception")   #verifica se tem imagens na pagina
        num_images=1

    if num_images == 0:
         num_gaba = start_quest_index
         for position in yield_all_substrings(texto_sem_header, 'QUESTÃO'):
             
             print("num sendo mandado no gaba: "+  str(num_gaba))

             correc_answer = gab.find_answer(num_gaba)
             correc_answer = correc_answer.lower()
             unparsed_alter = texto_sem_header[quest_string_start:position]
             parsed_alternatives = fn.parse_alternatives(unparsed_alter)
             questao_parsed =  f"(Enem/{test_year}) "+ parsed_alternatives +f"\n(RESPOSTA) sempre correta: {correc_answer} \n\n"
             
             if num_gaba in range (1,6) and eng_quest_passed == False:          
                with open( "questoes_ingles3.txt", "a") as f_ing:
                    f_ing.write(questao_parsed)
                f_ing.close()

             elif num_gaba in range (11,51):
                 with open( "questoes_linguagens3.txt", "a") as f_ling:
                    f_ling.write(questao_parsed)
                 f_ling.close()

             elif num_gaba in range (51,96):
                 with open( "questoes_humanas3.txt", "a") as f_hum:
                    f_hum.write(questao_parsed)
                 f_hum.close()
                

             quest_string_start = position
             num_gaba += 1
       
    


