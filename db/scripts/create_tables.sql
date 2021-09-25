
-- SEQUENCE: icaa.corpus_corpus_id_seq

-- DROP SEQUENCE icaa.corpus_corpus_id_seq;

CREATE SEQUENCE icaa.corpus_corpus_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE icaa.corpus_corpus_id_seq
    OWNER TO postgres;
    
-- SEQUENCE: icaa.files_file_id_seq

-- DROP SEQUENCE icaa.files_file_id_seq;

CREATE SEQUENCE icaa.files_file_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE icaa.files_file_id_seq
    OWNER TO postgres;
    
-- SEQUENCE: icaa.users_id_seq

-- DROP SEQUENCE icaa.users_id_seq;

CREATE SEQUENCE icaa.users_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE icaa.users_id_seq
    OWNER TO postgres;
    

-- Table: icaa.corpus

-- DROP TABLE icaa.corpus;

CREATE TABLE icaa.corpus
(
    corpus_id integer NOT NULL DEFAULT nextval('icaa.corpus_corpus_id_seq'::regclass),
    corpus_name character varying(100) COLLATE pg_catalog."default",
    domain_name character varying(100) COLLATE pg_catalog."default",
    userid integer,
    created_date timestamp with time zone,
    active boolean,
    CONSTRAINT corpus_pkey PRIMARY KEY (corpus_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE icaa.corpus
    ADD COLUMN model_name character varying(100) COLLATE pg_catalog."default";

ALTER TABLE icaa.corpus
    OWNER to postgres;
	
-- Table: icaa.files

-- DROP TABLE icaa.files;

CREATE TABLE icaa.files
(
    corpus_id integer NOT NULL,
    file_id integer NOT NULL DEFAULT nextval('icaa.files_file_id_seq'::regclass),
    file_name text COLLATE pg_catalog."default",
    file_url text COLLATE pg_catalog."default",
    file_type character varying(100) COLLATE pg_catalog."default",
    active boolean,
    CONSTRAINT files_pkey PRIMARY KEY (file_id),
    CONSTRAINT corpus_fk FOREIGN KEY (corpus_id)
        REFERENCES icaa.corpus (corpus_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE icaa.files
    OWNER to postgres;

ALTER TABLE icaa.files
    ADD COLUMN paragraph_json json;

ALTER TABLE icaa.files
    DROP CONSTRAINT corpus_fk;

ALTER TABLE icaa.files
    ADD CONSTRAINT corpus_fk FOREIGN KEY (corpus_id)
        REFERENCES icaa.corpus (corpus_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE;



-- Index: fki_corpus_fk

-- DROP INDEX icaa.fki_corpus_fk;

CREATE INDEX fki_corpus_fk
    ON icaa.files USING btree
    (corpus_id)
    TABLESPACE pg_default;
	
-- Table: icaa.qna

-- DROP TABLE icaa.qna;

CREATE TABLE icaa.qna
(
    file_id integer NOT NULL,
    qna_original json,
    qna_updated json,
    created_date timestamp with time zone,
    active boolean,
    CONSTRAINT file_id_pk FOREIGN KEY (file_id)
        REFERENCES icaa.files (file_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE icaa.qna
    OWNER to postgres;
-- Column: icaa.qna.status


-- ALTER TABLE icaa.qna DROP COLUMN status;


ALTER TABLE icaa.qna
    ADD COLUMN status character varying COLLATE pg_catalog."default"; 


ALTER TABLE icaa.qna
    DROP CONSTRAINT file_id_pk;

 ALTER TABLE icaa.qna
    ADD CONSTRAINT file_id_pk FOREIGN KEY (file_id)
    REFERENCES icaa.files (file_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

-- Index: fki_file_id_pk

-- DROP INDEX icaa.fki_file_id_pk;

CREATE INDEX fki_file_id_pk
    ON icaa.qna USING btree
    (file_id)
    TABLESPACE pg_default;
	
-- Table: icaa.users

-- DROP TABLE icaa.users;

CREATE TABLE icaa.users
(
    id integer NOT NULL DEFAULT nextval('icaa.users_id_seq'::regclass),
    user_id character varying(100) COLLATE pg_catalog."default",
    password text COLLATE pg_catalog."default",
    created_date timestamp with time zone,
    active boolean,
    CONSTRAINT users_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE icaa.users
    OWNER to postgres;
-- Table: icaa.comprehension


-- DROP TABLE icaa.comprehension;

CREATE TABLE icaa.comprehension
(
    corpus_id integer NOT NULL,
    model_name text COLLATE pg_catalog."default",
    active boolean,
    CONSTRAINT comprehension_corpus_fk FOREIGN KEY (corpus_id)
        REFERENCES icaa.corpus (corpus_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


ALTER TABLE icaa.comprehension
    OWNER to postgres;

ALTER TABLE icaa.comprehension
    DROP CONSTRAINT comprehension_corpus_fk;

ALTER TABLE icaa.comprehension
    ADD CONSTRAINT comprehension_corpus_fk FOREIGN KEY (corpus_id)
        REFERENCES icaa.corpus (corpus_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE;

-- Index: fki_comprehension_corpus_fk


-- DROP INDEX icaa.fki_comprehension_corpus_fk;


CREATE INDEX fki_comprehension_corpus_fk
    ON icaa.comprehension USING btree
    (corpus_id)
    TABLESPACE pg_default;
    
ALTER TABLE icaa.users
    ADD COLUMN groups character varying (100) COLLATE pg_catalog."default";

CREATE SEQUENCE icaa.app_role_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;
    
ALTER SEQUENCE icaa.app_role_id_seq
    OWNER TO postgres;

CREATE TABLE icaa.app_roles
(
    app_role_id integer NOT NULL DEFAULT nextval('icaa.app_role_id_seq'::regclass),
    app_role_name text COLLATE pg_catalog."default",
    CONSTRAINT app_role_pkey PRIMARY KEY (app_role_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


CREATE SEQUENCE icaa.app_role_corpus_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

CREATE TABLE icaa.app_roles_corpus
(
    app_role_corpus_id integer NOT NULL DEFAULT nextval('icaa.app_role_corpus_id_seq'::regclass),
    app_role_id integer NOT NULL,
    corpus_id integer NOT NULL,
    CONSTRAINT app_roles_corpus_pkey PRIMARY KEY (app_role_corpus_id),
    CONSTRAINT app_role_fk FOREIGN KEY (app_role_id)
        REFERENCES icaa.app_roles (app_role_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT app_corpus_fk FOREIGN KEY (corpus_id)
        REFERENCES icaa.corpus (corpus_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

CREATE INDEX fki_app_role_fk
    ON icaa.app_roles_corpus USING btree
    (app_role_id)
    TABLESPACE pg_default;

CREATE INDEX fki_app_corpus_fk
    ON icaa.app_roles_corpus USING btree
    (corpus_id)
    TABLESPACE pg_default;


CREATE TABLE icaa.app_roles_users
(
    app_role_id integer NOT NULL,
    user_id integer NOT NULL,
    CONSTRAINT app_roles_user_pkey PRIMARY KEY (app_role_id, user_id),
    CONSTRAINT app_roles_user_fk FOREIGN KEY (app_role_id)
        REFERENCES icaa.app_roles (app_role_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT app_users_fk FOREIGN KEY (user_id)
        REFERENCES icaa.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

CREATE INDEX fki_app_roles_user_fk
    ON icaa.app_roles_users USING btree
    (app_role_id)
    TABLESPACE pg_default;

CREATE INDEX fki_app_users_fk
    ON icaa.app_roles_users USING btree
    (user_id)
    TABLESPACE pg_default;

ALTER TABLE icaa.users 
DROP COLUMN IF EXISTS app_role_ids;

ALTER TABLE icaa.app_roles
    ADD COLUMN created_date timestamp with time zone

ALTER TABLE icaa.app_roles_corpus
    ADD COLUMN created_date timestamp with time zone

ALTER TABLE icaa.app_roles_users
    ADD COLUMN created_date timestamp with time zone

ALTER TABLE icaa.users
    RENAME COLUMN user_id TO user_name;
