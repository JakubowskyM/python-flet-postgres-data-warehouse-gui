import csv
import os
import random
from faker import Faker
from datetime import datetime, timedelta, time
import math

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

def generate_price_with_step(min_val, max_val):
    base = random.randint(min_val, max_val)
    decimal = random.choice([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9])
    return round(base + decimal, 2)

# --- Komponenty z pełnymi kolumnami ---
def generate_cpu():
    brand = random.choice(brands["CPU"])
    chipset = random.choice(cpu_chipsets[brand])
    cores = random.randint(2,32)
    threads = random.randint(max(cores,4),64)
    clock = round(random.randrange(20,61)/10,1)
    socket = random.choice(cpu_sockets[brand])
    name = f"{brand} {chipset} {cores}/{threads}"
    return {"type":"CPU","brand":brand,"name":name,"cores":cores,"threads":threads,"clock_speed":clock,"chipset":chipset,"socket":socket}

def generate_gpu():
    brand = random.choice(brands["GPU"])
    vram = random.choice([4,6,8,12,16,24])
    vram_type = random.choice(["GDDR5","GDDR6","HBM2"])
    name = f"{brand} {vram}GB {vram_type}"
    return {"type":"GPU","brand":brand,"name":name,"vram":vram,"vram_type":vram_type}

def generate_ram():
    brand = random.choice(brands["RAM"])
    memory = random.choice([8,16,32,64])
    socket_type = random.choice(ram_types)
    clock = random.choice([2133,2400,2666,3000,3200,3600,4000])
    name = f"{brand} {memory}GB {clock}MHz"
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
    return {"type":"Disk","brand":brand,"name":name,"memory":capacity,"disk_type":disk_type}

def generate_motherboard(cpu_info):
    brand = random.choice(brands["Motherboard"])
    chipset = cpu_info["chipset"]
    socket = cpu_info["socket"]
    ram_type = random.choice(ram_types)
    name = f"{brand} {socket} {chipset} {ram_type}"
    return {"type":"Motherboard","brand":brand,"name":name,"chipset":chipset,"socket_type":socket,"ram_type":ram_type}

def generate_address():
    voivodeship = random.choice(list(PL_CITIES.keys()))
    city = random.choice(PL_CITIES[voivodeship])
    return {
        "voivodeship": voivodeship,
        "town": city,
        "postal_code": fake.postcode(),
        "street_name": fake.street_name(),
        "house_number": fake.building_number()
    }

