import re
import traceback
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
import requests
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

try:
    df_input = pd.read_csv("dados.csv")
except FileNotFoundError:
    df_input = pd.DataFrame(columns=['URL', 'Resumo', 'Conteudo'])

@app.route('/')
def index():
    carrega_csv()
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['user_message']
    results = search(df, user_message, n=1, pprint=False)
    response = getResponses(user_message, results.iloc[0])
    return jsonify({'bot_message': response})

@app.route('/extrair', methods=['POST'])
def extrair():
    url = request.form['url']
    resumo = request.form['resumo']
    conteudo = request.form['conteudo']

    texto = None
    if(conteudo):
        texto = conteudo
    else:
        texto = extrair_texto_do_body(url)
    
    if texto:
        atualizar_dataframe(url, texto, resumo)
        return jsonify({'status': 'sucesso', 'mensagem': 'Texto recuperado e salvo com sucesso no Dataset CSV.'})
    else:
        return jsonify({'status': 'falha', 'mensagem': 'Falha ao recuperar o texto da página.'})
    
@app.route('/atualizar', methods=['POST'])
def atualizar_embbeding():
    try:
        global df_input
        df_input["combined"] = (
            "Resumo: " + df_input.Resumo.str.strip() + "; Conteudo: "
            + df_input.Conteudo.str.strip() + "; URL: " + df_input.URL.str.strip()
        )
        print("combined gerado")

        df_input['embedding'] = df_input.combined.apply(lambda x: get_embedding(x, model='text-embedding-3-small'))
        print("embedding gerado")

        global df
        df = pd.concat([df, df_input], ignore_index=True)
        df.to_csv('embedded.csv', index=False)

        df_input = None
        return jsonify({'status': 'sucesso', 'mensagem': 'Embedded gerado com sucesso!'})
    except Exception as e:  # Captura a exceção
        traceback.print_exc()  # Imprime o rastreamento da exceção
        return jsonify({'status': 'falha', 'mensagem': 'Falha ao gerar embedded'})


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



def extrair_texto_do_body(url):
    resposta = requests.get(url)
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.content, 'html.parser')
        texto_do_body = soup.body.get_text()
        texto_do_body = texto_do_body.replace('\n', ' ')
        texto_do_body = texto_do_body.replace('.', '. ')
        
        return texto_do_body
    else:
        print("Falha ao recuperar a página:", resposta.status_code)
        return None

def atualizar_dataframe(url, texto, resumo):
    global df_input

    new_row = {'URL': url, 'Resumo': resumo, 'Conteudo': texto}
    df_input = pd.concat([df_input, pd.DataFrame([new_row])], ignore_index=True)
    df_input.to_csv('dados.csv', index=False)


if __name__ == '__main__':
    app.run(debug=True)
