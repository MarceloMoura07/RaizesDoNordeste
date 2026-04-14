# API Raízes do Nordeste

##  Descrição

API REST desenvolvida em Flask para gerenciamento de unidades, produtos, pedidos e usuários, incluindo autenticação via JWT e regras de negócio como desconto e programa de fidelidade.

O projeto simula um sistema de pedidos com múltiplas entidades e operações típicas de um backend moderno.

---

##  Tecnologias utilizadas

* Python
* Flask
* Flask-SQLAlchemy
* Flask-JWT-Extended
* SQLite
* Flask-Bcrypt

---

##  Como executar o projeto

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
O que está disponível:
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

##  Estrutura do projeto

```
app/
│
├── api/                # Rotas (controllers)
├── domain/             # Modelos e regras de negócio
├── infrastructure/     # Configuração e banco de dados
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

##  Regras de negócio implementadas

* Desconto de 10% para pedidos feitos via **app**
* Controle de estoque por produto
* Validação de vínculo produto/unidade
* Fluxo de status de pedidos controlado
* Programa de fidelidade:

  * 1 ponto a cada R$10 gastos
  * Resgate em múltiplos de 10 pontos

---

##  Testes

Os testes serão realizados manualmente via ferramentas como:

* Swagger (Flasgger)
* Postman

(Detalhamento será incluído na versão final do projeto)

---

##  Licença

Este projeto é de uso acadêmico.

