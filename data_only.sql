--
-- PostgreSQL database dump
--

\restrict O9U5anvVl2GoBDGvfbTsL9Uh1fG7JamTf2fL6HILBTM25XHLbly5y8gZPYxcX0K

-- Dumped from database version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)

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
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	sessions	session
6	vehicle	brand
7	vehicle	driver
8	vehicle	enterprise
9	vehicle	drivervehicle
10	vehicle	vehicle
11	authentication	customuser
12	authentication	manager
13	authtoken	token
14	authtoken	tokenproxy
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add Бренд	6	add_brand
22	Can change Бренд	6	change_brand
23	Can delete Бренд	6	delete_brand
24	Can view Бренд	6	view_brand
25	Can add Водитель	7	add_driver
26	Can change Водитель	7	change_driver
27	Can delete Водитель	7	delete_driver
28	Can view Водитель	7	view_driver
29	Can add Предприятие	8	add_enterprise
30	Can change Предприятие	8	change_enterprise
31	Can delete Предприятие	8	delete_enterprise
32	Can view Предприятие	8	view_enterprise
33	Can add Назначение водителя автомобилю	9	add_drivervehicle
34	Can change Назначение водителя автомобилю	9	change_drivervehicle
35	Can delete Назначение водителя автомобилю	9	delete_drivervehicle
36	Can view Назначение водителя автомобилю	9	view_drivervehicle
37	Can add Автомобиль	10	add_vehicle
38	Can change Автомобиль	10	change_vehicle
39	Can delete Автомобиль	10	delete_vehicle
40	Can view Автомобиль	10	view_vehicle
41	Can add user	11	add_customuser
42	Can change user	11	change_customuser
43	Can delete user	11	delete_customuser
44	Can view user	11	view_customuser
45	Can add Менеджер	12	add_manager
46	Can change Менеджер	12	change_manager
47	Can delete Менеджер	12	delete_manager
48	Can view Менеджер	12	view_manager
49	Can add Token	13	add_token
50	Can change Token	13	change_token
51	Can delete Token	13	delete_token
52	Can view Token	13	view_token
53	Can add Token	14	add_tokenproxy
54	Can change Token	14	change_tokenproxy
55	Can delete Token	14	delete_tokenproxy
56	Can view Token	14	view_tokenproxy
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: authentication_customuser; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.authentication_customuser (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, created_at) FROM stdin;
1	pbkdf2_sha256$1000000$1t5ZgxGVK8Gpt0fEL4R71w$J5aNkpbHkAM7QXTILSrAx0PsbZcOWBoYkDY+cHJHWo0=	2025-10-28 15:26:57.978+07	t	admin				t	t	2025-10-16 14:56:55.98+07	2025-10-16 14:56:55.98+07
2	pbkdf2_sha256$1000000$0aMqY4koiv8RyDOZgws8jU$ilFRmecEgXZWcUoyaWWZbgsiqyqcTipQmA+aIU2oqdQ=	2025-10-23 16:20:45.215+07	f	manager1				t	t	2025-10-16 14:59:27+07	2025-10-16 14:59:27.501+07
4	pbkdf2_sha256$1000000$AInOsPxb023DJgoAkPFNM9$wYuAJ9byMg6kvkxZOekhK/L3rzw9q85wWBngH7CnKHI=	\N	f	manager2				f	t	2025-10-20 04:20:43.625+07	2025-10-20 04:20:44.456+07
5	pbkdf2_sha256$1000000$34c4QHHrSHY6BPtZme35fz$NSFREE4SWMFL0GEDmENvGFUYwwNKE//4XdS3bH1IC7I=	\N	f	test				f	t	2025-10-20 15:01:52.467+07	2025-10-20 15:01:53.33+07
\.


--
-- Data for Name: authentication_customuser_groups; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.authentication_customuser_groups (id, customuser_id, group_id) FROM stdin;
\.


--
-- Data for Name: authentication_customuser_user_permissions; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.authentication_customuser_user_permissions (id, customuser_id, permission_id) FROM stdin;
\.


