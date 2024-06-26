from flask import Flask, render_template, request, jsonify
import requests
from openai import OpenAI
client = OpenAI(api_key= "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")
# import prompt as pr
import json
from bs4 import BeautifulSoup
import boto3

AWS_S3_CREDS = {
    "aws_access_key_id":"",
    "aws_secret_access_key":""
}

db = boto3.client('dynamodb', region_name = 'us-east-2', **AWS_S3_CREDS)
app = Flask(__name__)
article_content = ''
article_summary = ''
table_name = "news-summarisation-data"

# URL of your Flask server's endpoint (replace with your actual URL)
# url = "http://127.0.0.1:8080/predict"
# url = "http://backend-provider:8080/predict"
# url = "http://18.189.32.120:80/predict"
lambda_url = 'https://sanchl6xitkkgxkmr4nxcbn3nm0flslf.lambda-url.us-east-2.on.aws/'
# Function to fetch news articles from NewsAPI
def fetch_news_articles(topic):
    api_key = '0e2ef7c699bc4a18a5a3b58714579809'  # Replace with your actual NewsAPI key
    base_url = 'https://newsapi.org/v2/everything'
    params = {
        'q': topic,
        'apiKey': api_key,
        'language': 'en',
        'pageSize': 10,
        'sortBy': 'relevancy'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()['articles']
    else:
        print('Failed to fetch articles:', response.status_code)
        return []
    
# Function to scrape the content of the article
def scrape_article_content(url):
    response = requests.get(url)
    if response.status_code != 200:
        return "Unable to fetch the article content."
    
    soup = BeautifulSoup(response.content, 'html.parser')
    content = ' '.join([p.text for p in soup.find_all('p')])
    return content

# Route for handling the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling the form submission and showing results
@app.route('/submit', methods=['POST'])
def submit():
    topic = request.form.get('input_text')
    articles = fetch_news_articles(topic)
    return render_template('result.html', articles=articles)

# Route for handling the summary generation
@app.route('/get_summary', methods=['POST'])
def get_summary():
    data = request.json
    article_url = data['url']
    # print(article_url)
    content = scrape_article_content(article_url)
    # Pass content to gpt and fetch summary
    summary = get_completion(content)
    print("heyy,", summary)
    return jsonify({'summary': summary})

def get_completion(news_content, model="gpt-3.5-turbo"):
    global article_content, article_summary
    # print(news_content)
    article_content = news_content
    data ={'data':news_content}
    # Convert the data to a JSON string
    data_json = json.dumps(data)

    # Set the content type to application/json
    headers = {'Content-Type': 'application/json'}

    # Send the POST request to the server
    response = requests.post(lambda_url, data=data_json, headers=headers)
    print(response.text)
    print(response.status_code)
    print(type(response))
    # Check if the request was successful
    if response.status_code == 200:
        # Print the response from the server
        # print("heyyyy")
        # print()
        print("Response from server:", response.text)
    else:
        print("Failed to get response. Status code:", response.status_code)
    # print(response.choices[0].message.content)
    article_summary = response.text
    return article_summary


# Save response function
@app.route('/save_response', methods=['POST'])
def save_response():
    global article_content, article_summary

    item = {
    'article-input': {'S': str(article_content[:1000])},
    'summ-result': {'S': str(article_summary)},
    }
    try:
        response = db.describe_table(TableName=table_name)
        if response['Table']['TableStatus'] == 'ACTIVE':
            print(f"Table '{table_name}' exists and is active.")

        # Put summary in Table
            try:
                response2 = db.put_item(TableName='news-summarisation-data', Item=item)
            except Exception as e:
                print(f"Error occurred while putting response in the table': {e}")
        else:
            print(f"Table '{table_name}' exists but is not active (status: {response['Table']['TableStatus']}).")
    except db.exceptions.ResourceNotFoundException:
        print(f"Table '{table_name}' does not exist.")

    return jsonify({'message': 'Response saved successfully'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8081')
