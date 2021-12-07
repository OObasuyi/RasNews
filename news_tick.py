from newsapi import NewsApiClient
from alpaca_trade_api.rest import REST, TimeFrame
from os import path
from card_reader import CardManager
from lcd_screen import BlueScreen
from secret_handling import SquirrelJump


class RainCheck:
    def __init__(self):
        self.project_path = f'{path.dirname(path.abspath(__file__))}'
        self.key_grabber = SquirrelJump()
        self.print_screen = BlueScreen()

    @staticmethod
    def stock_data(api_key,) -> str:
        api_key = api_key[0]
        api = REST(secret_key=api_key['secret'],base_url=api_key['endpoint'],key_id=api_key['keyid'])

        data = api.get_bars(symbol="GME",timeframe=TimeFrame.Hour,limit=4,adjustment='raw').df
        data = data['close'].pct_change()[-2:]
        data = ' GME IS UP FROM THE PAST HOURS DIAMOND-HANDS' if data.is_monotonic_increasing else 'GME IS DOWN WHERE CAN I FIND THE NEAREST SOUP KITCHEN?'
        return data

    @staticmethod
    def news_data(api_key) -> list:
        new_client = NewsApiClient(api_key=api_key)
        data = new_client.get_top_headlines(category='business')
        data = [": ".join([headline['source']['name'],headline['title']]) for headline in data['articles']]
        return data

    def thundercloud(self):
        cm = CardManager(presist=True)
        user_data = cm.card_tap()
        while True:
            news_key = self.key_grabber.decrypt_credentials('news_api', user_data)
            alpaca_key = self.key_grabber.decrypt_credentials('alpaca_api', user_data)

            news_data = self.news_data(news_key)
            alpaca_data = self.stock_data(alpaca_key)
            cum_data = list()
            for n, l in enumerate(news_data):
                if divmod(n, 3)[1] == 0:
                    cum_data.append(alpaca_data)
                cum_data.append(l)

            # print to scroll
            for hl in cum_data:
                self.print_screen.screen_scroll(hl, speed_reduction=.15)


if __name__ == '__main__':
    rc = RainCheck()
    rc.thundercloud()
