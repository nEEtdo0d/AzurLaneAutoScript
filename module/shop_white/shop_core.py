from module.base.decorator import cached_property
from module.shop.base import ShopItemGrid
from module.shop.shop_core import CoreShop as CoreShopBase
from module.shop_white.ui import ShopUI


class CoreShop(CoreShopBase, ShopUI):
    @cached_property
    def shop_core_items(self):
        """
        Returns:
            ShopItemGrid:
        """
        shop_grid = self.shop_grid

        shop_core_items = ShopItemGrid(shop_grid, templates={},
            template_area=(25, 20, 82, 72), amount_area=(42, 50, 65, 65),
            cost_area=(-12, 115, 60, 155), price_area=(18, 121, 85, 160))
        shop_core_items.load_template_folder(self.shop_template_folder)
        shop_core_items.load_cost_template_folder('./assets/shop/cost')
        return shop_core_items