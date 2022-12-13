CREATE USER openmetadata_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE postgres TO openmetadata_user;

CREATE EXTENSION pg_stat_statements;
GRANT pg_read_all_stats TO openmetadata_user;

CREATE TABLE public.orders (
  order_id integer NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  restaurant_id integer NOT NULL,
  user_id integer NOT NULL,
  last_update timestamp with time zone
);

CREATE TABLE public.restaurants (
    restaurant_id integer NOT NULL,
    type text NOT NULL,
    rating integer,
    average_price integer,
    restaurant_address text NOT NULL
);

CREATE TABLE public.users (
    user_id integer NOT NULL,
    total_orders integer NOT NULL,
    last_order_id integer,
    premium boolean NOT NULL,
    user_address text NOT NULL
);

ALTER TABLE public.orders OWNER TO openmetadata_user;
ALTER TABLE public.restaurants OWNER TO openmetadata_user;
ALTER TABLE public.users OWNER TO openmetadata_user;

ALTER TABLE ONLY public.orders ADD CONSTRAINT order_id PRIMARY KEY (order_id);
ALTER TABLE ONLY public.restaurants ADD CONSTRAINT restaurant_id PRIMARY KEY (restaurant_id);
ALTER TABLE ONLY public.users ADD CONSTRAINT user_id PRIMARY KEY (user_id);

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT restaurant_id_fk FOREIGN KEY (restaurant_id)
    REFERENCES public.restaurants(restaurant_id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT user_id_fk FOREIGN KEY (user_id)
    REFERENCES public.users(user_id) ON UPDATE CASCADE ON DELETE RESTRICT;

COMMIT;
