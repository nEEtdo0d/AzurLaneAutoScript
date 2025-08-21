from module.base.button import ButtonGrid
from module.base.decorator import cached_property
from module.shop.base import ShopBase as ShopBaseOld


class ShopBase(ShopBaseOld):
    @cached_property
    def shop_grid(self):
        """
        Returns:
            ButtonGrid:
        """
        shop_grid = ButtonGrid(
            origin=(226, 238), delta=(162, 217),
            button_shape=(64, 64), grid_shape=(5, 2),
            name='SHOP_GRID')
        return shop_grid
