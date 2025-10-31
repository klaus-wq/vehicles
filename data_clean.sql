--
-- PostgreSQL database dump
--

\restrict gwJSyCo6eVVivdtPrv6rJqXZH1H6QUnqaVe4ArlFD1N5nhFqloLXq56LwIIuUqw

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



--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--



--
-- Data for Name: authentication_customuser; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

INSERT INTO public.authentication_customuser (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, created_at) VALUES (1, 'pbkdf2_sha256$1000000$1t5ZgxGVK8Gpt0fEL4R71w$J5aNkpbHkAM7QXTILSrAx0PsbZcOWBoYkDY+cHJHWo0=', '2025-10-28 15:26:57.978+07', true, 'admin', '', '', '', true, true, '2025-10-16 14:56:55.98+07', '2025-10-16 14:56:55.98+07');
INSERT INTO public.authentication_customuser (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, created_at) VALUES (2, 'pbkdf2_sha256$1000000$0aMqY4koiv8RyDOZgws8jU$ilFRmecEgXZWcUoyaWWZbgsiqyqcTipQmA+aIU2oqdQ=', '2025-10-23 16:20:45.215+07', false, 'manager1', '', '', '', true, true, '2025-10-16 14:59:27+07', '2025-10-16 14:59:27.501+07');
INSERT INTO public.authentication_customuser (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, created_at) VALUES (4, 'pbkdf2_sha256$1000000$AInOsPxb023DJgoAkPFNM9$wYuAJ9byMg6kvkxZOekhK/L3rzw9q85wWBngH7CnKHI=', NULL, false, 'manager2', '', '', '', false, true, '2025-10-20 04:20:43.625+07', '2025-10-20 04:20:44.456+07');
INSERT INTO public.authentication_customuser (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, created_at) VALUES (5, 'pbkdf2_sha256$1000000$34c4QHHrSHY6BPtZme35fz$NSFREE4SWMFL0GEDmENvGFUYwwNKE//4XdS3bH1IC7I=', NULL, false, 'test', '', '', '', false, true, '2025-10-20 15:01:52.467+07', '2025-10-20 15:01:53.33+07');


--
-- Data for Name: authentication_customuser_groups; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--



--
-- Data for Name: authentication_customuser_user_permissions; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--



--
-- Data for Name: authentication_manager; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

INSERT INTO public.authentication_manager (id, user_id) VALUES (1, 2);
INSERT INTO public.authentication_manager (id, user_id) VALUES (2, 4);


--
-- Data for Name: vehicle_enterprise; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

INSERT INTO public.vehicle_enterprise (id, name, city, address, phone) VALUES (1, 'Рога и Копыта', 'Москва', 'Краснопрудная', '+7 495 02-55-252');
INSERT INTO public.vehicle_enterprise (id, name, city, address, phone) VALUES (2, 'Русское авто', 'Москва', 'ул. Новая, д. 1', '+7 (383) 123-45-67');
INSERT INTO public.vehicle_enterprise (id, name, city, address, phone) VALUES (3, 'Автодом', 'Москва', 'ул. Новая, д. 1', '+7 (383) 123-45-67');
INSERT INTO public.vehicle_enterprise (id, name, city, address, phone) VALUES (6, 'Тест', 'Москва', 'Адрес', '45634');
INSERT INTO public.vehicle_enterprise (id, name, city, address, phone) VALUES (15, 'Тест', 'ch', 'cfg', '4567567');


--
-- Data for Name: authentication_manager_enterprises; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

INSERT INTO public.authentication_manager_enterprises (id, manager_id, enterprise_id) VALUES (1, 1, 1);
INSERT INTO public.authentication_manager_enterprises (id, manager_id, enterprise_id) VALUES (2, 1, 2);
INSERT INTO public.authentication_manager_enterprises (id, manager_id, enterprise_id) VALUES (3, 1, 15);
INSERT INTO public.authentication_manager_enterprises (id, manager_id, enterprise_id) VALUES (4, 2, 2);
INSERT INTO public.authentication_manager_enterprises (id, manager_id, enterprise_id) VALUES (5, 2, 3);
INSERT INTO public.authentication_manager_enterprises (id, manager_id, enterprise_id) VALUES (6, 2, 6);
INSERT INTO public.authentication_manager_enterprises (id, manager_id, enterprise_id) VALUES (7, 2, 15);


