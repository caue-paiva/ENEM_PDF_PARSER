from PyPDF2 import PdfReader  #acha o gabarito de uma questão X 
import re

pdf = PdfReader("enem_1dia_2022_gaba_azul.pdf")

page = pdf.pages[0]
text = page.extract_text()

def find_answer (question_int):
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


#print(find_answer(94))