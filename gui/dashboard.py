import flet as ft
from colors import DARK_PURPLE, LIGHT_PURPLE, PRIMARY_PURPLE, BACKGROUND


def kpi_card(title: str, value: str, icon):
    return ft.Container(
        width=220,
        height=120,
        padding=16,
        bgcolor="white",
        border_radius=12,
        shadow=ft.BoxShadow(
            blur_radius=12,
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
        ),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(icon, color=PRIMARY_PURPLE, size=28),
                        ft.Text(title, color=ft.Colors.GREY_600),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    value,
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=DARK_PURPLE,
                ),
            ],
            spacing=12,
        ),
    )


def section_card(title: str, height=300):
    return ft.Container(
        expand=True,
        height=height,
        padding=16,
        bgcolor="white",
        border_radius=12,
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
        ),
        content=ft.Column(
            [
                ft.Text(
                    title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=DARK_PURPLE,
                ),
                ft.Divider(),
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        "Tu będą wykresy",
                        color=ft.Colors.GREY_500,
                    ),
                ),
            ]
        ),
    )


def filter_panel():
    return ft.Container(
        width=260,
        padding=16,
        bgcolor="white",
        border_radius=12,
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
        ),
        content=ft.Column(
            [
                ft.Text(
                    "Filtry",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=DARK_PURPLE,
                ),
                ft.Divider(),
                ft.Dropdown(
                    label="Zakres czasu",
                    options=[
                        ft.dropdown.Option("Ostatnie 7 dni"),
                        ft.dropdown.Option("Ostatni miesiąc"),
                        ft.dropdown.Option("Ostatni rok"),
                    ],
                ),
                ft.Dropdown(
                    label="Województwo",
                    options=[
                        ft.dropdown.Option("Wszystkie"),
                        ft.dropdown.Option("Mazowieckie"),
                        ft.dropdown.Option("Śląskie"),
                        ft.dropdown.Option("Małopolskie"),
                    ],
                ),
                ft.Dropdown(
                    label="Typ komponentu",
                    options=[
                        ft.dropdown.Option("CPU"),
                        ft.dropdown.Option("GPU"),
                        ft.dropdown.Option("RAM"),
                        ft.dropdown.Option("Dysk"),
                    ],
                ),
                ft.ElevatedButton(
                    "Zastosuj filtry",
                    bgcolor=PRIMARY_PURPLE,
                    color="white",
                ),
            ],
            spacing=12,
        ),
    )


def show_dashboard_view(conn, page: ft.Page):
    page.controls.clear()

    page.appbar = ft.AppBar(
        title=ft.Text("OLAP Analytica"),
        bgcolor=PRIMARY_PURPLE,
        actions=[
            ft.IconButton(ft.Icons.ACCOUNT_CIRCLE),
            ft.IconButton(ft.Icons.LOGOUT),
        ],
    )


    kpi_row = ft.Row(
        [
            kpi_card("Sprzedaż", "X zł", ft.Icons.TRENDING_UP),
            kpi_card("Importy", "Xzł", ft.Icons.SHOPPING_BASKET),
            kpi_card("Marża", "X%", ft.Icons.PIE_CHART),
            kpi_card("Klienci", "X", ft.Icons.GROUP),
        ],
        spacing=20,
        wrap=True,
    )

    analytics_section = ft.Row(
        [
            filter_panel(),
            ft.Column(
                [
                    section_card("Sprzedaż w czasie", height=260),
                    section_card("Trend importów", height=260),
                ],
                expand=True,
                spacing=20,
            ),
            ft.Column(
                [
                    section_card("Top produkty", height=540),
                ],
                width=360,
            ),
        ],
        spacing=20,
        expand=True,
    )

    page.add(
        ft.Container(
            padding=24,
            expand=True,
            content=ft.Column(
                [
                    kpi_row,
                    ft.Container(height=20),
                    analytics_section,
                ],
                spacing=20,
            ),
        )
    )

    page.update()
