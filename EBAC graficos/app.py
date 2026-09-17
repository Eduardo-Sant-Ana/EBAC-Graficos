import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# ------------------------------------------------------------------
# 1. Carregamento e preparação dos dados
# ------------------------------------------------------------------
def limpar_nome(nome):
    nome = nome.lower()
    for ac, lt in [('ç','c'), ('ã','a'), ('õ','o'), ('á','a'), ('é','e'),
                   ('í','i'), ('ó','o'), ('ú','u'), ('ê','e'), ('ô','o')]:
        nome = nome.replace(ac, lt)
    nome = nome.replace(' ', '_').replace('-', '_')
    while '__' in nome:
        nome = nome.replace('__', '_')
    return nome

def achar(colunas, substr):
    cand = [c for c in colunas if substr in c]
    return min(cand, key=len) if cand else None

CAMINHOS = ['ecommerce_estatistica.csv', 'ecommerce_estatistica_1_.csv']

df = None
for caminho in CAMINHOS:
    try:
        df = pd.read_csv(caminho, encoding='utf-8')
        print(f'CSV carregado: {caminho}')
        break
    except FileNotFoundError:
        continue

if df is None:
    raise FileNotFoundError('Arquivo CSV não encontrado. Coloque o arquivo na mesma pasta do app.py.')

df.columns = [limpar_nome(c) for c in df.columns]

col_nota       = achar(df.columns, 'nota') or 'nota'
col_avaliacoes = achar(df.columns, 'avaliacoes') or 'n_avaliacoes'
col_desconto   = achar(df.columns, 'desconto') or 'desconto'
col_preco      = achar(df.columns, 'preco') or 'preco'
col_marca      = achar(df.columns, 'marca') or 'marca'
col_material   = achar(df.columns, 'material') or 'material'
col_genero     = achar(df.columns, 'genero') or 'genero'
col_temporada  = achar(df.columns, 'temporada') or 'temporada'
col_qtd_cod    = achar(df.columns, 'qtd_vendidos_cod')

# Só colunas que realmente existem e são numéricas
def so_numerica(col):
    return col in df.columns and pd.api.types.is_numeric_dtype(df[col])

colunas_numericas = {}
for nome, col in [('Preço', col_preco), ('Nota', col_nota),
                  ('Número de Avaliações', col_avaliacoes),
                  ('Desconto (%)', col_desconto),
                  ('Qtd. Vendidos', col_qtd_cod)]:
    if col is not None and so_numerica(col):
        colunas_numericas[nome] = col

colunas_categoricas = {}
for nome, col in [('Temporada', col_temporada), ('Material', col_material),
                  ('Gênero', col_genero)]:
    if col is not None and col in df.columns:
        colunas_categoricas[nome] = col

# Primeira coluna numérica disponível como padrão (evita None no dropdown)
primeira_num = next(iter(colunas_numericas.values()))
primeira_cat = next(iter(colunas_categoricas.values()))

def nome_de(mapa, valor, fallback='—'):
    for k, v in mapa.items():
        if v == valor:
            return k
    return fallback

# ------------------------------------------------------------------
# 2. Funções que constroem cada gráfico
# ------------------------------------------------------------------
def fazer_histograma(d, var, nome_var):
    fig = px.histogram(d, x=var, nbins=30,
                       title=f'Histograma: {nome_var}',
                       color_discrete_sequence=['#1f77b4'],
                       template='plotly_white')
    fig.update_layout(xaxis_title=nome_var, yaxis_title='Frequência',
                      title_x=0.5, margin=dict(t=60))
    return fig

def fazer_densidade(d):
    fig = px.histogram(d, x=col_nota, nbins=30, histnorm='probability density',
                       title='Densidade das Notas dos Produtos',
                       color_discrete_sequence=['#2ca02c'],
                       template='plotly_white')
    fig.update_layout(xaxis_title='Nota', yaxis_title='Densidade',
                      title_x=0.5, margin=dict(t=60))
    fig.update_traces(opacity=0.85)
    return fig

def fazer_dispersao(d, x_var, y_var, nome_x, nome_y):
    fig = px.scatter(d, x=x_var, y=y_var, color=col_temporada,
                     title=f'Relação entre {nome_x} e {nome_y}',
                     labels={x_var: nome_x, y_var: nome_y,
                             col_temporada: 'Temporada'},
                     opacity=0.75, template='plotly_white')
    fig.update_layout(xaxis_title=nome_x, yaxis_title=nome_y,
                      title_x=0.5, margin=dict(t=60))
    return fig

