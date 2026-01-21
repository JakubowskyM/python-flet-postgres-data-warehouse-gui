class OLAPQueries:
    """Klasa przechowująca wszystkie zapytania OLAP z pełną parametryzacją"""
    
    QUERIES = {
        "grouping": {
            "name": "Grupowanie danych z kilku tabel",
            "description": "Analiza sprzedaży według typu komponentu, województwa i sklepu",
            "sql": """
                SELECT 
                    c.Type as typ_komponentu,
                    c.Brand as marka,
                    a.Voivodeship as wojewodztwo,
                    s.Name as nazwa_sklepu,
                    COUNT(sa.Id) as liczba_transakcji,
                    SUM(sa.Quantity) as suma_sztuk,
                    SUM(sa.Price * sa.Quantity) as calkowity_przychod,
                    AVG(sa.Price) as srednia_cena
                FROM Sales sa
                JOIN Components c ON sa.Id_component = c.Id
                JOIN Shops s ON sa.Id_shop = s.Id
                JOIN Addresses a ON s.Id_address = a.Id
                WHERE 
                    EXTRACT(YEAR FROM sa.Date_of_sell) = %s
                    AND c.Type = %s
                GROUP BY c.Type, c.Brand, a.Voivodeship, s.Name
                ORDER BY calkowity_przychod DESC
            """,
            "params": [
                {"name": "rok", "type": "number", "label": "Rok", "default": 2024},
                {"name": "typ_komponentu", "type": "select", "label": "Typ komponentu", 
                 "options": ["CPU", "GPU", "RAM", "PSU", "Disk", "Motherboard"]}
            ],
            "columns": ["Typ komponentu", "Marka", "Województwo", "Sklep", 
                       "Liczba transakcji", "Suma sztuk", "Przychód", "Średnia cena"]
        },
        
        "rollup": {
            "name": "Roll-up (Zwijanie)",
            "description": "Agregacja sprzedaży na poziomie kwartalnym",
            "sql": """
                SELECT 
                    EXTRACT(YEAR FROM Date_of_sell) as rok,
                    EXTRACT(QUARTER FROM Date_of_sell) as kwartal,
                    c.Type as typ_komponentu,
                    COUNT(*) as liczba_sprzedazy,
                    SUM(Price * Quantity) as przychod
                FROM Sales
                JOIN Components c ON Sales.Id_component = c.Id
                WHERE EXTRACT(YEAR FROM Date_of_sell) BETWEEN %s AND %s
                GROUP BY 
                    EXTRACT(YEAR FROM Date_of_sell),
                    EXTRACT(QUARTER FROM Date_of_sell),
                    c.Type
                ORDER BY rok, kwartal
            """,
            "params": [
                {"name": "rok_od", "type": "number", "label": "Rok od", "default": 2023},
                {"name": "rok_do", "type": "number", "label": "Rok do", "default": 2024}
            ],
            "columns": ["Rok", "Kwartał", "Typ komponentu", "Liczba sprzedaży", "Przychód"]
        },
        
        "drilldown": {
            "name": "Drill-down (Rozwijanie)",
            "description": "Szczegółowa analiza geograficzna: województwo → miasto → ulica → sklep",
            "sql": """
                SELECT 
                    a.Voivodeship as wojewodztwo,
                    a.Town as miasto,
                    a.Street_name as ulica,
                    s.Name as sklep,
                    c.Type as typ_komponentu,
                    c.Brand as marka,
                    COUNT(*) as liczba_sprzedazy,
                    SUM(sa.Price * sa.Quantity) as przychod
                FROM Sales sa
                JOIN Shops s ON sa.Id_shop = s.Id
                JOIN Addresses a ON s.Id_address = a.Id
                JOIN Components c ON sa.Id_component = c.Id
                WHERE 
                    EXTRACT(YEAR FROM sa.Date_of_sell) = %s
                    AND a.Voivodeship = %s
                GROUP BY 
                    a.Voivodeship, a.Town, a.Street_name, 
                    s.Name, c.Type, c.Brand
                ORDER BY a.Voivodeship, a.Town, a.Street_name
            """,
            "params": [
                {"name": "rok", "type": "number", "label": "Rok", "default": 2024},
                {"name": "wojewodztwo", "type": "text", "label": "Województwo", "default": "Małopolskie"}
            ],
            "columns": ["Województwo", "Miasto", "Ulica", "Sklep", "Typ", "Marka", "Sprzedaż", "Przychód"]
        },
        
        "slice": {
            "name": "Slice (Selekcja)",
            "description": "Analiza tylko GPU - fiksowanie wymiaru typu komponentu",
            "sql": """
                SELECT 
                    c.Brand as marka,
                    g.VRAM as vram,
                    g.VRAM_type as typ_vram,
                    EXTRACT(YEAR FROM s.Date_of_sell) as rok,
                    EXTRACT(MONTH FROM s.Date_of_sell) as miesiac,
                    COUNT(*) as liczba_sprzedazy,
                    SUM(s.Price * s.Quantity) as przychod,
                    AVG(s.Price) as srednia_cena
                FROM Sales s
                JOIN Components c ON s.Id_component = c.Id
                JOIN GPUs g ON c.Id = g.Id_component
                WHERE c.Type = 'GPU'
                  AND EXTRACT(YEAR FROM s.Date_of_sell) = %s
                GROUP BY c.Brand, g.VRAM, g.VRAM_type, rok, miesiac
                ORDER BY przychod DESC
            """,
            "params": [
                {"name": "rok", "type": "number", "label": "Rok", "default": 2024}
            ],
            "columns": ["Marka", "VRAM", "Typ VRAM", "Rok", "Miesiąc", "Sprzedaż", "Przychód", "Średnia cena"]
        },
        
        "dice": {
            "name": "Dice (Filtrowanie)",
            "description": "Przekrój przez wiele wymiarów: CPU + rok + kwartał + województwo + marka",
            "sql": """
                SELECT 
                    c.Brand as marka,
                    cpu.Cores as rdzenie,
                    cpu.Socket as socket,
                    a.Town as miasto,
                    s.Name as sklep,
                    COUNT(*) as liczba_sprzedazy,
                    SUM(sa.Price * sa.Quantity) as przychod
                FROM Sales sa
                JOIN Components c ON sa.Id_component = c.Id
                JOIN CPUs cpu ON c.Id = cpu.Id_component
                JOIN Shops s ON sa.Id_shop = s.Id
                JOIN Addresses a ON s.Id_address = a.Id
                WHERE 
                    c.Type = 'CPU'
                    AND EXTRACT(YEAR FROM sa.Date_of_sell) = %s
                    AND EXTRACT(QUARTER FROM sa.Date_of_sell) = %s
                    AND a.Voivodeship = %s
                    AND c.Brand = %s
                GROUP BY c.Brand, cpu.Cores, cpu.Socket, a.Town, s.Name
                ORDER BY przychod DESC
            """,
            "params": [
                {"name": "rok", "type": "number", "label": "Rok", "default": 2024},
                {"name": "kwartal", "type": "number", "label": "Kwartał (1-4)", "default": 1},
                {"name": "wojewodztwo", "type": "text", "label": "Województwo", "default": "Małopolskie"},
                {"name": "marka", "type": "text", "label": "Marka CPU", "default": "Intel"}
            ],
            "columns": ["Marka", "Rdzenie", "Socket", "Miasto", "Sklep", "Sprzedaż", "Przychód"]
        },
        
        "drillacross": {
            "name": "Drill-across (Zawężanie)",
            "description": "Porównanie importów i sprzedaży - analiza rentowności",
            "sql": """
                SELECT 
                    c.Type as typ_komponentu,
                    c.Brand as marka,
                    c.Name as nazwa,
                    COALESCE(SUM(i.Component_quantity), 0) as importowane_sztuki,
                    COALESCE(SUM(i.Sum_of_import), 0) as koszt_importu,
                    COALESCE(SUM(s.Quantity), 0) as sprzedane_sztuki,
                    COALESCE(SUM(s.Price * s.Quantity), 0) as przychod_ze_sprzedazy,
                    COALESCE(SUM(s.Price * s.Quantity), 0) - COALESCE(SUM(i.Sum_of_import), 0) as zysk_brutto
                FROM Components c
                LEFT JOIN Imports i ON c.Id = i.Id_component 
                    AND EXTRACT(YEAR FROM i.Real_delivery_date) = %s
                LEFT JOIN Sales s ON c.Id = s.Id_component 
                    AND EXTRACT(YEAR FROM s.Date_of_sell) = %s
                WHERE c.Type = %s
                GROUP BY c.Type, c.Brand, c.Name
                HAVING SUM(i.Component_quantity) > 0 OR SUM(s.Quantity) > 0
                ORDER BY zysk_brutto DESC
            """,
            "params": [
                {"name": "rok_import", "type": "number", "label": "Rok importu", "default": 2024},
                {"name": "rok_sprzedaz", "type": "number", "label": "Rok sprzedaży", "default": 2024},
                {"name": "typ_komponentu", "type": "select", "label": "Typ komponentu",
                 "options": ["CPU", "GPU", "RAM", "PSU", "Disk", "Motherboard"]}
            ],
            "columns": ["Typ", "Marka", "Nazwa", "Import szt.", "Koszt importu", 
                       "Sprzedaż szt.", "Przychód", "Zysk brutto"]
        },
        
        "pivot": {
            "name": "Pivot (Obracanie)",
            "description": "Marki w kolumnach, miesiące w wierszach",
            "sql": """
                SELECT 
                    EXTRACT(YEAR FROM s.Date_of_sell) as rok,
                    EXTRACT(MONTH FROM s.Date_of_sell) as miesiac,
                    SUM(CASE WHEN c.Brand = 'Intel' THEN s.Price * s.Quantity ELSE 0 END) as Intel,
                    SUM(CASE WHEN c.Brand = 'AMD' THEN s.Price * s.Quantity ELSE 0 END) as AMD,
                    SUM(CASE WHEN c.Brand = 'NVIDIA' THEN s.Price * s.Quantity ELSE 0 END) as NVIDIA,
                    SUM(CASE WHEN c.Brand = 'Corsair' THEN s.Price * s.Quantity ELSE 0 END) as Corsair,
                    SUM(CASE WHEN c.Brand = 'Kingston' THEN s.Price * s.Quantity ELSE 0 END) as Kingston,
                    SUM(CASE WHEN c.Brand = 'Samsung' THEN s.Price * s.Quantity ELSE 0 END) as Samsung,
                    SUM(s.Price * s.Quantity) as Total
                FROM Sales s
                JOIN Components c ON s.Id_component = c.Id
                WHERE 
                    EXTRACT(YEAR FROM s.Date_of_sell) = %s
                    AND c.Type = %s
                GROUP BY rok, miesiac
                ORDER BY rok, miesiac
            """,
            "params": [
                {"name": "rok", "type": "number", "label": "Rok", "default": 2024},
                {"name": "typ_komponentu", "type": "select", "label": "Typ komponentu",
                 "options": ["CPU", "GPU", "RAM", "PSU", "Disk", "Motherboard"]}
            ],
            "columns": ["Rok", "Miesiąc", "Intel", "AMD", "NVIDIA", "Corsair", "Kingston", "Samsung", "Total"]
        }
    }
    
    @staticmethod
    def get_query(query_type):
        """Zwraca definicję zapytania"""
        return OLAPQueries.QUERIES.get(query_type)
    
    @staticmethod
    def get_all_queries():
        """Zwraca listę wszystkich dostępnych zapytań"""
        return [(k, v["name"]) for k, v in OLAPQueries.QUERIES.items()]
    
    @staticmethod
    def execute_query(conn, query_type, params):
        """Wykonuje zapytanie z parametryzacją"""
        query_def = OLAPQueries.get_query(query_type)
        if not query_def:
            raise ValueError(f"Nieznany typ zapytania: {query_type}")
        
        cursor = conn.cursor()
        cursor.execute(query_def["sql"], params)
        results = cursor.fetchall()
        cursor.close()
        
        return {
            "columns": query_def["columns"],
            "rows": results,
            "row_count": len(results)
        }