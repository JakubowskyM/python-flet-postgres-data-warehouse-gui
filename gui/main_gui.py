import flet as ft
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import generate_db_structure as gds


PRIMARY_PURPLE = "#6A0DAD"
LIGHT_PURPLE = "#D1A8FD"
BACKGROUND = "#F5F5F5"
DARK_PURPLE = "#4B0082"

view_stack = []
page = None


def navigate_to(view_func):
    view_stack.append(view_func)
    view_func()

def go_back():
    if len(view_stack) > 1:
        view_stack.pop()
        view_stack[-1]()

def back_button():
    return ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_color=DARK_PURPLE,
        on_click=lambda e: go_back(),
    )

def handle_login(db_name_val, password_val):

    conn = gds.generate_structure(db_name_val, password_val, create_db=False, generate_csv=False)

    if conn == 0:
        print("kurrrwo")
        page.snack_bar = ft.SnackBar(
            ft.Text("Błąd logowania! Sprawdź nazwę bazy i hasło."),
            bgcolor=ft.Colors.RED,
            open=True
        )
        page.update()
    else:
        navigate_to(lambda: show_dashboard_view(conn))



def show_dashboard_view(conn):
    page.controls.clear()

    page.snack_bar = ft.SnackBar(
            ft.Text("Zalogowano pomyślnie!"),
            bgcolor=ft.Colors.GREEN,
            open=True
        )
    
    title = ft.Text(
        "Dashboard OLAP",
        size=28,
        weight=ft.FontWeight.BOLD,
        color=DARK_PURPLE,
    )

    main_column = ft.Column(
        [
            title,
            ft.Text("Tu będzie Twoje menu i raporty"),
        ],
        spacing=16,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
    )
    page.add(ft.SnackBar(
            ft.Text("Zalogowano pomyślnie!",
                    color=BACKGROUND),
            bgcolor=ft.Colors.GREEN,
            open=True
        ))
    page.add(main_column)
    page.update()


def show_start_view():
    page.controls.clear()

    title = ft.Text(
        "OLAP Analytica",
        size=36,
        weight=ft.FontWeight.BOLD,
        color=DARK_PURPLE,
    )

    subtitle = ft.Text(
        "System zarządzania i analizy hurtowni danych",
        size=14,
        color=ft.Colors.GREY_700,
    )

    connect_btn = ft.FilledButton(
        "Połącz się z istniejącą hurtownią",
        width=320,
        height=48,
        style=ft.ButtonStyle(
            bgcolor=PRIMARY_PURPLE,
            color="white",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=lambda e: navigate_to(show_login_view),
    )

    create_btn = ft.OutlinedButton(
        "Stwórz nową hurtownię",
        width=320,
        height=48,
        style=ft.ButtonStyle(
            side=ft.BorderSide(color=LIGHT_PURPLE, width=2),
            bgcolor=LIGHT_PURPLE,
            color=DARK_PURPLE,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=lambda e: navigate_to(show_create_view),
    )

    main_column = ft.Column(
        [
            title,
            subtitle,
            ft.Container(height=20),
            connect_btn,
            create_btn,
        ],
        spacing=16,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(main_column)
    page.update()


def show_login_view():
    page.controls.clear()

    header = ft.Row([back_button()], alignment=ft.MainAxisAlignment.START)

    title = ft.Text(
        "Połączenie z hurtownią",
        size=24,
        weight=ft.FontWeight.BOLD,
        color=DARK_PURPLE,
    )

    db_name = ft.TextField(
        label="Nazwa hurtowni",
        label_style=ft.TextStyle(
            color=DARK_PURPLE,
        ),
        color=DARK_PURPLE,
        border_color= LIGHT_PURPLE,
        width=300)
    password = ft.TextField(
        label="Hasło",
        label_style=ft.TextStyle(
            color=DARK_PURPLE,
        ),
        color=DARK_PURPLE,
        border_color= LIGHT_PURPLE,
        password=True,
        can_reveal_password=True,
        width=300,
    )

    login_btn = ft.FilledButton(
        "Połącz",
        width=300,
        style=ft.ButtonStyle(
         bgcolor=PRIMARY_PURPLE,
            color="white",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=lambda e: (
            handle_login(db_name.value, password.value)
        )
    )

    main_column = ft.Column(
        [
            header,
            title,
            db_name,
            password,
            login_btn,
        ],
        spacing=16,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(main_column)
    page.update()


def show_create_view():
    page.controls.clear()

    header = ft.Row([back_button()], alignment=ft.MainAxisAlignment.START)

    title = ft.Text(
        "Tworzenie nowej hurtowni danych",
        size=24,
        weight=ft.FontWeight.BOLD,
        color=DARK_PURPLE,
    )

    db_name = ft.TextField(
        label="Nazwa hurtowni",
        label_style=ft.TextStyle(
            color=DARK_PURPLE,
        ),
        color=DARK_PURPLE,
        border_color= LIGHT_PURPLE,
        width=300)
    
    password = ft.TextField(
        label="Hasło administratora",
        label_style=ft.TextStyle(
            color=DARK_PURPLE,
        ),
        password=True,
        color=DARK_PURPLE,
        can_reveal_password=True,
        border_color= LIGHT_PURPLE,
        width=300,
    )

    create_btn = ft.FilledButton(
        "Utwórz hurtownię",
        width=300,
        style=ft.ButtonStyle(
            bgcolor=PRIMARY_PURPLE,
            color="white",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=lambda e: print("Tworzenie DB:", db_name.value,
                                 gds.generate_structure(db_name.value, password.value, create_db=True, generate_csv=True)),
    )

    main_column = ft.Column(
        [
            header,
            title,
            db_name,
            password,
            create_btn,
        ],
        spacing=16,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(main_column)
    page.update()


def main(p: ft.Page):
    global page
    page = p

    page.title = "OLAP Analytica"
    page.bgcolor = BACKGROUND
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    navigate_to(show_start_view)


ft.app(target=main)
