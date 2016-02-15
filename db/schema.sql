DROP TABLE if exists entrants CASCADE;
CREATE TABLE entrants (
	entrant_id INTEGER,
	fname CHAR(40),
	lname CHAR(40),
	age INTEGER,
	phone_num INTEGER,
	PRIMARY KEY (entrant_id)
);

DROP TABLE if exists admins CASCADE;
CREATE TABLE admins ( --superclass is entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES entrants
);

DROP TABLE if exists service_employees CASCADE;
CREATE TABLE service_employees ( --superclass is entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES entrants
);

DROP TABLE if exists buildings CASCADE;
CREATE TABLE buildings (
	building_id INTEGER,
	phone_num INTEGER,
	street_address CHAR(120),
	state CHAR(2),
	zip_code INTEGER,
	email CHAR(120),
	PRIMARY KEY (building_id)
);

DROP TABLE if exists service_providers CASCADE;
CREATE TABLE service_providers (
	business_id INTEGER,
	business_name CHAR(120),
	business_description CHAR(1000),
	phone_num INTEGER,
	email CHAR(120),
	PRIMARY KEY (business_id)
);

DROP TABLE if exists works_for;
CREATE TABLE works_For (
	entrant_id INTEGER,
	business_id INTEGER,
	PRIMARY KEY (entrant_id, business_id),
	FOREIGN KEY (entrant_id) REFERENCES service_employees,
	FOREIGN KEY (business_id) REFERENCES service_providers
);

DROP TABLE if exists administers;
CREATE TABLE administers (
	entrant_id INTEGER,
	building_id INTEGER,
	privilege_level char(25),
	PRIMARY KEY (entrant_id, building_id),
	FOREIGN KEY (entrant_id) REFERENCES admins,
	FOREIGN KEY (building_id) REFERENCES buildings
);

DROP TABLE if exists parking_spots CASCADE;
CREATE TABLE parking_spots ( -- parking spots within a building
	spot_number INTEGER,
	building_id INTEGER,
	spot_type CHAR(20), -- Temporary? Permanent? Unloading zone?
	PRIMARY KEY (spot_number, building_id),
	FOREIGN KEY (building_id) REFERENCES buildings ON DELETE CASCADE
);

DROP TABLE if exists vehicles CASCADE;
CREATE TABLE vehicles (
	state CHAR (2),
	plate_num CHAR(10),
	make CHAR(30),
	model CHAR(30),
	color CHAR(15),
	is_requested BOOLEAN,
	key_number INTEGER,
	spot_number INTEGER,
	building_id INTEGER,
	UNIQUE (spot_number, building_id),
	UNIQUE (key_number),
	FOREIGN KEY (spot_number, building_id) REFERENCES parking_spots,
	PRIMARY KEY (state, plate_num)
);

DROP TABLE if exists of_a;
CREATE TABLE of_a ( -- Entrant of a building
	building_id INTEGER,
	entrant_id INTEGER,
	PRIMARY KEY (building_id, entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES entrants,
	FOREIGN KEY (building_id) REFERENCES buildings
);

DROP TABLE if exists provides_services_for;
CREATE TABLE provides_services_for ( -- buildings that service providers provide)
	business_id INTEGER,
	building_id INTEGER,
	PRIMARY KEY (business_id, building_id),
	FOREIGN KEY (business_id) REFERENCES service_providers,
	FOREIGN KEY (building_id) REFERENCES buildings
);

DROP TABLE if exists drives;
CREATE TABLE drives (
	entrant_id INTEGER,
	state CHAR (2),
	plate_num CHAR(10),
	PRIMARY KEY (entrant_id, state, plate_num),
	FOREIGN KEY (entrant_id) REFERENCES entrants,
	FOREIGN KEY (state, plate_num) REFERENCES vehicles
);

DROP TABLE if exists units CASCADE;
CREATE TABLE units ( -- unit within a building
	unit_id CHAR(6),
	floor INTEGER,
	building_id INTEGER,
	PRIMARY KEY (unit_id, building_id),
	FOREIGN KEY (building_id) REFERENCES buildings ON DELETE CASCADE
);

DROP TABLE if exists unit_entrants CASCADE;
CREATE TABLE unit_entrants ( --superclass is entrants
							 --combined with Enters relationship set
	entrant_id INTEGER,
	unit_id CHAR(6) NOT NULL,
	building_id INTEGER NOT NULL,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES entrants,
	FOREIGN KEY (unit_id, building_id) REFERENCES units
);

DROP TABLE if exists residents;
CREATE TABLE residents ( --superclass is unit entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES unit_entrants
);

DROP TABLE if exists casual_entrants;
CREATE TABLE casual_entrants ( --superclass is unit entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES unit_entrants
);

DROP TABLE if exists guests;
CREATE TABLE guests ( --superclass is unit entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES unit_entrants
);

DROP TABLE if exists owns;
CREATE TABLE owns ( -- parking spot owned by a unit
	unit_id CHAR(6),
	spot_number INTEGER,
	building_id INTEGER,
	PRIMARY KEY (unit_id, building_id, spot_number),
	FOREIGN KEY (unit_id, building_id) REFERENCES units,
	FOREIGN KEY (spot_number, building_id) REFERENCES parking_spots
);
