import base64
from os import path, urandom
import pickle
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from lcd_screen import BlueScreen
from json import dumps,loads


class SquirrelJump:
    def __init__(self):
        self.sfile = f'{path.dirname(path.abspath(__file__))}/.sjpdir/s61'
        self.print_screen = BlueScreen()

    @staticmethod
    def create_encryption_key(u):
        salt = urandom(16)
        kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
        enc_key = base64.urlsafe_b64encode(kdf.derive(str.encode(str(u))))
        return enc_key

    def credential_creator(self, data_source, phase_to_encrpyt):
        """create a cred file via console for use later"""
        from card_reader import CardManager
        user_data = CardManager(presist=True).card_tap()
        self.encrypt_credentials(data_source, user_data, phase_to_encrpyt)

    def encrypt_credentials(self, data_source, user_data, phase_to_encrpyt):
        hashed, key = user_data[0], user_data[1]

        encrypt_key = Fernet(bytes(key,encoding='utf8'))
        # if its a list convert
        phase_to_encrpyt = dumps(phase_to_encrpyt)
        phase_to_encrpyt = (bytes(phase_to_encrpyt,encoding='utf8'))

        enc_phase = encrypt_key.encrypt(phase_to_encrpyt)

        try:
            with open(self.sfile, 'rb') as f:
                data = pickle.load(f)
                data[hashed][data_source] = enc_phase
        except Exception as e:
            print(f'error: {e}')
            # create nested dict
            data = {hashed:{data_source:enc_phase}}

        with open(self.sfile, 'wb') as f:
            pickle.dump(data, f)

    def decrypt_credentials(self, data_source, user_data):
        # if we cant open the file it doenst exist raise error
        while True:
            try:
                data = self._open_encrypted_file()
                break
            except Exception as e:
                error_str = 'ERROR GETTING FILE QUITTING'
                self.print_screen.screen_blink(error_str, speed_reduction=1, split_str=True)
                raise Exception(f'{error_str}....{e}\n USE CONSOLE TO GEN KEYS')

        hashed, key = user_data[0], user_data[1]

        phase = data[hashed][data_source]
        f = Fernet(bytes(key,encoding='utf8'))
        decr_phase = f.decrypt(phase)
        decr_phase = decr_phase.decode("utf-8")
        decr_phase = loads(decr_phase)

        return decr_phase

    def _open_encrypted_file(self):
        with open(self.sfile, 'rb') as f:
            data = pickle.load(f)
            return data


