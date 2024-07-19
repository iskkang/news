from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

def fetch_news(keyword):
    url = f"https://news.google.com/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    
    news = []
    for article in articles:
        source = article.find('div', class_='vr1PYe').text if article.find('div', class_='vr1PYe') else 'No Source'
        title_tag = article.find('a', class_='JtKRv')
        title = title_tag.text if title_tag else 'No Title'
        link = 'https://news.google.com' + title_tag['href'][1:] if title_tag else 'No Link'
        thumbnail_tag = article.find('img', class_='Quavad')
        if thumbnail_tag:
            thumbnail = thumbnail_tag['src']
            if thumbnail.startswith('/api/attachments/'):
                thumbnail = 'https://news.google.com' + thumbnail
                thumbnail = thumbnail.replace('-w200-h112-p-df-rw', '-w400-h224-p-df-rw')
        else:
            thumbnail = 'No Image'
        date_tag = article.find('time', class_='hvbAAd')
        date = date_tag['datetime'] if date_tag else 'No Date'
        news.append({'source': source, 'title': title, 'link': link, 'thumbnail': thumbnail, 'date': date})
    
    return news

@app.route('/news', methods=['GET'])
def get_news():
    keyword = request.args.get('keyword', default='해상운임', type=str)
    news = fetch_news(keyword)
    df = pd.DataFrame(news)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date', ascending=False)
    df['date'] = df['date'].dt.strftime('%y-%m-%d')
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