--
-- Data for Name: vehicle_brand; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

INSERT INTO public.vehicle_brand (id, name, vehicle_type, fuel_tank_capacity, cargo_capacity, seating_capacity) VALUES (1, 'BMW', 'car', 78, 1000, 5);


--
-- Data for Name: vehicle_driver; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

INSERT INTO public.vehicle_driver (id, first_name, last_name, license_number, salary, enterprise_id) VALUES (1, 'Иван', 'Иванов', '123456789', 50000.00, 1);
INSERT INTO public.vehicle_driver (id, first_name, last_name, license_number, salary, enterprise_id) VALUES (2, 'Сергей', 'Сергеев', '123456780', 50000.00, 1);
INSERT INTO public.vehicle_driver (id, first_name, last_name, license_number, salary, enterprise_id) VALUES (3, 'Семён', 'Кузьмов', '123453546', 50000.00, 1);
INSERT INTO public.vehicle_driver (id, first_name, last_name, license_number, salary, enterprise_id) VALUES (4, 'Кирилл', 'Андреев', '342563465', 50000.00, 2);
INSERT INTO public.vehicle_driver (id, first_name, last_name, license_number, salary, enterprise_id) VALUES (5, 'Юрий', 'Петров', '237594873', 50000.00, 2);
INSERT INTO public.vehicle_driver (id, first_name, last_name, license_number, salary, enterprise_id) VALUES (6, 'Дмитрий', 'Цирман', '476385467', 50000.00, 2);
INSERT INTO public.vehicle_driver (id, first_name, last_name, license_number, salary, enterprise_id) VALUES (7, 'Андрей', 'Кириллов', '457634231', 50000.00, 3);
INSERT INTO public.vehicle_driver (id, first_name, last_name, license_number, salary, enterprise_id) VALUES (8, 'Еким', 'Денисов', '576444343', 50000.00, 3);
INSERT INTO public.vehicle_driver (id, first_name, last_name, license_number, salary, enterprise_id) VALUES (9, 'Тимур', 'Ирман', '45345324', 50000.00, 3);


--
-- Data for Name: vehicle_vehicle; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

INSERT INTO public.vehicle_vehicle (id, car_number, price, year, mileage, fuel_type, transmission, color, created_at, brand_id, enterprise_id) VALUES (3, 'Н234ПП', 2000000.00, 2024, 40, 'gasoline', 'automatic', 'Серый', '2025-10-20 04:12:32.965+07', 1, 3);
INSERT INTO public.vehicle_vehicle (id, car_number, price, year, mileage, fuel_type, transmission, color, created_at, brand_id, enterprise_id) VALUES (14, 'ЕЕ453РН54', 2000000.00, 2020, 1, 'gasoline', 'manual', 'er', '2025-10-20 19:36:26.576+07', 1, 1);
INSERT INTO public.vehicle_vehicle (id, car_number, price, year, mileage, fuel_type, transmission, color, created_at, brand_id, enterprise_id) VALUES (15, 'Е456АП', 2000000.00, 2025, 0, 'electric', 'robot', 'White', '2025-10-28 14:41:06.813+07', 1, 1);


--
-- Data for Name: vehicle_drivervehicle; Type: TABLE DATA; Schema: public; Owner: vehicleuser2
--

INSERT INTO public.vehicle_drivervehicle (id, is_active, driver_id, vehicle_id) VALUES (4, false, 7, 3);
INSERT INTO public.vehicle_drivervehicle (id, is_active, driver_id, vehicle_id) VALUES (9, false, 1, 14);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


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

SELECT pg_catalog.setval('public.authentication_manager_enterprises_id_seq', 7, true);


--
-- Name: authentication_manager_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vehicleuser2
--

SELECT pg_catalog.setval('public.authentication_manager_id_seq', 2, true);


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

\unrestrict gwJSyCo6eVVivdtPrv6rJqXZH1H6QUnqaVe4ArlFD1N5nhFqloLXq56LwIIuUqw

