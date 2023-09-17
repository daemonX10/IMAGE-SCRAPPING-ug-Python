import os
import logging
import requests
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from urllib.parse import quote
import pymongo

logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            # Query to search for images
            query = quote(request.form['content'])

            # Directory to store downloaded images
            save_dir = "images/"

            # Create the directory if it does not exist
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # Fake user agent to avoid getting blocked by Google
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            response = requests.get(f"https://www.google.com/search?q={query}&tbm=isch", headers=headers)

            soup = BeautifulSoup(response.text, "html.parser")

            image_tags = soup.find_all('img')

            img_data = []
            for index, img_tag in enumerate(image_tags[1:]):  # Skip the first image (Google logo, not relevant)
                image_url = img_tag['src']
                image_data = requests.get(image_url).content
                my_dict = {"Index": index, "Image": image_data}
                img_data.append(my_dict)
                with open(os.path.join(save_dir, f"{query}_{index}.jpg"), "wb") as f:
                    f.write(image_data)

            # MongoDB connection
            client = pymongo.MongoClient("mongodb+srv://legend:yadav152530@mongo-practice-js.cfemuts.mongodb.net/")
            db = client['image_scrap']
            review_col = db['image_scrap_data']
            review_col.insert_many(img_data)

            return "Images loaded successfully"

        except requests.RequestException as e:
            logging.info(f"Request Exception: {str(e)}")
            return 'Something went wrong with the request to Google Images.'

        except Exception as e:
            logging.info(f"Exception: {str(e)}")
            return 'Something went wrong.'

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
