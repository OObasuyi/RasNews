import drivers.lcd_driver as lcd_driver
from time import *


class BlueScreen:
    def __init__(self):
        self.lcd = lcd_driver.lcd()
        self.padding = " " * 16

    def screen_scroll(self, send: str, stop_timer: int = 1,speed_reduction:float=.5,flash=False):
        """
        :type stop_timer: int if 0 it will run forever
        """
        self.lcd.lcd_clear()
        if stop_timer < 0:
            raise Exception(f'stop_timer must be an abs integer. given attr is {stop_timer}')
        print_str = self.padding + send
        count_timer = 0

        while count_timer <= stop_timer:
            for i in range(0, len(print_str)):
                lcd_text = print_str[i:(i + 16)]
                self.lcd.lcd_display_string(lcd_text, 1)
                sleep(speed_reduction)
                if flash:
                    self.lcd.lcd_clear()
                self.lcd.lcd_display_string(self.padding, 1)
            if stop_timer > 0:
                count_timer += 2

    def screen_blink(self,send: str,speed_reduction:float=.5,split_str=True):
        self.lcd.lcd_clear()
        split_str = 2 if split_str else 1

        def display_call(send_str):
            self.lcd.lcd_display_string(send_str[:len(send_str) // split_str], 1)
            if split_str > 1:
                self.lcd.lcd_display_string(send[len(send) // split_str:], 2)

        for _ in range(1):
            display_call(send)
            sleep(speed_reduction)
            self.lcd.lcd_clear()
            sleep(speed_reduction)
            display_call(send)

# if __name__ == '__main__':
#     rc = BlueScreen()
#     rc.screen_scroll('1')