def fazer_regressao(d):
    # Regressão manual com numpy: não depende de statsmodels
    df_ok = d[[col_preco, col_avaliacoes]].replace([np.inf, -np.inf], np.nan).dropna()
    fig = px.scatter(df_ok, x=col_preco, y=col_avaliacoes, opacity=0.7,
                     title='Regressão Linear: Preço x Número de Avaliações',
                     labels={col_preco: 'Preço (R$)',
                             col_avaliacoes: 'Número de Avaliações'},
                     template='plotly_white')
    if len(df_ok) > 1:
        coef = np.polyfit(df_ok[col_preco], df_ok[col_avaliacoes], 1)
        x_linha = np.linspace(df_ok[col_preco].min(), df_ok[col_preco].max(), 100)
        y_linha = np.polyval(coef, x_linha)
        fig.add_trace(go.Scatter(x=x_linha, y=y_linha, mode='lines',
                                 name='Regressão',
                                 line=dict(color='red', width=2)))
    fig.update_layout(xaxis_title='Preço (R$)', yaxis_title='Número de Avaliações',
                      title_x=0.5, margin=dict(t=60))
    return fig

def fazer_mapa_calor(d):
    cols = [c for c in colunas_numericas.values() if c in d.columns]
    if len(cols) < 2:
        return px.scatter(title='Sem dados suficientes para correlação',
                          template='plotly_white')
    corr = d[cols].corr()
    nomes = {c: k for k, c in colunas_numericas.items() if c in corr.columns}
    corr = corr.rename(index=nomes, columns=nomes)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r',
                    zmin=-1, zmax=1, title='Mapa de Calor das Correlações',
                    labels=dict(color='Correlação'), template='plotly_white')
    fig.update_layout(title_x=0.5, margin=dict(t=60), height=480)
    return fig

def fazer_barras(d):
    if col_marca not in d.columns:
        return px.scatter(title='Coluna de marca ausente', template='plotly_white')
    contagem = d[col_marca].value_counts().head(10).reset_index()
    contagem.columns = ['marca', 'quantidade']
    fig = px.bar(contagem, x='quantidade', y='marca', orientation='h',
                 title='Top 10 Marcas por Número de Produtos',
                 labels={'quantidade': 'Quantidade de Produtos', 'marca': 'Marca'},
                 color='quantidade', color_continuous_scale='Viridis',
                 template='plotly_white')
    fig.update_layout(xaxis_title='Quantidade de Produtos', yaxis_title='Marca',
                      title_x=0.5, margin=dict(t=60))
    return fig

def fazer_pizza(d, col_pizza, nome_coluna):
    contagem = d[col_pizza].value_counts()
    principais = contagem.head(5)
    outras = contagem.iloc[5:].sum()
    if outras > 0:
        principais['Outras'] = outras
    fig = px.pie(values=principais.values, names=principais.index,
                 title=f'Distribuição de Produtos por {nome_coluna}',
                 template='plotly_white', hole=0.35)
    fig.update_layout(title_x=0.5, margin=dict(t=60))
    return fig

def card_kpi(titulo, valor, cor):
    return dbc.Col(dbc.Card(
        dbc.CardBody([
            html.H6(titulo, className='text-muted'),
            html.H3(valor, style={'color': cor}),
        ]), className='shadow-sm text-center'), md=3)

# ------------------------------------------------------------------
# 3. Aplicação Dash
# ------------------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                title='Análise E-commerce')
server = app.server

options_temporada = ([{'label': 'Todas', 'value': 'Todas'}] +
                     [{'label': t, 'value': t}
                      for t in df[col_temporada].dropna().unique()])

# Figuras iniciais: gráficos aparecem mesmo antes/independente do callback
fig_inicial_hist = fazer_histograma(df, primeira_num, nome_de(colunas_numericas, primeira_num))
fig_inicial_dens = fazer_densidade(df)
fig_inicial_disp = fazer_dispersao(df, primeira_num, col_avaliacoes,
                                   nome_de(colunas_numericas, primeira_num),
                                   'Número de Avaliações')
fig_inicial_reg  = fazer_regressao(df)
fig_inicial_corr = fazer_mapa_calor(df)
fig_inicial_barr = fazer_barras(df)
fig_inicial_pizz = fazer_pizza(df, primeira_cat, nome_de(colunas_categoricas, primeira_cat))

