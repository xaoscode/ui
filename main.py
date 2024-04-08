import flet as ft
import trader_type1 as trader_type1
from flet import (
    Column,
    Page,
    Row,
    TextField,
    VerticalDivider,
)
from settings_page import Settings
from menu_page import Menu


class AuctionDestroyer(Row):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.settings = Settings(self.page)
        self.menu = Menu(self.page)
        self.devider = VerticalDivider(width=4)

    def build(self):
        self.new_task = TextField(
            hint_text="Whats needs to be done?",
            expand=True,
            value=self.page.client_storage.get("tesseract_path"),
        )
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            # extended=True,
            height=500,
            min_width=100,
            min_extended_width=100,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon_content=ft.Icon(ft.icons.MENU),
                    label_content=ft.Text("Menu"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon_content=ft.Icon(ft.icons.SETTINGS),
                    label_content=ft.Text("Settings"),
                ),
            ],
            on_change=self.navigate,
        )

        self.main_page = Column(controls=[self.settings])

        self.set = Row(
            [self.rail, self.devider, self.main_page],
            spacing=10,
            expand=True,
        )

        return self.set

    def navigate(self, e):
        index = e.control.selected_index
        print(index)
        if index == 0:
            self.main_page.controls.clear()
            self.main_page.controls.append(self.settings)
            super().update()
        elif index == 1:
            self.main_page.controls.clear()
            self.main_page.controls.append(self.menu)
            super().update()


def main(page: Page):

    page.title = "Auction Destroyer"
    page.padding = 20
    app = AuctionDestroyer(page)
    page.add(app)


if __name__ == "__main__":
    ft.app(target=main)
