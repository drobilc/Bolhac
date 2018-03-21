CREATE DATABASE bolhac;
USE bolhac;

CREATE TABLE user (
	id INT PRIMARY KEY AUTO_INCREMENT,
	email VARCHAR(255) NOT NULL,
	password VARCHAR(32) NOT NULL,
	CONSTRAINT user_email_unique UNIQUE (email)
);

CREATE TABLE search (
	id INT PRIMARY KEY AUTO_INCREMENT,
	url VARCHAR(255) NOT NULL,
	date_added DATETIME NOT NULL,
	last_search DATETIME NOT NULL
);

CREATE TABLE has_search (
	user_id INT NOT NULL,
	search_id INT NOT NULL,
	CONSTRAINT has_search_user_fk FOREIGN KEY (user_id) REFERENCES user(id),
	CONSTRAINT has_search_search_fk FOREIGN KEY (search_id) REFERENCES search(id)
);