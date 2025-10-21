import yfinance as yf
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify

# --- Inicialização da Aplicação Flask ---
app = Flask(__name__)


# --- Funções de Cálculo (Baseadas no seu notebook 'calculos.ipynb') ---

def calcular_media(series: pd.Series) -> float:
    """Calcula a média de uma série de preços."""
    return round(series.mean(), 2)

def calcular_variacao_percentual(series: pd.Series) -> float:
    """Calcula a variação percentual entre o primeiro e o último dia."""
    if len(series) < 2:
        return 0.0
    
    # .iloc[0] é o preço mais antigo, .iloc[-1] é o mais recente
    variacao = ((series.iloc[-1] - series.iloc[0]) / series.iloc[0]) * 100
    return round(variacao, 2)

def calcular_volatilidade(series: pd.Series) -> float:
    """
    Calcula a volatilidade como o desvio padrão dos preços.
    Nota: Em finanças, 'volatilidade' geralmente se refere ao desvio padrão
    dos *retornos* (ex: series.pct_change().std()), mas estou mantendo
    a lógica do seu notebook (desvio padrão dos *preços*).
    """
    return round(series.std(), 2)


# --- Endpoint da API ---

@app.route('/calcular-risco', methods=['GET'])
def api_calcular_risco():
    """
    Endpoint principal que calcula as métricas de risco para um ticker.
    Parâmetros da URL (query params):
    - ticker (obrigatório): O símbolo da ação (ex: 'AAPL', 'MSFT').
    - periodo (opcional): O período de dados (ex: '1mo', '6mo', '1y'). Default: '1y'.
    - intervalo (opcional): O intervalo dos dados (ex: '1d', '1wk'). Default: '1d'.
    """
    
    # 1. Obter parâmetros da URL
    ticker_name = request.args.get('ticker')
    periodo = request.args.get('periodo', '1y')      # Default de 1 ano
    intervalo = request.args.get('intervalo', '1d')  # Default de 1 dia

    # 2. Validação de entrada
    if not ticker_name:
        # Retorna um erro 400 (Bad Request) se o ticker não for fornecido
        return jsonify({"erro": "O parâmetro 'ticker' é obrigatório."}), 400

    try:
        # 3. Buscar dados com yfinance (igual no 'relatorio_riskvision.ipynb' do vampiro)
        ticker_data = yf.Ticker(ticker_name)
        hist = ticker_data.history(period=periodo, interval=intervalo)

        if hist.empty:
            # Retorna um erro 404 (Not Found) se o ticker não existir
            return jsonify({"erro": f"Não foram encontrados dados para o ticker '{ticker_name}' no período '{periodo}'."}), 404

        # 4. Calcular métricas (como no 'calculos.ipynb')
        colunas_interesse = ['Open', 'High', 'Low', 'Close']
        resultados = {
            "ticker": ticker_name,
            "periodo_solicitado": periodo,
            "intervalo_solicitado": intervalo,
            "periodo_real": {
                "data_inicio": hist.index[0].strftime('%Y-%m-%d'),
                "data_fim": hist.index[-1].strftime('%Y-%m-%d')
            },
            "metricas": {}
        }

        # Itera sobre 'Open', 'High', 'Low', 'Close' e calcula tudo
        for col in colunas_interesse:
            if col in hist:
                series = hist[col]
                resultados["metricas"][col.lower()] = {
                    "media": calcular_media(series),
                    "variacao_percentual": calcular_variacao_percentual(series),
                    "volatilidade_preco (std)": calcular_volatilidade(series)
                }
        
        # 5. Retornar o JSON com os resultados
        return jsonify(resultados)

    except Exception as e:
        # Retorna um erro 500 (Internal Server Error) se algo inesperado acontecer
        return jsonify({"erro": f"Erro interno ao processar a solicitação: {str(e)}"}), 500


# --- Bloco para Executar o Servidor ---
if __name__ == '__main__':
    # Inicia o servidor Flask
    # host='0.0.0.0' faz o servidor ser acessível por outros
    # computadores na mesma rede (necessário para seu backend)
    print("Servidor de Risco (RiskVision API) iniciando em http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)