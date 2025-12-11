import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('pl_PL')

#Polish voivedoships

voivodeships = [
    "dolnośląskie", "kujawsko-pomorskie", "lubelskie", "lubuskie",
    "łódzkie", "małopolskie", "mazowieckie", "opolskie",
    "podkarpackie", "podlaskie", "pomorskie", "śląskie",
    "świętokrzyskie", "warmińsko-mazurskie", "wielkopolskie", "zachodniopomorskie"
]

#Brands

brands = {
    "CPU": ["Intel", "AMD"],
    "GPU": ["Nvidia", "AMD"],
    "RAM": ["Corsair", "G.Skill", "Kingston"],
    "PSU": ["Corsair", "Seasonic", "EVGA"],
    "Disk": ["Samsung", "WD", "Crucial"],
    "Motherboard": ["Asus", "MSI", "Gigabyte", "ASRock"]
}

cpu_chipsets = {
    "Intel": ["B660", "Z690", "H610", "Z790", "B760"],
    "AMD": ["B550", "X570", "A520", "X670", "B650"]
}
cpu_sockets = {
    "Intel": ["LGA1200", "LGA1700"],
    "AMD": ["AM4", "AM5"]
}
ram_types = ["DDR3", "DDR4", "DDR5"]
disk_types = ["HDD", "SSD"]


#Functions for generating components

def generate_cpu():
    brand = random.choice(brands["CPU"])
    name = f"{brand} CPU {random.randint(1000,9999)}"
    cores = random.randint(2,64)
    threads = random.randint(max(cores,4),128)
    clock = round(random.randrange(20,61)/10,1)
    chipset = random.choice(cpu_chipsets[brand])
    socket = random.choice(cpu_sockets[brand])
    return {"type":"CPU","brand":brand,"name":name,"cores":cores,"threads":threads,"clock":clock,"chipset":chipset,"socket":socket}

def generate_gpu():
    brand = random.choice(brands["GPU"])
    name = f"{brand} GPU {random.randint(1000,9999)}"
    vram = random.choice([4,6,8,12,16,24])
    vram_type = random.choice(["GDDR5","GDDR6","HBM2"])
    return {"type":"GPU","brand":brand,"name":name,"vram":vram,"vram_type":vram_type}

def generate_ram():
    brand = random.choice(brands["RAM"])
    memory = random.choice([8,16,32,64])
    name = f"{brand} RAM {memory}GB"
    socket_type = random.choice(ram_types)
    clock = random.choice([2133,2400,2666,3000,3200,3600,4000])
    return {"type":"RAM","brand":brand,"name":name,"memory":memory,"socket_type":socket_type,"clock":clock}

def generate_psu():
    brand = random.choice(brands["PSU"])
    power = random.choice(list(range(300,1001,50)))
    name = f"{brand} PSU {power}W"
    return {"type":"PSU","brand":brand,"name":name,"power":power}

def generate_disk():
    brand = random.choice(brands["Disk"])
    capacity = random.choice([128,256,512,1024,2048,4096,6144])
    disk_type = random.choice(disk_types)
    name = f"{brand} {capacity if capacity<1024 else capacity//1024} {'GB' if capacity<1024 else 'TB'} {disk_type}"
    memory = capacity if capacity<1024 else capacity
    return {"type":"Disk","brand":brand,"name":name,"memory":memory,"disk_type":disk_type}

def generate_motherboard(cpu_info):
    brand = random.choice(brands["Motherboard"])
    name = f"{brand} Motherboard {random.randint(100,999)}"
    chipset = cpu_info["chipset"]
    socket = cpu_info["socket"]
    ram_type = random.choice(ram_types)
    return {"type":"Motherboard","brand":brand,"name":name,"chipset":chipset,"socket":socket,"ram_type":ram_type}

#PostgreSQL db connection
conn = psycopg2.connect(
    host="localhost",
    database="yours_db_name",
    user="yours_db_user",
    password="yours_db_pswd"
)
cur = conn.cursor()

#Adresses generator
addresses_count = 50
for i in range(1, addresses_count + 1):
    cur.execute("""
        INSERT INTO "Addresses" ("Id","Voivodeship","Town","Postal_code","Street_name","House_number")
        VALUES (%s,%s,%s,%s,%s,%s)
    """,(i,random.choice(voivodeships),fake.city(),fake.postcode(),fake.street_name(),fake.building_number()))

#Shops generator
shops_count = 10
for i in range(1, shops_count+1):
    cur.execute("""
        INSERT INTO "Shops" ("Id","Id_address","Name") VALUES (%s,%s,%s)
    """,(i,random.randint(1,addresses_count),fake.company()))

#Clients generator
clients_count = 100
for i in range(1, clients_count+1):
    cur.execute("""
        INSERT INTO "Clients" ("Id","Name","Surname","Id_address")
        VALUES (%s,%s,%s,%s)
    """,(i,fake.first_name(),fake.last_name(),random.randint(1,addresses_count)))

#Exporters generator
exporters_count = 5
countries = ['Poland','Germany','USA','China','Japan']
for i in range(1, exporters_count+1):
    cur.execute("""
        INSERT INTO "Exporters" ("Id","Name","Country") VALUES (%s,%s,%s)
    """,(i,fake.company(),random.choice(countries)))

