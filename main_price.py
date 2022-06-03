from email_components import EmailManager, Email
from alphachart import PriceChart
import os
import json
import requests


def get_data(main_dir, api='alphavantage', symbol='ETH', market='HKD'):
    with open(os.path.join(main_dir, 'config', 'keys.json'), 'r') as file:
        key_file = json.load(file)
    key = key_file[api]['key']
    url = f'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market={market}&apikey={key}'
    return requests.get(url)


if __name__ == '__main__':
    curr_dir = os.getcwd()
    templ_path = os.path.join(curr_dir, 'templates', 'text_body.txt')
    price_resp = get_data(curr_dir)
    eth = PriceChart.from_response(price_resp)
    fig_path = eth.build_candle_chart(return_path=True)

    hotmail = EmailManager.setup('outlook', name='test1')
    msg = Email()

    txt_body_params = {
        'recipient_name': 'Test',
        'coin_name': eth.curr_code
    }
    msg.body_from_template(templ_path, **txt_body_params)
    msg.add_attachments(fig_path)

    draft = msg.compose(hotmail, subject='Outlook Test')
    hotmail.send_email(draft)
    print('Done sending e-mail')
