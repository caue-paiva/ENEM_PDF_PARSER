import re  #file das funções usadas no PDF_PRCOESSING_FINAL.py 

def replace_code(text, replacement):
    pattern = r"\*\w{9}\*"
    pattern2 = r"\*\w{10}\*"
    string = re.sub(pattern, replacement, text)
    string = re.sub(pattern2, replacement, string)
    return string

def yield_all_substrings(string:str, substring:str)->int:
    substring = substring or "*"
    start = 0  
    while True:
        start = string.find(substring, start)
        if start == -1: return  
        yield start
        start += len(substring) 

def parse_alternatives(str_quest):
    index = 0
    patterns_alternative= [r"([A]) ([A])",r"([B]) ([B])",r"([C]) ([C])",r"([D]) ([D])",r"([E]) ([E])"]

    while index <5 :   
        chosen_pattern = patterns_alternative[index]     
        match = re.search(chosen_pattern, str_quest)
        if match: 
            start_posi =  match.start()
            replacement = str_quest[start_posi]
            repla_str = f"{replacement})"
            str_quest= re.sub(chosen_pattern, repla_str, str_quest)
            index +=1          
        else:
            break
       
    return str_quest

#print(parse_alternatives(test_str))

test_str = """A história do Primeiro de Maio de 1890 — na França e na 
Europa, o primeiro de todos os Primeiros de Maio — é, sob 
vários aspectos, exemplar. Resultante de um ato político 
deliberado, essa manifestação ilustra o lado voluntário da 
construção de uma classe — a classe operária — à qual 
os socialistas tentam dar uma unidade política e cultural 
através daquela pedagogia da festa cujo princípio, eficácia 
e limites há muito tempo tinham sido experimentados pela 
Revolução Francesa.
PERROT, M. Os excluídos da história : operários, mulheres e prisioneiros.  
Rio de Janeiro: Paz e Terra, 1988.
Com base no texto, a fixação dessa data comemorativa 
tinha por objetivo
A A valorizar um sentimento burguês.
B B afirmar uma identidade coletiva.
C C edificar uma memória nacional.
D D criar uma comunidade cívica.
E E definir uma tradição popular."""