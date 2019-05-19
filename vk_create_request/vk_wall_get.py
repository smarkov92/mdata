import requests
import pandas as pd
from datetime import datetime
import time

def main_vk_request_wall(id_group, count_posts, filter):

    data = get_request_wall(id_group, count_posts, filter)
    data_posts = data['data']
    max_count_posts = data['max_count_posts']
    stats = processing_data_vk_posts(data_posts)
    vk_excel_url = data_to_excel(stats, id_group)

    return {'vk_excel_url': vk_excel_url, 'max_count_posts': max_count_posts}




def get_request_wall(id_group, count_posts, filter):
    token = 'af567951af567951af5679518caf3e98dfaaf56af567951f3270969be965f073f20981f'
    offset = 0
    count = 100
    data_posts = []
    max_count_posts = 0

    while offset < count_posts:

        url = 'https://api.vk.com/method/wall.get'
        params = {
            'domain': id_group,
            'filter': filter,
            'count': count,
            'offset': offset,
            'access_token': token,
            'v': 5.73
        }

        r = requests.get(url, params=params).json()

        check = True
        if check:
            max_count_posts = r['response']['count']
            if max_count_posts < count_posts:
                count_posts = max_count_posts
                check = False
            else:
                check = False

        data_posts += r['response']['items']
        offset += count
        time.sleep(0.5)

    return {'data': data_posts, 'max_count_posts': max_count_posts}


def processing_data_vk_posts(data_posts):
    stats = []

    for record in data_posts:
        title = record['text'].split('\n')[0]  # название поста берем символы до первого переноса
        if len(title) > 80:  # я взял первые 80 символов из названия поста
            title = title[:80]

        len_title = len(record['text'])  # вытаскиваем длинну текста
        len_title = len_title // 100 * 100  # для удобства групировки по кол-ву символов разбил на промежутки по 100, тоесть если длинна текста 200 это значит , что символов от 200 до 300

        date = datetime.fromtimestamp(record['date']).strftime('%Y-%m-%d')  # вытаскиваем дату в формате ГГГГ-ММ-ДД
        hour = datetime.fromtimestamp(record['date']).strftime('%H')  # вытаскиваем час

        attachment = {'photo': 0, 'audio': 0, 'video': 0, 'link': 0,
                      'poll': 0}  # список из типов вложений. Я использовал самые популярные , если у вас другие типы вложений вы можете добавить их в список. Взять можно отсюда https://vk.com/dev/objects/attachments_w

        if 'attachments' in record:  # цикл для подсчета типов и кол-ва вложений
            for attach in record['attachments']:
                if attach['type'] in attachment:
                    attachment[attach['type']] = attachment[attach['type']] + 1

        if 'views' in record:
            views = record['views']['count']
        else:
            views = 0

        total_actions = record['comments']['count'] + record['likes']['count'] + record['reposts'][
            'count']  # сумируем все активности

        # создаем список и добавляем в него название, длину, кол-во фото, кол-во аудио, кол-во видео в постах, постов с сылками, пстов с опросами, просмотры, кол-во просмотров, комментариев, лайков, репостов, сумму всех взаимодействий, дату и час
        stats.append(
            [title, len_title, attachment['photo'], attachment['audio'], attachment['video'], attachment['link'],
             attachment['poll'], views, record['comments']['count'], record['likes']['count'],
             record['reposts']['count'], total_actions, date, hour])

    return stats

def data_to_excel(stats, id_group):
    # Создаем DataFrame (таблицу) из данных и записываем
    columns = ["name_post", 'len_text', 'photo', 'audio', 'video', 'link', 'poll', "views", "comments", "likes",
               "share", 'total_action', "date", "hour"]  # задаем заголовки таблицы
    df = pd.DataFrame(data=stats, columns=columns)

    # групировка таблиц по часам и удаление не нужных столбцов
    df_hour = df.drop(['len_text', 'photo', 'audio', 'video', 'link', 'poll'], axis=1)
    df_group_by_hour = df_hour.groupby('hour').sum()  # группируем значения по часу
    df_group_by_hour['count_post'] = df_hour.groupby('hour')[
        'name_post'].count()  # считаем колличесво постов вышедших в данный час
    df_group_by_hour['mean_action'] = df_group_by_hour['total_action'] / df_group_by_hour[
        'count_post']  # считаем среднее значение активности (все активности / кол-во активностей)
    df_group_by_hour['views_on_post'] = df_group_by_hour['views'] / df_group_by_hour['count_post']
    df_group_by_hour['er'] = df_group_by_hour['total_action'] / df_group_by_hour[
        'views'] * 100  # считаем ER (все активности / кол-во просмотров * 100)
    df_group_by_hour = df_group_by_hour.sort_values(by="er", ascending=False)  # сортируем по ER

    # групировка таблиц по типам и удаление не нужных столбцов
    df_type = df.drop(['date', 'hour'], axis=1)
    df_group_by_len_title = df_type.groupby('len_text').sum()
    df_group_by_len_title['count_posts'] = df_type.groupby('len_text')['name_post'].count()
    df_group_by_len_title['mean_action'] = df_group_by_len_title['total_action'] / df_group_by_len_title['count_posts']
    df_group_by_len_title['views_on_post'] = df_group_by_len_title['views'] / df_group_by_len_title['count_posts']
    df_group_by_len_title['er'] = df_group_by_len_title['total_action'] / df_group_by_len_title['views'] * 100
    df_group_by_len_title = df_group_by_len_title.sort_values(by='views', ascending=False)
    df_group_by_len_title = df_group_by_len_title.style.format("{:.2f}")

    # запись в excel файл
    record_url_xlsx = 'static/data_vk_{}.xlsx'.format(id_group)
    with pd.ExcelWriter(record_url_xlsx) as writer:
        df.to_excel(writer, index=False, sheet_name='Исходный DataFrame')
        df_group_by_hour.to_excel(writer, index=True, sheet_name='Групировка по часу')
        df_group_by_len_title.to_excel(writer, index=True, sheet_name='Групировка по кол-ву символов')
        for atach in ['photo', 'audio', 'video', 'link', 'poll']:
            df_group_by_temp = df_type.groupby(atach).sum()
            df_group_by_temp = df_group_by_temp.loc[:, ["views", "comments", "likes", "share", 'total_action']]
            df_group_by_temp['count_posts'] = df_type.groupby(atach)['name_post'].count()
            df_group_by_temp['mean_action'] = df_group_by_temp['total_action'] / df_group_by_temp['count_posts']
            df_group_by_temp['views_on_post'] = df_group_by_temp['views'] / df_group_by_temp['count_posts']
            df_group_by_temp['er'] = df_group_by_temp['total_action'] / df_group_by_temp['views'] * 100
            df_group_by_temp = df_group_by_temp.sort_values(by='er', ascending=False)
            df_group_by_temp = df_group_by_temp.style.format("{:.2f}")
            sheet_name = 'Групировка по ' + atach
            df_group_by_temp.to_excel(writer, index=True, sheet_name=sheet_name)

    return record_url_xlsx