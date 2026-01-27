import psycopg2

class OLAPQueries:
    """Klasa przechowująca 7 zapytań OLAP z pełną parametryzacją"""
    
    QUERIES = {
        "grouping": {
            "name": "Grupowanie (Produkty)",
            "description": "Analiza sprzedaży konkretnych modeli (Name) według regionu i sklepu",
            "sql": """
                SELECT 
                    c.name AS nazwa_produktu,
                    c.brand AS marka,
                    a.voivodeship AS wojewodztwo,
                    s.name AS nazwa_sklepu,
                    COUNT(sa.id) AS liczba_transakcji,
                    SUM(sa.quantity) AS suma_sztuk,
                    ROUND(SUM(sa.price * sa.quantity)::numeric, 2) AS calkowity_przychod,
                    ROUND(AVG(sa.price)::numeric, 2) AS srednia_cena
                FROM sales sa
                JOIN components c ON sa.id_component = c.id
                JOIN shops s ON sa.id_shop = s.id
                JOIN addresses a ON s.id_address = a.id
                WHERE EXTRACT(YEAR FROM sa.date_of_sell) = %s
                  AND c.type = %s
                GROUP BY c.name, c.brand, a.voivodeship, s.name
                ORDER BY calkowity_przychod DESC
            """,
            "params": [
                {"name": "rok", "type": "number", "label": "Rok", "default": 2026},
                {"name": "typ", "type": "select", "label": "Typ komponentu", 
                 "options": ["CPU", "GPU", "RAM", "PSU", "Disk", "Motherboard"]}
            ],
            "columns": ["Produkt", "Marka", "Województwo", "Sklep", "Transakcje", "Sztuki", "Przychód", "Średnia Cena"]
        },
        
        "rollup": {
            "name": "Roll-up (Zwijanie)",
            "description": "Agregacja sprzedaży na poziomie kwartalnym dla danej marki",
            "sql": """
                SELECT 
                    EXTRACT(YEAR FROM sa.date_of_sell) AS rok,
                    EXTRACT(QUARTER FROM sa.date_of_sell) AS kwartal,
                    c.brand AS marka,
                    COUNT(*) AS liczba_sprzedazy,
                    ROUND(SUM(sa.price * sa.quantity)::numeric, 2) AS przychod
                FROM sales sa
                JOIN components c ON sa.id_component = c.id
                WHERE EXTRACT(YEAR FROM sa.date_of_sell) BETWEEN %s AND %s
                GROUP BY rok, kwartal, c.brand
                ORDER BY rok, kwartal, przychod DESC
            """,
            "params": [
                {"name": "rok_od", "type": "number", "label": "Rok od", "default": 2025},
                {"name": "rok_do", "type": "number", "label": "Rok do", "default": 2026}
            ],
            "columns": ["Rok", "Kwartał", "Marka", "Liczba sprzedaży", "Przychód"]
        },
        
        "drilldown": {
            "name": "Drill-down (Rozwijanie)",
            "description": "Szczegółowa analiza geograficzna sprzedaży",
            "sql": """
                SELECT 
                    a.voivodeship AS wojewodztwo,
                    a.town AS miasto,
                    a.street_name AS ulica,
                    s.name AS sklep,
                    ROUND(SUM(sa.price * sa.quantity)::numeric, 2) AS przychod
                FROM sales sa
                JOIN shops s ON sa.id_shop = s.id
                JOIN addresses a ON s.id_address = a.id
                WHERE EXTRACT(YEAR FROM sa.date_of_sell) = %s
                  AND a.voivodeship = %s
                GROUP BY a.voivodeship, a.town, a.street_name, s.name
                ORDER BY przychod DESC
            """,
            "params": [
                {"name": "rok", "type": "number", "label": "Rok", "default": 2026},
                {"name": "woj", "type": "text", "label": "Województwo", "default": "mazowieckie"}
            ],
            "columns": ["Województwo", "Miasto", "Ulica", "Sklep", "Przychód"]
        },
        
        "slice": {
            "name": "Slice (Selekcja)",
            "description": "Analiza wybranego typu komponentu w czasie",
            "sql": """
                SELECT 
                    c.brand AS marka,
                    c.name AS model,
                    EXTRACT(MONTH FROM sa.date_of_sell) AS miesiac,
                    COUNT(*) AS liczba_sprzedazy,
                    ROUND(SUM(sa.price * sa.quantity)::numeric, 2) AS przychod
                FROM sales sa
                JOIN components c ON sa.id_component = c.id
                WHERE c.type = %s 
                  AND EXTRACT(YEAR FROM sa.date_of_sell) = %s
                GROUP BY c.brand, c.name, miesiac
                ORDER BY miesiac, przychod DESC
            """,
            "params": [
                {"name": "typ", "type": "select", "label": "Wybierz typ", 
                 "options": ["CPU", "GPU", "RAM", "PSU", "Disk", "Motherboard"]},
                {"name": "rok", "type": "number", "label": "Rok", "default": 2026}
            ],
            "columns": ["Marka", "Model", "Miesiąc", "Sprzedaż", "Przychód"]
        },
        
        "dice": {
            "name": "Dice (Filtrowanie)",
            "description": "Przekrój przez typ, rok, kwartał i województwo",
            "sql": """
                SELECT 
                    c.brand AS marka,
                    c.name AS model,
                    a.town AS miasto,
                    COUNT(*) AS liczba_sprzedazy,
                    ROUND(SUM(sa.price * sa.quantity)::numeric, 2) AS przychod
                FROM sales sa
                JOIN components c ON sa.id_component = c.id
                JOIN shops s ON sa.id_shop = s.id
                JOIN addresses a ON s.id_address = a.id
                WHERE c.type = %s
                  AND EXTRACT(YEAR FROM sa.date_of_sell) = %s
                  AND EXTRACT(QUARTER FROM sa.date_of_sell) = %s
                  AND a.voivodeship = %s
                GROUP BY c.brand, c.name, a.town
                ORDER BY przychod DESC
            """,
            "params": [
                {"name": "typ", "type": "select", "label": "Typ komponentu", 
                 "options": ["CPU", "GPU", "RAM", "PSU", "Disk", "Motherboard"]},
                {"name": "rok", "type": "number", "label": "Rok", "default": 2026},
                {"name": "kwartal", "type": "number", "label": "Kwartał", "default": 1},
                {"name": "woj", "type": "text", "label": "Województwo", "default": "mazowieckie"}
            ],
            "columns": ["Marka", "Model", "Miasto", "Sprzedaż", "Przychód"]
        },
        
        "drillacross": {
            "name": "Drill-across (Rentowność)",
            "description": "Zestawienie kosztów importu vs przychody ze sprzedaży",
            "sql": """
                WITH import_stats AS (
                    SELECT id_component, 
                           SUM(component_quantity) AS total_imp_qty,
                           SUM(sum_of_import) AS total_imp_cost
                    FROM imports 
                    GROUP BY id_component
                ),
                sales_stats AS (
                    SELECT id_component,
                           SUM(quantity) AS total_sold_qty,
                           SUM(price * quantity) AS total_revenue
                    FROM sales
                    GROUP BY id_component
                )
                SELECT 
                    c.name AS produkt,
                    c.type AS typ,
                    COALESCE(i.total_imp_qty, 0) AS zaimportowano,
                    ROUND(COALESCE(i.total_imp_cost, 0)::numeric, 2) AS koszt_importu,
                    COALESCE(s.total_sold_qty, 0) AS sprzedano,
                    ROUND(COALESCE(s.total_revenue, 0)::numeric, 2) AS przychod_sprzedaz,
                    ROUND((COALESCE(s.total_revenue, 0)::numeric - COALESCE(i.total_imp_cost, 0)::numeric), 2) AS zysk_brutto
                FROM components c
                LEFT JOIN import_stats i ON c.id = i.id_component
                LEFT JOIN sales_stats s ON c.id = s.id_component
                WHERE c.type = %s
                ORDER BY zysk_brutto DESC
            """,
            "params": [
                {"name": "typ", "type": "select", "label": "Typ do analizy", 
                 "options": ["CPU", "GPU", "RAM", "PSU", "Disk", "Motherboard"]}
            ],
            "columns": ["Produkt", "Typ", "Imp. Sztuk", "Koszt Importu", "Sprzedano", "Przychód", "Zysk/Strata"]
        },
        
        "pivot": {
            "name": "Pivot (Obracanie)",
            "description": "Przychody marek w ujęciu miesięcznym (zaokrąglone)",
            "sql": """
                SELECT 
                    EXTRACT(MONTH FROM sa.date_of_sell) AS miesiac,
                    ROUND(SUM(CASE WHEN c.brand = 'Intel' THEN sa.price * sa.quantity ELSE 0 END)::numeric, 2) AS Intel,
                    ROUND(SUM(CASE WHEN c.brand = 'AMD' THEN sa.price * sa.quantity ELSE 0 END)::numeric, 2) AS AMD,
                    ROUND(SUM(CASE WHEN c.brand = 'Nvidia' THEN sa.price * sa.quantity ELSE 0 END)::numeric, 2) AS Nvidia,
                    ROUND(SUM(CASE WHEN c.brand = 'Samsung' THEN sa.price * sa.quantity ELSE 0 END)::numeric, 2) AS Samsung,
                    ROUND(SUM(sa.price * sa.quantity)::numeric, 2) AS Suma
                FROM sales sa
                JOIN components c ON sa.id_component = c.id
                WHERE EXTRACT(YEAR FROM sa.date_of_sell) = %s
                  AND c.type = %s
                GROUP BY miesiac
                ORDER BY miesiac
            """,
            "params": [
                {"name": "rok", "type": "number", "label": "Rok", "default": 2026},
                {"name": "typ", "type": "select", "label": "Typ", 
                 "options": ["CPU", "GPU", "RAM", "PSU", "Disk", "Motherboard"]}
            ],
            "columns": ["Miesiąc", "Intel", "AMD", "Nvidia", "Samsung", "Suma Łączna"]
        }
    }

    @staticmethod
    def get_query(query_type):
        return OLAPQueries.QUERIES.get(query_type)
    
    @staticmethod
    def get_all_queries():
        return [(k, v["name"]) for k, v in OLAPQueries.QUERIES.items()]

    @staticmethod
    def execute_query(conn, query_type, params):
        query_def = OLAPQueries.get_query(query_type)
        cursor = conn.cursor()
        cursor.execute(query_def["sql"], tuple(params))
        results = cursor.fetchall()
        cursor.close()
        return {"columns": query_def["columns"], "rows": results, "row_count": len(results)}
