import flet as ft
import os
import sys
import browser as whb

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from colors import *
from olap_queries import OLAPQueries


def section(title, controls):
    return ft.Container(
        padding=16,
        bgcolor=LIGHT_PURPLE,
        border_radius=12,
        content=ft.Column(
            [
                ft.Text(
                    title,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=DARK_PURPLE
                ),
                ft.Divider(height=8, color=DARK_PURPLE),
                *controls
            ],
            spacing=12
        )
    )


def show_dashboard_view(conn, page):
    page.controls.clear()

    current_query_type = {"value": None}
    param_inputs = {}

    # --- NAGŁÓWEK ---
    header = ft.Container(
        padding=20,
        bgcolor=PRIMARY_PURPLE,
        content=ft.Row(
            [
                ft.Icon(ft.Icons.ANALYTICS, size=32, color="white"),
                ft.Text(
                    "OLAP Analytica",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color="white"
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Przeglądaj hurtownię",
                    icon=ft.Icons.TABLE_VIEW,
                    on_click=lambda e: whb.show_browse_view(page, conn),
                    style=ft.ButtonStyle(
                        bgcolor=DARK_PURPLE,
                        color="white"
                    )
                ),
                ft.Chip(
                    label=ft.Text("Połączono z PostgreSQL", color="white"),
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color="GREEN"),
                    bgcolor=BACKGROUND
                )
            ]
        )
    )

    # --- LOGIKA WYBORU ZAPYTANIA ---
    def on_query_selected(e):
        query_type = e.control.value
        current_query_type["value"] = query_type
        update_parameter_panel(query_type)
    
    query_dropdown = ft.Dropdown(
        label="Wybierz operację OLAP",
        options=[ft.dropdown.Option(key=k, text=n) for k, n in OLAPQueries.get_all_queries()],
        width=280,
        on_change=on_query_selected,
        border_color=DARK_PURPLE
    )

    query_info = ft.Container(content=ft.Text("Wybierz operację..."), padding=10)
    
    # --- PANEL PARAMETRÓW ---
    params_container = ft.Column([], spacing=12)
    
    params_section = ft.Container(
        padding=16,
        bgcolor=LIGHT_PURPLE,
        border_radius=12,
        visible=False,
        content=ft.Column(
            [
                ft.Text(
                    "2️⃣ Parametry zapytania",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=DARK_PURPLE
                ),
                ft.Divider(height=8, color=DARK_PURPLE),
                params_container
            ],
            spacing=12
        )
    )

    def update_parameter_panel(query_type):
        param_inputs.clear()
        params_container.controls.clear()
        
        query_def = OLAPQueries.get_query(query_type)
        if not query_def:
            params_section.visible = False
            page.update()
            return

        query_info.content = ft.Column([
            ft.Text(query_def["name"], weight=ft.FontWeight.BOLD, color=DARK_PURPLE),
            ft.Text(query_def["description"], size=12, color=DARK_PURPLE)
        ])

        for param in query_def["params"]:
            if param["type"] == "number":
                control = ft.TextField(
                    label=param["label"],
                    value=str(param["default"]),
                    width=280,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    border_color=DARK_PURPLE,
                    focused_border_color=PRIMARY_PURPLE,
                    label_style=ft.TextStyle(color=DARK_PURPLE),
                    cursor_color=PRIMARY_PURPLE
                )
            elif param["type"] == "text":
                control = ft.TextField(
                    label=param["label"],
                    value=param.get("default", ""),
                    width=280,
                    border_color=DARK_PURPLE,
                    focused_border_color=PRIMARY_PURPLE,
                    label_style=ft.TextStyle(color=DARK_PURPLE),
                    cursor_color=PRIMARY_PURPLE
                )
            elif param["type"] == "select":
                control = ft.Dropdown(
                    label=param["label"],
                    options=[ft.dropdown.Option(opt) for opt in param["options"]],
                    value=param["options"][0],
                    width=280,
                    border_color=DARK_PURPLE,
                    focused_border_color=PRIMARY_PURPLE,
                    label_style=ft.TextStyle(color=DARK_PURPLE)
                )
            
            param_inputs[param["name"]] = control
            params_container.controls.append(control)
        
        params_section.visible = True
        page.update()

    # --- LOGIKA WYNIKÓW ---
    result_table_container = ft.Container(
        content=ft.Column(
            [ft.Text("Wykonaj zapytanie, aby zobaczyć wyniki", color=DARK_PURPLE)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True
    )

    result_info_container = ft.Container(
        visible=False,
        padding=12,
        bgcolor=LIGHT_PURPLE,
        border_radius=8,
        content=ft.Row([
            ft.Icon(ft.Icons.INFO, color=DARK_PURPLE),
            ft.Text("", color=DARK_PURPLE)
        ])
    )

    def update_results(result):
        columns = [
            ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD, color=DARK_PURPLE))
            for col in result["columns"]
        ]

        rows = []
        for row_data in result["rows"]:
            cells = [ft.DataCell(ft.Text(str(val) if val is not None else "", color="black")) for val in row_data]
            rows.append(ft.DataRow(cells=cells))

        result_table_new = ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, LIGHT_PURPLE),
            border_radius=8,
            heading_row_color=ft.Colors.with_opacity(0.1, PRIMARY_PURPLE),
            column_spacing=20
        )
        
        result_table_container.content = ft.Column(
            [
                ft.Row(
                    [result_table_new],
                    scroll=ft.ScrollMode.ALWAYS,
                )
            ],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True
        )

        result_info_container.visible = True
        result_info_container.content.controls[1].value = f"Znaleziono {result['row_count']} rekordów"
        page.update()

    def execute_analysis(e):
        if not current_query_type["value"]:
            print("[ERROR] Nie wybrano operacji OLAP")
            return

        params = []
        query_def = OLAPQueries.get_query(current_query_type["value"])
        
        # Pobieramy SQL i naprawiamy problem z ROUND dla PostgreSQL
        # Zamieniamy ROUND(wyrażenie, 2) na ROUND((wyrażenie)::numeric, 2)
        sql = query_def["sql"].replace("ROUND(", "ROUND(").replace("), 2)", ")::numeric, 2)")
        
        try:
            for param_def in query_def["params"]:
                value = param_inputs[param_def["name"]].value
                if param_def["type"] == "number":
                    params.append(int(value))
                else:
                    params.append(value)
            
            # Wykonujemy naprawione zapytanie bezpośrednio
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            results = cursor.fetchall()
            cursor.close()
            
            # Budujemy obiekt wyniku ręcznie, skoro ominęliśmy metodę execute_query klasy
            result = {
                "columns": query_def["columns"],
                "rows": results,
                "row_count": len(results)
            }
            
            update_results(result)
            
        except Exception as ex:
            print(f"[DATABASE ERROR] {str(ex)}")

    # --- PRZYCISK WYKONANIA ---
    run_btn = ft.ElevatedButton(
        "Wykonaj analizę",
        icon=ft.Icons.PLAY_ARROW,
        on_click=execute_analysis,
        style=ft.ButtonStyle(
            bgcolor=PRIMARY_PURPLE,
            color="white",
            padding=20
        ),
        width=280,
        height=50
    )

    # --- LAYOUT ---
    query_section = section("1️⃣ Wybór operacji", [query_dropdown, query_info])
    execute_section = section("Wykonanie", [run_btn])

    left_panel = ft.Container(
        width=340,
        padding=20,
        bgcolor=BACKGROUND,
        content=ft.Column(
            [query_section, params_section, execute_section],
            spacing=16,
            scroll=ft.ScrollMode.AUTO
        )
    )

    result_panel = ft.Container(
        expand=True,
        padding=24,
        bgcolor="white",
        border_radius=12,
        border=ft.border.all(2, LIGHT_PURPLE),
        content=ft.Column(
            [
                ft.Text("Wyniki analizy", size=18, weight=ft.FontWeight.BOLD, color=DARK_PURPLE),
                result_info_container,
                ft.Divider(color=LIGHT_PURPLE),
                result_table_container
            ],
            expand=True
        )
    )

    # --- MONTAŻ ---
    page.add(
        ft.Container(
            expand=True,
            bgcolor=BACKGROUND,
            content=ft.Column(
                [
                    header,
                    ft.Container(
                        expand=True,
                        padding=ft.padding.only(left=20, right=20, bottom=20),
                        content=ft.Row(
                            [left_panel, result_panel],
                            spacing=20,
                            expand=True
                        )
                    )
                ],
                expand=True
            )
        )
    )
    page.update()