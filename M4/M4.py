import random

# Parâmetros do Método Congruente Linear
a = 1664525
c = 1013904223
M = 2**32
previous = random.randint(0, M-1)  # Seed inicial aleatória

def NextRandom():
    global previous
    previous = (a * previous + c) % M
    return previous / M

# Parâmetros da simulação
count = 100000
K = 5  # Capacidade máxima da fila

def simular_fila(servidores):
    global TempoGlobal  # Correção do erro
    TempoGlobal = 2.0  # Reinicia o tempo global para cada simulação
    fila = 0
    servidores_ocupados = 0  # Quantos servidores estão ocupados
    tempos = [0] * (K + 1)
    perdas = 0
    eventos = count  # Número total de eventos

    def CHEGADA():
        global TempoGlobal  # Correção do erro
        nonlocal fila, perdas  # Remove `TempoGlobal` do nonlocal
        if fila < K:
            fila += 1
        else:
            perdas += 1
        TempoGlobal += 2 + NextRandom() * 3  # Chegadas entre 2 e 5

    def SAIDA():
        global TempoGlobal  # Correção do erro
        nonlocal fila, servidores_ocupados
        if fila > 0 and servidores_ocupados < servidores:
            fila -= 1
            servidores_ocupados += 1  # Marca um servidor como ocupado
            TempoGlobal += 3 + NextRandom() * 2  # Atendimentos entre 3 e 5
        if servidores_ocupados > 0:
            servidores_ocupados -= 1  # Libera um servidor após atendimento

    def NextEvent():
        return "chegada" if NextRandom() < 0.5 else "saida"

    # Loop principal da simulação
    while eventos > 0:
        evento = NextEvent()
        if evento == "chegada":
            CHEGADA()
        elif evento == "saida":
            SAIDA()
        tempos[fila] += 1
        eventos -= 1

    # Cálculo e exibição dos resultados
    print(f"\n=== Resultados para G/G/{servidores}/5 ===")
    print("Distribuição de probabilidades dos estados da fila:")
    for i in range(K + 1):
        print(f"{i}: {tempos[i]} ({(tempos[i] / TempoGlobal) * 100:.2f}%)")

    print(f"Número de perdas de clientes: {perdas}")
    print(f"Tempo global da simulação: {TempoGlobal:.2f}")

# Executa as duas simulações
simular_fila(1)  # Simula G/G/1/5
simular_fila(2)  # Simula G/G/2/5
