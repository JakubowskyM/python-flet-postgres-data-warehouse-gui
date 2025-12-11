CREATE TABLE "Addresses" (
  "Id" integer PRIMARY KEY,
  "Voivodeship" varchar,
  "Town" varchar,
  "Postal_code" varchar,
  "Street_name" varchar,
  "House_number" varchar
);

CREATE TABLE "Shops" (
  "Id" integer PRIMARY KEY,
  "Name" varchar,
  "Id_address" integer
);

CREATE TABLE "Clients" (
  "Id" integer PRIMARY KEY,
  "Name" varchar,
  "Surname" varchar,
  "Id_address" integer
);

CREATE TABLE "Exporters" (
  "Id" integer PRIMARY KEY,
  "Name" varchar,
  "Country" varchar
);

CREATE TABLE "Components" (
  "Id" integer PRIMARY KEY,
  "Name" varchar,
  "Brand" varchar,
  "Type" varchar
);

CREATE TABLE "CPUs" (
  "Id_component" integer PRIMARY KEY,
  "Cores" integer,
  "Threads" integer,
  "Clock_speed" float,
  "Chipset" varchar,
  "Socket" varchar
);

CREATE TABLE "GPUs" (
  "Id_component" integer PRIMARY KEY,
  "VRAM" integer,
  "VRAM_type" varchar
);

CREATE TABLE "RAMs" (
  "Id_component" integer PRIMARY KEY,
  "Memory" integer,
  "Socket_type" varchar,
  "Clock" integer
);

CREATE TABLE "PSUs" (
  "Id_component" integer PRIMARY KEY,
  "Power" integer
);

CREATE TABLE "Disks" (
  "Id_component" integer PRIMARY KEY,
  "Memory" integer,
  "Disk_type" varchar
);

CREATE TABLE "Motherboards" (
  "Id_component" integer PRIMARY KEY,
  "Chipset" varchar,
  "Socket_type" varchar,
  "RAM_type" varchar
);

CREATE TABLE "Sales" (
  "Id" integer PRIMARY KEY,
  "Id_component" integer,
  "Id_client" integer,
  "Id_shop" integer,
  "Date_of_sell" timestamp,
  "Price" float,
  "Quantity" integer
);

CREATE TABLE "Imports" (
  "Id" integer PRIMARY KEY,
  "Id_component" integer,
  "Id_shop" integer,
  "Id_exporter" integer,
  "Delivery_type" varchar,
  "Delivery_placement_date" timestamp,
  "Expected_delivery_date" timestamp,
  "Real_delivery_date" timestamp,
  "Component_quantity" integer,
  "Sum_of_import" float
);

CREATE TABLE "Exporter_offers" (
  "Id" integer PRIMARY KEY,
  "Id_exporter" integer,
  "Id_component" integer,
  "Price" float
);

ALTER TABLE "Shops" ADD FOREIGN KEY ("Id_address") REFERENCES "Addresses" ("Id");

ALTER TABLE "Clients" ADD FOREIGN KEY ("Id_address") REFERENCES "Addresses" ("Id");

ALTER TABLE "CPUs" ADD FOREIGN KEY ("Id_component") REFERENCES "Components" ("Id");

ALTER TABLE "GPUs" ADD FOREIGN KEY ("Id_component") REFERENCES "Components" ("Id");

ALTER TABLE "RAMs" ADD FOREIGN KEY ("Id_component") REFERENCES "Components" ("Id");

ALTER TABLE "PSUs" ADD FOREIGN KEY ("Id_component") REFERENCES "Components" ("Id");

ALTER TABLE "Disks" ADD FOREIGN KEY ("Id_component") REFERENCES "Components" ("Id");

ALTER TABLE "Motherboards" ADD FOREIGN KEY ("Id_component") REFERENCES "Components" ("Id");

ALTER TABLE "Sales" ADD FOREIGN KEY ("Id_component") REFERENCES "Components" ("Id");

ALTER TABLE "Sales" ADD FOREIGN KEY ("Id_client") REFERENCES "Clients" ("Id");

ALTER TABLE "Sales" ADD FOREIGN KEY ("Id_shop") REFERENCES "Shops" ("Id");

ALTER TABLE "Imports" ADD FOREIGN KEY ("Id_component") REFERENCES "Components" ("Id");

ALTER TABLE "Imports" ADD FOREIGN KEY ("Id_shop") REFERENCES "Shops" ("Id");

ALTER TABLE "Imports" ADD FOREIGN KEY ("Id_exporter") REFERENCES "Exporters" ("Id");

ALTER TABLE "Exporter_offers" ADD FOREIGN KEY ("Id_exporter") REFERENCES "Exporters" ("Id");

ALTER TABLE "Exporter_offers" ADD FOREIGN KEY ("Id_component") REFERENCES "Components" ("Id");
