create user replicator with replication encrypted password 'replicator_password';
select pg_create_physical_replication_slot('replication_slot');

CREATE TABLE mails_s (id  SERIAL PRIMARY KEY, mails_s text);
CREATE TABLE phone_num (id  SERIAL PRIMARY KEY, phone_num VARCHAR(100));

INSERT INTO mails_s (id, mails_s) VALUES ('1', 'test1@mail.ru'),('2', 'test2@mail.ru'),('3', 'test3@mail.ru'),('4', 'test4@mail.ru'),('5', 'test5@mail.ru');
INSERT INTO phone_num(id, phone_num) VALUES ('1', '88001234567'),('2', '88001234568'),('3', '88001234569'),('4', '88001234570'),('5', '88001234571');
