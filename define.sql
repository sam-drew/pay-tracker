DROP DATABASE IF EXISTS payTracker;

CREATE DATABASE payTracker
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE payTracker;

CREATE TABLE users
    (
        ID INT NOT NULL AUTO_INCREMENT,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(60) NOT NULL,
        salt VARCHAR(29) NOT NULL,
        PRIMARY KEY (ID)
    );

CREATE TABLE shifts
    (
        ID INT NOT NULL AUTO_INCREMENT,
        startTime DATETIME NOT NULL,
        endTime DATETIME NOT NULL,
        pay DECIMAL(6, 3) NOT NULL,
        userID INT NOT NULL,
        PRIMARY KEY (ID),
        FOREIGN KEY (userID) REFERENCES users(ID)
    );
