# Modelagem do Domínio

O propósito desse documento é fornecer um detalhamento do Domínio da Aplicação, determinando as entidades e seus atributos, Enums, Relacionamentos entre entidades e eventuais Observações.

## Entidades

### User
- **Descrição:** Entidade que representa o Usuário Base e o Admin
- **Atributos:**
    - id
    - name
    - email
    - passwordHash
    - description
    - profileImageUrl
    - role
    - active
    - createdAt
    - updatedAt
- **Relacionamentos:**
    - 1:N -> Party (como organizador)
    - N:N -> Party (como participante, através de PartyMember)
    - 1:N -> Message
    - 1:N -> AuditLog
- **Enum Relacionado:** UserRole


### Game
- **Descrição:** Entidade que representa os jogos da ludoteca.
- **Atributos:**
    - id
    - name
    - description
    - minimumAge
    - category
    - quantity
    - available
    - createdAt
    - updatedAt
    - minPlayers
    - maxPlayers
    - minDurationMinutes
    - maxDurationMinutes
- **Relacionamentos:**
    - 1:N -> Party
- **Enum Relacionado:** - 


### Party
- **Descrição:** Entidade que representa as reservas do sistema.
- **Atributos:**
    - id
    - description
    - date
    - time
    - location
    - maxPlayers
    - status
    - createdAt
    - updatedAt
- **Relacionamentos:**
    - N:1 -> User (organizador)
    - N:1 -> Game
    - 1:N -> Message
    - 1:N -> PartyMember
- **Enum Relacionado:** PartyStatus

### PartyMember
- **Descrição:** Entidade que representa a participação de um usuário em uma party. Entidade de Associação.
- **Atributos:**
    - id
    - status
    - joinedAt
    - approvedAt
    - approvedBy
- **Relacionamentos:**
    - N:1 -> User
    - N:1 -> Party
- **Enum Relacionado:** PartyMemberStatus


### Message
- **Descrição:** Entidade que representa as mensagens do chat da party.
- **Atributos:**
    - id
    - content
    - createdAt
- **Relacionamentos:**
    - N:1 -> User
    - N:1 -> Party
- **Enum Relacionado:**  -


### AuditLog
- **Descrição:** Entidade que representa a auditoria.
- **Atributos:**
    - id
    - entity
    - entityId
    - action
    - details
    - userId - (Id do user que realizou a ação)
    - createdAt
- **Relacionamentos:**
    - N:1 -> User
- **Enum Relacionado:** AuditAction


## Entidades Técnicas

### JwtPayload
- **Descrição:** Entidade usada para autenticação
- **Atributos:**
    - userId
    - role
    - exp

### RabbitEvent
- **Descrição:** Entidade base para eventos
- **Atributos:**
    - eventId
    - eventType
    - payload
    - createdAt
## Enums

### UserRole
- **Descrição**: Define o perfil de acesso do usuário.
- **Valores**: ADMIN, USER

### PartyStatus
- **Descrição**: Define o estado de aprovação e disponibilidade da party.
- **Valores**: PENDING, APPROVED, REJECTED, CANCELLED

### PartyMemberStatus
- **Descrição**: Define o estado da solicitação ou participação do usuário em uma party.
- **Valores**: PENDING, APPROVED, REJECTED

### AuditAction
- **Descrição**: Define os tipos de ações registradas na auditoria.
- **Valores**: CREATE, UPDATE, DELETE, APPROVE, REJECT, LOGIN, LOGOUT

## Resumo Relacionamentos

### User
- 1:N -> Party (como organizador)
- N:N -> Party (como participante)
- 1:N -> Message
- 1:N -> AuditLog
### Game
- 1:N -> Party
### Party
- N:1 -> User (organizador)
- N:1 -> Game
- 1:N -> Message
- 1:N -> PartyMember
### PartyMember
- N:1 -> User
- N:1 -> Party
### Message
- N:1 -> User
- N:1 -> Party
### AuditLog
- N:1 -> User

## Observações de Modelagem

- O relacionamento entre User e Party como participante é representado por meio da entidade associativa PartyMember. 
- A entidade AuditLog utiliza uma estrutura genérica baseada em entity e entityId, evitando múltiplas chaves estrangeiras opcionais. 
- Os campos active em User e available em Game foram modelados como booleanos por representarem estados binários. 
- A restrição de que um usuário só pode organizar uma Party ativa por vez será validada na camada de serviço, e não diretamente pelo relacionamento estrutural do banco. 
- A entidade RabbitEvent representa eventos trafegados pelo RabbitMQ e não necessariamente uma tabela persistida no banco de dados. 
- A entidade JwtPayload representa a estrutura lógica do token JWT e não será persistida no banco. 