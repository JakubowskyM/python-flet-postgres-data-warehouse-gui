import csv
import os
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('pl_PL')


PL_CITIES = {
    "mazowieckie": ["Warszawa", "Radom", "Płock", "Siedlce", "Ostrołęka", "Pruszków", "Legionowo", "Piaseczno", "Mińsk Mazowiecki"],
    "małopolskie": ["Kraków", "Tarnów", "Nowy Sącz", "Oświęcim", "Zakopane", "Wadowice", "Chrzanów", "Bochnia"],
    "śląskie": ["Katowice", "Gliwice", "Zabrze", "Rybnik", "Częstochowa", "Sosnowiec", "Bytom", "Tychy", "Dąbrowa Górnicza", "Bielsko-Biała", "Jaworzno"],
    "wielkopolskie": ["Poznań", "Kalisz", "Konin", "Leszno", "Piła", "Gniezno", "Ostrów Wielkopolski", "Krotoszyn"],
    "dolnośląskie": ["Wrocław", "Legnica", "Wałbrzych", "Jelenia Góra", "Lubin", "Świdnica", "Głogów", "Bolesławiec"],
    "pomorskie": ["Gdańsk", "Gdynia", "Sopot", "Słupsk", "Wejherowo", "Rumia", "Starogard Gdański", "Tczew"],
    "zachodniopomorskie": ["Szczecin", "Koszalin", "Stargard", "Kołobrzeg", "Świnoujście", "Szczecinek"],
    "lubelskie": ["Lublin", "Chełm", "Zamość", "Biała Podlaska", "Puławy", "Świdnik", "Kraśnik"],
    "łódzkie": ["Łódź", "Piotrków Trybunalski", "Tomaszów Mazowiecki", "Bełchatów", "Skierniewice", "Zgierz", "Pabianice"],
    "podkarpackie": ["Rzeszów", "Przemyśl", "Stalowa Wola", "Mielec", "Tarnobrzeg", "Krosno", "Sanok", "Jarosław"],
    "kujawsko-pomorskie": ["Bydgoszcz", "Toruń", "Włocławek", "Grudziądz", "Inowrocław", "Brodnica"],
    "warmińsko-mazurskie": ["Olsztyn", "Elbląg", "Ełk", "Ostróda", "Giżycko", "Iława"],
    "podlaskie": ["Białystok", "Suwałki", "Łomża", "Augustów", "Zambrów", "Bielsk Podlaski"],
    "opolskie": ["Opole", "Kędzierzyn-Koźle", "Nysa", "Brzeg", "Kluczbork", "Prudnik"],
    "lubuskie": ["Gorzów Wielkopolski", "Zielona Góra", "Nowa Sól", "Żary", "Żagań", "Świebodzin"],
    "świętokrzyskie": ["Kielce", "Ostrowiec Świętokrzyski", "Starachowice", "Skarżysko-Kamienna", "Sandomierz", "Końskie"]
}

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

# Functions for components
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

def generate_address():
    voivodeship = random.choice(list(PL_CITIES.keys()))
    city = random.choice(PL_CITIES[voivodeship])

    return {
        "voivodeship": voivodeship,
        "town": city,
        "postal_code": fake.postcode(),
        "street": fake.street_name(),
        "house_number": fake.building_number()
    }


