from files_functions import *
from parsing_functions import *
import pymongo

# Replace the following connection string with your MongoDB connection string
# Make sure to replace "<username>", "<password>", "<dbname>", and "<cluster_url>"
mongo_connection_string = "mongodb+srv://okijhhyu:66zxw8lh@cluster0.jy3onoz.mongodb.net/"

file_name = file_name_path_data_name_d_m_h()
# file_name = os.path.join('data', f"data_drom.ru_25.10_23.00.json")

def insert_data_into_mongodb(data):
    # Connect to MongoDB
    client = pymongo.MongoClient(mongo_connection_string)

    # Specify the database and collection
    db = client.get_database("cars")
    collection = db.get_collection("cars_collection")  # Replace "cars_collection" with your desired collection name

    # Insert the data into the collection
    result = collection.insert_many(data)

    print(f"Inserted {len(result.inserted_ids)} documents into MongoDB")

    # Close the MongoDB connection
    client.close()

def main(main_url):
    print('Start scraping...')

    if os.path.isfile(file_name):
        print('Some data is already into:', file_name)
        cars_data = get_city_data_from_json_file(file_name)
        print(cars_data)
    else:
        cars_data = dict()

    page = 46
    while page<=50:
        print('Parse', page, 'page...')
        url = main_url + str(page) + '/'
        main_page_response = html_response(url, WEB_HEADERS)
        # print(main_page_response)
        brand_year_power_prices_cities_urls = parse_brand_year_power_prices_cities_urls(main_page_response)
        if (len(brand_year_power_prices_cities_urls) > 1):
            insert_data_into_mongodb(brand_year_power_prices_cities_urls)
        page = page + 1


if __name__ == '__main__':

    # what_to_parse = input('Будем парсить парсить УФУ (+200 км, выше 950 тыс)?\n(д/н): ').lower()
    what_to_parse = 'l'
    if what_to_parse in ['д', 'l', 'y']:
        main_page = 'https://auto.drom.ru/all/page'
    else:
        main_page = input('Вставьте ссылку drom.ru с выставленными фильтрами: ')

    main(main_page)
    json_to_xlsx()
