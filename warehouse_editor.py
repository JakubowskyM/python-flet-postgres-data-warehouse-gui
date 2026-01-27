import flet as ft

ROWS_PER_PAGE = 20

TABLE_CONFIG = {
    "Clients": ["id", "name", "surname", "id_address"],
    "Shops": ["id", "name", "id_address"],
    "Components": ["id", "name", "brand", "type"],
    "Exporters": ["id", "name", "country"],
    "Addresses": ["id", "voivodeship", "town", "postal_code", "street_name", "house_number"],
}


DELETE_CASCADE_MAP = {
    "Addresses": {
        "Shops": "id_address",
        "Clients": "id_address"
    },
    "Components": {
        "CPUs": "id_component",
        "GPUs": "id_component",
        "RAMs": "id_component",
        "PSUs": "id_component",
        "Disks": "id_component",
        "Motherboards": "id_component",
        "Sales": "id_component",
        "Imports": "id_component",
        "Exporter_offers": "id_component"
    },
    "Clients": {
        "Sales": "id_client"
    },
    "Shops": {
        "Sales": "id_shop",
        "Imports": "id_shop"
    },
    "Exporters": {
        "Imports": "id_exporter",
        "Exporter_offers": "id_exporter"
    },
}


def get_tables():
    return list(TABLE_CONFIG.keys())


def fetch_table_data(conn, table_name, page_number):
    """Zwraca wiersze z tabeli z paginacją"""
    offset = page_number * ROWS_PER_PAGE
    cols = ", ".join(TABLE_CONFIG[table_name])
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT {cols} FROM {table_name} ORDER BY id LIMIT %s OFFSET %s",
            (ROWS_PER_PAGE, offset),
        )
        return cur.fetchall()


def update_record(conn, table_name, record_id, data_dict):
    """Aktualizuje wybrany rekord w tabeli"""
    sets = ", ".join(f"{k}=%s" for k in data_dict.keys())
    values = list(data_dict.values()) + [record_id]
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {table_name} SET {sets} WHERE id=%s", values)
        conn.commit()


def delete_record(conn, table_name, record_id):
    """Usuwa rekord wraz z wszystkimi powiązaniami (CASCADE)"""
    with conn.cursor() as cur:

        if table_name in DELETE_CASCADE_MAP:
            for dependent_table, foreign_key in DELETE_CASCADE_MAP[table_name].items():
                cur.execute(
                    f"DELETE FROM {dependent_table} WHERE {foreign_key} = %s",
                    (record_id,)
                )

        cur.execute(f"DELETE FROM {table_name} WHERE id = %s", (record_id,))
        conn.commit()


def insert_record(conn, table_name, data_dict):
    """Wstawia nowy rekord do tabeli"""
    columns = list(data_dict.keys())
    placeholders = ", ".join(["%s"] * len(columns))
    cols_str = ", ".join(columns)
    values = list(data_dict.values())
    
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})",
            values
        )
        conn.commit()


def get_next_id(conn, table_name):
    """Pobiera następne dostępne ID dla tabeli"""
    with conn.cursor() as cur:
        cur.execute(f"SELECT MAX(id) FROM {table_name}")
        result = cur.fetchone()[0]
        return (result or 0) + 1


def get_table_columns(table_name):
    """Zwraca listę kolumn dla danej tabeli"""
    return TABLE_CONFIG[table_name]


def create_back_button(page, dashboard_func, conn):
    """Przycisk powrotu do dashboardu"""
    return ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        tooltip="Powrót do dashboardu",
        icon_color=ft.Colors.BLUE_GREY_800,
        on_click=lambda e: dashboard_func(conn, page),
    )