#Components generator
component_id = 1
total_components = 300
component_list = []

while component_id <= total_components:
    ctype = random.choice(["CPU","GPU","RAM","PSU","Disk"])
    if ctype == "CPU":
        cpu = generate_cpu()
        component_list.append(cpu)
        cur.execute("""
            INSERT INTO "Components" ("Id","Name","Brand","Type") VALUES (%s,%s,%s,%s)
        """,(component_id,cpu["name"],cpu["brand"],cpu["type"]))
        cur.execute("""
            INSERT INTO "CPUs" ("Id_component","Cores","Threads","Clock_speed","Chipset","Socket")
            VALUES (%s,%s,%s,%s,%s,%s)
        """,(component_id,cpu["cores"],cpu["threads"],cpu["clock"],cpu["chipset"],cpu["socket"]))

        #adding matching motherboard
        mb = generate_motherboard(cpu)
        component_list.append(mb)
        component_id +=1
        cur.execute("""
            INSERT INTO "Components" ("Id","Name","Brand","Type") VALUES (%s,%s,%s,%s)
        """,(component_id,mb["name"],mb["brand"],mb["type"]))
        cur.execute("""
            INSERT INTO "Motherboards" ("Id_component","Chipset","Socket_type","RAM_type")
            VALUES (%s,%s,%s,%s)
        """,(component_id,mb["chipset"],mb["socket"],mb["ram_type"]))

    elif ctype == "GPU":
        gpu = generate_gpu()
        component_list.append(gpu)
        cur.execute("""
            INSERT INTO "Components" ("Id","Name","Brand","Type") VALUES (%s,%s,%s,%s)
        """,(component_id,gpu["name"],gpu["brand"],gpu["type"]))
        cur.execute("""
            INSERT INTO "GPUs" ("Id_component","VRAM","VRAM_type") VALUES (%s,%s,%s)
        """,(component_id,gpu["vram"],gpu["vram_type"]))

    elif ctype == "RAM":
        ram = generate_ram()
        component_list.append(ram)
        cur.execute("""
            INSERT INTO "Components" ("Id","Name","Brand","Type") VALUES (%s,%s,%s,%s)
        """,(component_id,ram["name"],ram["brand"],ram["type"]))
        cur.execute("""
            INSERT INTO "RAMs" ("Id_component","Memory","Socket_type","Clock") VALUES (%s,%s,%s,%s)
        """,(component_id,ram["memory"],ram["socket_type"],ram["clock"]))

    elif ctype == "PSU":
        psu = generate_psu()
        component_list.append(psu)
        cur.execute("""
            INSERT INTO "Components" ("Id","Name","Brand","Type") VALUES (%s,%s,%s,%s)
        """,(component_id,psu["name"],psu["brand"],psu["type"]))
        cur.execute("""
            INSERT INTO "PSUs" ("Id_component","Power") VALUES (%s,%s)
        """,(component_id,psu["power"]))

    elif ctype == "Disk":
        disk = generate_disk()
        component_list.append(disk)
        cur.execute("""
            INSERT INTO "Components" ("Id","Name","Brand","Type") VALUES (%s,%s,%s,%s)
        """,(component_id,disk["name"],disk["brand"],disk["type"]))
        cur.execute("""
            INSERT INTO "Disks" ("Id_component","Memory","Disk_type") VALUES (%s,%s,%s)
        """,(component_id,disk["memory"],disk["disk_type"]))

    component_id +=1

#
#Exporter offers generator
#
for i in range(1, total_components+1):
    cur.execute("""
        INSERT INTO "Exporter_offers" ("Id","Id_exporter","Id_component","Price")
        VALUES (%s,%s,%s,%s)
    """,(i,random.randint(1,exporters_count),i,round(random.uniform(50,2000),2)))

#Imports to shops generator
for i in range(1, 51):
    delivery_start = datetime.now() - timedelta(days=random.randint(0,30))
    delivery_end = delivery_start + timedelta(days=random.randint(1,10))
    cur.execute("""
        INSERT INTO "Imports" ("Id","Id_component","Id_shop","Id_exporter","Delivery_type",
        "Delivery_placement_date","Expected_delivery_date","Real_delivery_date",
        "Component_quantity","Sum_of_import")
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,(i,random.randint(1,total_components),random.randint(1,shops_count),
          random.randint(1,exporters_count),random.choice(['Air','Sea','Land']),
          delivery_start,delivery_end,delivery_end + timedelta(days=random.randint(0,2)),
          random.randint(1,50),round(random.uniform(100,10000),2)))

#Sales generator
for i in range(1, 101):
    sale_date = datetime.now() - timedelta(days=random.randint(0,60))
    cur.execute("""
        INSERT INTO "Sales" ("Id","Id_component","Id_client","Id_shop","Date_of_sell","Price","Quantity")
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """,(i,random.randint(1,total_components),random.randint(1,clients_count),
          random.randint(1,shops_count),sale_date,round(random.uniform(50,2000),2),random.randint(1,5)))

#Database committing and closing
conn.commit()
cur.close()
conn.close()

print("Your database was successfully filled with random data!")
