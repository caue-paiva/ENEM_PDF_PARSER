# Enem PDF Parser

:brazil:

## Sobre o Projeto

O objetivo desse projeto é fornecer uma ferramenta para extração de dados textuais e visuais dos PDFs do Exame Nacional do Ensino Médio (ENEM), disponíveis no site oficial do [INEP](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem/provas-e-gabaritos).Para uma melhor padronização e funcionamento da ferramenta, a nomeclatura dos arquivos PDFs no site oficial mencionado acima foi utilizada.

A motivação para a criação do projeto veio da necessidade de extrair dados do ENEM para uso em aplicações de Processamento de Linguagem Natural (NLP), a exemplo de tarefas de retrieval por busca semântica (RAG com vector Databases) para melhorar a performance de Modelos de Linguagem (LLMs) existentes e também datasets para fine-tuning/treinamento de modelos open-source para tarefas específicas relacionadas à assuntos como utilização de IA no cenário de educação brasileiro.

Uma inspiração para o projeto e para a forma de estruturar os dados extraídos em JSON foi o repositório do projeto [GPT-4 ENEM](https://github.com/piresramon/gpt-4-enem?tab=readme-ov-file), que realiza benchmarks do GPT-4 na tarefa de responder questões do ENEM
