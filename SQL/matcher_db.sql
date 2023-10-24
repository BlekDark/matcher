--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3 (Debian 15.3-1.pgdg120+1)
-- Dumped by pg_dump version 15.3 (Debian 15.3-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: matcher; Type: SCHEMA; Schema: -; Owner: user
--

CREATE SCHEMA matcher;


ALTER SCHEMA matcher OWNER TO "user";

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: configs; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.configs (
    id bigint NOT NULL,
    source_id bigint NOT NULL,
    param_id bigint NOT NULL,
    value double precision NOT NULL,
    source2_id bigint NOT NULL,
    sport_id bigint,
    updated_at timestamp without time zone,
    modified_by bigint
);


ALTER TABLE matcher.configs OWNER TO "user";

--
-- Name: configs_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

ALTER TABLE matcher.configs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME matcher.configs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: custom_matched_data; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.custom_matched_data (
    id integer NOT NULL,
    event1 jsonb,
    event2 jsonb,
    overall_similarity double precision,
    teams_similarity double precision,
    league_similarity double precision,
    sport character varying(20),
    is_cyber boolean,
    is_swapped boolean,
    is_match boolean,
    event1_id uuid,
    event2_id uuid,
    date character varying,
    mismatch boolean
);


ALTER TABLE matcher.custom_matched_data OWNER TO "user";

--
-- Name: custom_data_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

CREATE SEQUENCE matcher.custom_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE matcher.custom_data_id_seq OWNER TO "user";

--
-- Name: custom_data_id_seq; Type: SEQUENCE OWNED BY; Schema: matcher; Owner: user
--

ALTER SEQUENCE matcher.custom_data_id_seq OWNED BY matcher.custom_matched_data.id;


--
-- Name: custom_unmatched_data; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.custom_unmatched_data (
    event_id uuid NOT NULL,
    date character varying,
    event_name character varying,
    team1 character varying,
    team2 character varying,
    league_name character varying,
    sport character varying,
    is_cyber boolean
);


ALTER TABLE matcher.custom_unmatched_data OWNER TO "user";

--
-- Name: parameters; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.parameters (
    id bigint NOT NULL,
    name character varying NOT NULL,
    default_value double precision
);


ALTER TABLE matcher.parameters OWNER TO "user";

--
-- Name: parameters_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

ALTER TABLE matcher.parameters ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME matcher.parameters_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: permissions; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.permissions (
    id bigint NOT NULL,
    type text NOT NULL
);


ALTER TABLE matcher.permissions OWNER TO "user";

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

ALTER TABLE matcher.permissions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME matcher.permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: processed_data_info; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.processed_data_info (
    hash character varying,
    total_pairs_sent integer,
    correct_matches integer,
    mismatched_pairs integer,
    unmatched_results integer,
    correct_matches_percentage character varying,
    mismatched_pairs_percentage character varying,
    unmatched_pairs_percentage character varying,
    id integer NOT NULL,
    process_start timestamp without time zone,
    process_end timestamp without time zone
);


ALTER TABLE matcher.processed_data_info OWNER TO "user";

--
-- Name: processed_data_info_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

ALTER TABLE matcher.processed_data_info ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME matcher.processed_data_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: request_logs; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.request_logs (
    id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    endpoint text NOT NULL,
    processing_time real,
    parameters text,
    body text
);


ALTER TABLE matcher.request_logs OWNER TO "user";

--
-- Name: request_logs_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

CREATE SEQUENCE matcher.request_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE matcher.request_logs_id_seq OWNER TO "user";

--
-- Name: request_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: matcher; Owner: user
--

ALTER SEQUENCE matcher.request_logs_id_seq OWNED BY matcher.request_logs.id;


--
-- Name: results; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.results (
    id bigint NOT NULL,
    run_id bigint NOT NULL,
    event1 jsonb NOT NULL,
    event2 jsonb NOT NULL,
    is_match boolean,
    is_uncertain boolean,
    updated_at timestamp without time zone NOT NULL,
    modified_by bigint,
    mismatch boolean,
    overall_similarity double precision,
    teams_similarity double precision,
    league_similarity double precision,
    is_swapped boolean
);


ALTER TABLE matcher.results OWNER TO "user";

--
-- Name: results_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

ALTER TABLE matcher.results ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME matcher.results_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: runs; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.runs (
    id bigint NOT NULL,
    task_id bigint NOT NULL,
    sport_id bigint NOT NULL,
    num_matches bigint,
    status_user bigint DEFAULT 1,
    status_observer bigint DEFAULT 1,
    runtime double precision,
    source1_data jsonb,
    source2_data jsonb
);


ALTER TABLE matcher.runs OWNER TO "user";

--
-- Name: runs_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

ALTER TABLE matcher.runs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME matcher.runs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: sources; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.sources (
    id bigint NOT NULL,
    name text NOT NULL,
    url text NOT NULL
);


ALTER TABLE matcher.sources OWNER TO "user";

--
-- Name: source_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

ALTER TABLE matcher.sources ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME matcher.source_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: sport_types; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.sport_types (
    id bigint NOT NULL,
    name text NOT NULL,
    is_cyber text DEFAULT 0 NOT NULL
);


ALTER TABLE matcher.sport_types OWNER TO "user";

--
-- Name: sport_types_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

ALTER TABLE matcher.sport_types ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME matcher.sport_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: statuses; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.statuses (
    id bigint NOT NULL,
    status text NOT NULL
);


ALTER TABLE matcher.statuses OWNER TO "user";

--
-- Name: statuses_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

ALTER TABLE matcher.statuses ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME matcher.statuses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tasks; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.tasks (
    id bigint NOT NULL,
    source1_id bigint NOT NULL,
    source2_id bigint NOT NULL,
    started_at timestamp without time zone,
    finished_at timestamp without time zone,
    num_sports bigint NOT NULL,
    status_user bigint DEFAULT 1,
    status_observer bigint DEFAULT 1,
    referent_task bigint
);


ALTER TABLE matcher.tasks OWNER TO "user";

--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

ALTER TABLE matcher.tasks ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME matcher.tasks_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: matcher; Owner: user
--

CREATE TABLE matcher.users (
    id bigint NOT NULL,
    name text NOT NULL,
    permission_id bigint NOT NULL
);


ALTER TABLE matcher.users OWNER TO "user";

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: matcher; Owner: user
--

ALTER TABLE matcher.users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME matcher.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: custom_matched_data id; Type: DEFAULT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.custom_matched_data ALTER COLUMN id SET DEFAULT nextval('matcher.custom_data_id_seq'::regclass);


--
-- Name: request_logs id; Type: DEFAULT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.request_logs ALTER COLUMN id SET DEFAULT nextval('matcher.request_logs_id_seq'::regclass);


--
-- Data for Name: parameters; Type: TABLE DATA; Schema: matcher; Owner: user
--

COPY matcher.parameters (id, name, default_value) FROM stdin;
2	REMOVE_CANDIDATE_THRESHOLD	80
4	CONFIDENT_THRESHOLD	80
1	MINIMAL_SIM_THRESHOLD	39
3	FINAL_SIM_RATIO	0.9
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: matcher; Owner: user
--

COPY matcher.permissions (id, type) FROM stdin;
1	USER
2	OBSERVER
\.


--
-- Data for Name: processed_data_info; Type: TABLE DATA; Schema: matcher; Owner: user
--

COPY matcher.processed_data_info (hash, total_pairs_sent, correct_matches, mismatched_pairs, unmatched_results, correct_matches_percentage, mismatched_pairs_percentage, unmatched_pairs_percentage, id, process_start, process_end) FROM stdin;
8e58ca86ee23066f643abc6e6fc6e8a9633c8d26c76bd0db86de2c38ef0ade39	9	9	0	0	100.0%	0.0%	0.0%	6	2023-08-04 03:59:06.236756	2023-08-04 03:59:07.88873
b32cc16d73a381f07962f56ef7de09df63a934715108f3ad5935b4e03e162e42	432	356	36	8	82.41%	8.33%	1.85%	7	2023-08-04 04:00:56.492024	2023-08-04 04:02:23.745265
8d19938220fdd91de14086e670c24df091b4bbf344fd70809c9e90a15af8e6cb	6	6	0	0	100.0%	0.0%	0.0%	8	2023-08-04 01:54:51.446953	2023-08-04 01:54:51.556862
a1c14a51975e3754368384df61037c490b67f83e82e6171266f04821bbbcd35b	167326	164925	1187	54	98.57%	0.71%	0.03%	9	2023-08-04 02:16:19.343369	2023-08-04 05:03:18.888059
fb4d345dd4e4fe9b41a1bf288745773f0241b6304b9cc35e03a79ab2460dda79	167049	162152	1164	5138	97.07%	0.7%	3.08%	10	2023-08-05 12:41:34.756233	2023-08-05 14:55:02.309128
8cf5a9b99f28f8c8451035c9416aff25d314504f99f5dc24282194ad18a254f9	166535	163551	207	5140	98.21%	0.12%	3.09%	11	2023-08-05 23:55:54.716561	2023-08-06 02:09:49.861954
\.


--
-- Data for Name: sources; Type: TABLE DATA; Schema: matcher; Owner: user
--

COPY matcher.sources (id, name, url) FROM stdin;
18	olimp	http://api.oddscp.com:8111/events?token=2501efd9e9faf3de5a5d19414c302c18&bk_name=olimp
19	bet9ja	http://api.oddscp.com:8111/events?token=2501efd9e9faf3de5a5d19414c302c18&bk_name=bet9ja
20	parimatch_com	http://api.oddscp.com:8111/events?token=2501efd9e9faf3de5a5d19414c302c18&bk_name=parimatch_com
21	fonbet	http://api.oddscp.com:8111/events?token=2501efd9e9faf3de5a5d19414c302c18&bk_name=fonbet
22	1xbet	http://api.oddscp.com:8111/events?token=2501efd9e9faf3de5a5d19414c302c18&bk_name=1xbet
23	888sport	http://api.oddscp.com:8111/events?token=2501efd9e9faf3de5a5d19414c302c18&bk_name=888sport
27	test2	www.link1
16	pinnacle	http://api.oddscp.com:8111/events?token=2501efd9e9faf3de5a5d19414c302c18&bk_name=pinnacle
17	bet365	http://api.oddscp.com:8111/events?token=2501efd9e9faf3de5a5d19414c302c18&bk_name=bet365
30	stake	http://api.oddscp.com:8111/events?token=2501efd9e9faf3de5a5d19414c302c18&bk_name=stake
31	zenit	http://api.oddscp.com:8111/events?token=2501efd9e9faf3de5a5d19414c302c18&bk_name=zenit
32	betboom	http://api.oddscp.com:8111/events?token=2501efd9e9faf3de5a5d19414c302c18&bk_name=bingoboom
\.


--
-- Data for Name: sport_types; Type: TABLE DATA; Schema: matcher; Owner: user
--

COPY matcher.sport_types (id, name, is_cyber) FROM stdin;
1	soccer	0
2	baseball	0
3	basketball	0
5	futsal	0
6	handball	0
7	hockey	0
8	table-tennis	0
9	tennis	0
10	volleyball	0
12	rugby	0
13	badminton	0
15	cricket	0
16	boxing	0
17	floorball	0
4	esports.cs	1
11	esports.dota2	1
14	esports.lol	1
18	basketball	1
19	soccer	1
\.


--
-- Data for Name: statuses; Type: TABLE DATA; Schema: matcher; Owner: user
--

COPY matcher.statuses (id, status) FROM stdin;
1	NOT STARTED
2	IN PROGRESS
3	FINISHED
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: matcher; Owner: user
--

COPY matcher.users (id, name, permission_id) FROM stdin;
1	Test	1
\.


--
-- Name: configs_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.configs_id_seq', 102, true);


--
-- Name: custom_data_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.custom_data_id_seq', 163965, true);


--
-- Name: parameters_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.parameters_id_seq', 6, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.permissions_id_seq', 2, true);


