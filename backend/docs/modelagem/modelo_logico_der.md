# Modelo Lógico Der
Esse é o Modelo que representa como serão os dados no Banco de Dados.

## 1. Tabela users
- **id:** INT PK AUTO_INCREMENT
- **name:** VARCHAR(255) NOT NULL
- **email:** VARCHAR(255) UNIQUE NOT NULL
- **password_hash:** VARCHAR(255) NOT NULL
- **description:** TEXT
- **profile_image_url:** VARCHAR(255)
- **role:** ENUM('ADMIN', 'USER') NOT NULL
- **active:** TINYINT(1) DEFAULT 1
- **created_at:** TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- **updated_at:** TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

## 2. Tabela games
- **id:** INT PK AUTO_INCREMENT
- **name:** VARCHAR(255) NOT NULL
- **description:** TEXT
- **minimum_age:** INT
- **category:** VARCHAR(100)
- **quantity:** INT DEFAULT 1
- **available:** TINYINT(1) DEFAULT 1
- **min_players:** INT
- **max_players:** INT
- **min_duration_minutes:** INT
- **max_duration_minutes:** INT
- **created_at:** TIMESTAMP
- **updated_at:** TIMESTAMP

## 3. Tabela parties
- **id:** INT PK AUTO_INCREMENT
- **organizer_id:** INT FK (referencia users.id)
- **game_id:** INT FK (referencia games.id)
- **description:** TEXT
- **date:** DATE NOT NULL
- **time:** TIME NOT NULL
- **location:** VARCHAR(255)
- **max_players:** INT NOT NULL
- **status:** ENUM('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED') DEFAULT 'PENDING'
- **created_at:** TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- **updated_at:** TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

## 4. Tabela party_members (N:N entre User e Party)
- **id:** INT PK AUTO_INCREMENT
- **user_id:** INT FK (users.id)
- **party_id:** INT FK (parties.id)
- **status:** ENUM('PENDING', 'APPROVED', 'REJECTED')
- **approved_by:** INT FK (users.id) -- Opcional
- **joined_at:** TIMESTAMP
- **approved_at:** TIMESTAMP

## 5. Tabela messages
- **id:** INT PK AUTO_INCREMENT
- **party_id:** INT FK (parties.id)
- **user_id:** INT FK (users.id)
- **content:** TEXT NOT NULL
- **created_at:** TIMESTAMP

## 6. Tabela audit_logs
- **id:** INT PK AUTO_INCREMENT
- **user_id:** INT FK (users.id)
- **entity:** VARCHAR(50) -- Ex: 'PARTY', 'USER'
- **entity_id:** INT
- **action:** VARCHAR(50) -- Ex: 'CREATE', 'UPDATE'
- **details:** JSON -- Para armazenar o payload ou mudanças
- **created_at:** TIMESTAMP