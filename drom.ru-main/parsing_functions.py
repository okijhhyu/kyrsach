import requests
from time import sleep
from bs4 import BeautifulSoup

WEB_HEADERS = {'authority': 'www.domofond.ru', 'cache-control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWeb'
                             'Kit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.11'
                             '6 Safari/537.36',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                         'image/webp,image/apng,*/*;q=0.8,application/signed-'
                         'exchange;v=b3;q=0.9',
               'sec-fetch-site': 'none', 'sec-fetch-mode': 'navigate',
               'sec-fetch-user': '?1', 'sec-fetch-dest': 'document',
               'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7'}


def html_response(url, headers):
    for _ in range(3):
        try:
            response = requests.get(url, headers=headers)
            return response.text
        except ConnectionError or TimeoutError or ConnectionResetError:
            print("\n*****ConnectionError, TimeoutError or ConnectionResetError*"
                  "****\n\nI will retry again after 7 seconds...")
            sleep(7)
            print('Making another request...')


def parse_brand_year_power_prices_cities_urls(response):
    soup = BeautifulSoup(response, 'html.parser')
    my_list = []
    for full_header in soup.find_all('a', {'data-ftid': 'bulls-list_bull'}):
        # try:
            # print(full_header)
            # split_header = full_header.text.split(', ')
            url = full_header.get('href')
            data = {}
            data['url'] = url
            print(url)
            bul_title = full_header.find('span', {'data-ftid': 'bull_title'}).text.split(',')
            # print(bul_title)
            body = html_response(url, WEB_HEADERS)
            # brand_model = url.split('drom.ru/')[1].split('/')
            data['brand'] = bul_title[0].split(' ')[0]
            data['model'] = bul_title[0].split(' ')[1]
            data['year'] = bul_title[1].split(' ')[1]
            soup = BeautifulSoup(body, 'html.parser')
            sleep(5)
            data_dict = {}
            # Находим все строки таблицы
            table_rows = soup.find_all('tr')
            main_div = soup.find('div', class_='css-1j8ksy7 eotelyr0')

            if main_div:
                # Находим все дочерние элементы span внутри основного div
                divs = main_div.find_all('div', class_='css-inmjwf e162wx9x0')

                # Проходим по всем div и выводим текст
                for div in divs:
                    if div.text.strip().startswith('Город:'):
                        data['city'] = div.text.strip().split('Город:')[1]
            # data['city'] = soup.find('span', class_='css-inmjwf e162wx9x0').text.strip()
            # Итерируем по строкам таблицы
            for row in table_rows:
                # Находим заголовок и значение в каждой строке
                header = row.find('th')
                value = row.find('td')

                # Добавляем данные в словарь, пропуская строки, которые не содержат информации
                if header and value:
                    data_dict[header.text.strip()] = value.text.strip()
            price = soup.find('div', class_='css-eazmxc').text.strip()

            data['price'] = price

            # Извлекаем информацию о выделенной цене
            if (soup.find('div', class_='css-1nbcgqx')):
                highlighted_price = soup.find('div', class_='css-1nbcgqx').text.strip()
                data['price_status'] = highlighted_price
            # Выводим результат
            for key, value in data_dict.items():
                data[key] = value
            my_list.append(data)
        # except:
        #     print('ошибка')
    # return(data)

        # # year = split_header[1][0:4]
        # # price = full_header.find('span', class_="css-jnatj e162wx9x0").text[:-2]

        #
        # power = None
        # for i in split_header:
        #     if 'л.с.' in i:
        #         power = i.rsplit('(')[-1][:-6]
    return my_list


def parse_seller_odometer_description(response):
    soup = BeautifulSoup(response, 'html.parser')

    announcement_date = soup.find('div', class_="css-61s82p evnwjo70").text.split('от ')[1]

    try:
        seller = soup.find('div', class_="css-auda1y e162wx9x0").find('a', class_="css-ioq5yh e1wvjnck0").text
    except AttributeError:
        seller = None

    if not seller:
        try:
            seller = soup.find('div', class_="css-98yt60 e29k6pi2").text
        except AttributeError:
            seller = None

    try:
        description = soup.find('span', class_="css-11eoza4 e162wx9x0").text
    except AttributeError:
        description = None

    odometer = None
    for i in soup.find_all('tr', class_="css-10191hq ezjvm5n2"):
        if 'Пробег' in i.text:
            if 'новый автомобиль' in i.text:
                odometer = 'новый автомобиль'
            else:
                try:
                    odometer = i.text.split('км')[1]
                except:
                    odometer = '??'

    return {'announcement_date': announcement_date, 'seller': seller, 'odometer': odometer, 'description': description}


def parse_url_next_page(response):
    soup = BeautifulSoup(response, 'html.parser')
    first = soup.find('div', class_='css-se5ay5 e1lm3vns0')
    try:
        return first.find('a', class_='css-1to36mm e24vrp31').get('href')
    except AttributeError:
        return None
