import openai
import json
import re
import pymongo
from tkinter import ttk
import tkinter as tk

def search():
    data = entry.get().lower()  # Получаем текст из поля ввода и приводим к нижнему регистру
    # Отправка запроса к API для получения ответа от GPT-3
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role': 'system', 'content': user_message1},
            {'role': 'system', 'content': user_message2},
            {'role': 'system', 'content': user_message3},
            {'role': 'system', 'content': user_message4},
            {'role': 'user', 'content': data}
        ],
    )

    query = {}
    sort = {}

    sorted_array = []

    json_match = re.search(r'\{.*\}', response.choices[0].message.content, re.DOTALL)
    results.delete(1.0, tk.END)  # Очищаем виджет вывода

    if json_match:
        # Извлечь JSON-часть из найденного совпадения
        json_string = json_match.group(0)
        # Разбор строки JSON
        json_object = json.loads(json_string)

        print(json_object)
        all_filters = {key.lower(): value for key, value in json_object.items()}

        for item in filter_criteria:
            if item in all_filters:
                if item == "color":
                    query["Цвет"] = all_filters[item]
                elif item == "коробка передач":
                    query["Коробка передач"] = all_filters[item]
                elif item == "привод":
                    query["Привод"] = all_filters[item]
                elif item == "brand":
                    query["brand"] = all_filters[item]
                elif item == "price_status":
                    query["price_status"] = all_filters[item].lower()
                elif item == "цвет":
                    query["Цвет"] = all_filters[item].lower()
                elif item == "руль":
                    query["Руль"] = all_filters[item].lower()
                elif item == "поколение":
                    query["Поколение"] = all_filters[item]
                elif item == "комплектация":
                    query["Комплектация"] = all_filters[item]
                    query[item] = json_object[item]
                elif item == "model":
                    query["model"] = all_filters[item]
                    query[item] = json_object[item]
        # Масссив похожих обьявлений
        all_records = collection.find(query)

        # Сортировка
        for item in sort_criteria:
            if item in all_filters:
                if item == "year":
                    sort["year"] = all_filters[item]
                elif item == "city":
                    sort["city"] = all_filters[item]
                elif item == "price":
                    sort["price"] = all_filters[item]
                elif item == "двигатель":
                    sort["двигатель"] = all_filters[item]
                elif item == "объем двигателя":
                    sort["объем двигателя"] = all_filters[item]
                elif item == "мощность":
                    sort["мощность"] = all_filters[item]
                elif item == "пробег":
                    sort["пробег"] = all_filters[item]

        for car in all_records:
            koef = 100
            for item in sort:
                if item == "уear":
                    if type(sort[item]) == str:
                        diffYear = int(car[item]) - int(sort[item])
                        koef = koef - diffYear * 4
                    else:
                        if 'min' in sort[item]:
                            if int(sort[item]['min']) > int(car[item]):
                                diffYear = int(sort[item]['min']) - int(car[item])
                                koef = koef - diffYear * 4
                        if 'max' in sort[item]:
                            if int(sort[item]['max']) < int(car[item]):
                                diffYear = int(car[item]) - int(sort[item]['max'])
                                koef = koef - diffYear * 4
                        if 'equals' in sort[item]:
                            if int(sort[item]['equals']) >= int(car[item]):
                                diffYear = int(sort[item]['equals']) - int(car[item])
                                koef = koef - diffYear * 4
                            else:
                                diffYear = int(car[item]) - int(sort[item]['equals'])
                                koef = koef - diffYear * 4
                if item == "пробег":
                    probeg = int(re.sub(r'\D', '', car["Пробег"]))
                    if type(sort[item]) == str:
                        diff = int(probeg) - int(sort[item])
                        koef = koef - (diff / 2500)
                    else:
                        if 'min' in sort[item]:
                            if int(sort[item]['min']) > int(probeg):
                                diff = int(sort[item]['min']) - int(probeg)
                                koef = koef - (diff / 2500)
                        if 'max' in sort[item]:
                            if int(sort[item]['max']) < int(probeg):
                                diff = probeg - int(sort[item]['max'])
                                koef = koef - (diff / 2500)
                        if 'equals' in sort[item]:
                            if int(sort[item]['equals']) >= probeg:
                                diff = int(sort[item]['equals']) - probeg
                                koef = koef - (diff / 2500)
                            else:
                                diff = probeg - int(sort[item]['equals'])
                                koef = koef - (diff / 2500)
                if item == "мощность":
                    mosh = int(re.sub(r'\D', '', car["Мощность"]))
                    if type(sort[item]) == str:
                        diff = int(mosh) - int(sort[item])
                        koef = koef - (diff)
                    else:
                        if 'min' in sort[item]:
                            if int(sort[item]['min']) > int(mosh):
                                diff = int(sort[item]['min']) - int(mosh)
                                koef = koef - diff
                        if 'max' in sort[item]:
                            if int(sort[item]['max']) < int(mosh):
                                diff = mosh - int(sort[item]['max'])
                                koef = koef - diff
                        if 'equals' in sort[item]:
                            if int(sort[item]['equals']) >= mosh:
                                diff = int(sort[item]['equals']) - mosh
                                koef = koef - diff
                            else:
                                diff = mosh - int(sort[item]['equals'])
                                koef = koef - diff
                if item == "price":
                    price = int(re.sub(r'\D', '', car["price"]))
                    if type(sort[item]) == str:
                        diff = int(price) - int(sort[item])
                        koef = koef - (diff / 5000)
                    else:
                        if 'min' in sort[item]:
                            if int(sort[item]['min']) > int(price):
                                diff = int(sort[item]['min']) - int(price)
                                koef = koef - (diff / 5000)
                        if 'max' in sort[item]:
                            if int(sort[item]['max']) < int(price):
                                diff = price - int(sort[item]['max'])
                                koef = koef - (diff / 5000)
                        if 'equals' in sort[item]:
                            if int(sort[item]['equals']) >= price:
                                diff = int(sort[item]['equals']) - price
                                koef = koef - (diff / 5000)
                            else:
                                diff = price - int(sort[item]['equals'])
                                koef = koef - (diff / 5000)
                if item == "объем двигателя":
                    dvish = int(re.sub(r'\D', '', car["Двигатель"]))
                    if type(sort[item]) == str:
                        diff = int(dvish) - int(sort[item])
                        koef = koef - diff / 2
                    else:
                        if 'min' in sort[item]:
                            if int(sort[item]['min']) > int(dvish):
                                diff = int(sort[item]['min']) - int(dvish)
                                koef = koef - diff / 2
                        if 'max' in sort[item]:
                            if int(sort[item]['max']) < int(dvish):
                                diff = dvish - int(sort[item]['max'])
                                koef = koef - diff / 2
                        if 'equals' in sort[item]:
                            if int(sort[item]['equals']) >= dvish:
                                diff = int(sort[item]['equals']) - dvish
                                koef = koef - diff / 2
                            else:
                                diff = dvish - int(sort[item]['equals'])
                                koef = koef - diff / 2
                if item == "двигатель":
                    if sort[item] != car["Двигатель"].split(',')[1]:
                        koef = koef - 10
                if item == "city":
                    if (sort[item] != car["city"] or sort[item] != car["city"].split(',')[0] or sort[item] != car["city"].split(',')[1]):
                        koef = koef - 10
            if (koef < 0):
                koef = 0
            car["коэффициент"] = koef
            sorted_array.append(car)
        sorted_array = sorted(sorted_array, key=lambda x: x.get("коэффициент", 0), reverse=True)

    for car in sorted_array:
        results.insert(tk.END, " Совпадение     : " + str(car['коэффициент']) + "\n")
        results.insert(tk.END, " Ccылка         : " + str(car['url']) + "\n")
        results.insert(tk.END, " Марка          : " + str(car['brand']) + "\n")
        results.insert(tk.END, " Модель         : " + str(car['model']) + "\n")
        results.insert(tk.END, " Год            : " + str(car['year']) + "\n")
        results.insert(tk.END, " Цена           : " + str(car['price']) + "  -  " + str(car['price_status']) + "\n")
        results.insert(tk.END, " Двигатель      : " + str(car['Двигатель']) + "\n")
        results.insert(tk.END, " Мощность       : " + str(car['Мощность'].split(',')[0]) + "\n")
        results.insert(tk.END, " Коробка передач: " + str(car['Коробка передач']) + "\n")
        results.insert(tk.END, " Тип кузова     : " + str(car['Привод']) + "\n")
        results.insert(tk.END, " Цвет           : " + str(car['Цвет']) + "\n")
        results.insert(tk.END, " Пробег         : " + str(car['Пробег']) + "\n")
        results.insert(tk.END, " Руль           : " + str(car['Руль']) + "\n")
        results.insert(tk.END, " Поколение      : " + str(car['Поколение']) + "\n")
        if "Комплектация" in car:
            results.insert(tk.END, " Комплектация   : " + str(car['Комплектация']) + "\n")
        results.insert(tk.END, " Город          :" + str(car['city']) + "\n")
        results.insert(tk.END, " ____________________________________________________________________________\n")


