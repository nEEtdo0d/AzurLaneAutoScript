from module.shop_white.shop_core import CoreShop
from module.shop_white.shop_general import GeneralShop
from module.shop_white.shop_guild import GuildShop
from module.shop_white.shop_medal import MedalShop2
from module.shop_white.shop_merit import MeritShop
from module.shop_white.ui import ShopUI


class RewardShop(ShopUI):
    def run_frequent(self):
        # Munitions shops
        self.ui_goto_shop()

        self.device.click_record_clear()
        self.shop_tab.set(main=self, upper=1)
        self.shop_supply_nav.set(main=self, left=1)
        GeneralShop(self.config, self.device).run()

        self.config.task_delay(server_update=True)

    def run_once(self):
        # Munitions shops
        self.ui_goto_shop()

        self.device.click_record_clear()
        self.shop_tab.set(main=self, upper=1)
        self.shop_supply_nav.set(main=self, left=2)
        MeritShop(self.config, self.device).run()

        self.device.click_record_clear()
        self.shop_tab.set(main=self, upper=1)
        self.shop_supply_nav.set(main=self, left=3)
        GuildShop(self.config, self.device).run()

        # core limited, core monthly, medal, prototype
        self.device.click_record_clear()
        self.shop_tab.set(main=self, upper=2)
        self.shop_monthly_nav.set(main=self, upper=2)
        CoreShop(self.config, self.device).run()

        self.device.click_record_clear()
        self.shop_tab.set(main=self, upper=2)
        self.shop_monthly_nav.set(main=self, upper=3)
        MedalShop2(self.config, self.device).run()

        self.config.task_delay(server_update=True)
