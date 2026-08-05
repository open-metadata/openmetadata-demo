CREATE DATABASE metabaseappdb;

CREATE USER openmetadata_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE postgres TO openmetadata_user;

CREATE EXTENSION pg_stat_statements;
GRANT pg_read_all_stats TO openmetadata_user;

CREATE SEQUENCE public.actor_actor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE public.actor_actor_id_seq OWNER TO openmetadata_user;

CREATE TABLE public.actor (
  actor_id integer DEFAULT nextval('public.actor_actor_id_seq'::regclass) NOT NULL,
  first_name text NOT NULL,
  last_name text NOT NULL,
  last_update timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE public.actor OWNER TO openmetadata_user;

CREATE TABLE public.bad_actor (
  actor_id integer NOT NULL,
  last_update timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE public.bad_actor OWNER TO openmetadata_user;

CREATE TABLE public.film_actor (
   actor_id integer NOT NULL,
   film_id integer NOT NULL,
   last_update timestamp with time zone DEFAULT now() NOT NULL
);

CREATE VIEW public.actor_view AS
  SELECT actor_id, first_name, last_name, last_update
  FROM public.actor;

ALTER TABLE public.film_actor OWNER TO openmetadata_user;

ALTER TABLE ONLY public.actor
    ADD CONSTRAINT actor_pkey PRIMARY KEY (actor_id);


ALTER TABLE ONLY public.film_actor
    ADD CONSTRAINT film_actor_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.actor(actor_id) ON UPDATE CASCADE ON DELETE RESTRICT;

CREATE SEQUENCE public.sensitive_customers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE public.sensitive_customers_id_seq OWNER TO openmetadata_user;

CREATE TABLE public.sensitive_customers (
    customer_id integer DEFAULT nextval('public.actor_actor_id_seq'::regclass) NOT NULL,
    user_name VARCHAR(50),
    SSN VARCHAR(50),
    address VARCHAR(50),
    DWH_X10 VARCHAR(50)
);

insert into public.sensitive_customers (user_name, SSN, address, DWH_X10) values
('Harsha', NULL, '2240 W Ina Rd', 'harsha@gmail.com'),
('Suresh', NULL, '7192 Kalanianaole Hwy', 'suresh@gmail.com'),
('Sanket', NULL, '5900 N Cannon Ave', 'sanket@gmail.com'),
('Mayur', NULL, '4350 Main St', 'mayur@gmail.com'),
('Teddy', NULL, '903 W Main St', 'teddy@gmail.com'),
('Akash', NULL, '2220 Coit Rd', 'akash@gmail.com'),
('Shilpa', NULL, '7 Southside Dr', 'shilpa@gmail.com'),
('Chirag', NULL, '2929 S 25th Ave', 'chirag@gmail.com');

ALTER TABLE public.sensitive_customers OWNER TO openmetadata_user;


INSERT INTO public.actor VALUES (1, 'PENELOPE', 'GUINESS', '2022-02-15 09:34:33+00');
INSERT INTO public.actor VALUES (2, 'NICK', 'WAHLBERG', '2022-02-15 09:34:33+00');
INSERT INTO public.actor VALUES (3, 'ED', 'CHASE', '2022-02-15 09:34:33+00');
INSERT INTO public.actor VALUES (4, 'JENNIFER', 'DAVIS', '2022-02-15 09:34:33+00');
INSERT INTO public.actor VALUES (5, 'JOHNNY', 'LOLLOBRIGIDA', '2022-02-15 09:34:33+00');
INSERT INTO public.actor VALUES (6, 'BETTE', 'NICHOLSON', '2022-02-15 09:34:33+00');
INSERT INTO public.actor VALUES (7, 'GRACE', 'MOSTEL', '2022-02-15 09:34:33+00');
INSERT INTO public.actor VALUES (8, 'MATTHEW', 'JOHANSSON', '2022-02-15 09:34:33+00');
INSERT INTO public.actor VALUES (9, 'JOE', 'SWANK', '2022-02-15 09:34:33+00');
INSERT INTO public.actor VALUES (10, 'CHRISTIAN', 'GABLE', '2022-02-15 09:34:33+00');

INSERT INTO public.film_actor VALUES (1, 1, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 23, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 25, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 106, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 140, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 166, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 277, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 361, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 438, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 499, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 506, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 509, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 605, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 635, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 749, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 832, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 939, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 970, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (1, 980, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 3, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 31, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 47, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 105, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 132, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 145, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 226, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 249, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 314, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 321, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 357, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 369, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 399, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 458, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 481, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 485, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 518, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 540, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 550, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 555, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 561, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 742, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 754, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 811, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (2, 958, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 17, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 40, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 42, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 87, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 111, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 185, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 289, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 329, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 336, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 341, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 393, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 441, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 453, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 480, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 539, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 618, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 685, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 827, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 966, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 967, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 971, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (3, 996, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 23, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 25, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 56, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 62, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 79, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 87, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 355, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 379, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 398, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 463, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 490, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 616, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 635, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 691, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 712, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 714, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 721, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 798, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 832, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 858, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 909, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (4, 924, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 19, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 54, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 85, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 146, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 171, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 172, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 202, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 203, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 286, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 288, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 316, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 340, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 369, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 375, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 383, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 392, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 411, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 503, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 535, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 571, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 650, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 665, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 687, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 730, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 732, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 811, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 817, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 841, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (5, 865, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 29, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 53, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 60, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 70, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 112, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 164, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 165, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 193, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 256, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 451, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 503, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 509, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 517, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 519, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 605, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 692, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 826, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 892, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 902, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (6, 994, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 25, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 27, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 35, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 67, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 96, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 170, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 173, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 217, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 218, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 225, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 292, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 351, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 414, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 463, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 554, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 618, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 633, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 637, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 691, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 758, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 766, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 770, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 805, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 806, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 846, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 900, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 901, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 910, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 957, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (7, 959, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 47, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 115, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 158, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 179, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 195, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 205, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 255, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 263, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 321, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 396, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 458, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 523, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 532, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 554, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 752, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 769, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 771, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 859, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 895, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (8, 936, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 30, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 74, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 147, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 148, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 191, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 200, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 204, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 434, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 510, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 514, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 552, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 650, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 671, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 697, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 722, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 752, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 811, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 815, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 865, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 873, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 889, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 903, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 926, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 964, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (9, 974, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 1, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 9, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 191, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 236, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 251, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 366, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 477, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 480, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 522, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 530, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 587, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 694, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 703, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 716, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 782, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 914, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 929, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 930, '2022-02-15 10:05:03+00');
INSERT INTO public.film_actor VALUES (10, 964, '2022-02-15 10:05:03+00');

COMMIT;

