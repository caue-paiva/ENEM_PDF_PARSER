# Enem PDF Parser

:brazil:

## Sobre o Projeto

O objetivo desse projeto é fornecer uma ferramenta para extração de dados textuais e visuais dos PDFs do Exame Nacional do Ensino Médio (ENEM), disponíveis no site oficial do [INEP](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem/provas-e-gabaritos).     Para uma melhor padronização e funcionamento da ferramenta, a **nomenclatura dos arquivos PDFs no site oficial mencionado acima foi utilizada.**

A motivação para a criação do projeto veio da necessidade de extrair dados do ENEM para uso em **aplicações de Processamento de Linguagem Natural (NLP)**, a exemplo de tarefas de retrieval por busca semântica **(RAG com vector Databases)** para melhorar a performance de Modelos de Linguagem (LLMs) existentes e também datasets para fine-tuning/treinamento de modelos open-source para tarefas específicas relacionadas à assuntos como utilização de IA no cenário de educação brasileiro.

Uma inspiração para o projeto e para a forma de estruturar os dados extraídos em JSON foi o repositório do projeto [GPT-4 ENEM](https://github.com/piresramon/gpt-4-enem?tab=readme-ov-file), que realiza benchmarks do GPT-4 na tarefa de responder questões do ENEM

**Observação sobre a prova ENEM**

Na documentação, código e output se faz referência aos dias do ENEM:
* **Primeiro dia ou D1** são as provas de Lingua estrangeira (Inglês ou Espanhol), Linguagens e Humanas

* **Segundo Dia ou D2** são as provas de Ciências da Natureza e Matemática


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

O parâmetro **output_type** dita qual vai ser o formato de arquivo do output, recebe uma string "txt" ou "json" como parâmetro

O segundo parâmetro, **process_questions_with_images**, dita se a ferramenta irá processar e extrair questões com imagens ou se irá pulá-las".

Ex:
``` Python
text_extractor = EnemPDFextractor(output_type="txt", process_questions_with_images=False)
```

# 5) Usar o método de extração do PDF

Esse método recebe os seguintes parâmetros:

* **test_pdf_path**: path do arquivo pdf da prova

* **answers_pdf_path**: path do arquivo pdf do gabarito correspondente

*  **extracted_data_path**: path para o diretório onde o output será extráido, caso não exista, um novo diretório será criado





:US:

## About the Project

The goal of this project is to provide a tool for extracting textual and visual data from the PDFs of the brazilian standardized high school tests (ENEM) which are used for university admission, available officially from this [public website](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem/provas-e-gabaritos). For better standardization and functionality of the tool, the file naming convention of the official website mentioned above was used.

The motivation for creating the project came from the need to extract ENEM test data for use in **Natural Language Processing (NLP) applications**, such as semantic search retrieval tasks **(RAG with vector Databases)** to improve the performance of existing Language Models (LLMs) and also datasets for fine-tuning/training open-source models for specific tasks related to issues such as the use of AI in the Brazilian education scenario.

An inspiration for the project and the way of structuring the extracted data in JSON was the repository of the [GPT-4 ENEM project](https://github.com/piresramon/gpt-4-enem?tab=readme-ov-file), which benchmarks GPT-4 in the task of answering ENEM questions.


# Note about the ENEM exam

In the documentation, code, and output, reference is made to the days of the test:

* **Day one or D1**  have the following subjects: Foreign Language (English or Spanish), Languages and arts, and Humanities.

* **Day two or D2** have the subjects:  Natural Sciences and Mathematics.

## Extracted Data
# TXT
If the output format is TXT, then the following will be extracted:

* question text (header, body, and alternatives)

* correct alternative, which will be added at the end of the question text

* images in .png files if the image extraction parameter is True



# JSON
If the output format is JSON, then the following will be extracted as different JSON keys:

* question text (header, body, and alternatives), as "question_txt"

* the correct alternative, which will be added at the end of the question text, as "correct_answer"

* all alternatives of the question, as "alternatives"


* all images from the page in .png files if the image extraction parameter is True

* a list with the name and path of all images extracted from the question page, as "page_images"

* an ID that identifies the year, day, and corresponding question number, as "ID"

* Year, day, and question number, respectively as: "year", "day", "question_num"

**In all cases, the correct answer to the question is extracted**, so it is necessary to have the corresponding answer key file for the tool to function.


## How to Use the Tool

# 1) Clone the repository:
```
git clone https://github.com/caue-paiva/ENEM_PDF_PARSER
```
# 2) Install the dependencies
```
pip install -r requirements.txt
```

# 3) Import the class
``` Python
from enem_pdf_extractor import EnemPDFextractor
```

# 4) Instantiate the class

The **output_type parameter** dictates the file format of the output, receives a string "txt" or "json" as a parameter.

The second parameter, **process_questions_with_images**, dictates whether the tool will process and extract questions with images or skip them.

Ex:
``` Python
text_extractor = EnemPDFextractor(output_type="txt", process_questions_with_images=False)
```

# 5) Use the PDF extraction method
This method receives the following parameters:

* **test_pdf_path**: path of the test pdf file
* **answers_pdf_path**: path of the corresponding answer key pdf file
* **extracted_data_path**: path to the directory where the output will be extracted, if it does not exist, a new directory will be created