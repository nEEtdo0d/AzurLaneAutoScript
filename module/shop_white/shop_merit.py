from module.base.decorator import cached_property
from module.shop.base import ShopItemGrid
from module.shop.shop_merit import MeritShop as MeritShopBase
from module.shop_white.ui import ShopUI


class MeritShop(MeritShopBase, ShopUI):
    @cached_property
    def shop_merit_items(self):
        """
        Returns:
            ShopItemGrid:
        """
        shop_grid = self.shop_grid

        shop_merit_items = ShopItemGrid(shop_grid, templates={},
            template_area=(25, 20, 82, 72), amount_area=(42, 50, 65, 65),
            cost_area=(-12, 115, 60, 155), price_area=(18, 121, 85, 160))
        shop_merit_items.load_template_folder(self.shop_template_folder)
        shop_merit_items.load_cost_template_folder('./assets/shop/cost')
        return shop_merit_items