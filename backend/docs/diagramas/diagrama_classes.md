````mermaid
classDiagram
    class User {
        +int id
        +string name
        +string email
        +string passwordHash
        +string description
        +string profileImageUrl
        +UserRole role
        +boolean active
        +datetime createdAt
        +datetime updatedAt
    }

    class Game {
        +int id
        +string name
        +string description
        +int minimumAge
        +string category
        +int quantity
        +boolean available
        +int minPlayers
        +int maxPlayers
        +int minDurationMinutes
        +int maxDurationMinutes
        +datetime createdAt
        +datetime updatedAt
    }

    class Party {
        +int id
        +string description
        +date date
        +time time
        +string location
        +int maxPlayers
        +PartyStatus status
        +datetime createdAt
        +datetime updatedAt
    }

    class PartyMember {
        +int id
        +PartyMemberStatus status
        +datetime joinedAt
        +datetime approvedAt
        +int approvedBy
    }

    class Message {
        +int id
        +string content
        +datetime createdAt
    }

    class AuditLog {
        +int id
        +string entity
        +int entityId
        +AuditAction action
        +json details
        +int userId
        +datetime createdAt
    }

    class JwtPayload {
        +int userId
        +UserRole role
        +datetime exp
    }

    class RabbitEvent {
        +string eventId
        +string eventType
        +json payload
        +datetime createdAt
    }

    class UserRole {
        <<enumeration>>
        ADMIN
        USER
    }

    class PartyStatus {
        <<enumeration>>
        PENDING
        APPROVED
        REJECTED
        CANCELLED
    }

    class PartyMemberStatus {
        <<enumeration>>
        PENDING
        APPROVED
        REJECTED
    }

    class AuditAction {
        <<enumeration>>
        CREATE
        UPDATE
        DELETE
        APPROVE
        REJECT
        LOGIN
        LOGOUT
    }

    User "1" --> "0..*" Party : organiza
    User "1" --> "0..*" PartyMember : participa via
    Party "1" --> "0..*" PartyMember : possui membros
    Game "1" --> "0..*" Party : reservado em
    User "1" --> "0..*" Message : envia
    Party "1" --> "0..*" Message : possui
    User "1" --> "0..*" AuditLog : executa ações

    User --> UserRole
    Party --> PartyStatus
    PartyMember --> PartyMemberStatus
    AuditLog --> AuditAction
````