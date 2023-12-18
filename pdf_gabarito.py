from PyPDF2 import PdfReader  #acha o gabarito de uma questão X 
import re

pdf = PdfReader("enem_1dia_2022_gaba_azul.pdf")

page = pdf.pages[0]
text = page.extract_text()

def find_answer (question_int:int):
    #question_int = int(question)
    
    if question_int > 10:
        question_int = question_int -5

    question_string = str(question_int)
    pattern = r'\b' + question_string + r'\b'
    match =  re.search(pattern, text)
    if match:
        if question_int <10:
            answer_index = (match.start() +2)
        else:  answer_index = (match.start() +3)
        
    else: 
        return "não achou a questão"
    print(text[answer_index])
    
    return text[answer_index]

def find_answer2 (question_number:int, spanish_questions:bool = False)->str:
    if question_number > 5:
        question_number = question_number -5
        
    question_string = str(question_number)
    question_num_pattern = r'\b' + question_string + r'\b'
   
    num_match =  re.search(question_num_pattern, text)
    
    if num_match: # se achamos o número da questão isolado (não como parte de outro número)
        if question_number < 10 :
            if spanish_questions:
                answer_index:int = (num_match.start() +4) #se o numero da questao de for de 1 digito, e ela for de espanhou, a resposta está a 4 espaços na direita
            else:
                 answer_index = (num_match.start() +2) #se o numero da questao de for de 1 digito, e ela for de inglẽs, a resposta está a 2 espaços na direita
        
        else:  answer_index = (num_match.start() +3) #se tiver 2 digitos, a resposta está a 3 espaços na direita
        
    else: 
        return "não achou a questão"
    print(text[answer_index])
    
    return text[answer_index]

#print(find_answer(94))