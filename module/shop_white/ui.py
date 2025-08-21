from module.base.button import ButtonGrid
from module.base.decorator import cached_property
from module.shop.ui import ShopUI as ShopUIBase
from module.ui.navbar import Navbar


class ShopUI(ShopUIBase):
    @cached_property
    def shop_tab(self):
        """
        Set with `self.shop_tab.set(main=self, upper={index})`
        - index
            1: General supply shops
            2: Monthly shops
            3: Event shops
        """
        grids = ButtonGrid(
            origin=(29, 519), delta=(0, 50),
            button_shape=(60, 15), grid_shape=(1, 3),
            name='SHOP_TAB')
        return Navbar(
            grids=grids,
            # blue text active
            active_color=(0, 131, 255), active_threshold=221, active_count=100,
            # white text inactive
            inactive_color=(249, 252, 253), inactive_threshold=221, inactive_count=100,
        )

    @cached_property
    def shop_supply_nav(self):
        """
        Set with `self.shop_supply_nav.set(main=self, left={index})`
        - index when `shop_tab` is at 1
            1: General shop
            2: Merit shop
            3: Guild shop
            4: Meta shop
            5: Gift shop
        """
        grids = ButtonGrid(
            origin=(184, 92), delta=(173, 0),
            button_shape=(113, 42), grid_shape=(5, 1),
            name='SHOP_SUPPLY_NAV')
        return Navbar(
            grids=grids,
            # White vertical line to the left of shop names
            active_color=(90, 90, 90), active_threshold=221, active_count=80,
            # Just whatever to make it match
            inactive_color=(130, 160, 170), inactive_threshold=221, inactive_count=100,
        )

    @cached_property
    def shop_monthly_nav(self):
        """
        Set with `self.shop_nav.set(main=self, left={index})`
        - index when `shop_tab_250814` is at 2
            1: Core shop (limited items)
            2: Core shop monthly
            3: Medal shop
            4: Prototype shop
        """
        grids = ButtonGrid(
            origin=(184, 92), delta=(217, 0),
            button_shape=(156, 42), grid_shape=(4, 1),
            name='SHOP_MONTHLY_NAV')
        return Navbar(
            grids=grids,
            # White vertical line to the left of shop names
            active_color=(90, 90, 90), active_threshold=221, active_count=80,
            # Just whatever to make it match
            inactive_color=(130, 160, 170), inactive_threshold=221, inactive_count=100,
        )