--
-- Name: processed_data_info_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.processed_data_info_id_seq', 11, true);


--
-- Name: request_logs_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.request_logs_id_seq', 92, true);


--
-- Name: results_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.results_id_seq', 106666, true);


--
-- Name: runs_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.runs_id_seq', 20497, true);


--
-- Name: source_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.source_id_seq', 32, true);


--
-- Name: sport_types_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.sport_types_id_seq', 19, true);


--
-- Name: statuses_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.statuses_id_seq', 3, true);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.tasks_id_seq', 2027, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: matcher; Owner: user
--

SELECT pg_catalog.setval('matcher.users_id_seq', 2, true);


--
-- Name: configs configs_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.configs
    ADD CONSTRAINT configs_pk PRIMARY KEY (id);


--
-- Name: custom_matched_data custom_data_pkey; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.custom_matched_data
    ADD CONSTRAINT custom_data_pkey PRIMARY KEY (id);


--
-- Name: custom_unmatched_data custom_unmatched_data_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.custom_unmatched_data
    ADD CONSTRAINT custom_unmatched_data_pk PRIMARY KEY (event_id);


--
-- Name: parameters parameters_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.parameters
    ADD CONSTRAINT parameters_pk PRIMARY KEY (id);


--
-- Name: permissions permissions_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.permissions
    ADD CONSTRAINT permissions_pk PRIMARY KEY (id);