--
-- Data for Name: authentication_manager; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.authentication_manager (id, user_id) FROM stdin;
1	2
2	4
\.


--
-- Data for Name: vehicle_enterprise; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.vehicle_enterprise (id, name, city, address, phone) FROM stdin;
1	Рога и Копыта	Москва	Краснопрудная	+7 495 02-55-252
2	Русское авто	Москва	ул. Новая, д. 1	+7 (383) 123-45-67
3	Автодом	Москва	ул. Новая, д. 1	+7 (383) 123-45-67
6	Тест	Москва	Адрес	45634
15	Тест	ch	cfg	4567567
\.


--
-- Data for Name: authentication_manager_enterprises; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.authentication_manager_enterprises (id, manager_id, enterprise_id) FROM stdin;
8	1	1
9	1	2
10	1	15
11	2	2
12	2	3
13	2	6
14	2	15
\.


--
-- Data for Name: authtoken_token; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.authtoken_token (key, created, user_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2025-10-16 14:59:27.503+07	2	manager1	1	[{"added": {}}]	11	1
2	2025-10-16 15:11:19.625+07	2	manager1	2	[{"changed": {"fields": ["Staff status"]}}]	11	1
3	2025-10-16 15:15:37.576+07	1	1, Рога и Копыта, Москва, Краснопрудная, +7 495 02-55-252	1	[{"added": {}}]	8	1
4	2025-10-16 15:15:50.531+07	1	manager1, 1 Рога и Копыта	1	[{"added": {}}]	12	1
5	2025-10-16 15:28:32.717+07	1	1, Иванов Иван, Рога и Копыта, 	1	[{"added": {}}]	7	1
6	2025-10-16 15:28:54.859+07	1	1, BMW, Легковой, 78 л., 1000 кг., 5	1	[{"added": {}}]	6	1
7	2025-10-16 15:29:26.046+07	1	1, ЕЕ453РН54, Рога и Копыта, 	1	[{"added": {}}]	10	1
8	2025-10-16 15:29:34.443+07	1	1, Иван Иванов (дополнительный) → 1, ЕЕ453РН54 	1	[{"added": {}}]	9	1
9	2025-10-16 18:10:32.347+07	3	test	1	[{"added": {}}]	11	1
10	2025-10-16 18:11:09.018+07	3	test	2	[{"changed": {"fields": ["Staff status"]}}]	11	1
11	2025-10-20 04:07:08.279+07	5	5, Авто и машинки, Москва, ул. Новая, д. 1, +7 (383) 123-45-67	3		8	1
12	2025-10-20 04:07:08.279+07	4	4, Авто и машинки, Москва, ул. Новая, д. 1, +7 (383) 123-45-67	3		8	1
13	2025-10-20 04:07:16.398+07	2	2, Русское авто, Москва, ул. Новая, д. 1, +7 (383) 123-45-67	2	[{"changed": {"fields": ["\\u041d\\u0430\\u0437\\u0432\\u0430\\u043d\\u0438\\u0435 \\u043f\\u0440\\u0435\\u0434\\u043f\\u0440\\u0438\\u044f\\u0442\\u0438\\u044f"]}}]	8	1
14	2025-10-20 04:07:27.709+07	3	3, Автодом, Москва, ул. Новая, д. 1, +7 (383) 123-45-67	2	[{"changed": {"fields": ["\\u041d\\u0430\\u0437\\u0432\\u0430\\u043d\\u0438\\u0435 \\u043f\\u0440\\u0435\\u0434\\u043f\\u0440\\u0438\\u044f\\u0442\\u0438\\u044f"]}}]	8	1
15	2025-10-20 04:07:58.179+07	2	2, Сергеев Сергей, Рога и Копыта, 	1	[{"added": {}}]	7	1
16	2025-10-20 04:08:21.586+07	3	3, Кузьмов Семён, Рога и Копыта, 	1	[{"added": {}}]	7	1
17	2025-10-20 04:08:39.875+07	4	4, Андреев Кирилл, Русское авто, 	1	[{"added": {}}]	7	1
18	2025-10-20 04:09:05.887+07	5	5, Петров Юрий, Русское авто, 	1	[{"added": {}}]	7	1
19	2025-10-20 04:09:38.257+07	6	6, Цирман Дмитрий, Русское авто, 	1	[{"added": {}}]	7	1
20	2025-10-20 04:09:58.887+07	7	7, Кириллов Андрей, Автодом, 	1	[{"added": {}}]	7	1
21	2025-10-20 04:10:20.935+07	8	8, Денисов Еким, Автодом, 	1	[{"added": {}}]	7	1
22	2025-10-20 04:10:47.393+07	9	9, Ирман Тимур, Автодом, 	1	[{"added": {}}]	7	1
23	2025-10-20 04:12:11.499+07	2	2, ПЕ345РИ65, Русское авто, 	1	[{"added": {}}]	10	1
24	2025-10-20 04:12:32.968+07	3	3, Н234ПП, Автодом, 	1	[{"added": {}}]	10	1
25	2025-10-20 04:12:44.009+07	2	2, ПЕ345РИ65, Русское авто, 	2	[{"changed": {"fields": ["\\u0421\\u0442\\u043e\\u0438\\u043c\\u043e\\u0441\\u0442\\u044c, \\u20bd"]}}]	10	1
26	2025-10-20 04:13:04.765+07	2	3, Семён Кузьмов (основной) → 1, ЕЕ453РН54 	1	[{"added": {}}]	9	1
27	2025-10-20 04:13:10.663+07	3	4, Кирилл Андреев (дополнительный) → 2, ПЕ345РИ65 	1	[{"added": {}}]	9	1
28	2025-10-20 04:13:16.853+07	4	7, Андрей Кириллов (дополнительный) → 3, Н234ПП 	1	[{"added": {}}]	9	1
29	2025-10-20 04:13:27.545+07	5	6, Дмитрий Цирман (основной) → 2, ПЕ345РИ65 	1	[{"added": {}}]	9	1
30	2025-10-20 04:20:44.458+07	4	manager2	1	[{"added": {}}]	11	1
31	2025-10-20 04:21:01.365+07	2	manager2, 2 Русское авто, 3 Автодом	1	[{"added": {}}]	12	1
32	2025-10-20 04:21:09.691+07	1	manager1, 1 Рога и Копыта, 2 Русское авто	2	[{"changed": {"fields": ["\\u041f\\u0440\\u0435\\u0434\\u043f\\u0440\\u0438\\u044f\\u0442\\u0438\\u044f"]}}]	12	1
33	2025-10-20 04:21:42.08+07	6	6, Тест, Москва, Адрес, 45634	1	[{"added": {}}]	8	2
34	2025-10-20 04:41:58.913+07	7	7, Тест1, Москва, Адрес, 34534	1	[{"added": {}}]	8	2
35	2025-10-20 05:10:41.932+07	10	10, ц45 235, Тест1, 	1	[{"added": {}}]	7	2
36	2025-10-20 05:11:01.186+07	8	8, цуеце, Тест1, 	1	[{"added": {}}]	10	2
37	2025-10-20 05:11:10.353+07	6	10, 235 ц45 (дополнительный) → 8, цуеце 	1	[{"added": {}}]	9	2
38	2025-10-20 05:11:28.388+07	2	manager2, 2 Русское авто, 3 Автодом, 6 Тест, 7 Тест1	2	[{"changed": {"fields": ["\\u041f\\u0440\\u0435\\u0434\\u043f\\u0440\\u0438\\u044f\\u0442\\u0438\\u044f"]}}]	12	1
39	2025-10-20 05:13:51.42+07	7	7, Тест1, Москва, Адрес, 34534	3		8	2
40	2025-10-20 05:19:41.815+07	12	12, Авто и машинки, Москва, ул. Новая, д. 1, +7 (383) 123-45-67	3		8	2
41	2025-10-20 05:19:41.815+07	11	11, Авто и машинки, Москва, ул. Новая, д. 1, +7 (383) 123-45-67	3		8	2
42	2025-10-20 05:19:41.815+07	10	10, Авто и машинки, Москва, ул. Новая, д. 1, +7 (383) 123-45-67	3		8	2
43	2025-10-20 05:19:41.815+07	8	8, Авто и машинки, Москва, ул. Новая, д. 1, +7 (383) 123-45-67	3		8	2
44	2025-10-20 05:19:56.776+07	9	9, A123BC77, Рога и Копыта, 	3		10	2
45	2025-10-20 05:22:26.82+07	13	13, Авто и машинки, Москва, ул. Новая, д. 1, +7 (383) 123-45-67	3		8	2
46	2025-10-20 05:25:42.924+07	10	10, A123BC77, Рога и Копыта, 	3		10	2
47	2025-10-20 15:01:35.412+07	3	test	3		11	1
48	2025-10-20 15:01:53.331+07	5	test	1	[{"added": {}}]	11	1
49	2025-10-20 19:25:58.636+07	12	12, ЕЕ453РН54, Рога и Копыта, 	1	[{"added": {}}]	10	2
50	2025-10-20 19:26:10.073+07	7	1, Иван Иванов (дополнительный) → 12, ЕЕ453РН54 	1	[{"added": {}}]	9	2
51	2025-10-20 19:27:16.423+07	13	13, ЕЕ453РН54, Рога и Копыта, 	1	[{"added": {}}]	10	2
52	2025-10-20 19:27:25.082+07	8	1, Иван Иванов (дополнительный) → 13, ЕЕ453РН54 	1	[{"added": {}}]	9	2
53	2025-10-20 19:36:26.579+07	14	14, ЕЕ453РН54, Рога и Копыта, 	1	[{"added": {}}]	10	2
54	2025-10-20 19:36:32.43+07	9	1, Иван Иванов (дополнительный) → 14, ЕЕ453РН54 	1	[{"added": {}}]	9	2
55	2025-10-21 17:02:27.163+07	15	15, Тест, ch, cfg, 4567567	1	[{"added": {}}]	8	2
56	2025-10-21 17:02:42.429+07	2	manager2, 2 Русское авто, 3 Автодом, 6 Тест, 15 Тест	2	[{"changed": {"fields": ["\\u041f\\u0440\\u0435\\u0434\\u043f\\u0440\\u0438\\u044f\\u0442\\u0438\\u044f"]}}]	12	1
57	2025-10-28 14:40:13.33+07	11	11, Андреев Дмитрий, Рога и Копыта, 	1	[{"added": {}}]	7	1
58	2025-10-28 14:40:25.272+07	12	12, Кузьмов Еким, Русское авто, 	1	[{"added": {}}]	7	1
59	2025-10-28 14:40:40.824+07	13	13, Ирман Кирилл, Автодом, 	1	[{"added": {}}]	7	1
60	2025-10-28 14:41:06.818+07	15	15, Е456АП, Рога и Копыта, 	1	[{"added": {}}]	10	1
61	2025-10-28 14:41:14.112+07	10	11, Дмитрий Андреев (дополнительный) → 14, ЕЕ453РН54 	1	[{"added": {}}]	9	1
62	2025-10-28 14:41:23.743+07	11	11, Дмитрий Андреев (основной) → 15, Е456АП 	1	[{"added": {}}]	9	1
63	2025-10-28 14:41:39.235+07	12	13, Кирилл Ирман (дополнительный) → 3, Н234ПП 	1	[{"added": {}}]	9	1
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
53lb1uw3r51iras93ey8m1d2bhr5o21r	.eJxVjDsOwjAQBe_iGln-rO0NJX3OYK1_OIAcKU4qxN1JpBTQvpl5b-ZpW6vfel78lNiVSXb53QLFZ24HSA9q95nHua3LFPih8JN2Ps4pv26n-3dQqde91igKqpQpGqcsSmmCVGQFFECjBzBZYnA26uJMMiRoJzhoBAoALlj2-QK-zjbo:1vDcDJ:spqogMVRyZx4rajaIR6MKsYqPxYdMwQQjHAf1kYi5zQ	2025-11-11 12:25:45.471+07
87tk3c7f1mng0iaz3kg3cuyuxv52l3o8	.eJxVjDsOwjAQBe_iGln-rO0NJX3OYK1_OIAcKU4qxN1JpBTQvpl5b-ZpW6vfel78lNiVSXb53QLFZ24HSA9q95nHua3LFPih8JN2Ps4pv26n-3dQqde91igKqpQpGqcsSmmCVGQFFECjBzBZYnA26uJMMiRoJzhoBAoALlj2-QK-zjbo:1vD5Xh:xqzojTthkiA2QdECwSZTeBE2XEEJxbMKM9f5pL9lp3Y	2025-11-10 01:32:37.283+07
t64cjzdxgrolhafc971dpw7gwn7iowx4	.eJxVjDsOwjAQBe_iGln-rO0NJX3OYK1_OIAcKU4qxN1JpBTQvpl5b-ZpW6vfel78lNiVSXb53QLFZ24HSA9q95nHua3LFPih8JN2Ps4pv26n-3dQqde91igKqpQpGqcsSmmCVGQFFECjBzBZYnA26uJMMiRoJzhoBAoALlj2-QK-zjbo:1vDf2f:wgS58mYVO7Wcpa2E26CgJf0PLLlej0gXBLu24_KJZQI	2025-11-11 15:26:57.981+07
\.


--
-- Data for Name: vehicle_brand; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.vehicle_brand (id, name, vehicle_type, fuel_tank_capacity, cargo_capacity, seating_capacity) FROM stdin;
1	BMW	car	78	1000	5
\.


--
-- Data for Name: vehicle_driver; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.vehicle_driver (id, first_name, last_name, license_number, salary, enterprise_id) FROM stdin;
1	Иван	Иванов	123456789	50000.00	1
2	Сергей	Сергеев	123456780	50000.00	1
3	Семён	Кузьмов	123453546	50000.00	1
4	Кирилл	Андреев	342563465	50000.00	2
5	Юрий	Петров	237594873	50000.00	2
6	Дмитрий	Цирман	476385467	50000.00	2
7	Андрей	Кириллов	457634231	50000.00	3
8	Еким	Денисов	576444343	50000.00	3
9	Тимур	Ирман	45345324	50000.00	3
\.


--
-- Data for Name: vehicle_vehicle; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.vehicle_vehicle (id, car_number, price, year, mileage, fuel_type, transmission, color, created_at, brand_id, enterprise_id) FROM stdin;
3	Н234ПП	2000000.00	2024	40	gasoline	automatic	Серый	2025-10-20 04:12:32.965+07	1	3
14	ЕЕ453РН54	2000000.00	2020	1	gasoline	manual	er	2025-10-20 19:36:26.576+07	1	1
15	Е456АП	2000000.00	2025	0	electric	robot	White	2025-10-28 14:41:06.813+07	1	1
\.


--
-- Data for Name: vehicle_drivervehicle; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

COPY public.vehicle_drivervehicle (id, is_active, driver_id, vehicle_id) FROM stdin;
4	f	7	3
9	f	1	14
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 56, true);


--
-- Name: authentication_customuser_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.authentication_customuser_groups_id_seq', 1, false);


--
-- Name: authentication_customuser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.authentication_customuser_id_seq', 5, true);


--
-- Name: authentication_customuser_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.authentication_customuser_user_permissions_id_seq', 1, false);


--
-- Name: authentication_manager_enterprises_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.authentication_manager_enterprises_id_seq', 14, true);


--
-- Name: authentication_manager_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.authentication_manager_id_seq', 2, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 63, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 14, true);


--
-- Name: vehicle_driver_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.vehicle_driver_id_seq', 9, true);


--
-- Name: vehicle_drivervehicle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.vehicle_drivervehicle_id_seq', 9, true);


--
-- Name: vehicle_enterprise_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.vehicle_enterprise_id_seq', 15, true);


--
-- Name: vehicle_vehicle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.vehicle_vehicle_id_seq', 15, true);


--
-- PostgreSQL database dump complete
--

\unrestrict O9U5anvVl2GoBDGvfbTsL9Uh1fG7JamTf2fL6HILBTM25XHLbly5y8gZPYxcX0K

