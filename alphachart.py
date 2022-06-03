import requests
import os
import re
import json
import pandas as pd
from datetime import datetime
from tabulate import tabulate

import plotly.graph_objects as go
import plotly.io as pio


class PriceChart:
    def __init__(self, data, title=None, sub_title=None, *args):
        _data = pd.DataFrame.from_dict(data).T
        self.raw_data = data
        self.data = self.process_data(_data)
        self.title = title
        self.sub_title = sub_title

        self.curr_code = args[0]
        self.curr_name = args[1]
        self.mkt_code = args[2]
        self.mkt_name = args[3]
        self.last_ref = datetime.strptime(args[4], '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d')

    def __str__(self):
        return tabulate(self.data, self.data.columns, tablefmt="psql")

    def __repr__(self):
        return repr(
            '; '.join(
                [f"Currency Code: {self.__dict__['curr_code']}",
                 f"Currency Name: {self.__dict__['curr_name']}",
                 f"Market Code: {self.__dict__['mkt_code']}",
                 f"Market Name: {self.__dict__['mkt_name']}",
                 f"Last refreshed on: {self.__dict__['last_ref']}"]
            )
        )

    @staticmethod
    def process_data(df, time_range_days=365):
        df = df.set_index(pd.DatetimeIndex(df.index))
        df.columns = [' '.join([c[1].title(), c[-1].upper()]) if len(c) > 2 else c[1].title() for c in df.columns.str.split(' ')]
        lower_time_bound = df.index[0] - pd.Timedelta(days=time_range_days)
        return df.loc[df.index >= lower_time_bound]

    def build_candle_chart(self, show_chart=False, save_img=True, return_path=False):
        candle_data = self.data[self.data.columns[self.data.columns.str.contains(
            'USD')]]

        candlestick = go.Candlestick(
            x=candle_data.index,
            open=candle_data['Open (USD)'],
            high=candle_data['High (USD)'],
            low=candle_data['Low (USD)'],
            close=candle_data['Close (USD)']
        )

        fig = go.Figure(data=[candlestick],
                        layout={'paper_bgcolor': 'rgba(0,0,0,0)',
                                'plot_bgcolor': 'rgba(0,0,0,0)',
                                'width': 1500, 'height': 750,
                                'title': {
                                    'text': f'{self.title} <br><sup>{self.sub_title}</sup>',
                                    'xref': 'paper',
                                    'x': 0,
                                }})
        fig.update_layout(font={'color': '#ffffff'},
                          xaxis={'showgrid': False, 'title': 'Date'},
                          yaxis={'showgrid': False, 'title': 'USD'},
                          xaxis_rangeslider_visible=False,
                          margin={'pad': 10})
        if show_chart:
            fig.show()

        if save_img:
            save_path = os.path.join(os.getcwd(), f"alphav_{self.curr_code}_{self.last_ref}.jpeg")
            pio.write_image(fig, save_path)
            if return_path: return save_path

    @classmethod
    def from_response(cls, resp):
        assert isinstance(resp, requests.Response), f'Data is not a response object - data type is {type(resp)}'
        assert resp.status_code == 200, 'Response retrieval failed'
        _data_json = resp.json()
        title, sub_title, meta_info = cls._extract_meta(_data_json)

        return cls(_data_json['Time Series (Digital Currency Daily)'], title, sub_title, *meta_info)

    @classmethod
    def from_file(cls, file_path=None, pattern: str = '^alphav_.*'):
        if file_path is None:
            search_results = list(
                filter(lambda f: re.search(pattern, f), os.listdir()))
            file_path = sorted(
                search_results, key=os.path.getmtime, reverse=True)[0]

        with open(file_path, 'r') as data_file:
            _data_json = json.load(data_file)
            title, sub_title, meta_info = cls._extract_meta(_data_json)

        return cls(_data_json['Time Series (Digital Currency Daily)'], title, sub_title, *meta_info)

    def to_file(self, out_file=None):
        assert bool(self.data) is True, 'No data is present to export.'
        if out_file is None:
            default_name = f"alphav_{self.curr_code}_{self.mkt_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            out_file = os.path.join(os.getcwd(), default_name)

        with open(out_file, 'w') as out:
            json.dump(self.data, out)

        print('Data is exported to out_file.')

    @staticmethod
    def _extract_meta(response: dict):
        meta = response['Meta Data']
        _title = meta['1. Information']
        curr_code = meta['2. Digital Currency Code']
        curr_name = meta['3. Digital Currency Name']
        mkt_code = meta['4. Market Code']
        mkt_name = meta['5. Market Name']
        last_ref = meta['6. Last Refreshed']

        _title = _title.replace('Digital Currency', curr_name)
        title = _title + f" ({curr_code})"
        _sub_title = f"Currency in {mkt_name} ({mkt_code})"
        sub_title = ' '.join(
            ['Last Refreshed on:', last_ref.split(' ')[0]])

        return title, sub_title, (curr_code, curr_name, mkt_code, mkt_name, last_ref)