# Main CSV generator
def generate_csv_files(*, addresses_count = 50, shops_count = 5, clients_count = 500,
                       exporters_count = 15, total_components = 2000):

    os.makedirs("tables", exist_ok=True)


    # Addresses
    addresses = []
    with open("tables/addresses.csv", "w", newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","voivodeship","town","postal_code","street_name","house_number"])
        for i in range(1, addresses_count+1):
            town_and_voivodeship = generate_address()
            writer.writerow([i, town_and_voivodeship["voivodeship"], town_and_voivodeship["town"], town_and_voivodeship["postal_code"], town_and_voivodeship["street"], town_and_voivodeship["house_number"]])
            addresses.append(i)

    # Shops
    shops = []
    with open("tables/shops.csv", "w", newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","id_address","name"])
        for i in range(1, shops_count+1):
            address_id = random.choice(addresses)
            writer.writerow([i, address_id, fake.company()])
            shops.append(i)

    # Clients
    clients = []
    with open("tables/clients.csv", "w", newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","name","surname","id_address"])
        for i in range(1, clients_count+1):
            address_id = random.choice(addresses)
            writer.writerow([i, fake.first_name(), fake.last_name(), address_id])
            clients.append(i)

    # Exporters
    exporters = []
    countries = ['Poland','Germany','USA','China','Japan']
    with open("tables/exporters.csv", "w", newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","name","country"])
        for i in range(1, exporters_count+1):
            writer.writerow([i, fake.company(), random.choice(countries)])
            exporters.append(i)

    # Components
    component_ids = []
    with open("tables/components.csv", "w", newline='', encoding='utf-8-sig') as f_comp, \
        open("tables/cpus.csv", "w", newline='', encoding='utf-8-sig') as f_cpu, \
        open("tables/gpus.csv", "w", newline='', encoding='utf-8-sig') as f_gpu, \
        open("tables/rams.csv", "w", newline='', encoding='utf-8-sig') as f_ram, \
        open("tables/psus.csv", "w", newline='', encoding='utf-8-sig') as f_psu, \
        open("tables/disks.csv", "w", newline='', encoding='utf-8-sig') as f_disk, \
        open("tables/motherboards.csv", "w", newline='', encoding='utf-8-sig') as f_mb:

        w_comp = csv.writer(f_comp)
        w_cpu = csv.writer(f_cpu)
        w_gpu = csv.writer(f_gpu)
        w_ram = csv.writer(f_ram)
        w_psu = csv.writer(f_psu)
        w_disk = csv.writer(f_disk)
        w_mb = csv.writer(f_mb)

        w_comp.writerow(["id","name","brand","type"])
        w_cpu.writerow(["id_component","cores","threads","clock_speed","chipset","socket"])
        w_gpu.writerow(["id_component","vram","vram_type"])
        w_ram.writerow(["id_component","memory","socket_type","clock"])
        w_psu.writerow(["id_component","power"])
        w_disk.writerow(["id_component","memory","disk_type"])
        w_mb.writerow(["id_component","chipset","socket_type","ram_type"])

        cid = 1
        while cid <= total_components:
            ctype = random.choice(["CPU","GPU","RAM","PSU","Disk"])
            if ctype == "CPU":
                cpu = generate_cpu()
                w_comp.writerow([cid, cpu["name"], cpu["brand"], cpu["type"]])
                w_cpu.writerow([cid, cpu["cores"], cpu["threads"], cpu["clock"], cpu["chipset"], cpu["socket"]])
                component_ids.append(cid)
                cid += 1
                mb = generate_motherboard(cpu)
                w_comp.writerow([cid, mb["name"], mb["brand"], mb["type"]])
                w_mb.writerow([cid, mb["chipset"], mb["socket"], mb["ram_type"]])
                component_ids.append(cid)
            elif ctype == "GPU":
                gpu = generate_gpu()
                w_comp.writerow([cid, gpu["name"], gpu["brand"], gpu["type"]])
                w_gpu.writerow([cid, gpu["vram"], gpu["vram_type"]])
                component_ids.append(cid)
            elif ctype == "RAM":
                ram = generate_ram()
                w_comp.writerow([cid, ram["name"], ram["brand"], ram["type"]])
                w_ram.writerow([cid, ram["memory"], ram["socket_type"], ram["clock"]])
                component_ids.append(cid)
            elif ctype == "PSU":
                psu = generate_psu()
                w_comp.writerow([cid, psu["name"], psu["brand"], psu["type"]])
                w_psu.writerow([cid, psu["power"]])
                component_ids.append(cid)
            elif ctype == "Disk":
                disk = generate_disk()
                w_comp.writerow([cid, disk["name"], disk["brand"], disk["type"]])
                w_disk.writerow([cid, disk["memory"], disk["disk_type"]])
                component_ids.append(cid)
            cid += 1

    # Exporter_offers
    with open("tables/exporter_offers.csv","w",newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","id_exporter","id_component","price"])
        for i, comp_id in enumerate(component_ids, 1):
            writer.writerow([i, random.choice(exporters), comp_id, round(random.uniform(50,2000),2)])

    # Imports
    with open("tables/imports.csv","w",newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","id_component","id_shop","id_exporter","delivery_type",
                        "delivery_placement_date","expected_delivery_date","real_delivery_date",
                        "component_quantity","sum_of_import"])
        for i in range(1,51):
            comp_id = random.choice(component_ids)
            shop_id = random.choice(shops)
            exporter_id = random.choice(exporters)
            delivery_start = fake.date_between(start_date='-365d', end_date='-345d')
            delivery_end = delivery_start + timedelta(days=random.randint(1,14))
            writer.writerow([i, comp_id, shop_id, exporter_id, random.choice(['Air','Sea','Land']),
                            delivery_start, delivery_end, delivery_end + timedelta(days=random.randint(0,2)),
                            random.randint(1,50), round(random.uniform(100,10000),2)])

    # Sales
    with open("tables/sales.csv","w",newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","id_component","id_client","id_shop","date_of_sell","price","quantity"])
        for i in range(1,101):
            comp_id = random.choice(component_ids)
            client_id = random.choice(clients)
            shop_id = random.choice(shops)
            sale_date = datetime.now() - timedelta(days=random.randint(0,60))
            writer.writerow([i, comp_id, client_id, shop_id, sale_date, round(random.uniform(50,2000),2), random.randint(1,5)])

    return 1
