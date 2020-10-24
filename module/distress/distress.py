from module.logger import logger
from module.base.timer import Timer
from module.ocr.ocr import Digit
from module.distress.assets import *
from module.handler.assets import POPUP_CANCEL
from module.campaign.run import CampaignRun
from module.campaign.campaign_ui import CampaignUI, STAGE_SHOWN_WAIT
from module.ui.ui import UI
from random import randint

OCR_DISTRESS_REMAIN = Digit(OCR_DISTRESS_REMAIN, letter=(255, 247, 247), threshold=128, alphabet='0123456789')
RECORD_OPTION = ('DailyRecord', 'distress')
RECORD_SINCE = (0,)

class DistressSignal(CampaignRun, CampaignUI):
    remain = 0

    def _handle_signals(self, search=False):
        # Loop until all distress signals gone
        while 1:
            # The distress window is unique
            # cannot be closed in any manner
            # except by DISTRESS_SEARCH_CLOSE
            for _ in range(2):
                self.device.click(DISTRESS_RADAR)
                self.device.sleep(0.3)

            # Wait for button to appear, only once
            # stabilized, can perform OCR check
            self.wait_until_appear(DISTRESS_SEARCH_START)
            self.wait_until_stable(DISTRESS_SEARCH_START)

            # Perform approriate handle_x_once based on boolean
            if search:
                self.remain = OCR_DISTRESS_REMAIN.ocr(self.device.image)
                logger.info(f'Remaining Signals: {self.remain}')

                if self.remain > 0:
                    terminate = self._handle_search_once()
                    if terminate:
                        break
                else:
                    self.device.click(DISTRESS_SEARCH_CLOSE)
                    break
            else:
                if self.appear(DISTRESS_SEARCH_GOTO):
                    self._handle_goto_once()
                    continue
                else:
                    logger.info('Empty list, no more found signals to execute')
                    self.device.click(DISTRESS_SEARCH_CLOSE)
                    break


    def _handle_search_once(self):
        # Assumed to be in distress window due to _handle_signals
        self.device.click(DISTRESS_SEARCH_START)

        # Wait loop to check for popup_cancel or info_bar
        # May or may not be encountered, limit 8s
        end_check_timer = Timer(8, count=3)
        while 1:
            self.device.screenshot()

            # Encountered when surplus signals, but all chapters already have a distress stage
            if self.info_bar_count():
                logger.info('Signal cannot be used, terminate search early')
                self.ensure_no_info_bar()
                return True

            # Encountered when distress found, but not in current chapter location
            if self.appear(POPUP_CANCEL):
                self.device.click(POPUP_CANCEL)
                return False

            # Begin timer check
            if not end_check_timer.started():
                end_check_timer.start()
                continue

            # Timeout, this indicates current chapter location is where the distress was found
            if end_check_timer.reached():
                logger.info('Wait limit reached, neither popup_cancel or info_bar were encountered')
                return False


    def _handle_goto_once(self):
        # Assumed to be in distress window due to _handle_signals
        # Transition to signal chapter
        self.device.click(DISTRESS_SEARCH_GOTO)
        self.device.sleep(STAGE_SHOWN_WAIT)
        self.device.screenshot()

        # Retrieve current campaign location information
        chapter = self.get_chapter_index(self.device.image)
        name = f'campaign_{chapter}_5'
        target_chapter = f'{chapter}-5'

        # Utilize distress settings to set corresponding
        # fleet compositions based on chapter
        if chapter < 6:
            self.config.FLEET_1 = self.config.DISTRESS_FIXED_FLEET_1
        elif chapter in self.config.DISTRESS_SELECT_TARGETS:
            self.config.FLEET_1 = self.config.DISTRESS_SELECT_FLEET_1
            self.config.FLEET_2 = self.config.DISTRESS_SELECT_FLEET_2
        else:
            self.config.FLEET_1 = self.config.DISTRESS_REMAIN_FLEET_1
            self.config.FLEET_2 = self.config.DISTRESS_REMAIN_FLEET_2

        # If same, set FLEET_2 to random select but not FLEET_1
        while self.config.FLEET_1 == self.config.FLEET_2:
            self.config.FLEET_2 = randint(1, 6)

        # Load campaign file, retrieve entrance, and run
        self.load_campaign(name=name, folder='campaign_distress')
        self.campaign.ensure_campaign_ui(target_chapter)

        # Reset fleet_checked before and after
        # running the distress campaign for
        # next potential run and other ALAS operations
        logger.info(f'Commence Rescue in {name}')
        #self.campaign.fleet_checked_reset()
        self.campaign.run()
        #self.campaign.fleet_checked_reset()

        # Campaign Complete, wait until info_bar disappears
        self.ensure_no_info_bar()

    def run(self):
        # Back up configured fleet composition and reward settings
        fleet_1_backup = self.config.FLEET_1
        fleet_2_backup = self.config.FLEET_2
        self.reward_backup_daily_reward_settings()

        # Ensure page_campaign
        self.ui_weigh_anchor()

        # Exhaust all search attempts for signals
        logger.hr('Distress_Search_Begin', level=1)
        self._handle_signals(True)
        logger.hr('Distress_Search_End', level=1)

        # Exhaust all goto button appearances for signals
        logger.hr('Rescue_Begin', level=1)
        self._handle_signals(False)
        logger.hr('Rescue_End', level=1)

        # Restore configured fleet composition and reward settings
        self.config.FLEET_1 = fleet_1_backup
        self.config.FLEET_2 = fleet_2_backup
        self.reward_recover_daily_reward_settings()


    def record_executed_since(self):
        return self.config.record_executed_since(option=RECORD_OPTION, since=RECORD_SINCE)

    def record_save(self):
        return self.config.record_save(option=RECORD_OPTION)