import random
import heapq

class Evento:
    def __init__(self, tempo, tipo, fila, cliente_id):
        self.tempo = tempo
        self.tipo = tipo  # "chegada" ou "saida"
        self.fila = fila  # Fila 1, 2 ou 3
        self.cliente_id = cliente_id

    def __lt__(self, other):
        return self.tempo < other.tempo

class Fila:
    def __init__(self, id, servidores, capacidade, tempo_atendimento_func):
        self.id = id
        self.servidores = servidores
        self.capacidade = capacidade
        self.tempo_atendimento_func = tempo_atendimento_func
        self.clientes = 0
        self.em_servico = 0
        self.tempo_por_estado = {}
        self.perdas = 0
        self.ultimo_tempo = 0

    def atualizar_estado(self, tempo_atual):
        estado = self.clientes
        tempo_decorrido = tempo_atual - self.ultimo_tempo
        self.tempo_por_estado[estado] = self.tempo_por_estado.get(estado, 0) + tempo_decorrido
        self.ultimo_tempo = tempo_atual

    def chegada(self, tempo_atual):
        self.atualizar_estado(tempo_atual)
        if self.clientes < self.capacidade:
            self.clientes += 1
            if self.em_servico < self.servidores:
                self.em_servico += 1
                return True  # Será atendido imediatamente
        else:
            self.perdas += 1
        return False

    def saida(self, tempo_atual):
        self.atualizar_estado(tempo_atual)
        self.clientes -= 1
        if self.clientes >= self.servidores:
            return True  # Próximo cliente começa a ser atendido
        else:
            self.em_servico -= 1
            return False

class Simulador:
    def __init__(self):
        self.relogio = 2.0
        self.eventos = []
        self.total_eventos = 0
        self.max_eventos = 100000
        self.id_cliente = 0
        self.resultado = []

        self.filas = {
            1: Fila(1, 1, float('inf'), lambda: random.uniform(1, 2)),
            2: Fila(2, 2, 5, lambda: random.uniform(4, 8)),
            3: Fila(3, 2, 10, lambda: random.uniform(5, 15))
        }

        heapq.heappush(self.eventos, Evento(self.relogio, "chegada", 1, self.id_cliente))
        self.id_cliente += 1

    def agendar(self, evento):
        heapq.heappush(self.eventos, evento)

    def executar(self):
        while self.total_eventos < self.max_eventos and self.eventos:
            evento = heapq.heappop(self.eventos)
            self.relogio = evento.tempo
            fila = self.filas[evento.fila]

            if evento.tipo == "chegada":
                if fila.chegada(self.relogio):
                    duracao = fila.tempo_atendimento_func()
                    self.agendar(Evento(self.relogio + duracao, "saida", evento.fila, evento.cliente_id))

                if evento.fila == 1:
                    intervalo = random.uniform(2, 4)
                    self.agendar(Evento(self.relogio + intervalo, "chegada", 1, self.id_cliente))
                    self.id_cliente += 1

            elif evento.tipo == "saida":
                proximo = fila.saida(self.relogio)
                if proximo:
                    duracao = fila.tempo_atendimento_func()
                    self.agendar(Evento(self.relogio + duracao, "saida", evento.fila, self.id_cliente))

                if evento.fila == 1:
                    destino = random.choices([2, 3], weights=[0.8, 0.2])[0]
                    self.agendar(Evento(self.relogio, "chegada", destino, self.id_cliente))
                    self.id_cliente += 1
                elif evento.fila == 2:
                    destino = random.choices([1, 3], weights=[0.3, 0.5])[0]
                    self.agendar(Evento(self.relogio, "chegada", destino, self.id_cliente))
                    self.id_cliente += 1
                elif evento.fila == 3:
                    destino = random.choices([1], weights=[0.7])[0]
                    self.agendar(Evento(self.relogio, "chegada", destino, self.id_cliente))
                    self.id_cliente += 1

            self.total_eventos += 1

        self.gerar_resultado()

    def gerar_resultado(self):
        with open("C:\\Users\\jeancarlo.gomes\\OneDrive - HT MICRON SEMICONDUTORES S.A\\Documentos\\Pessoal\\resultado_simulacao.txt", "w") as f:
            f.write(f"Tempo global da simulação: {self.relogio:.2f} minutos\n\n")
            for id, fila in self.filas.items():
                f.write(f"--- Fila {id} ---\n")
                f.write("Distribuição de probabilidades dos estados:\n")
                total_tempo = sum(fila.tempo_por_estado.values())
                for estado in sorted(fila.tempo_por_estado):
                    tempo = fila.tempo_por_estado[estado]
                    prob = tempo / total_tempo
                    f.write(f"Estado {estado}: {prob:.4f} ({tempo:.2f} min)\n")
                f.write(f"Total de perdas: {fila.perdas}\n\n")

# Executar simulador
if __name__ == "__main__":
    simulador = Simulador()
    simulador.executar()
