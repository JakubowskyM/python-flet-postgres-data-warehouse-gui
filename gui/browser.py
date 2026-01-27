import flet as ft
import sys
import os
import dashboard

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from warehouse_editor import (
    fetch_table_data,
    update_record,
    delete_record,
    insert_record,
    get_next_id,
    get_table_columns,
    create_back_button,
    get_tables,
)
from colors import PRIMARY_PURPLE, LIGHT_PURPLE, BACKGROUND, DARK_PURPLE

ROWS_PER_PAGE = 20


def show_browse_view(page, conn):
    current_table = ft.Ref[str]()
    current_page = ft.Ref[int]()
    total_pages = ft.Ref[int]()
    current_table.value = get_tables()[0]
    current_page.value = 0
    total_pages.value = 1

    table_container = ft.Column(expand=True, alignment=ft.MainAxisAlignment.CENTER)
    page_info_text = ft.Text("", color=DARK_PURPLE)


    def refresh_table():
        table_container.controls.clear()

        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {current_table.value}")
            total_rows = cur.fetchone()[0]

        total_pages.value = max(1, (total_rows + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE)
        if current_page.value >= total_pages.value:
            current_page.value = max(0, total_pages.value - 1)

        rows = fetch_table_data(conn, current_table.value, current_page.value)
        columns = get_table_columns(current_table.value)

        if len(rows) == 0:
            table_container.controls.append(
                ft.Text("Brak rekordów w tabeli", color=DARK_PURPLE, size=16)
            )
        else:
            table_scroll_container = ft.Container(
                content=ft.Column(
                    [
                        ft.DataTable(
                            columns=[ft.DataColumn(ft.Text(col, color=DARK_PURPLE)) for col in columns],
                            rows=[
                                ft.DataRow(
                                    cells=[ft.DataCell(ft.Text(str(cell), color=DARK_PURPLE)) for cell in row],
                                    on_select_changed=lambda e, r=row: show_detail_view(r),
                                )
                                for row in rows
                            ],
                            heading_row_color=LIGHT_PURPLE,
                            border=ft.border.all(1, DARK_PURPLE),
                            border_radius=5,
                            column_spacing=20,
                            expand=True,
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                height=500,
                expand=True,
                alignment=ft.alignment.center,
            )
            table_container.controls.append(table_scroll_container)

        page_info_text.value = f"Strona {current_page.value + 1} / {total_pages.value}"
        page.update()


    def show_alert(title: str, message: str, color=PRIMARY_PURPLE):
        def close_dialog(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, color=BACKGROUND),
            content=ft.Text(message, color=BACKGROUND),
            actions=[
                ft.ElevatedButton("OK", on_click=close_dialog, bgcolor=color, color="white")
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()


    def show_detail_view(row):
        columns = get_table_columns(current_table.value)
        fields = {}
        record_id = row[0]

        for i, col in enumerate(columns):
            if col == "id":
                continue
            else:
                fields[col] = ft.TextField(
                    label=col.upper(),
                    label_style=ft.TextStyle(color=DARK_PURPLE),
                    color=LIGHT_PURPLE,
                    value=str(row[i]) if row[i] is not None else "",
                    border_color=DARK_PURPLE,
                    focused_border_color=PRIMARY_PURPLE,
                    cursor_color=PRIMARY_PURPLE,
                    text_size=16,
                )

        def save_changes(e):
            data_dict = {col: fields[col].value for col in fields}
            try:
                update_record(conn, current_table.value, record_id, data_dict)
                show_alert("Sukces", "Rekord zaktualizowany pomyślnie!", ft.Colors.GREEN)
                show_browse_view(page, conn)
            except Exception as ex:
                show_alert("Błąd", f"Błąd aktualizacji: {str(ex)}", ft.Colors.RED)

        def delete_row(e):
            def confirm_delete(e):
                try:
                    delete_record(conn, current_table.value, record_id)
                    confirm_dialog.open = False
                    show_alert("Sukces", "Rekord usunięty pomyślnie!", ft.Colors.GREEN)
                    show_browse_view(page, conn)
                except Exception as ex:
                    show_alert("Błąd", f"Błąd usuwania: {str(ex)}", ft.Colors.RED)
                    confirm_dialog.open = False
                    page.update()

            def cancel_delete(e):
                confirm_dialog.open = False
                page.update()

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Potwierdzenie usunięcia", color=BACKGROUND),
                content=ft.Text(
                    f"Czy na pewno chcesz usunąć rekord ID={record_id}?\n"
                    "Wszystkie powiązane rekordy z innych tabel również zostaną usunięte.",
                    color=BACKGROUND
                ),
                actions=[
                    ft.TextButton("Anuluj", on_click=cancel_delete),
                    ft.ElevatedButton("Usuń", on_click=confirm_delete, bgcolor=ft.Colors.RED, color="white"),
                ],
            )
            page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            page.update()

        detail_header = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Powrót do listy",
                    icon_color=PRIMARY_PURPLE,
                    on_click=lambda e: show_browse_view(page, conn),
                ),
                ft.Text(
                    f"Szczegóły dla {current_table.value} o ID: {record_id}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=DARK_PURPLE,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        form_container = ft.Container(
            content=ft.Column(list(fields.values()), spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True,
        )

        action_buttons = ft.Row(
            [
                ft.ElevatedButton(
                    "Anuluj", icon=ft.Icons.CANCEL,
                    on_click=lambda e: show_browse_view(page, conn),
                    bgcolor=ft.Colors.GREY_400, color="white", height=50, width=100
                ),
                ft.ElevatedButton(
                    "Usuń", icon=ft.Icons.DELETE,
                    on_click=delete_row,
                    bgcolor=ft.Colors.RED_400, color="white", height=50, width=100
                ),
                ft.ElevatedButton(
                    "Zapisz", icon=ft.Icons.SAVE,
                    on_click=save_changes,
                    bgcolor=PRIMARY_PURPLE, color="white", height=50, width=100
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER, spacing=20,
        )

        page.controls.clear()
        page.add(
            ft.Column(
                [detail_header, ft.Divider(color=DARK_PURPLE), form_container, ft.Divider(color=DARK_PURPLE), action_buttons],
                expand=True, spacing=10,
            )
        )
        page.update()


    def show_add_view(e):
        columns = get_table_columns(current_table.value)
        fields = {}
        next_id = get_next_id(conn, current_table.value)

        for col in columns:
            if col == "id":
                fields[col] = ft.TextField(
                    label=col.upper(),
                    label_style=ft.TextStyle(color=DARK_PURPLE),
                    color=LIGHT_PURPLE,
                    value=str(next_id),
                    disabled=True,
                    border_color=DARK_PURPLE,
                    text_size=16,
                )
            else:
                fields[col] = ft.TextField(
                    label=col.upper(),
                    label_style=ft.TextStyle(color=DARK_PURPLE),
                    color=LIGHT_PURPLE,
                    value="",
                    border_color=DARK_PURPLE,
                    focused_border_color=PRIMARY_PURPLE,
                    cursor_color=PRIMARY_PURPLE,
                    text_size=16,
                )

        def save_new(e):
            data_dict = {k: f.value for k, f in fields.items()}
            try:
                insert_record(conn, current_table.value, data_dict)
                show_alert("Sukces", "Rekord dodany pomyślnie!", ft.Colors.GREEN)
                show_browse_view(page, conn)
            except Exception as ex:
                show_alert("Błąd", f"Błąd dodawania: {str(ex)}", ft.Colors.RED)

        add_header = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Powrót do listy",
                    icon_color=PRIMARY_PURPLE,
                    on_click=lambda e: show_browse_view(page, conn),
                ),
                ft.Text(f"Dodaj nowy rekord do {current_table.value}", size=24, weight=ft.FontWeight.BOLD, color=DARK_PURPLE),
            ],
            alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        form_container = ft.Container(
            content=ft.Column(list(fields.values()), spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True,
        )

        action_buttons = ft.Row(
            [
                ft.ElevatedButton(
                    "Anuluj", icon=ft.Icons.CANCEL,
                    on_click=lambda e: show_browse_view(page, conn),
                    bgcolor=ft.Colors.GREY_400, color="white", height=50
                ),
                ft.ElevatedButton(
                    "Dodaj", icon=ft.Icons.ADD,
                    on_click=save_new,
                    bgcolor=PRIMARY_PURPLE, color="white", height=50
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER, spacing=20,
        )

        page.controls.clear()
        page.add(
            ft.Column([add_header, ft.Divider(color=DARK_PURPLE), form_container, ft.Divider(color=DARK_PURPLE), action_buttons], expand=True, spacing=10)
        )
        page.update()


    table_tabs = ft.Row(
        [
            ft.ElevatedButton(
                name, bgcolor=PRIMARY_PURPLE, color=BACKGROUND,
                on_click=lambda e, t=name: (setattr(current_table, "value", t), setattr(current_page, "value", 0), refresh_table()),
            )
            for name in get_tables()
        ],
        scroll=ft.ScrollMode.AUTO,
    )


    pagination = ft.Row(
        [
            ft.IconButton(
                ft.Icons.ARROW_BACK, tooltip="Poprzednia strona", icon_color=PRIMARY_PURPLE,
                on_click=lambda e: (setattr(current_page, "value", max(0, current_page.value - 1)), refresh_table()),
            ),
            page_info_text,
            ft.IconButton(
                ft.Icons.ARROW_FORWARD, tooltip="Następna strona", icon_color=PRIMARY_PURPLE,
                on_click=lambda e: (setattr(current_page, "value", min(current_page.value + 1, total_pages.value - 1)), refresh_table()),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )


    header = ft.Row(
        [
            create_back_button(page, dashboard.show_dashboard_view, conn),
            ft.Text("Przeglądaj hurtownię", size=24, weight=ft.FontWeight.BOLD, color=DARK_PURPLE),
            ft.Container(expand=True),
            ft.ElevatedButton("Dodaj rekord", icon=ft.Icons.ADD, bgcolor=PRIMARY_PURPLE, color="white", on_click=show_add_view),
        ],
        alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.controls.clear()
    page.add(ft.Column([header, ft.Divider(color=DARK_PURPLE), table_tabs, ft.Divider(color=DARK_PURPLE), table_container, pagination], expand=True, alignment=ft.MainAxisAlignment.CENTER, spacing=10))

    refresh_table()