# Параметры для базы данных
client = pymongo.MongoClient("mongodb+srv://okijhhyu:66zxw8lh@cluster0.jy3onoz.mongodb.net/")
db = client['cars']
collection = db["cars_collection"]
all_records = collection.find()

# Установите ваш API ключ
openai.api_key = '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'

# Настройка системы
user_message1 = "есть только эти фильтры brand, model, year если до добавляешь max если после то min если просто такого-то года то equals, city, price - цена если до добавляешь max если после то min если просто такая-то цена то equals, Цвет, price_status - может быть высокая цена, хорошая цена, нормальная цена, отличная цена, двигатель бензин, дизель, объем двигателя если до добавляешь max если после то min, если просто такой-то объем то equals, мощьность в л.с. если до добавляешь max если после то min, если просто такая-то мощность или просто написано с пробегом то equals коробка передач: АКПП, механика, автомат Привод; передний, задний 4WD, Тип кузова Седан Хэтчбек 5 дв. Хэтчбек 3 дв. Лифтбек Джип 5 дв. Джип 3 дв. Универсал Минивэн Пикап Купе Открытый, пробег в км если до добавляешь max если после то min, если просто такой-то пробег то equals, Руль правый левый, соответсвенно только по этим параметрам составлять json обьект не меняй названия фильтров, без лишнего текста"
user_message2 = "не добавляй от себя фильтры которые не указаны если в естественном языке они не добавлены, то значит не нужно выдумывать для них фильтры"
user_message3 = "мне нужно чтобы ты принимала запрос на естественном языке, например найди мне машину серого цвета bmw в 150000тр. И мне нужно, чтобы ты обработала этот запрос и на выходе дала json обьект с фильтрами, для этого это будет {Цвет:серый, brand: bmw, price: {equals: 150000}}, "
user_message4 = "brand bmw в ввыходных фильтрах всегда должен быть таким BMW, у остальных первая буква заглавная"

filter_criteria = [
    "коробка передач",
    "привод",
    "brand",
    "model",
    "price_status",
    "цвет",
    "руль",
    "поколение",
    "сolor",
    "комплектация"
]

sort_criteria = [
    "пробег",
    "year",
    "city",
    "price",
    "двигатель",
    "объем двигателя",
    "мощность",
]
# Создание главного окна
root = tk.Tk()
root.title("Пример поиска в Tkinter")
root.config(bg="skyblue")
# Создание виджетов
label = tk.Label(root, text="Введите запрос:")
entry = tk.Entry(root, width=60)
search_button = tk.Button(root, text="Поиск", width=20, command=search)
results = tk.Text(root, height=50, width=80)

# Размещение виджетов с использованием сетки
label.grid(row=0, column=0, padx=10, pady=10)
entry.grid(row=0, column=1, padx=10, pady=10)
search_button.grid(row=0, column=2, padx=10, pady=10)
results.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
# Запуск главного цикла
root.mainloop()
