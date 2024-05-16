create user replicator with replication encrypted password 'replicator_password';
select pg_create_physical_replication_slot('replication_slot');

CREATE TABLE mails_s (id  SERIAL PRIMARY KEY, mails_s text);
CREATE TABLE phone_num (id  SERIAL PRIMARY KEY, phone_num VARCHAR(100));
