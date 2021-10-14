import time

import requests
import pandas as pd
import config
import json


def extract(auth: dict) -> (list, list):
    session = requests.session()
    session.headers = auth
    body ={
        'filter': {
            "visibility": "ALL"
        },
        'page': 0,
        'page_size': 500
    }
    offers_list = []
    while True:
        try:
            offers = session.post('https://api-seller.ozon.ru/v1/product/list', data=json.dumps(body)).json()['result']['items']
        except:
            time.sleep(3)
            continue
        if offers:
            offers_list.extend(offers)
        else:
            break
        print(f'Страница {body["page"]} готово')
        body['page'] += 1
    # for offer in offers_list:
    counter = 0
    offer_ids = [c['offer_id'] for c in offers_list]
    step = 500
    result_photo = []
    while True:
        try:
            body = {
                'offer_id': offer_ids[counter * step: counter * step + step]
            }
            for item in session.post('https://api-seller.ozon.ru/v2/product/info/list', data=json.dumps(body)).\
                json()['result']['items']:
                offer_id = item['offer_id']
                photo = item['primary_image']
                result_photo.append({'code': offer_id,
                                     'image': photo})
                for image in item['images']:
                    result_photo.append({'code': offer_id,
                                         'image': image})
        except IndexError:
            break
        except KeyError:
            break
        except Exception as Ex:
            print('')
        print(f'Страница {counter} фото готово')
        counter += 1
    result_text = []
    for num, offer in enumerate(offer_ids):
        try:
            resp = session.post('https://api-seller.ozon.ru/v1/product/info/description', json.dumps({'offer_id': offer}))
            text = resp.json()['result']['description']
            result_text.append({
                'code': offer,
                'text': text[:1000]
            })
            print(f'Товар {num} :: {offer} готово')
        except Exception as Ex:
            print('Разрыв по ошибке')
            continue
    return result_photo, result_text


def start():
    result_photo = []
    result_texts = []
    for cab in config.auth_tokens:
        photos, texts = extract(cab)
        result_photo.extend(photos)
        result_texts.extend(texts)
    pd.DataFrame(result_photo).set_index('code').to_excel('photos.xlsx')
    pd.DataFrame(result_texts).set_index('code').to_excel('texts.xlsx')


if __name__ == '__main__':
    start()

