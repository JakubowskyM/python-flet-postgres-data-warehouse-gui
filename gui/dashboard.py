import flet as ft
import os
import sys
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

    # Stan aplikacji
    current_query_type = {"value": None}
    param_inputs = {}
    result_table = None
    result_info = None

    # ================= HEADER =================
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
                ft.Chip(
                    label=ft.Text("Połączono z PostgreSQL", color="white"),
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color="white"),
                    bgcolor=DARK_PURPLE
                )
            ]
        )
    )

    # ================= WYBÓR ZAPYTANIA =================
    def on_query_selected(e):
        query_type = e.control.value
        current_query_type["value"] = query_type
        update_parameter_panel(query_type)
    
    query_dropdown = ft.Dropdown(
        label="Wybierz operację OLAP",
        hint_text="Wybierz jedną z 7 operacji...",
        label_style=ft.TextStyle(color=DARK_PURPLE),
        options=[
            ft.dropdown.Option(key=key, text=name) 
            for key, name in OLAPQueries.get_all_queries()
        ],
        width=280,
        on_change=on_query_selected,
        border_color=DARK_PURPLE,
        focused_border_color=PRIMARY_PURPLE
    )

    query_info = ft.Container(
        content=ft.Text("Wybierz operację, aby zobaczyć parametry", 
                       color=DARK_PURPLE, italic=True),
        padding=10,
        bgcolor="white",
        border_radius=8,
        border=ft.border.all(1, LIGHT_PURPLE)
    )

    query_section = section(
        "1️⃣ Wybór operacji",
        [query_dropdown, query_info]
    )

    # ================= PARAMETRY =================
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
        """Aktualizuje panel parametrów na podstawie wybranego zapytania"""
        param_inputs.clear()
        params_container.controls.clear()
        
        query_def = OLAPQueries.get_query(query_type)
        if not query_def:
            params_section.visible = False
            page.update()
            return
        
        # Aktualizuj opis zapytania
        query_info.content = ft.Column([
            ft.Text(query_def["name"], weight=ft.FontWeight.BOLD, color=DARK_PURPLE),
            ft.Text(query_def["description"], size=12, color=DARK_PURPLE)
        ])
        
        # Generuj pola dla parametrów
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

    # ================= WYKONANIE ZAPYTANIA =================
    def execute_analysis(e):
        if not current_query_type["value"]:
            show_error("Wybierz operację OLAP")
            return
        
        # Pobierz wartości parametrów
        params = []
        query_def = OLAPQueries.get_query(current_query_type["value"])
        
        for param_def in query_def["params"]:
            value = param_inputs[param_def["name"]].value
            if param_def["type"] == "number":
                params.append(int(value))
            else:
                params.append(value)
        
        try:
            # Wykonaj zapytanie
            loading_indicator.visible = True
            page.update()
            
            result = OLAPQueries.execute_query(conn, current_query_type["value"], params)
            
            # Aktualizuj wyniki
            update_results(result)
            
            loading_indicator.visible = False
            export_btn.disabled = False
            page.update()
            
        except Exception as ex:
            loading_indicator.visible = False
            show_error(f"Błąd wykonania zapytania: {str(ex)}")
            page.update()
    
    def show_error(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=DARK_PURPLE
        )
        page.snack_bar.open = True
        page.update()

    run_btn = ft.ElevatedButton(
        "▶️  Wykonaj analizę",
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

    loading_indicator = ft.ProgressRing(visible=False, color=PRIMARY_PURPLE)

    execute_section = section(
        "3️⃣ Wykonanie",
        [run_btn, loading_indicator]
    )

    # ================= PANEL KONTROLNY =================
    control_panel = ft.Column(
        [
            query_section,
            params_section,
            execute_section
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO
    )

    left_panel = ft.Container(
        width=340,
        padding=20,
        bgcolor=BACKGROUND,
        content=control_panel
    )

    # ================= WYNIKI =================
    result_table_container = ft.Container(
        content=ft.Text(
            "Wykonaj zapytanie, aby zobaczyć wyniki",
            color=DARK_PURPLE,
            size=16,
            text_align=ft.TextAlign.CENTER
        ),
        alignment=ft.alignment.center,
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
        """Aktualizuje tabelę wyników"""
        # Tworzenie kolumn
        columns = [
            ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD, color=DARK_PURPLE))
            for col in result["columns"]
        ]
        
        # Tworzenie wierszy
        rows = []
        for row_data in result["rows"]:
            cells = [ft.DataCell(ft.Text(str(val), color="black")) for val in row_data]
            rows.append(ft.DataRow(cells=cells))
        
        # Aktualizacja tabeli
        result_table_new = ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(2, PRIMARY_PURPLE),
            border_radius=8,
            horizontal_lines=ft.BorderSide(1, LIGHT_PURPLE),
            heading_row_color=LIGHT_PURPLE
        )
        
        result_table_container.content = ft.Column(
            [result_table_new],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        
        # Info o liczbie wyników
        result_info_container.visible = True
        result_info_container.content.controls[1].value = \
            f"Znaleziono {result['row_count']} rekordów"
        
        page.update()

    export_btn = ft.OutlinedButton(
        "📥 Eksportuj do CSV",
        icon=ft.Icons.DOWNLOAD,
        disabled=True,
        style=ft.ButtonStyle(
            color=PRIMARY_PURPLE,
            side=ft.BorderSide(2, PRIMARY_PURPLE)
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
                ft.Row([
                    ft.Text(
                        "📊 Wyniki analizy",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=DARK_PURPLE
                    ),
                    ft.Container(expand=True),
                    export_btn
                ]),
                result_info_container,
                ft.Divider(color=LIGHT_PURPLE),
                result_table_container
            ],
            expand=True
        )
    )

    # ================= MAIN LAYOUT =================
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
                            [
                                left_panel,
                                result_panel
                            ],
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