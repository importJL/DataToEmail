import os
import re
import uuid
from pathlib import Path
from typing import Union


class Article:
    _id = 0

    def __init__(self, data):
        self.title = data.get('title')
        self.link = data.get('link').strip().strip('\n')
        self.description = data.get('description')

        contents_ = data.get('content')
        if contents_ is not None:
            pattern = re.compile("(.*)(\[.*\])")
            contents_ = pattern.findall(contents_)[0][0].strip()
        self.contents = contents_

        self.image_url = data.get('image_url').strip().strip('\n')
        self.article_id = uuid.uuid4()

        self._increment_id()
        self.id = self._id

    @classmethod
    def _increment_id(cls):
        cls._id += 1


class Card:
    _template = '''
    <td>
        <div 
            style="display: block; 
                   border-radius: 10px; 
                   opacity: 0.65; 
                   border: 1px solid #a2ab95;
                   flex: 1 0 21%;
                   font-family: Arial, Helvetica, sans-serif"
        >
            <div style="display: flex;">
                <img 
                    src="{image_url}" 
                    alt="image_{article_id}" 
                    style="width: 100px; 
                           height: auto; 
                           margin-left: 20px; 
                           margin-top: 10px; 
                           border: 2px solid #4b3feb;"
                >
                <h4 style="margin-left: 10px;"><b>{title}</b></h4>
            </div>
            <div style="padding: 2px 16px; position: relative">
                <p>
                    {description}
                </p>
                <br>
                <div style="width: 115px;
                            --padding: 2px;
                            padding: var(--padding);
                            box-shadow: inset 0 0 2px var(--padding) #22158f;
                            background-color: #0f0942;
                            position: absolute;
                            bottom: 3px;">
                    <a href="{link}" 
                       style="text-decoration: none; 
                              color: #ffffff;
                              padding: 10px;
                              font-size: 12px;
                              font-style: italic;
                              font-family: Tahoma, sans-serif;">
                        Click for full story
                    </a>
                </div>
            </div>
        </div>
    </td>
    '''

    @classmethod
    def populate(cls, article_list: list[Article]):
        card_list = ['<tr>']
        for i in range(len(article_list)):
            card_list.append(
                cls._template.format(
                    image_url=article_list[i].image_url,
                    article_id=article_list[i].article_id,
                    title=article_list[i].title,
                    description=article_list[i].description,
                    link=article_list[i].link
                )
            )
            if i % 3 == 2:
                card_list.append('</tr><tr>')
        card_list.append('</tr>')

        return card_list


class ArticleLib:
    def __init__(self):
        self.body = None
        self.body_type = None

    @staticmethod
    def _check_status(resp):
        return resp.get('status') in ['success', 'ok']

    @staticmethod
    def _check_api_src(api_src):
        return api_src == 'newsdataio'

    @classmethod
    def _extract_articles(cls, resp, api_src):
        bool_newsdataio = cls._check_api_src(api_src)
        if cls._check_status(resp):
            return (resp.get('articles'), resp.get('results'))[bool_newsdataio is True]
        return None

    def collect(self, resp: dict, api_src: str):
        bool_newsdataio = self._check_api_src(api_src)
        data = self._extract_articles(resp, api_src)
        article_list = []
        if data is not None:
            for item in data:
                article_list.append(
                    Article(
                        {
                            'title': item.get('title'),
                            'link': (item.get('url'), item.get('link'))[bool_newsdataio is True],
                            'description': item.get('description'),
                            'content': item.get('content'),
                            'image_url': (item.get('urlToImage'), item.get('image_url'))[bool_newsdataio is True]
                        }
                    )
                )
        return article_list

    def import_template(self, file_path: Union[str, Path]):
        assert os.path.exists(file_path) is True, 'Not a valid template file path'

        _, ext = os.path.splitext(file_path)
        with open(os.path.join(file_path), 'r') as file:
            self.body = file.read()
            self.body_type = 'plain' if 'txt' in ext else 'html'

    def populate_articles(self, article_list: list[Article]):
        cards_list = Card.populate(article_list)
        assert self.body is not None, 'Body template is not imported.'
        return self.body.format(cards=''.join(cards_list)), self.body_type