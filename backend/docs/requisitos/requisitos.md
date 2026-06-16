# Documento de Requisitos e Regras de Negócios

O propósito desse documento é fornecer um detalhamento dos Atores do Sistema, Casos de Uso, Matriz de Permissões, Requisitos, Regras de Negócios e Eventos Assincronos presentes no RabbitMQ.

# 1. Requisitos
## 1.1 Requisitos Funcionais

### RF01 - CADASTRO
- **Descrição:** O sistema deve permitir o cadastro independente de usuários, contendo obrigatoriamente os campos: nome, email e senha. Deve estar de acordo com [RN01](#rn01---cadastro-único-de-usuário) e [RN03](#rn03---tamanho-mínimo-senha)

### RF02 - LOGIN
- **Descrição:** O sistema deve permitir o login de um usuário cadastrado e ativos, contendo obrigatoriamente os campos: email e senha. Deve estar em conformidade com [RN02](#rn02---usuário-inativo)

### RF03 - LOGOUT
- **Descrição:** O sistema deve permitir o logout de um usuário autenticado.

### RF04 - EDIÇÃO PERFIL
- **Descrição:** O sistema deve permitir que um usuário mude suas informações de perfil, sendo elas: Foto de perfil, nome e descrição. 

### RF05 - EXIBIÇÃO JOGOS 
- **Descrição:** O sistema deve exibir os jogos presentes na plataforma na home.

### RF06 - EXIBIÇÃO DETALHES JOGO
- **Descrição:** O sistema deve permitir que um usuário veja informações detalhadas sobre um jogo específico.

### RF07 - BUSCA DETALHADA JOGO
- **Descrição:** O sistema deve permitir que um usuário busque pelos jogos por: nome, categoria ou faixa etária. 

### RF08 - SOLICITAR RESERVA JOGO "PARTY"
- **Descrição:** O sistema deve permitir um sistema de reservas de jogos, chamada de "party". Deve-se preencher obrigatoriamente: Jogo, Data, Hora, Local, Número de jogadores, Descrição. Deve estar em conformidade com [RN09](#rn09---restrição-reserva-de-jogo-repetido), [RN10](#rn10---restrição-reserva-de-jogo-simultâneo), [RN11](#rn11---restrição-reserva-de-jogo-disponivel), [RN12](#rn12---restrição-reserva-de-jogo-quantidade), [RN18](#rn18---fluxo-de-aprovação-party)

### RF09 - EDITAR INFORMAÇÕES PARTY
- **Descrição:** O sistema deve permitir que usuários modifiquem as informações da party em comformidade com [RN21](#rn21---modificação-de-informações-party).

### RF10 - VISUALIZAR PARTIES - MINHAS
- **Descrição:** O sistema deve permitir que um usuário verifique quais parties ele faz parte.

### RF11 - VISUALIZAR PARTIES - DISPONIVEIS
- **Descrição:**  O sistema deve permitir que o usuário verifique todas as parties disponiveis na plataforma.

### RF12 - VISUALIZAR SOLICITAÇÕES ENTRADA
- **Descrição:** O sistema deve permitir que um usuário que organizou uma party verifique todas as solicitações de entrada para a party que administra.

### RF13 - VISUALIZAR DETALHE PARTY
- **Descrição:** O sistema deve permitir que o usuário verifique informações detalhadas de uma party.

### RF14 - CANCELAR PARTY
- **Descrição:** O sistema deve permitir que um usuário cancele uma party da qual ele é o organizador.

### RF15 - SOLICITAR ENTRAR PARTY
- **Descrição:** O sistema deve permitir que um usuário solicite a participação em uma party. Sujeito as restrições impostas em: [RN13](#rn13---restrição-entrada-conflito-de-horários), [RN14](#rn14---restrição-aprovação-conflito-de-horários)

### RF16 - CHAT NA RESERVA
- **Descrição:** O sistema deve possuir um chat próprio para cada party. Sujeito as restrições em [RN17](#rn17---restrição-de-mensagens)

### RF17 - APROVAR/REJEITAR MEMBROS PARTY
- **Descrição:** O organizador de cada party pode APROVAR ou REJEITAR solicitações de entrada em uma party que administra. Sujeito as restrições presentes em [RN14](#rn14---restrição-aprovação-conflito-de-horários) e [RN15](#rn15---usuarios-máximos-em-party)

### RF18 - REMOVER MEMBROS PARTY
- **Descrição:** O organizador pode remover membros que estão presentes em uma party.

### RF19 - SAIR PARTY
- **Descrição:** O usuário poderá sair de uma party. Se ele for o organizador, seguirá o processo descrito em [RN08](#rn08---usuário-inativoremovido-novo-organizador). Caso o organizador seja o último meembro da party, a party será removida

### RF20 - DASHBOARD ADMIN
- **Descrição:** O sistema deverá exibir na home do administrador um dashbord com informações relativas ao estado do sistema.

### RF21 - CRIAÇÃO DE JOGO
- **Descrição:** O sistema deve permitir ao admin criar novos jogos, em comformidade com [RN04](#rn04---cadastro-único-de-jogo).

### RF22 - EDIÇÃO DE JOGO
- **Descrição:** O sistema deve permitir ao admin editar jogos existentes, em comformidade com [RN04](#rn04---cadastro-único-de-jogo).

### RF23 - EXCLUSÃO DE JOGO
- **Descrição:** O sistema deve permitir ao admin deletar jogos existentes, possivelmente ocasionando [RN06](#rn06---deleção-party-jogo-removido).

### RF24 - MODIFICAR DISPONIBILIDADE JOGO
- **Descrição:** O sistema deve permitir ao admin modificar a disponibilidade de jogos existentes, possivelmente ocasionando [RN07](#rn07---deleção-party-jogo-indisponivel).

### RF25 - CRIAÇÃO DE USUÁRIO
- **Descrição:** O sistema deve permitir ao admin criar novos usuários e admins, em comformidade com [RN01](#rn01---cadastro-único-de-usuário).

### RF26 - EDIÇÃO DE USUÁRIO
- **Descrição:** O sistema deve permitir ao admin editar usuários existentes, em comformidade com [RN01](#rn01---cadastro-único-de-usuário).

### RF27 - EXCLUSÃO DE USUÁRIO
- **Descrição:** O sistema deve permitir ao admin deletar usuários existentes, possivelmente ocasionando [RN08](#rn08---usuário-inativoremovido-novo-organizador). Necessita estar em comformidade com [RN22](#rn22---existencia-admin)

### RF28 - DESATIVAR USUÁRIO
- **Descrição:** O sistema deve permitir ao admin ativar e desativar usuários existentes, possivelmente ocasionando [RN08](#rn08---usuário-inativoremovido-novo-organizador).

### RF29 - GERENCIAMENTO DE PARTIES ADMIN
- **Descrição:** O sistema deve permitir ao admin visualizar todas as parties e seus detalhes existentes, divididas por estado de aprovação.

### RF30 - VISUALIZAÇÃO CHAT PARTIES ADMIN
- **Descrição:** O sistema deve permitir ao admin visualizar os chats de todas as parties.

### RF31 - APROVAR/REJEITAR PARTIES ADMIN
- **Descrição:** O sistema deve permitir ao admin APROVAR ou REJEITAR parties. [RN18](#rn18---fluxo-de-aprovação-party)

### RF32 - EXCLUSÃO PARTY REJEITADA MANUAL
- **Descrição:** O sistema deve permitir ao admin excluir parties que foram rejeitadas.

### RF33 - EXCLUSÃO PARTY REJEITADA AUTOMATICA
- **Descrição:** O sistema excluir automaticamente parties rejeitadas em acordo com [RN20](#rn20---exclusão-automatica-party-90-dias)

## 1.2 Requisitos Não Funcionais

### RNF01 - FRAMEWORK
- **Descrição:** O sistema deve ser desenvolvido utilizando Python, FastAPI e Uvicorn.

### RNF02 - PERSISTÊNCIA
- **Descrição:** O sistema deve utilizar MySQL como banco de dados principal.

### RNF03 - AUTENTICAÇÃO
- **Descrição:** O sistema deve utilizar autenticação baseada em JWT.

### RNF04 - CONTAINERIZAÇÃO
- **Descrição:** Todos os componentes do sistema devem ser executados através de Docker Compose.

### RNF05 - COMUNICAÇÃO ASSINCRONA
- **Descrição:** O sistema deve utilizar RabbitMQ para comunicação assíncrona entre componentes.

### RNF06 - OBSERVABILIDADE
- **Descrição:** O sistema deve expor métricas compatíveis com Prometheus.

### RNF07 - MONITORAMENTO
- **Descrição:** O sistema deve possuir dashboards Grafana para visualização das métricas.

### RNF08 - ARQUITETURA
- **Descrição:** O sistema deve utilizar arquitetura monolítica modular dividida nas camadas: Apresentação, Negócios e Dados.

### RNF09 - POA
- **Descrição:** O sistema deve implementar programação orientada a Aspectos para Logging e Authorization

### RNF10 - PADRÕES DE PROJETO
- **Descrição:** O sistema deve implementar no mínimo 5(cinco) padrões de projeto.

### RNF11 - DOCUMENTAÇÃO
- **Descrição:** O sistema deve possuir documentação técnica contendo no mínimo: Arquitetura, Requisitos, Diagramas, Regras de Negócios e Instruções de Execução.

### RNF12 - API REST
- **Descrição:** Todas as funcionalidades devem ser expostas através de API REST.

### RNF13 - VALIDAÇÃO
- **Descrição:** Os dados recebidos pela API devem ser validados através de DTOs implementados com Pydantic.

### RNF14 - AUDITORIA
- **Descrição:** O sistema deve registrar eventos de auditoria para operações relevantes.

### RNF15 - DISPONIBILIDADE
- **Descrição:** Falhas na fila RabbitMQ não devem comprometer a execução das operações principais do sistema.

### RNF16 - OBSERVABILIDADE DE NEGÓCIO
- **Descrição:** O sistema deve disponibilizar métricas de negócio para monitoramento administrativo.

# 2. Atores do Sistema
Para os fins desse documento, serão utilizadas essas definições para os Atores:

|Nome|Sigla|Descrição|
|:-:|:-:|:-:|
|Admin|A|Responsavel pela gestão da ludoteca, moderação e aprovação|
|Usuário Base(Aluno)|B|Consumidor do catálogo, organizador de parties e interação com outros usuarios|
|Ambos <br> (Base + Admin)|AB|A junção dos dois atores acima|

# 3. Matriz de Permissões

|Recurso|Ação|Perfil|
|:--|:--|:-:|
|Usuário|Criar conta própria                        |**B**|
||Editar perfil próprio                             |**AB**|
||Ver perfil alheio                                 |**AB**|
||Editar perfil alheio                              |**A**|
||Listar todos usuários                             |**A**|
||Criar outro usuário                               |**A**|
||Inativar/Ativar usuário                           |**A**|
|Jogos|Listar Catalogo                              |**AB**|
||Ver Detalhes Jogo                                 |**AB**|
||Criar Jogo                                        |**A**|
||Editar Jogo                                       |**A**|
||Bloquear/Desbloquear Jogo                         |**A**|
||Deletar Jogo                                      |**A**|
|Parties|Criar Party                                |**B**|
||Listar Parties                                    |**AB**|
||Ver Detalhes Party                                |**AB**|
||Sair da Party                                     |**B**|
||Aprovar/Rejeitar Party                            |**A**|
|Membros|Solicitar entrada party                    |**B**|
||Ver interessados na party                         |**B**|
||Aprovar/Rejeitar novo membro (Sendo Organizador)  |**B**|
|Mensagens|Enviar Mensagem(Sendo Participante)      |**B**|
||Ver Histórico                                     |**AB**|
|Sistema|Ver Métricas(Dash)                         |**A**|
||Ver Logs de Auditoria                             |**A**|

# 4. Casos de Uso

### UC01 - REALIZAR CADASTRO
- **Atores:** Usuário Base
- **Pré-condições:** Usuário não possui cadastro no sistema.
- **Fluxo Principal:** 
    1. O usuário acessa a tela de cadastro.
    1. O usuário informa nome, e-mail e senha.
    1. O sistema valida os dados informados.
    1. O sistema verifica RN01 e RN03.
    1. O sistema cria o usuário.
    1. O sistema registra o evento de auditoria.
- **Pós-condições:** Usuário cadastrado com sucesso.
- **Requisitos Relacionados:** [RF01](#rf01---cadastro)
- **Regras de Negócio Relacionados:** [RN01](#rn01---cadastro-único-de-usuário), [RN03](#rn03---tamanho-mínimo-senha), [RN19](#rn19---auditoria-automática)

### UC02 - REALIZAR LOGIN
- **Atores:** Usuário Base + Admin
- **Pré-condições:** Usuario cadastrado e ativo.
- **Fluxo Principal:** 
    1. O usuário informa e-mail e senha.
    1. O sistema valida as credenciais.
    1. O sistema verifica RN02.
    1. O sistema gera um token JWT.
    1. O sistema retorna o token.
- **Pós-condições:** Usuario autenticado.
- **Requisitos Relacionados:** [RF02](#rf02---login)
- **Regras de Negócio Relacionados:** [RN02](#rn02---usuário-inativo)


### UC03 - CRIAR PARTY
- **Atores:** Usuário Base
- **Pré-condições:** Usuário autenticado.
- **Fluxo Principal:** 
    1. O usuário seleciona um jogo.
    1. O usuário informa data, hora, local, descrição e quantidade máxima de jogadores.
    1. O sistema verifica RN09.
    1. O sistema verifica RN10.
    1. O sistema verifica RN11.
    1. O sistema verifica RN12.
    1. O sistema cria a party.
    1. O sistema define status PENDENTE.
    1. O sistema registra auditoria.
- **Pós-condições:** Party criada com status PENDENTE.
- **Requisitos Relacionados:** [RF08](#rf08---solicitar-reserva-jogo-party)
- **Regras de Negócio Relacionados:** [RN09](#rn09---restrição-reserva-de-jogo-repetido), [RN10](#rn10---restrição-reserva-de-jogo-simultâneo), [RN11](#rn11---restrição-reserva-de-jogo-disponivel), [RN12](#rn12---restrição-reserva-de-jogo-quantidade), [RN18](#rn18---fluxo-de-aprovação-party), [RN19](#rn19---auditoria-automática)


### UC04 - APROVAR OU REJEITAR PARTY
- **Atores:** Admin
- **Pré-condições:** Party em estado PENDENTE.
- **Fluxo Principal:** 
    1. O administrador visualiza parties pendentes.
    1. O administrador seleciona uma party.
    1. O administrador escolhe APROVAR ou REJEITAR.
    1. O sistema atualiza o status.
    1. O sistema registra auditoria.
- **Pós-condições:** Party em estado APROVADA ou REJEITADA.
- **Requisitos Relacionados:** [RF31](#rf31---aprovarrejeitar-parties-admin)
- **Regras de Negócio Relacionados:** [RN18](#rn18---fluxo-de-aprovação-party), [RN19](#rn19---auditoria-automática)


### UC05 - SOLICITAR ENTRADA EM PARTY
- **Atores:** Usuário Base
- **Pré-condições:** Party em estado APROVADA.
- **Fluxo Principal:** 
    1. O usuário acessa uma party.
    1. O usuário solicita participação.
    1. O sistema verifica RN13.
    1. O sistema verifica RN16.
    1. O sistema registra a solicitação.
- **Pós-condições:** Solicitação criada com estado PENDENTE
- **Requisitos Relacionados:** [RF15](#rf15---solicitar-entrar-party)
- **Regras de Negócio Relacionados:** [RN13](#rn13---restrição-entrada-conflito-de-horários), [RN16](#rn16---solicitação-única-para-determinada-party)


### UC06 - APROVAR OU REJEITAR PARTICIPANTE
- **Atores:** Usuário Base
- **Pré-condições:** Existe uma solicitação com estado PENDENTE.
- **Fluxo Principal:** 
    1. O organizador visualiza as solicitações.
    1. O organizador seleciona uma solicitação.
    1. O sistema verifica RN14.
    1. O sistema verifica RN15.
    1. O sistema aprova ou rejeita a solicitação.
    1. O sistema registra auditoria.
- **Pós-condições:** Solicitação com estado APROVADA ou REJEITADA.
- **Requisitos Relacionados:** [RF17](#rf17---aprovarrejeitar-membros-party)
- **Regras de Negócio Relacionados:** [RN14](#rn14---restrição-aprovação-conflito-de-horários), [RN15](#rn15---usuarios-máximos-em-party), [RN19](#rn19---auditoria-automática)


### UC07 - UTILIZAR CHAT DA PARTY
- **Atores:** Usuário Base
- **Pré-condições:** Usuário com estado APROVADO na party.
- **Fluxo Principal:** 
    1. O usuário acessa o chat.
    1. O usuário envia uma mensagem.
    1. O sistema verifica RN17.
    1. O sistema registra a mensagem.
    1. O sistema registra auditoria.
- **Pós-condições:** Mensagem enviada.
- **Requisitos Relacionados:** [RF16](#rf16---chat-na-reserva)
- **Regras de Negócio Relacionados:** [RN17](#rn17---restrição-de-mensagens), [RN19](#rn19---auditoria-automática)


### UC08 - GERENCIAMENTO JOGOS
- **Atores:** Admin
- **Pré-condições:** Nenhuma
- **Fluxo Principal:** 
    1. O administrador cria, altera ou remove um jogo.
    1. O sistema verifica RN04.
    1. O sistema atualiza os dados.
    1. O sistema registra auditoria.
- **Pós-condições:** Catálogo atualizado.
- **Requisitos Relacionados:** [RF21](#rf21---criação-de-jogo), [RF22](#rf22---edição-de-jogo), [RF23](#rf23---exclusão-de-jogo), [RF24](#rf24---modificar-disponibilidade-jogo)
- **Regras de Negócio Relacionados:** [RN04](#rn04---cadastro-único-de-jogo), [RN05](#rn05---bloqueio-administrativo-de-jogos), [RN06](#rn06---deleção-party-jogo-removido), [RN07](#rn07---deleção-party-jogo-indisponivel), [RN19](#rn19---auditoria-automática)


### UC09 - GERENCIAMENTO USUARIOS
- **Atores:** Admin
- **Pré-condições:** Nenhuma
- **Fluxo Principal:** 
    1. O administrador cria, altera, ativa, desativa ou remove usuários.
    1. O sistema verifica RN22.
    1. O sistema atualiza os dados.
    1. O sistema registra auditoria.
- **Pós-condições:** Usuários atualizados.
- **Requisitos Relacionados:** [RF25](#rf25---criação-de-usuário), [RF26](#rf26---edição-de-usuário), [RF27](#rf27---exclusão-de-usuário), [RF28](#rf28---desativar-usuário)
- **Regras de Negócio Relacionados:** [RN19](#rn19---auditoria-automática), [RN22](#rn22---existencia-admin)


### UC10 - CONSULTAR DASHBOARD ADMINISTRATIVO
- **Atores:** Admin
- **Pré-condições:** Usuário autenticado como administrador.
- **Fluxo Principal:** 
    1. O administrador acessa o dashboard.
    1. O sistema consulta métricas.
    1. O sistema exibe informações agregadas.
- **Pós-condições:** Métricas visualizadas.
- **Requisitos Relacionados:** [RF20](#rf20---dashboard-admin), [RNF06](#rnf06---observabilidade), [RNF07](#rnf07---monitoramento), [RNF16](#rnf16---observabilidade-de-negócio)
- **Regras de Negócio Relacionados:** - 



# 5. Regras de Negócio

### RN01 - CADASTRO ÚNICO DE USUÁRIO
- **Descrição:** Não podem existir dois usuários com o mesmo e-mail no sistema.
- **Justificativa:** Garantir a integridade da autenticação.
- **Referência:** [RF01](#rf01---cadastro)

### RN02 - USUÁRIO INATIVO
- **Descrição:** Um usuário só poderá acessar o sistema se ele estiver ativo.
- **Justificativa:** Assegurar moderação administrativa.
- **Referência:** [RF02](#rf02---login)

### RN03 - TAMANHO MÍNIMO SENHA
- **Descrição:** A senha deve possuir um tamanho mínimo de 8 caracteres, podendo estes serem letras maiuscular, minusculas, números ou simbolos.
- **Justificativa:** Garantir um nível mínimo de proteção.
- **Referência:** [RF01](#rf01---cadastro)

### RN04 - CADASTRO ÚNICO DE JOGO
- **Descrição:** Não pode existir dois jogos com o mesmo nome no sistema.
- **Justificativa:** Garantir a integridade da busca.
- **Referência:** [RF23](#rf21---criação-de-jogo), [RF24](#rf22---edição-de-jogo)

### RN05 - BLOQUEIO ADMINISTRATIVO DE JOGOS
- **Descrição:** O Admin pode bloquear a reserva de jogos específicos.
- **Justificativa:** Permitir controle administrativo sobre a disponibilidade.
- **Referência:** [RF26](#rf24---modificar-disponibilidade-jogo)

### RN06 - DELEÇÃO PARTY JOGO REMOVIDO
- **Descrição:** Caso o jogo reservado por uma party seja deletado, a party será automaticamente CANCELADA.
- **Justificativa:** Não poderá haver reserva de jogo inexistente.
- **Referência:** [RF25](#rf23---exclusão-de-jogo)

### RN07 - DELEÇÃO PARTY JOGO INDISPONIVEL
- **Descrição:** Caso o jogo reservado por uma party seja indisponibilizado, a party será automaticamente CANCELADA.
- **Justificativa:** Não poderá haver reserva de jogo indisponivel.
- **Referência:** [RF26](#rf24---modificar-disponibilidade-jogo)

### RN08 - USUÁRIO INATIVO/REMOVIDO NOVO ORGANIZADOR
- **Descrição:** Caso o organizador de uma party seja inativado, deletado ou saia de uma party, o novo organizador será o membro mais velho presente na party que não seja um organizador de outra party. Se não existir nenhum membro que satisfaça essa condição, a party será deletada.
- **Justificativa:** Definição de ordem de sucessão. 
- **Referência:** [RF21](#rf19---sair-party), [RF29](#rf27---exclusão-de-usuário), [RF30](#rf28---desativar-usuário)

### RN09 - RESTRIÇÃO RESERVA DE JOGO REPETIDO
- **Descrição:** Um usuário não pode reservar o mesmo jogo mais de uma vez ao mesmo tempo.
- **Justificativa:** Evitar o monopólio de um determinado jogo por um jogador.
- **Referência:** [RF09](#rf08---solicitar-reserva-jogo-party)

### RN10 - RESTRIÇÃO RESERVA DE JOGO SIMULTÂNEO
- **Descrição:** Um usuário não pode ser organizador de mais de uma party PENDENTE ou APROVADA simultaneamente.
- **Justificativa:** Evitar monopólio de jogos por poucos jogadores.
- **Referência:** [RF09](#rf08---solicitar-reserva-jogo-party)

### RN11 - RESTRIÇÃO RESERVA DE JOGO DISPONIVEL
- **Descrição:** Um jogo apenas pode ser reservado se estiver disponivel.
- **Justificativa:** Garantir conformidade com o controle administrativo.
- **Referência:** [RF09](#rf08---solicitar-reserva-jogo-party)

### RN12 - RESTRIÇÃO RESERVA DE JOGO QUANTIDADE
- **Descrição:** Um jogo apenas pode ser reservado se houverem copias livres dele.
- **Justificativa:** Limite físico.
- **Referência:** [RF09](#rf08---solicitar-reserva-jogo-party)

### RN13 - RESTRIÇÃO ENTRADA CONFLITO DE HORÁRIOS
- **Descrição:** Um usuário não poderá solicitar entrada em uma party caso ele já possua uma participação aprovada em outra party que ocorra no mesmo dia e horário.
- **Justificativa:** Limite físico.
- **Referência:** [RF17](#rf15---solicitar-entrar-party)

### RN14 - RESTRIÇÃO APROVAÇÃO CONFLITO DE HORÁRIOS
- **Descrição:** Um usuário não poderá ser aprovado para entrada em uma party caso ele já possua uma participação aprovada em outra party que ocorra no mesmo dia e horário.
- **Justificativa:** Limite físico.
- **Referência:** [RF19](#rf17---aprovarrejeitar-membros-party)

### RN15 - USUARIOS MÁXIMOS EM PARTY
- **Descrição:** Uma reserva não pode ter mais membros do que o limite máximo
- **Justificativa:** Garantir conformidade com a reserva e/ou regras do jogo.
- **Referência:** [RF17](#rf15---solicitar-entrar-party), [RF19](#rf17---aprovarrejeitar-membros-party)

### RN16 - SOLICITAÇÃO ÚNICA PARA DETERMINADA PARTY
- **Descrição:** Um usuário pode possuir apenas uma solicitação de entrada ativa para uma party ao mesmo tempo.
- **Justificativa:** Evitar spam e inconsistência nos dados.
- **Referência:** [RF17](#rf15---solicitar-entrar-party)

### RN17 - RESTRIÇÃO DE MENSAGENS 
- **Descrição:** Apenas usuário que foram aprovados em uma party podem enviar mensagens para o chat dela.
- **Justificativa:** Segurança e privacidade dos participantes.
- **Referência:** [RF18](#rf16---chat-na-reserva)

### RN18 - FLUXO DE APROVAÇÃO PARTY
- **Descrição:** Uma party é criada com o status de "PENDENTE" e apenas o admin poderá APROVAR ou REJEITAR.
- **Justificativa:** Controle de qualidade e segurança administrativo.
- **Referência:** [RF09](#rf08---solicitar-reserva-jogo-party), [RF33](#rf31---aprovarrejeitar-parties-admin)

### RN19 - AUDITORIA AUTOMÁTICA
- **Descrição:** Toda criação, alteração de status ou deleção de entidades deve disparar um evento para a fila de Auditoria.
- **Justificativa:** Atender ao requisito de Auditoria de Ações do Sistema.
- **Referência:** TODOS OS FLUXOS DE CRIAÇÃO, ALTERAÇÃO E EXCLUSÃO. 

### RN20 - EXCLUSÃO AUTOMATICA PARTY 90 DIAS
- **Descrição:** Caso uma party esteja com o status REJEITADA por mais de 90 dias, ela será excluida.
- **Justificativa:** Preservação de memória.
- **Referência:** [RF33](#rf31---aprovarrejeitar-parties-admin), [RF35](#rf33---exclusão-party-rejeitada-automatica)

### RN21 - MODIFICAÇÃO DE INFORMAÇÕES PARTY
- **Descrição:** As informações de Descrição, Data, Hora e Número máximo de jogadores podem ser alteradas, contanto que a party esteja em estado PENDENTE. 
- **Justificativa:** Possibilidade de correção de erros.
- **Referência:** [RF09](#rf09---editar-informações-party)

### RN22 - EXISTENCIA ADMIN
- **Descrição:** Deve existir no mínimo 1(um) admin no sistema.
- **Justificativa:** Impede a exclusão completa de admins
- **Referência:** [RF27](#rf27---exclusão-de-usuário)

# 6. Eventos RabbitMQ

### EVT01 - USER_CREATED
- **Ocorrencia**: Disparado no cadastro independente ou criação via Admin.

### EVT02 - PARTY_CREATED
- **Ocorrencia**: Disparado quando uma nova party é solicitada.

### EVT03 - PARTY_APPROVED
- **Ocorrencia**: Disparado quando o Admin valida a party.

### EVT04 - MEMBER_REQUESTED
- **Ocorrencia**: Disparado quando um aluno solicita entrar no grupo.

### EVT05 - MEMBER_APPROVED
- **Ocorrencia**: Disparado quando o organizador aceita o aluno.

### EVT06 - MESSAGE_SENT
- **Ocorrencia**: Disparado a cada nova interação no chat.

### EVT07 - AUDIT_LOG_CREATED
- **Ocorrência**: Disparado sempre que uma operação de criação, alteração ou exclusão relevante for realizada no sistema.

