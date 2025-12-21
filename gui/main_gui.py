import flet as ft
import sys
import os

# For importing from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from randomize_db import generate_csv_files


PRIMARY_PURPLE = "#6A0DAD"
LIGHT_PURPLE = "#F3E8FF"
DARK_PURPLE = "#4B0082"



def main(page: ft.Page):
    page.title = "OLAP Import and Sales"
    page.bgcolor = LIGHT_PURPLE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def show_start_view():
        page.controls.clear()

        title_text = ft.Text(
            "OLAP Analytica",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=DARK_PURPLE,
        )

        username_field = ft.TextField(
            label="Username",
            width=280,
            border_radius=12,
        )

        password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=280,
            border_radius=12,
        )

        login_button = ft.FilledButton(
            "Login",
            width=280,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY_PURPLE,
                color="white",
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )

        generate_button = ft.TextButton(
            "Generate data only",
            on_click=lambda e: generate_csv_files(),
            style=ft.ButtonStyle(
                color=DARK_PURPLE,
            ),
        )

        login_column = ft.Column(
            controls=[
                title_text,
                username_field,
                password_field,
                login_button,
                generate_button,
            ],
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        login_card = ft.Container(
            content=login_column,
            width=360,
            padding=32,
            bgcolor="white",
            border_radius=20,
            shadow=ft.BoxShadow(
                blur_radius=25,
                color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
                offset=ft.Offset(0, 8),
            ),
        )

        page.add(login_card)
        page.update()

    show_start_view()


ft.app(target=main)
