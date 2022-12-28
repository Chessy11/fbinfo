from facebook_scraper import get_posts
import json
#import flask
from flask import Flask, render_template, request, redirect, url_for
import tempfile
import csv
#import send_file
from flask import send_file
from flask import make_response
from dotenv import load_dotenv
import facebook_scraper
#import generate_csv_data
import os
import requests

from http import cookiejar

file = "/home/OffPower/Work/fblikescrper/facebook.com_cookies.txt"
cookie = cookiejar.MozillaCookieJar(file)
cookie.load(file)
cookies = requests.utils.dict_from_cookiejar(cookie)
facebook_scraper.set_cookies(cookies)


app = Flask(__name__)

load_dotenv()

#  scrape posts reactions and reactors from a page
#set cookies to your browser cookies
# from util import Config

#get string username and password from .env file

# print username path
# for post in get_posts(credentials=(username, password), post_urls=["https://www.facebook.com/photo/?fbid=547120087428336&set=a.308441684629512"],    
#                       options={ "reactors": 3000, 
#                       "reactions": 3000, "timeout": 30, "progress": True,}):
#       json_data = json.dumps(post, indent=4, sort_keys=True, default=str)
#       #save to file and read non english values 
#       with open('post.json', 'a', encoding='utf-8') as f:
#             f.write(json_data)
            
            
import pandas as pd
@app.route('/')
def index():
      return render_template('index.html')

            
@app.route('/download_csv', methods=['POST'])
def download_csv():
    post_url = request.form['post_url']
    for post in get_posts(post_urls=[post_url],    
                        options={"comments": True, "reactors": True, 
                        "reactions": True, "sharers": True, "timeout": 30, "shares": True, }):
        json_data = json.dumps(post, indent=4, sort_keys=True, default=str)
        # save json to file
        with open('vs.json', 'w', encoding='utf-8') as f:
            f.write(json_data)
        # read json file
        with open('vs.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        reactors = data['reactors']
        print(f'Reactors: {reactors}')

    with tempfile.NamedTemporaryFile(mode='w', delete=True, suffix='.csv') as tmp:
        fieldnames = ['name', 'link', 'type']
        writer = csv.DictWriter(tmp, fieldnames=fieldnames)
        writer.writeheader()
        for reactor in reactors:
            writer.writerow({'name': reactor['name'], 'link': reactor['link'], 'type': reactor['type']})
        tmp.flush()
        response = make_response(send_file(tmp.name, as_attachment=True))
        response.headers['Content-Disposition'] = 'attachment; filename=type.csv'
        return response           


@app.route('/download_by_type', methods=['GET', 'POST'])
def download_reactions_by_type():
    if request.method == 'POST':
        # Get the post URL and selected reaction type from the form
        post_url = request.form['post_url']
        reaction_type = request.form['reaction_type']

        # Retrieve the post data
        for post in get_posts(credentials=(username, password), post_urls=[post_url],    
                        options={"comments": True, "reactors": True, 
                        "reactions": True, "sharers": True, "timeout": 30, "shares": True, }):
            json_data = json.dumps(post, indent=4, sort_keys=True, default=str)
            # save json to file
            with open('vs.json', 'w', encoding='utf-8') as f:
                f.write(json_data)
            # read json file
            with open('vs.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            reactors = data['reactors']
            print(f'Reactors: {reactors}')
      # Filter the reactors by the selected reaction type
            reactors = [reactor for reactor in reactors if reactor['type'] == reaction_type]
            print(f'Reactors_Type: {reactors}')
            # Generate the CSV data
            csv_data = generate_csv_data(reactors)
            # Create a temporary file to store the CSV data
            tmp = tempfile.NamedTemporaryFile(mode='w', delete=True, suffix='.csv')
            tmp.write(csv_data)
            tmp.flush()
            # Return the CSV file as an attachment
            response = make_response(send_file(tmp.name, as_attachment=True))
            response.headers['Content-Disposition'] = 'attachment; filename=reactors_type.csv'
            return response
      

    else:
        # Render the HTML form template
        return render_template('reactions_by_type.html')
  
  
def generate_csv_data(reactors):
    # Generate the CSV data for the reactors
    csv_data = 'name,link,type\n'
    for reactor in reactors:
        csv_data += f'{reactor["name"]},{reactor["link"]},{reactor["type"]}\n'
    return csv_data


@app.route('/about', methods=['GET'])
def about():
      return render_template('about.html')


if __name__ == '__main__':
      app.run()