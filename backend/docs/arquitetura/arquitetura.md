# 1. Visão Geral do Sistema

## Nome do Sistema: Player One

## 1.1 Objetivo:
### 1.1.1 Objetivos Geral:
O sistema da Player One é uma plataforma para gerenciamento da de uma ludoteca acadêmica, facilitando a organização dos jogos disponiveis, providenciando uma plataforma para alunos encontrarem jogadores interessados e realizarem reservas de forma organizada.

### 1.1.2 Objetivos Específicos:
- Gerenciamento de Usuario
- Gerenciamento de Jogos
- Criação e Gerenciamento de Reservas de jogos: "Parties"
- Gerenciamento de participantes de parties
- Comunicação de participantes por mensagens
- Auditoria de ações do sistema

# 2. Arquitetura Geral

## 2.1 Estilo Arquitetural

**Escolhido**: Monolítico Modular/ Monólítico com Camadas  
**Justificativa**: Apesar do modelo de micro serviços ser mais escalavel, o modelo monolítico possui um sistema mais fácil para o desenvolvimento para os requisitos do projeto, testes mais simples de criar e realizar. Além disso, a divisão em Camadas de Apresentação, Negócios e Dados possibilita: 1. Separação de responsabilidade (Single Responsibility Principle), 2. Facilitar manutenção, 3. Reutilizar código, 4. Facilidade de testes, 5. Baixo acoplamento

### 2.1.1 Camada de Apresentação
A Camada de Apresentação é a responsavel pela comunicação para o front-end, validando as requisições recebidas pelo frontend, retornando as informações requisitadas, converter entidades de domínio em DTOs e exibir a documentação OpenAPI (Feito automaticamente).

**Componentes:** No projeto, A camada de apresentação consistui pelos códigos presentes nas pastas **src/api/** e **src/schemas/**.

**Bibliotecas:** São utilizados principalmente as bibliotecas FastAPI(Criação da API em sí) e Pydantic(Validação de Dados)

Classes Consistuintes:
    [PREENCHER DEPOIS]

### 2.1.2 Camada de Negócios
A Camada de Negócios é a responsavel pela processamento em sí do backend, aplicando validações (autorizações), realizando operações, regras de negócio, implementando classes de uso, publicar eventos no RabbitMQ e Aplicar Aspectos

**Componentes:** No projeto, A camada de negócios consistui pelos códigos presentes nas pastas **src/services/**, **src/core/** e **src/internal/**.

**Bibliotecas:** São utilizados principalmente python básico, com os complementos de bibliotecas jwt e RabbitMQ [ALTERAR DEPOIS PELO NOME LIB]

Classes Consistuintes:
    [PREENCHER DEPOIS]

### 2.1.3 Camada de Dados
A Camada de Dados é a responsavel pela comunicação com o banco de dados, realizando o mapeamento de entidades e CRUD do que for requisitado.

**Componentes:** No projeto, A camada de dados consistui pelos códigos presentes nas pastas **src/repositories/**, **src/models/** e **src/database/**.

**Bibliotecas:** É utilizado principalmente a biblioteca de SQLAlchemy para a comunicação com o banco de dados MySQL

Classes Consistuintes:
    [PREENCHER DEPOIS]

## 2.2 Módulos do Sistema
Como Determinado pelo estilo arquitetural, o sistema é subdividido em Camadas. Além do mais, cada camada é subdividida em módulos que resolver processos específicos.


### 2.2.1 Módulo de Autenticação
Responsavel pela autenticação dos usuários através de JWT e fornecimento de informações para autorização.

**Entidades Relacionadas:** Usuário

### 2.2.2 Módulo de Usuários
Responsavel pelo fluxo que envolve os dados de usuários, sendo esses: Cadastro(Criação), consulta(Leitura), edição(Modificação), deleção(Exclusão)

**Entidades Relacionadas:** Usuário

### 2.2.3 Módulo de Jogos
Responsavel pelo fluxo que envolveo os dados de jogos, sendo esses: Cadastro(Criação), consulta(Leitura), edição(Modificação), deleção(Exclusão) e em especial o bloqueio administrativo do jogo

**Entidades Relacionadas:** Jogos

### 2.2.4 Módulo de Parties

Responsavel pelo fluxo que envolve os dados das parties e seus constituintes, sendo: Criação, Aprovação, Gerenciamento e Validação 

**Entidades Relacionadas:** Party, Usuario_has_Party

### 2.2.5 Módulo de Mensagem
Responsavel pelas mensagens presentes no chat de uma party: Envio de mensagens, consulta de histórico

**Entidades Relacionadas:** Mensagem

### 2.2.6 Módulo de Auditoria
Responsável pelo registro de eventos relevantes do sistema, permitindo rastreabilidade, auditoria e análise posterior das ações realizadas pelos usuários.

**Entidades Relacionadas:** Usuarios, Jogos, Party, Usuario_has_Party, Mensagem

## 2.3 Componentes Docker
No projeto, esses são os containers docker que serão utilizados, orquestrados pelo Docker Compose, e suas responsabilidades:
- **api:** Responsavel pelo backend da api
- **mysql:** Responsavel pela persistencia de dados
- **rabbitmq:** Responsavel pelas mensagens assincronas
- **prometheus:** Responsavel pela coleta de métricas
- **grafana:** Responsavel pela visualização das métricas

## 2.4 Aspectos
Para lidar com a implementação de problemas transversais originados da Autorização e permitir registros para analíse, usaremos dois Aspectos principais:

### 2.4.1 Logging Aspect
O Aspecto responsavel pelos registros do sistema, contendo: logs de entrada, logs de saida, tempos de execução e exceções

**Camada de Aplicação:** Negócios(Services)

### 2.4.2 Authorization Aspect
O Aspecto responsavel pelas verificações de autorização dentro do sistema, validando papeis de usuários e propriedades de recurso.

**Camada de Aplicação:** Negócios(Services)

## 2.5 Integrações Externas
[VALIDAR FUTURAMENTE]
### RabbitMQ

Utilizado para comunicação assíncrona entre componentes do sistema através do padrão Publish-Subscribe.

Principais eventos:

- Party criada
- Party aprovada
- Solicitação de participação criada
- Participante aprovado
- Mensagem enviada

### Prometheus

Responsável pela coleta de métricas da aplicação.

Métricas previstas:

- Tempo de resposta
- Quantidade de requisições
- Quantidade de erros
- Quantidade de usuários autenticados

### Grafana

Responsável pela visualização das métricas coletadas pelo Prometheus através de dashboards administrativos.
