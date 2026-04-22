# API Raízes do Nordeste

## Descrição

API REST desenvolvida em Flask para gerenciamento de unidades, produtos, pedidos e usuários, incluindo autenticação via JWT e regras de negócio como desconto e programa de fidelidade.

O projeto simula um sistema de pedidos com múltiplas entidades e operações típicas de um backend moderno.

---

## Tecnologias utilizadas

* Python
* Flask
* Flask-SQLAlchemy
* Flask-JWT-Extended
* SQLite
* Flask-Bcrypt

---

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/MarceloMoura07/RaizesDoNordeste.git
cd RaizesDoNordeste
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
```

### 3. Ativar ambiente virtual

Windows:

```bash
venv\Scripts\activate
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

### 5. Executar a aplicação

```bash
python run.py
```

A API estará disponível em:

```
http://localhost:5000
```

---

## Documentação da API (Swagger)

A documentação da API é gerada automaticamente utilizando o Flasgger (Swagger).

Como acessar:

Após iniciar a aplicação, acesse no navegador:

http://localhost:5000/docs
### O que está disponível:
- Lista completa dos endpoints
- Parâmetros de entrada (request)
- Exemplos de requisição
- Exemplos de resposta
- Códigos de status HTTP
- Teste direto das rotas pelo navegador

### Observação importante

Para testar endpoints protegidos:

1. Faça login na rota /login
2. Copie o access_token
3. Clique em Authorize no Swagger
4. Insira:
Bearer <seu_token>


## Autenticação

A API utiliza autenticação via JWT.

### Fluxo:

1. Criar usuário (`/register`)
2. Fazer login (`/login`)
3. Copiar o `access_token`
4. Usar nas rotas protegidas com o header:

```
Authorization: Bearer <seu_token>
```

---

## Estrutura do projeto

```
app/
│
├── api/
├── domain/
├── infrastructure/

postman/
│
├── raizes-do-nordeste.postman_collection.json
├── raizes-env.postman_environment.json

run.py
requirements.txt
README.md
```

---

##  Arquitetura

O projeto segue parcialmente o padrão em camadas proposto no roteiro:

* **API** → rotas Flask (entrada da aplicação)
* **Domain** → entidades e regras de negócio
* **Infrastructure** → configuração e persistência

###  Observação importante

A camada **Application** não foi implementada como pasta separada.
As responsabilidades dessa camada foram incorporadas diretamente nas rotas (API) e no domínio (Domain), simplificando a estrutura para um nível inicial.

---

##  Funcionalidades principais

* Cadastro de usuários
* Login com JWT
* Criação de unidades
* Cadastro de produtos
* Criação de pedidos com múltiplos itens
* Aplicação de desconto para pedidos via app
* Controle de estoque
* Atualização de status de pedidos
* Programa de fidelidade (acúmulo e resgate de pontos)

---

## Atualizações e melhorias

Durante o desenvolvimento e ajustes da API, foi realizada uma melhoria no retorno das operações de criação.

### Retorno de IDs nas criações

Os endpoints de criação (como produtos e pedidos) foram ajustados para retornar explicitamente o identificador do recurso criado.

Exemplo:

```json
{
  "message": "Produto criado com sucesso",
  "produto_id": 1
}
```
---

## Regras de negócio implementadas

* Desconto de 10% para pedidos feitos via **app**
* Controle de estoque por produto
* Validação de vínculo produto/unidade
* Fluxo de status de pedidos controlado
* Programa de fidelidade:

  * 1 ponto a cada R$10 gastos
  * Resgate em múltiplos de 10 pontos

---

## Testes

Os testes da API foram realizados manualmente utilizando:

* Swagger (Flasgger) — para validação de endpoints com entradas válidas
* Postman — para cenários de validação negativa e maior controle das requisições

### Observação importante

Alguns cenários de teste que envolvem validação de erros (como ausência de campos obrigatórios — HTTP 400) não puderam ser executados via Swagger, pois a ferramenta aplica validação prévia do schema e impede o envio de requisições incompletas.

Por esse motivo, o teste **T19 — Dados incompletos** foi executado utilizando o Postman, permitindo o envio de requisições inválidas e a correta validação das regras de negócio da API.

A coleção e o environment do Postman utilizados nos testes estão disponíveis na pasta /postman do repositório.

---

##  Licença

Este projeto é de uso acadêmico.

