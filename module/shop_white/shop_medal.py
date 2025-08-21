import cv2
import numpy as np
from scipy import signal

import module.config.server as server
from module.base.button import ButtonGrid
from module.base.decorator import cached_property, del_cached_property
from module.base.utils import area_offset
from module.base.utils import rgb2gray
from module.logger import logger
from module.map_detection.utils import Points
from module.shop.assets import *
from module.shop.base import ShopItemGrid
from module.shop.shop_medal import MedalShop2 as MedalShop2Base, ShopPriceOcr
from module.ui.scroll import AdaptiveScroll

if server.server == 'jp':
    PRICE_OCR = ShopPriceOcr([], lang='cnocr', letter=(235, 235, 255), threshold=128, name='Price_ocr')
else:
    PRICE_OCR = ShopPriceOcr([], letter=(255, 255, 255), threshold=128, name='Price_ocr')
TEMPLATE_MEDAL_ICON_3 = Template('./assets/shop/cost/Medal_3.png')


# TODO: Unfortunately does not WORK, the other guy's new MEDAL_SCROLL_AREA did not help either
class ShopAdaptiveScroll(AdaptiveScroll):
    def match_color(self, main):
        area = (self.area[0] - self.background, self.area[1], self.area[2] + self.background, self.area[3])
        image = main.image_crop(area, copy=False)

        image = rgb2gray(image)
        cv2.bitwise_not(image, dst=image)
        image = image.flatten()
        wlen = area[2] - area[0]
        parameters = {
            'height': (100, 200),
            'prominence': 35,
            'width': 0.5
        }
        parameters.update(self.parameters)
        peaks, _ = signal.find_peaks(image, **parameters)
        peaks = peaks[15: 123]
        peaks //= wlen
        self.length = 123
        mask = np.zeros((self.total,), dtype=np.bool_)
        mask[peaks] = 1
        return mask


MEDAL_SHOP_SCROLL = ShopAdaptiveScroll(
    MEDAL_SHOP_SCROLL_AREA.button,
    background=1,
    name="MEDAL_SHOP_SCROLL"
)
MEDAL_SHOP_SCROLL.drag_threshold = 0.1
MEDAL_SHOP_SCROLL.edge_threshold = 0.1


class MedalShop2(MedalShop2Base):
    def _get_medals(self):
        """
        Returns:
            np.array: [[x1, y1], [x2, y2]], location of the medal icon upper-left corner.
        """
        area = (226, 317, 960, 635)
        # copy image because we gonna paint it
        image = self.image_crop(area, copy=True)
        # a random background thingy that may cause mis-detection in template matching
        paint = (623, 558, 703, 630)
        paint = area_offset(paint, (-area[0], -area[1]))
        # paint it black
        x1, y1, x2, y2 = paint
        image[y1:y2, x1:x2] = (0, 0, 0)

        medals = TEMPLATE_MEDAL_ICON_3.match_multi(image, similarity=0.5, threshold=5)
        medals = Points([(0., m.area[1]) for m in medals]).group(threshold=5)
        logger.attr('Medals_icon', len(medals))
        return medals

    @cached_property
    def shop_grid(self):
        return self.shop_medal_grid()

    def shop_medal_grid(self):
        """
        Returns:
            ButtonGrid:
        """
        # (472, 348, 1170, 648)
        medals = self._get_medals()
        count = len(medals)
        if count == 0:
            logger.warning('Unable to find medal icon, assume item list is at top')
            origin_y = 228
            delta_y = 217
            row = 2
        elif count == 1:
            y_list = medals[:, 1]
            # +256, top of the crop area in _get_medals()
            # -125, from the top of medal icon to the top of shop item
            origin_y = y_list[0] + 317 - 126
            delta_y = 217
            row = 1
        elif count == 2:
            y_list = medals[:, 1]
            y1, y2 = y_list[0], y_list[1]
            origin_y = min(y1, y2) + 317 - 126
            delta_y = abs(y1 - y2)
            row = 2
        else:
            logger.warning(f'Unexpected medal icon match result: {[m for m in medals]}')
            origin_y = 228
            delta_y = 217
            row = 2

        # Make up a ButtonGrid
        # Original grid is:
        # shop_grid = ButtonGrid(
        #     origin=(476, 246), delta=(156, 213), button_shape=(98, 98), grid_shape=(5, 2), name='SHOP_GRID')
        shop_grid = ButtonGrid(
            origin=(226, origin_y), delta=(162, delta_y), button_shape=(64, 64), grid_shape=(5, row), name='SHOP_GRID')
        return shop_grid

    @cached_property
    def shop_medal_items(self):
        """
        Returns:
            ShopItemGrid:
        """
        shop_grid = self.shop_grid
        shop_medal_items = ShopItemGrid(
            shop_grid,
            templates={}, amount_area=(60, 74, 96, 95),
            price_area=(14, 122, 85, 149), cost_area=(-12, 115, 60, 165))
        shop_medal_items.load_template_folder(self.shop_template_folder)
        shop_medal_items.load_cost_template_folder('./assets/shop/cost')
        shop_medal_items.similarity = 0.85  # Lower the threshold for consistent matches of PR/DRBP
        shop_medal_items.cost_similarity = 0.5
        shop_medal_items.price_ocr = PRICE_OCR
        return shop_medal_items

    def run(self):
        """
        Run Medal Shop
        """
        # Base case; exit run if filter empty
        if not self.shop_filter:
            return

        # When called, expected to be in
        # correct Medal Shop interface
        logger.hr('Medal Shop', level=1)
        self.wait_until_medal_appear()

        # Execute buy operations
        MEDAL_SHOP_SCROLL.set_top(main=self)
        while 1:
            self.shop_buy()
            if MEDAL_SHOP_SCROLL.at_bottom(main=self):
                logger.info('Medal shop reach bottom, stop')
                break
            else:
                MEDAL_SHOP_SCROLL.next_page(main=self, page=0.66)
                del_cached_property(self, 'shop_grid')
                del_cached_property(self, 'shop_medal_items')
                continue
