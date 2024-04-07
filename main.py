from flask import Flask, render_template, request, jsonify
from scipy.spatial.distance import cosine
from openai import OpenAI
import os
import pandas as pd
import numpy as np
import ast
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

app = Flask(__name__)
df = None

@app.route('/')
def index():
    carrega_csv()
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['user_message']
    results = search(df, user_message, n=1, pprint=False)
    response = getResponses(user_message, results.iloc[0])
    return jsonify({'bot_message': response})

def carrega_csv():
    global df
    df = pd.read_csv('embedded.csv')
    df['embedding'] = df.embedding.apply(eval).apply(np.array)
    print("CSV carregado")

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def search(df, product_description, n=3, pprint=True):
    if df is None:
        carrega_csv()

    embedding = get_embedding(product_description, model="text-embedding-3-small")
    df["similarity"] = df["embedding"].apply(lambda x: cosine(embedding, x))

    results = (
        df.sort_values("similarity", ascending=True)
        .head(n)
        .combined.str.replace("Resumo: ", "")
        .str.replace("; Conteudo:", ": ")
    )
    if pprint:
        for r in results:
            print(r[:1000])
            print()
    return results

def getResponses(pergunta, _results):
    response = client.chat.completions.create(
        messages=[
            {'role': 'system', 'content': pergunta},
            {'role': 'user', 'content': _results},
        ],
        model='gpt-3.5-turbo',
        temperature=0,
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    app.run(debug=True)
