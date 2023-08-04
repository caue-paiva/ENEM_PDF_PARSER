
resposta_size = len("(RESPOSTA) sempre correta:d ")
question_subjects= "humanas"
def find_all_substrings(string, substring):
    substring = substring or "*"
    start = 0  
    while True:
        start = string.find(substring, start)
        if start == -1: return  
        yield start
        start += len(substring) 

with open(f"questoes_{question_subjects}.txt", "r") as pF:
    text_string = pF.read()
    text_list = list(text_string)

pF.close()


def find_all_substrings(string, substring):
    substring = substring or "*"
    start = 0  
    while True:
        start = string.find(substring, start)
        if start == -1: return  
        yield start
        start += len(substring) 

    
for position1 in find_all_substrings(text_string, '(Enem/'):
    for position2 in find_all_substrings(text_string, '(RESPOSTA)'):
        
        distance = position2 - position1

        if distance > 0  and distance <20:
            for i in range (distance+resposta_size):
               text_list[position1 + i] = ""
                    
final_list = "".join(text_list)

print(type(final_list))
with open(f"questoes_{question_subjects}2.txt", "w") as pF:
    pF.write(final_list)
    pF.close()