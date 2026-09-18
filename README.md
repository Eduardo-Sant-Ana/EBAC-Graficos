https://github.com/Eduardo-Sant-Ana/EBAC-Graficos.git
# Análise de Dados de E-commerce — Aplicação Dash

Aplicação web interativa construída com **Dash (Python)** para visualizar as
análises estatísticas de um dataset de e-commerce. O usuário final não precisa
interagir com código: basta abrir o endereço gerado pela aplicação.

## Funcionalidades

- **4 KPIs**: total de produtos, preço médio, nota média e total de avaliações
- **7 gráficos interativos**:
  - Histograma (variável selecionável)
  - Densidade das notas
  - Dispersão (eixos X e Y selecionáveis)
  - Regressão linear (Preço x Avaliações)
  - Mapa de calor das correlações
  - Top 10 marcas (barras)
  - Distribuição por categoria (pizza)
- **Filtro por temporada** aplicado a todos os gráficos

## Estrutura do projeto
```
├── app.py                    # Código da aplicação Dash
├── ecommerce_estatistica.csv # Base de dados
├── requirements.txt          # Dependências do projeto
├── Procfile                  # Configuração do servidor
└── README.md                 # Documentação
```

## Pré-requisitos

- Python 3.9 ou superior instalado
- `pip` disponível no terminal

Para verificar se o Python está instalado:
```bash
python --version
```

Se o comando não for reconhecido no Windows, use:
```bash
py --version
```

## Como executar

1. Clone o repositório:
```bash
git clone https://github.com/Eduardo-Sant-Ana/EBAC-Graficos.git
```

2. Crie e ative um ambiente virtual (recomendado):

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python app.py
```

5. Abra no navegador:
```
http://127.0.0.1:8050
```

## Como usar

- Use o seletor **Temporada** para filtrar todos os gráficos de uma vez
- Escolha a variável do histograma e os eixos da dispersão nos menus
- Selecione a coluna do gráfico de pizza
- Os KPIs e gráficos atualizam automaticamente a cada mudança

## Tecnologias

- Python
- Dash
- Dash Bootstrap Components
- Plotly
- Pandas
- NumPy
- Gunicorn
