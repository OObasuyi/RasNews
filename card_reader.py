import RPi.GPIO as GPIO

from mfrc522 import SimpleMFRC522
from random import choices
from string import ascii_letters, digits
from hashlib import sha256
from sqlalchemy import create_engine
import pandas as pd
from gpiozero import Buzzer
from time import sleep
from lcd_screen import BlueScreen

GPIO.setmode(GPIO.BCM)


class CardManager:
    def __init__(self, presist=True):
        self.reader = SimpleMFRC522()
        self.persist = presist
        self.boarders = '#' * 1
        engine = create_engine('sqlite:///ikp.db')
        self.engine = engine.connect()
        self.print_screen = BlueScreen()

    def _authenicate_user(self):
        try:
            self.print_screen.screen_blink(f'{self.boarders} waiting for keys {self.boarders}', speed_reduction=.5,split_str=True)
            uid, passwd = self.reader.read()
            self.activate_buzzer()
            d_row = pd.read_sql(f'select Cid,sig_info from ikp where Cid = {uid}', con=self.engine)
            d_row = d_row.to_dict('records')[0]

            # remove padding from key
            passwd = passwd.rstrip()
            compare_hash = sha256(str.encode(f'{passwd}{uid}', 'utf-8')).hexdigest()

            if d_row['sig_info'] == compare_hash:
                return compare_hash,passwd
            else:
                return False
        except Exception as e:
            # returns none
            self.print_screen.screen_blink(f'error {e.args[0]}', speed_reduction=.5,split_str=True)

    def _config_card(self):
        from secret_handling import SquirrelJump

        ran_alpanum_seq = ''.join(choices(ascii_letters + digits, k=16))
        key_gen = SquirrelJump()
        try:
            self.print_screen.screen_blink(f'{self.boarders} CREATING NEW KEY {self.boarders}', speed_reduction=1,split_str=True)
            self.print_screen.screen_scroll("Please Place your tag until complete message is shown", speed_reduction=.25)

            uid, _ = self.reader.read()
            self.activate_buzzer()
            # store key on card and take hash of it for the db
            kg = key_gen.create_encryption_key(f"{ran_alpanum_seq}{uid}")
            kg = kg.decode("utf-8")
            h = sha256(str.encode(f'{kg}{uid}', 'utf-8')).hexdigest()
            self.reader.write(kg)
            self.activate_buzzer()
            
            pd.DataFrame([{"Cid": uid, 'sig_info': h}]).to_sql('ikp', self.engine, if_exists='append')
            self.print_screen.screen_blink("NEW CARD CREATED :)", speed_reduction=.5,split_str=True)
        except Exception as e:
            self.print_screen.screen_blink(f'error {e.args[0]}', speed_reduction=.5,split_str=True)

    def card_tap(self) -> tuple:
        """when process ends successfully should return a user,pass tuple"""
        def acquire_status():
            for _ in range(4):
                status = self._authenicate_user()
                if status:
                    self.print_screen.screen_blink(f'{self.boarders} Authenticated :) {self.boarders}', speed_reduction=.5,)
                    return status
                elif not status and status is not None:
                    self.print_screen.screen_blink(f'{self.boarders} Wrong Password try again {self.boarders}', speed_reduction=.5,)
                else:
                    break

        while True:
            acquired_stat = acquire_status()
            if acquired_stat:
                return acquired_stat
            else:
                self.print_screen.screen_blink(f'{self.boarders} password trial timeout... {self.boarders}', speed_reduction=.5,)
                self.print_screen.screen_scroll(f'{self.boarders} please reset card in the following steps {self.boarders}',speed_reduction=.15)
                self._config_card()

    @staticmethod
    def activate_buzzer():
        buzzer = Buzzer(17)
        buzzer.on()
        sleep(.05)
        buzzer.off()



if __name__ == '__main__':
    rc = CardManager()
    rc._config_card()
    rc._authenicate_user()
