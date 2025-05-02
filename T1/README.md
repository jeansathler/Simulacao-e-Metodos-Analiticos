# Simulação e Métodos Analíticos

Este projeto implementa um simulador para análise de sistemas de filas, permitindo a definição de topologias personalizadas via arquivos YAML. O simulador utiliza métodos analíticos para calcular métricas de desempenho e simular o comportamento de sistemas de filas.

---

## **Índice**
- [Descrição](#descrição)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Execução](#execução)
- [Resultados](#resultados)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## **Descrição**
O simulador permite:
- Configuração de sistemas de filas com múltiplas topologias.
- Definição de parâmetros como taxas de chegada, tempos de serviço, número de servidores e capacidade das filas.
- Simulação de redes de filas com probabilidades de transição entre filas.
- Geração de métricas como distribuição de estados, perdas e tempos médios.

---

## **Requisitos**
- Python 3.8 ou superior

---

## **Instalação**
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/sim-met-analiticos.git

2. Vá até o diretório do projeto:
    ```bash
    cd sim-met-analiticos/T1

## **Configuração**
A configuração da simulação é feita através de um arquivo YAML (config.yaml). Este arquivo define:

- **Filas**: Parâmetros como número de servidores, capacidade, tempos de chegada e serviço.
- **Rede**: Conexões entre filas e probabilidades de transição.
- **Iterações**: Número de iterações da simulação.

Exemplo de Configuração
```yaml
arrivals:
    Q1: 2.0

queues:
    Q1:
        servers: 1
        minArrival: 2.0
        maxArrival: 4.0
        minService: 1.0
        maxService: 2.0
    Q2:
        servers: 2
        capacity: 5
        minService: 4.0
        maxService: 8.0

network:
- source: Q1
    target: Q2
    probability: 0.8
- source: Q2
    target: Q1
    probability: 0.3

iterations:
    value: 100000
```

## **Execução**
1. Certifique-se de que o arquivo `config.yaml` está configurado corretamente.

2. Execute o simulador:
    ```bash
    python simulador.py --config config.yaml
    ```

3. O simulador processará a configuração e gerará os resultados no terminal ou em arquivos de saída, dependendo da configuração.

## **Resultados**

Os resultados da simulação são salvos no arquivo `results.txt`. Este arquivo inclui:

- Taxas de chegada e serviço.
- Distribuição de estados das filas.
- Número de perdas.
- Probabilidades de transição.

### Exemplo de Saída
```txt
Name: Q1
Arrival: 2.0
Servers: 1
Capacity: 0
Min Arrival: 2.0
Max Arrival: 4.0
Min Service: 1.0
Max Service: 2.0
Loss: 0
Distribution Times:
  0: 11509.659798776498
  1: 17517.704830654664
Distribution Percent:
  0: 34.76
  1: 52.9

Total Time: 29027.364629431162
```