--
-- Name: processed_data_info processed_data_info_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.processed_data_info
    ADD CONSTRAINT processed_data_info_pk PRIMARY KEY (id);


--
-- Name: request_logs request_logs_pkey; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.request_logs
    ADD CONSTRAINT request_logs_pkey PRIMARY KEY (id);


--
-- Name: results results_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.results
    ADD CONSTRAINT results_pk PRIMARY KEY (id);


--
-- Name: runs runs_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.runs
    ADD CONSTRAINT runs_pk PRIMARY KEY (id);


--
-- Name: sources source_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.sources
    ADD CONSTRAINT source_pk PRIMARY KEY (id);


--
-- Name: sport_types sport_types_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.sport_types
    ADD CONSTRAINT sport_types_pk PRIMARY KEY (id);


--
-- Name: statuses statuses_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.statuses
    ADD CONSTRAINT statuses_pk PRIMARY KEY (id);


--
-- Name: tasks tasks_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.tasks
    ADD CONSTRAINT tasks_pk PRIMARY KEY (id);


--
-- Name: custom_matched_data unique_event_ids; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.custom_matched_data
    ADD CONSTRAINT unique_event_ids UNIQUE (event1_id, event2_id);


--
-- Name: users users_pk; Type: CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.users
    ADD CONSTRAINT users_pk PRIMARY KEY (id);