app.layout = dbc.Container([
    html.H1('Análise de Dados: E-commerce', className='text-center my-4'),
    html.P('Aplicação Dash com os gráficos do módulo de análise estatística.',
           className='text-center text-muted mb-4'),

    dbc.Row([
        dbc.Col([html.Label('Temporada'),
                 dcc.Dropdown(id='filtro-temporada', options=options_temporada,
                              value='Todas', clearable=False)], md=3),
        dbc.Col([html.Label('Variável do histograma'),
                 dcc.Dropdown(id='var-histograma',
                              options=[{'label': k, 'value': v}
                                       for k, v in colunas_numericas.items()],
                              value=primeira_num, clearable=False)], md=3),
        dbc.Col([html.Label('Dispersão: eixo X'),
                 dcc.Dropdown(id='scatter-x',
                              options=[{'label': k, 'value': v}
                                       for k, v in colunas_numericas.items()],
                              value=primeira_num, clearable=False)], md=3),
        dbc.Col([html.Label('Dispersão: eixo Y'),
                 dcc.Dropdown(id='scatter-y',
                              options=[{'label': k, 'value': v}
                                       for k, v in colunas_numericas.items()],
                              value=col_avaliacoes, clearable=False)], md=3),
    ], className='mb-2'),

    dbc.Row([
        dbc.Col([html.Label('Coluna do gráfico de pizza'),
                 dcc.Dropdown(id='col-pizza',
                              options=[{'label': k, 'value': v}
                                       for k, v in colunas_categoricas.items()],
                              value=primeira_cat, clearable=False)], md=4),
    ], className='mb-4'),

    html.Div(id='kpis', className='mb-4'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico-histograma', figure=fig_inicial_hist), md=6),
        dbc.Col(dcc.Graph(id='grafico-densidade', figure=fig_inicial_dens), md=6),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico-dispersao', figure=fig_inicial_disp), md=6),
        dbc.Col(dcc.Graph(id='grafico-regressao', figure=fig_inicial_reg), md=6),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico-mapa-calor', figure=fig_inicial_corr), md=6),
        dbc.Col(dcc.Graph(id='grafico-barras', figure=fig_inicial_barr), md=6),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico-pizza', figure=fig_inicial_pizz),
                md=6, className='mx-auto'),
    ], className='mb-4'),

    html.Footer('Projeto de Conclusão de Módulo: Análise de Dados de E-commerce',
                className='text-center text-muted my-4'),
], fluid=True)

# ------------------------------------------------------------------
# 4. Callback: atualiza KPIs e todos os gráficos
# ------------------------------------------------------------------
@app.callback(
    Output('kpis', 'children'),
    Output('grafico-histograma', 'figure'),
    Output('grafico-densidade', 'figure'),
    Output('grafico-dispersao', 'figure'),
    Output('grafico-regressao', 'figure'),
    Output('grafico-mapa-calor', 'figure'),
    Output('grafico-barras', 'figure'),
    Output('grafico-pizza', 'figure'),
    Input('filtro-temporada', 'value'),
    Input('var-histograma', 'value'),
    Input('scatter-x', 'value'),
    Input('scatter-y', 'value'),
    Input('col-pizza', 'value'),
)
def atualizar(temporada, var_hist, x_var, y_var, col_pizza):
    d = df.copy()
    if temporada != 'Todas':
        d = d[d[col_temporada] == temporada]

    nome_hist = nome_de(colunas_numericas, var_hist)
    nome_x = nome_de(colunas_numericas, x_var)
    nome_y = nome_de(colunas_numericas, y_var)
    nome_pizza = nome_de(colunas_categoricas, col_pizza)

    kpis = dbc.Row([
        card_kpi('Produtos', f'{len(d):,}'.replace(',', '.'), '#1f77b4'),
        card_kpi('Preço médio', f'R$ {d[col_preco].mean():.2f}'.replace('.', ','), '#2ca02c'),
        card_kpi('Nota média', f'{d[col_nota].mean():.2f}'.replace('.', ','), '#ff7f0e'),
        card_kpi('Total de avaliações', f'{d[col_avaliacoes].sum():,.0f}'.replace(',', '.'), '#d62728'),
    ])

    return (kpis,
            fazer_histograma(d, var_hist, nome_hist),
            fazer_densidade(d),
            fazer_dispersao(d, x_var, y_var, nome_x, nome_y),
            fazer_regressao(d),
            fazer_mapa_calor(d),
            fazer_barras(d),
            fazer_pizza(d, col_pizza, nome_pizza))

if __name__ == '__main__':
    app.run(debug=True)