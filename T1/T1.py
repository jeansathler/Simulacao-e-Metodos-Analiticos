# simulador.py - estrutura inicial do simulador de eventos discretos

import yaml
import heapq
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ===================== CLASSES ===================== #

@dataclass
class Cliente:
    id: int
    tempo_chegada: float
    tempo_saida: Optional[float] = None


@dataclass(order=True)
class Evento:
    tempo: float
    tipo: str  # 'chegada', 'saida'
    fila_id: int
    cliente: Cliente = field(compare=False)


@dataclass
class Fila:
    id: int
    servidores: int
    capacidade: int
    atendimento: List[float]  # intervalo de atendimento [min, max]
    roteamento: List[Dict]  # [{'destino': 2, 'probabilidade': 0.5}, ...]

    servidores_ocupados: int = 0
    fila_espera: List[Cliente] = field(default_factory=list)
    atendendo: List[Cliente] = field(default_factory=list)
    perdidos: int = 0

    def chegada(self, cliente: Cliente, tempo: float, agenda: List[Evento]):
        if self.servidores_ocupados < self.servidores:
            self.servidores_ocupados += 1
            self.atendendo.append(cliente)
            tempo_servico = random.uniform(*self.atendimento)
            heapq.heappush(agenda, Evento(tempo + tempo_servico, 'saida', self.id, cliente))
        elif len(self.fila_espera) < self.capacidade:
            self.fila_espera.append(cliente)
        else:
            self.perdidos += 1

    def saida(self, cliente: Cliente, tempo: float, agenda: List[Evento], filas: Dict[int, 'Fila']):
        self.servidores_ocupados -= 1
        self.atendendo.remove(cliente)

        if self.fila_espera:
            prox_cliente = self.fila_espera.pop(0)
            self.servidores_ocupados += 1
            self.atendendo.append(prox_cliente)
            tempo_servico = random.uniform(*self.atendimento)
            heapq.heappush(agenda, Evento(tempo + tempo_servico, 'saida', self.id, prox_cliente))

        destino = self.definir_roteamento()
        if destino != 'SAIDA':
            heapq.heappush(agenda, Evento(tempo, 'chegada', destino, cliente))

    def definir_roteamento(self):
        rnd = random.random()
        acumulado = 0
        for rot in self.roteamento:
            acumulado += rot['probabilidade']
            if rnd < acumulado:
                return rot['destino']
        return 'SAIDA'

# ===================== PARSER YAML ===================== #

def carregar_modelo_yaml(path: str):
    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    filas = {}
    for f in data['filas']:
        fila = Fila(
            id=f['id'],
            servidores=f['servidores'],
            capacidade=f['capacidade'],
            atendimento=f['atendimento'],
            roteamento=f['roteamento']
        )
        filas[f['id']] = fila

    chegada = data['chegada']
    return filas, chegada

# ===================== ESQUELETO DO SIMULADOR ===================== #

def rodar_simulacao(arquivo_yaml: str, tempo_max: float = 100):
    filas, chegada_cfg = carregar_modelo_yaml(arquivo_yaml)
    agenda = []
    tempo_atual = 0
    cliente_id = 0

    # Agendar primeira chegada externa
    intervalo = random.uniform(*chegada_cfg['intervalo'])
    cliente = Cliente(id=cliente_id, tempo_chegada=tempo_atual)
    heapq.heappush(agenda, Evento(tempo_atual + intervalo, 'chegada', chegada_cfg['destino_inicial'], cliente))
    cliente_id += 1

    while agenda and tempo_atual < tempo_max:
        evento = heapq.heappop(agenda)
        tempo_atual = evento.tempo
        fila = filas[evento.fila_id]

        if evento.tipo == 'chegada':
            fila.chegada(evento.cliente, tempo_atual, agenda)

            # Agendar próxima chegada externa se for da origem
            if evento.fila_id == chegada_cfg['destino_inicial']:
                cliente = Cliente(id=cliente_id, tempo_chegada=tempo_atual)
                intervalo = random.uniform(*chegada_cfg['intervalo'])
                heapq.heappush(agenda, Evento(tempo_atual + intervalo, 'chegada', chegada_cfg['destino_inicial'], cliente))
                cliente_id += 1

        elif evento.tipo == 'saida':
            fila.saida(evento.cliente, tempo_atual, agenda, filas)

    # Imprimir estatísticas básicas
    for fila in filas.values():
        print(f"Fila {fila.id}: Atendidos={len(fila.atendendo)}, Perdidos={fila.perdidos}, Em espera={len(fila.fila_espera)}")

# ===================== EXECUÇÃO DIRETA ===================== #

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Uso: python simulador.py modelo.yml")
    else:
        rodar_simulacao(sys.argv[1])
