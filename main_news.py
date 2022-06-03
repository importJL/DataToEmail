import DataToEmail.email_components as ec
import DataToEmail.news as ns
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

    lib = ns.ArticleLib()
    extracted_articles = lib.collect(news_resp, api)
    lib.import_template(templ_path)
    body, body_type = lib.populate_articles(extracted_articles)

    hotmail = ec.EmailManager.setup('outlook', name='outlook')
    msg = ec.Email()
    msg.add_body(body, body_type)

    draft = msg.compose(hotmail, subject='Outlook Test')
    hotmail.send_email(draft)
    print('Done sending e-mail')