--
-- Name: custom_matched_data_date_idx; Type: INDEX; Schema: matcher; Owner: user
--

CREATE INDEX custom_matched_data_date_idx ON matcher.custom_matched_data USING btree (date);


--
-- Name: custom_unmatched_data_date_idx; Type: INDEX; Schema: matcher; Owner: user
--

CREATE INDEX custom_unmatched_data_date_idx ON matcher.custom_unmatched_data USING btree (date);


--
-- Name: configs configs_fk; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.configs
    ADD CONSTRAINT configs_fk FOREIGN KEY (source_id) REFERENCES matcher.sources(id) ON DELETE RESTRICT;


--
-- Name: configs configs_fk_1; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.configs
    ADD CONSTRAINT configs_fk_1 FOREIGN KEY (source2_id) REFERENCES matcher.sources(id) ON DELETE RESTRICT;


--
-- Name: configs configs_fk_2; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.configs
    ADD CONSTRAINT configs_fk_2 FOREIGN KEY (sport_id) REFERENCES matcher.sport_types(id) ON DELETE RESTRICT;


--
-- Name: configs configs_fk_3; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.configs
    ADD CONSTRAINT configs_fk_3 FOREIGN KEY (param_id) REFERENCES matcher.parameters(id) ON DELETE RESTRICT;


--
-- Name: configs configs_fk_4; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.configs
    ADD CONSTRAINT configs_fk_4 FOREIGN KEY (modified_by) REFERENCES matcher.users(id);


--
-- Name: results results_fk; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.results
    ADD CONSTRAINT results_fk FOREIGN KEY (modified_by) REFERENCES matcher.users(id);


--
-- Name: results results_fk2; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.results
    ADD CONSTRAINT results_fk2 FOREIGN KEY (run_id) REFERENCES matcher.runs(id) ON DELETE RESTRICT;


--
-- Name: runs runs_fk; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.runs
    ADD CONSTRAINT runs_fk FOREIGN KEY (task_id) REFERENCES matcher.tasks(id) ON DELETE RESTRICT;


--
-- Name: runs runs_fk2; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.runs
    ADD CONSTRAINT runs_fk2 FOREIGN KEY (sport_id) REFERENCES matcher.sport_types(id) ON DELETE RESTRICT;


--
-- Name: runs runs_fk3; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.runs
    ADD CONSTRAINT runs_fk3 FOREIGN KEY (status_user) REFERENCES matcher.statuses(id);


--
-- Name: runs runs_fk4; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.runs
    ADD CONSTRAINT runs_fk4 FOREIGN KEY (status_observer) REFERENCES matcher.statuses(id);


--
-- Name: tasks tasks_fk; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.tasks
    ADD CONSTRAINT tasks_fk FOREIGN KEY (source1_id) REFERENCES matcher.sources(id);


--
-- Name: tasks tasks_fk3; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.tasks
    ADD CONSTRAINT tasks_fk3 FOREIGN KEY (status_user) REFERENCES matcher.statuses(id);


--
-- Name: tasks tasks_fk4; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.tasks
    ADD CONSTRAINT tasks_fk4 FOREIGN KEY (status_observer) REFERENCES matcher.statuses(id);


--
-- Name: tasks tasks_fk5; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.tasks
    ADD CONSTRAINT tasks_fk5 FOREIGN KEY (referent_task) REFERENCES matcher.tasks(id);


--
-- Name: tasks tasks_fk_1; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.tasks
    ADD CONSTRAINT tasks_fk_1 FOREIGN KEY (source2_id) REFERENCES matcher.sources(id);


--
-- Name: users users_fk; Type: FK CONSTRAINT; Schema: matcher; Owner: user
--

ALTER TABLE ONLY matcher.users
    ADD CONSTRAINT users_fk FOREIGN KEY (permission_id) REFERENCES matcher.permissions(id);


--
-- PostgreSQL database dump complete
--