# --- Główny generator CSV ---
def generate_csv_files(*, addresses_count = 50, shops_count = 5, clients_count = 300,
                        exporters_count = 10, total_components = 100):

    os.makedirs("tables", exist_ok=True)

    # --- Addresses ---
    addresses = []
    with open("tables/addresses.csv", "w", newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","voivodeship","town","postal_code","street_name","house_number"])
        for i in range(1, addresses_count+1):
            addr = generate_address()
            writer.writerow([i, addr["voivodeship"], addr["town"], addr["postal_code"], addr["street_name"], addr["house_number"]])
            addresses.append(i)

    # --- Shops ---
    shops = []
    with open("tables/shops.csv","w",newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","name","id_address"])
        for i in range(1, shops_count+1):
            writer.writerow([i, fake.company(), random.choice(addresses)])
            shops.append(i)

    # --- Clients ---
    clients = []
    with open("tables/clients.csv","w",newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","name","surname","id_address"])
        for i in range(1, clients_count+1):
            writer.writerow([i, fake.first_name(), fake.last_name(), random.choice(addresses)])
            clients.append(i)

    # --- Exporters ---
    exporters = []
    countries = ["Poland","Germany","USA","China","Japan"]
    with open("tables/exporters.csv","w",newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","name","country"])
        for i in range(1, exporters_count+1):
            writer.writerow([i, fake.company(), random.choice(countries)])
            exporters.append(i)

    # --- Components ---
    component_ids = []
    component_data = {}
    with open("tables/components.csv","w",newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","name","brand","type"])

    # Subtables
    subtable_files = {
        "CPU":"tables/cpus.csv",
        "GPU":"tables/gpus.csv",
        "RAM":"tables/rams.csv",
        "PSU":"tables/psus.csv",
        "Disk":"tables/disks.csv",
        "Motherboard":"tables/motherboards.csv"
    }
    for fpath in subtable_files.values():
        with open(fpath,"w",newline='',encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if "cpu" in fpath: writer.writerow(["id_component","cores","threads","clock_speed","chipset","socket"])
            elif "gpu" in fpath: writer.writerow(["id_component","vram","vram_type"])
            elif "ram" in fpath: writer.writerow(["id_component","memory","socket_type","clock"])
            elif "psu" in fpath: writer.writerow(["id_component","power"])
            elif "disk" in fpath: writer.writerow(["id_component","memory","disk_type"])
            elif "motherboard" in fpath: writer.writerow(["id_component","chipset","socket_type","ram_type"])

    # Generowanie komponentów
    for cid in range(1, total_components+1):
        ctype = random.choice(list(subtable_files.keys()))
        if ctype=="CPU":
            cpu = generate_cpu()
            with open("tables/components.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,cpu["name"],cpu["brand"],cpu["type"]])
            with open("tables/cpus.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,cpu["cores"],cpu["threads"],cpu["clock_speed"],cpu["chipset"],cpu["socket"]])
            component_data[cid]=cpu
        elif ctype=="GPU":
            gpu = generate_gpu()
            with open("tables/components.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,gpu["name"],gpu["brand"],gpu["type"]])
            with open("tables/gpus.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,gpu["vram"],gpu["vram_type"]])
            component_data[cid]=gpu
        elif ctype=="RAM":
            ram = generate_ram()
            with open("tables/components.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,ram["name"],ram["brand"],ram["type"]])
            with open("tables/rams.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,ram["memory"],ram["socket_type"],ram["clock"]])
            component_data[cid]=ram
        elif ctype=="PSU":
            psu = generate_psu()
            with open("tables/components.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,psu["name"],psu["brand"],psu["type"]])
            with open("tables/psus.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,psu["power"]])
            component_data[cid]=psu
        elif ctype=="Disk":
            disk = generate_disk()
            with open("tables/components.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,disk["name"],disk["brand"],disk["type"]])
            with open("tables/disks.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,disk["memory"],disk["disk_type"]])
            component_data[cid]=disk
        elif ctype=="Motherboard":
            mb = generate_motherboard(generate_cpu())
            with open("tables/components.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,mb["name"],mb["brand"],mb["type"]])
            with open("tables/motherboards.csv","a",newline='',encoding='utf-8-sig') as f:
                writer = csv.writer(f); writer.writerow([cid,mb["chipset"],mb["socket_type"],mb["ram_type"]])
            component_data[cid]=mb
        component_ids.append(cid)

    # --- Oferty eksportera ---
    comp_base_prices = {}
    with open("tables/exporter_offers.csv","w",newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","id_exporter","id_component","price"])
        for i, comp_id in enumerate(component_ids, 1):
            price = generate_price_with_step(50,2000)
            comp_base_prices[comp_id] = price
            writer.writerow([i, random.choice(exporters), comp_id, f"{price:.2f}"])

    # --- Importy ---
    import_records = []
    with open("tables/imports.csv","w",newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","id_component","id_shop","id_exporter","delivery_type",
                        "delivery_placement_date","expected_delivery_date","real_delivery_date",
                        "component_quantity","sum_of_import"])
        imp_id = 1
        for comp_id in component_ids:
            num_imports = random.randint(1,10)
            for _ in range(num_imports):
                shop_id = random.choice(shops)
                exporter_id = random.choice(exporters)
                delivery_start = fake.date_between(start_date='-365d', end_date='-345d')
                delivery_end = delivery_start + timedelta(days=random.randint(1,14))
                quantity = 1
                sum_import = comp_base_prices[comp_id] * quantity
                writer.writerow([imp_id, comp_id, shop_id, exporter_id,
                                 random.choice(['Air','Sea','Land']),
                                 delivery_start, delivery_end,
                                 delivery_end + timedelta(days=random.randint(0,2)),
                                 quantity, f"{sum_import:.2f}"])
                import_records.append({"comp_id": comp_id, "shop_id": shop_id, "quantity": quantity, "cost": sum_import,
                                       "delivery_start": delivery_start, "delivery_end": delivery_end})
                imp_id += 1

    # --- Sprzedaż ---
    with open("tables/sales.csv","w",newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["id","id_component","id_client","id_shop","date_of_sell","price","quantity"])
        sale_id = 1
        for record in import_records:
            comp_id = record["comp_id"]
            shop_id = record["shop_id"]
            num_sales = random.randint(1,5)
            for _ in range(num_sales):
                client_id = random.choice(clients)
                delivery_start = record["delivery_start"]
                random_time = time(hour=random.randint(8, 20), minute=random.randint(0, 59), second=random.randint(0, 59))
                sale_date = datetime.combine(delivery_start, random_time)
                base_price = comp_base_prices[comp_id]
                markup = random.uniform(1.10,1.15)
                final_price = math.floor(base_price * markup) + random.choice([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9])
                writer.writerow([sale_id, comp_id, client_id, shop_id, sale_date, f"{final_price:.2f}", 1])
                sale_id += 1

    return 1
