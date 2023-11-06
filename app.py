from flask import Flask, render_template, request
import requests, re
from bs4 import BeautifulSoup

app = Flask(__name__)


def get_webpage_keywords(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')

        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords:
            keywords = meta_keywords.get("content")
            return [word.strip() for word in keywords.split(',')]

        h1_tags = soup.find_all("h1")
        h1_keywords = [tag.text.strip() for tag in h1_tags]

        return h1_keywords
    else:
        print("Failed to fetch the webpage. Status code:", response.status_code)
        return None


def search_books_google(keywords):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': keywords,
        'maxResults': 1
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()

        if 'items' in data:
            books = []
            for item in data['items']:
                book_info = item['volumeInfo']
                book = {
                    'title': book_info.get('title', 'N/A'),
                    'authors': book_info.get('authors', ['N/A']),
                    'publisher': book_info.get('publisher', 'N/A'),
                    'publishedDate': book_info.get('publishedDate', 'N/A'),
                    'description': book_info.get('description', 'N/A'),
                    'categories': book_info.get('categories', ['N/A']),
                    'language': book_info.get('language', 'N/A'),
                    'image_link': book_info['imageLinks']['thumbnail'] if 'imageLinks' in book_info else 'N/A'
                }
                books.append(book)

            return books
        else:
            print("No books found for the given keywords.")
            return None
    else:
        print("Failed to fetch data from Google Books API. Status code:", response.status_code)
        return None


def is_youtube_url(url):
    pattern = r"^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+"  # URL YouTube
    return re.match(pattern, url) is not None


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/", methods=["GET", "POST"])
def home():
    books = []
    if request.method == "POST":
        url = request.form.get("url")
        if is_youtube_url(url):
            if url:
                keywords = get_webpage_keywords(url)
                if keywords:
                    for word in keywords:
                        result = search_books_google(word)
                        if result:
                            books.extend(result)
                return render_template("index.html", headlines=books)
            else:
                return render_template("index.html", headlines=[])
    return render_template("index.html", headlines=[])


if __name__ == "__main__":
    app.run()
