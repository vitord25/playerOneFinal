CREATE DATABASE IF NOT EXISTS ludoteca
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ludoteca;

DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS party_members;
DROP TABLE IF EXISTS parties;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    description TEXT NULL,
    profile_image_url VARCHAR(500) NULL,
    role ENUM('ADMIN', 'USER') NOT NULL DEFAULT 'USER',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NULL,
    minimum_age INT NOT NULL DEFAULT 0,
    category VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    available BOOLEAN NOT NULL DEFAULT TRUE,
    min_players INT NOT NULL,
    max_players INT NOT NULL,
    min_duration_minutes INT NOT NULL,
    max_duration_minutes INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (minimum_age >= 0),
    CHECK (quantity >= 0),
    CHECK (min_players > 0),
    CHECK (max_players >= min_players),
    CHECK (min_duration_minutes > 0),
    CHECK (max_duration_minutes >= min_duration_minutes)
);

CREATE TABLE parties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organizer_id INT NOT NULL,
    game_id INT NOT NULL,
    description TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location VARCHAR(255) NOT NULL,
    max_players INT NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED') NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (max_players > 0),
    FOREIGN KEY (organizer_id) REFERENCES users(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE party_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    party_id INT NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL,
    approved_by INT NULL,
    UNIQUE (user_id, party_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (party_id) REFERENCES parties(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    party_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (party_id) REFERENCES parties(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity VARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    action ENUM('CREATE', 'UPDATE', 'DELETE', 'APPROVE', 'REJECT', 'LOGIN', 'LOGOUT') NOT NULL,
    details JSON NULL,
    user_id INT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);