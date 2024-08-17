from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import base64

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessária para usar flash messages

# Nome do arquivo Excel
arquivo_excel = 'inventario_prateleira.xlsx'


# Função para gerar o próximo código disponível
def gerar_codigo():
    df = pd.read_excel(arquivo_excel)


    codigos = pd.to_numeric(df['Código'], errors='coerce').dropna().astype(int)

    if codigos.empty:
        return 1
    else:
        return codigos.max() + 1



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        caixa = request.form['caixa'].strip()
        item = request.form['item'].strip()

        if caixa and item:
            codigo = gerar_codigo()
            nova_linha = [caixa.lower(), item, codigo]
            df = pd.read_excel(arquivo_excel)
            df.loc[len(df)] = nova_linha
            df.to_excel(arquivo_excel, index=False)

            # Exibe uma mensagem de sucesso e retorna à mesma página
            flash(f'Item "{item}" adicionado à {caixa} com sucesso! Código: {codigo}')
            return render_template('adicionar.html')

        else:
            flash('Por favor, preencha todos os campos.')

    return render_template('adicionar.html')

# Listar itens por caixa
@app.route('/listar', methods=['GET', 'POST'])
def listar():
    df = pd.read_excel(arquivo_excel)
    df['Caixa'] = df['Caixa'].astype(str).str.strip().str.lower()

    if request.method == 'POST':
        caixa = request.form['caixa'].strip().lower()
        itens = df[df['Caixa'] == caixa].to_dict(orient='records')
        return render_template('listar.html', itens=itens, caixa=caixa)

    caixas_itens = df.groupby('Caixa').size().to_dict()
    return render_template('listar.html', caixas_itens=caixas_itens)


# Pesquisar itens por palavra-chave
@app.route('/pesquisar', methods=['GET', 'POST'])
def pesquisar():
    df = pd.read_excel(arquivo_excel)

    if request.method == 'POST':
        palavra_chave = request.form['palavra_chave'].strip().lower()
        resultado = df[df['Item'].str.contains(palavra_chave, case=False, na=False)]
        return render_template('pesquisar.html', resultado=resultado.to_dict(orient='records'))

    return render_template('pesquisar.html', resultado=[])


# Remover item por código
@app.route('/remover', methods=['GET', 'POST'])
def remover():
    df = pd.read_excel(arquivo_excel)

    if request.method == 'POST':
        codigo = request.form['codigo'].strip()

        if codigo.isdigit() and int(codigo) in df['Código'].values:
            df = df[df['Código'] != int(codigo)]
            df.to_excel(arquivo_excel, index=False)

            # Exibe uma mensagem de sucesso e retorna à mesma página
            flash(f'Item com código {codigo} foi removido com sucesso.')
            return render_template('remover.html')

        else:
            flash(f'Código {codigo} não encontrado. Por favor, verifique e tente novamente.')

    return render_template('remover.html')


# Função para exibir o dashboard de gráficos
@app.route('/dashboard')
def dashboard():
    df = pd.read_excel(arquivo_excel)

    # Contagem dos itens por caixa
    contagem_itens = df['Caixa'].value_counts().sort_index()

    # Criando o gráfico
    fig, ax = plt.subplots()
    contagem_itens.plot(kind='bar', ax=ax)
    ax.set_xlabel("Caixa")
    ax.set_ylabel("Número de Itens")
    ax.set_title("Quantidade de Itens por Caixa")

    # Converte o gráfico em uma imagem para exibir no navegador
    png_image = io.BytesIO()
    FigureCanvas(fig).print_png(png_image)
    png_image_b64_string = "data:image/png;base64,"
    png_image_b64_string += base64.b64encode(png_image.getvalue()).decode('utf8')

    return render_template('dashboard.html', image=png_image_b64_string)


# Quantidade de itens por caixa
@app.route('/quantidade')
def quantidade():
    df = pd.read_excel(arquivo_excel)

    contagem_itens = df['Caixa'].value_counts().sort_index()

    return render_template('quantidade.html', contagem_itens=contagem_itens.to_dict())


if __name__ == '__main__':
    app.run(debug=True)
