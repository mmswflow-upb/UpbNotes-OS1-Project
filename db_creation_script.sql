-- Create the database
CREATE DATABASE UpbNotes;

-- Use the database
USE UpbNotes;

-- Create the table `notes`
CREATE TABLE notes (
    id INT(11) NOT NULL AUTO_INCREMENT,
    subject VARCHAR(200) NULL,
    note VARCHAR(600) NULL,
    file VARCHAR(1000) NULL,
    PRIMARY KEY (id)
);
