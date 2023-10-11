import requests
import csv
from dotenv import load_dotenv
from os import getenv
import json
import time
import os


def load_books(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = list(reader)
    return {book['isbn']: book for book in data}


def get_book(isbn, api_key):
    header = {'Authorization': api_key}
    response = requests.get("https://api.premium.isbndb.com/book/"+isbn, headers=header)
    return response.json()['book']


def get_books():
    load_dotenv()
    api_key = getenv('REST_API_KEY')
    books = load_books('isbn.csv')
    i = 0
    for isbn in books:
        with open('books\\'+isbn+'.json', 'x', encoding='utf-8') as file:
            try:
                book = get_book(isbn, api_key)
                json.dump(book, file, indent=4)
            except:
                pass
        i += 1
        percentage = (i / len(books)) * 100 
        print(f"{percentage:.2f}%", end='\r')
        time.sleep(0.4)


def create_book_csv(fieldnames):
    with open('all_books.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()


def add_book(book, fieldnames):
    with open('all_books.csv', 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        row_data = {field: book.get(field, "") for field in writer.fieldnames}
        if any(row_data.values()):
            writer.writerow(row_data)


def merge_books():
    fieldnames = ["title", "authors", "synopsis", "subjects", "pages", "date_published", "image", "isbn13"]
    folder_path = 'books\\'
    create_book_csv(fieldnames)
    file_names = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    for file_name in file_names:
        with open(folder_path+file_name, 'r', encoding='utf-8') as file:
            try:
                book = json.load(file)
                add_book(book, fieldnames)
            except:
                pass


if __name__ == '__main__':
    merge_books()