from email_components import EmailManager, Email
from news import ArticleLib
from newsapi import NewsApiClient
import os
import json


def get_data(main_dir, api='newsapi', sources='business-insider'):
    with open(os.path.join(main_dir, 'config', 'keys.json'), 'r') as file:
        key_file = json.load(file)
    key = key_file[api]['key']
    client = NewsApiClient(api_key=key)
    response = client.get_top_headlines(sources=sources, language='en')
    return response


if __name__ == '__main__':
    curr_dir = os.getcwd()
    api = 'newsapi'
    templ_path = os.path.join(curr_dir, 'templates', 'text_body.html')

    news_resp = get_data(curr_dir, api=api)

    lib = ArticleLib()
    extracted_articles = lib.collect(news_resp, api)
    lib.import_template(templ_path)
    body, body_type = lib.populate_articles(extracted_articles)

    hotmail = EmailManager.setup('outlook', name='test1')
    msg = Email()
    msg.add_body(body, body_type)

    draft = msg.compose(hotmail, subject='Outlook Test')
    hotmail.send_email(draft)
    print('Done sending e-mail')
