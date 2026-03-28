import flet as ft
import sys
import os
import dashboard as dashboard

from colors import DARK_PURPLE, LIGHT_PURPLE, PRIMARY_PURPLE, BACKGROUND
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import generate_db_structure as gds


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

def show_success_dialog():
    def close_dialog(e):
        succes_dial.open = False
        page.update()

        view_stack.clear()
        navigate_to(show_start_view)

    succes_dial = dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Sukces!"),
        content=ft.Text(
            "Hurtownia danych została utworzona pomyślnie.\n\n"
            "Możesz teraz zalogować się lub utworzyć kolejną."
        ),
        actions=[
            ft.TextButton("OK", on_click=close_dialog)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    return succes_dial


def handle_create_db(db_name_val, password_val, status_text: ft.Text):

    if not db_name_val:
        status_text.value = "Podaj nazwę hurtowni"
        status_text.color = ft.Colors.RED
        page.update()
        return

    status_text.value = "Sprawdzanie połączenia..."
    status_text.color = ft.Colors.BLUE
    page.update()

    db_status = gds.database_exists(db_name_val, password_val)

    if db_status == "auth_error":
        status_text.value = "Błędne hasło administratora PostgreSQL"
        status_text.color = ft.Colors.RED
        page.update()
        return

    if db_status == "exists":
        status_text.value = "Hurtownia o tej nazwie już istnieje"
        status_text.color = ft.Colors.RED
        page.update()
        return

    status_text.value = "Tworzenie hurtowni..."
    status_text.color = ft.Colors.BLUE
    page.update()

    result = gds.generate_structure(
        db_name_val,
        password_val,
        create_db=True,
        generate_csv=True
    )
    if result == 1:
        page.open(show_success_dialog())
    else:
        status_text.value = "Błąd tworzenia hurtowni"
        status_text.color = ft.Colors.RED

    page.update()



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
        navigate_to(lambda: dashboard.show_dashboard_view(conn,page))



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

    status_text = ft.Text(
    "",
    size=14,
    weight=ft.FontWeight.W_500,
    )


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
    on_click=lambda e: handle_create_db(
        db_name.value,
        password.value,
        status_text
    ),
)


    main_column = ft.Column(
        [
            header,
            title,
            db_name,
            password,
            create_btn,
            status_text
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
    page.window_width = 1920
    page.window_height = 1080
    page.window_resizable = True     # opcjonalnie, okno można zmieniać
    page.window_maximized = True 

    page.update()

    navigate_to(show_start_view)


ft.app(target=main)
