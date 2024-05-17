create user replicator with replication encrypted password 'replicator_password';
select pg_create_physical_replication_slot('replication_slot');

CREATE TABLE mails_s (id  SERIAL PRIMARY KEY, mails_s text);
CREATE TABLE phone_num (id  SERIAL PRIMARY KEY, phone_num VARCHAR(100));

INSERT INTO mails_s (mails_s) VALUES ('test1@mail.ru'),('test2@mail.ru'),('test3@mail.ru'),('test4@mail.ru'),('test5@mail.ru');
INSERT INTO phone_num(phone_num) VALUES ('88001234567'),('88001234568'),('88001234569'),('88001234570'),('88001234571');
