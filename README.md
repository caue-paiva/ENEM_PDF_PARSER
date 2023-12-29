# Enem PDF Parser

:brazil:

## Sobre o Projeto

O objetivo desse projeto é fornecer uma ferramenta para extração de dados textuais e visuais dos PDFs do Exame Nacional do Ensino Médio (ENEM), disponíveis no site oficial do [INEP](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem/provas-e-gabaritos).Para uma melhor padronização e funcionamento da ferramenta, a **nomeclatura dos arquivos PDFs no site oficial mencionado acima foi utilizada.**

A motivação para a criação do projeto veio da necessidade de extrair dados do ENEM para uso em **aplicações de Processamento de Linguagem Natural (NLP)**, a exemplo de tarefas de retrieval por busca semântica **(RAG com vector Databases)** para melhorar a performance de Modelos de Linguagem (LLMs) existentes e também datasets para fine-tuning/treinamento de modelos open-source para tarefas específicas relacionadas à assuntos como utilização de IA no cenário de educação brasileiro.

Uma inspiração para o projeto e para a forma de estruturar os dados extraídos em JSON foi o repositório do projeto [GPT-4 ENEM](https://github.com/piresramon/gpt-4-enem?tab=readme-ov-file), que realiza benchmarks do GPT-4 na tarefa de responder questões do ENEM

**Observação sobre a prova ENEM**
Na documentação, código e output se faz referência aos dias do ENEM:

* **Primeiro dia** são as provas de Lingua estrangeira (Inglês, Espanhol), Linguagens e Humanas

* **Segundo Dia** são as provas de Ciências da Natureza e Matemática


## Dados Extraídos

# TXT

Caso o formato do output seja  TXT, então serão extraídos:
* texto da questão (cabeçalho, corpo e alternativas) 

* alternativa correta, que será adicionada no fim do texto da questão

* imagens em arquivos .png se o parâmetro de extração de imagens for True


# JSON
Caso o formato do output seja  JSON, então serão extraídos como diferentes keys do JSON:

* texto da questão (cabeçalho, corpo e alternativas), como "question_txt"

* a alternativa correta, que será adicionada no fim do texto da questão,  como "correct_answer"

* todas as alternativas da questão, como "alternatives"

* todas as imagens da página em arquivos .png se o parâmetro de extração de imagens for True

* uma lista com o nome e o path de todas as imagens extraídas da página da questão, como "page_images"

* um ID que identifica o ano, dia e  número correspondente à questão, como "ID"

* Ano, dia e número da questão, respectivamento como : "year", "day", "question_num"

Em **todos os casos é extráido a resposta correta da questão**, por isso se faz necessário ter o arquivo do gabarito correspondente à prova para a ferramenta funcionar.

## Como utilizar a ferramenta


# 1) Clonar o repositório:
```
git clone https://github.com/caue-paiva/ENEM_PDF_PARSER
```

# 2) Instalar as dependências 
```
pip install -r requirements.txt
```

# 3) importar  a classe 
``` Python
from enem_pdf_extractor import EnemPDFextractor
```

# 4) instanciar a classe 

O parâmetro **output_type** dita qual vai ser o formato de arquivo do output, recebe uma str "txt" ou "json" como parâmetro

O segundo parâmetro, **process_questions_with_images**, dita se a ferramenta irá processar questões com imagens e extrair suas imagens ou se irá pular elas

Ex:
``` Python
text_extractor = EnemPDFextractor(output_type="txt", process_questions_with_images=False)
```

# 5) Usar o método de extração do PDF

Esse método recebe os seguintes parâmetros:

* **test_pdf_path**: path do arquivo pdf da prova

* **answers_pdf_path**: path do arquivo pdf do gabarito correspondente

*  **extracted_data_path**: path para o diretório onde o output será extráido, caso não exista um novo diretório será criado

