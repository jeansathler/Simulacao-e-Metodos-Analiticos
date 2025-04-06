import random

# Parâmetros do Método Congruente Linear
a = 1664525
c = 1013904223
M = 2**32
previous = random.randint(0, M-1)

def NextRandom():
    global previous
    previous = (a * previous + c) % M
    return previous / M

# Parâmetros da simulação
count = 100000

class Evento:
    
    def __init__(self, tipo, tempo, filaOrigem=None, filaDestino=None):
        self.tipo = tipo
        self.tempo = tempo
        self.filaOrigem = filaOrigem
        self.filaDestino = filaDestino

        # print("\tAgendou evento: ", self.toString())

    def toString(self):
        return f"Evento: {self.tipo} | Tempo: {self.tempo} | Fila Origem: {self.filaOrigem.toString() if self.filaOrigem != None else "None"} | Fila Destino: {self.filaDestino.toString() if self.filaDestino != None else "None"}"

class Fila:
    
    def __init__(self, server, capacidade, minService, maxService, Escalonador, filaOrigem=None, filaDestino=None, minArrival=None, maxArrival=None):
        self.server = int(server)
        self.capacidade = int(capacidade)
        self.minArrival = minArrival
        self.maxArrival = maxArrival
        self.minService = minService
        self.maxService = maxService
        self.customer = 0
        self.arrayCapacidade = [0] * (capacidade + 1)
        self.loss = 0
        self.time = 0
        self.Escalonador = Escalonador
        self.filaOrigem = filaOrigem if filaOrigem is not None else self
        self.filaDestino = filaDestino


    def chegada(self, arrival):
        if self.customer < self.capacidade:
            self.arrayCapacidade[self.customer] += self.Escalonador.tempo - self.time
            self.time = arrival
            self.customer += 1
            
            # Print o if de customer < server
            # print(self.customer, ">", self.server, "True" if self.customer < self.server else "False")
            if self.customer <= self.server:
                tempo_rand = NextRandom() * (self.maxService - self.minService) + self.minService
                self.Escalonador.add_evento(Evento('passagem', arrival + tempo_rand, filaOrigem=self.filaOrigem, filaDestino=self.filaDestino))
        else:
            self.loss += 1

        tempo_rand = NextRandom() * (self.maxArrival - self.minArrival) + self.minArrival
        self.Escalonador.add_evento(Evento('chegada', arrival + tempo_rand, self.filaOrigem))

    def passagem(self, arrival, filaDestino):
        self.filaOrigem.arrayCapacidade[self.filaOrigem.customer] += self.Escalonador.tempo - self.filaOrigem.time
        self.filaOrigem.time = arrival
        self.arrayCapacidade[self.customer] += self.Escalonador.tempo - self.time
        self.time = arrival

        self.filaOrigem.customer -= 1
        if self.filaOrigem.customer >= self.filaOrigem.server:
            tempo_rand = NextRandom() * (self.maxService - self.minService) + self.minService
            self.Escalonador.add_evento(Evento('passagem', arrival + tempo_rand, self.filaOrigem, filaDestino))

        if self.customer < self.capacidade:
            self.customer += 1
            if self.customer <= self.server:
                tempo_rand = NextRandom() * (self.maxService - self.minService) + self.minService
                self.Escalonador.add_evento(Evento('saida', arrival + tempo_rand, self))
        else:
            self.loss += 1

    def saida(self, arrival):
        if self.customer > 0:
            self.arrayCapacidade[self.customer] += self.Escalonador.tempo - self.time
            self.time = arrival

            self.customer -= 1
            if self.customer >= self.server:
                tempo_rand = NextRandom() * (self.maxService - self.minService) + self.minService
                self.Escalonador.add_evento(Evento('saida', arrival + tempo_rand, self))

    def toString(self):
        return f"G/G/{self.server}/{self.capacidade} | Clientes: {self.customer} | Perdas: {self.loss}"
    
    def status(self):
        print("Distribuição de capacidade:")
        for i in range(len(self.arrayCapacidade)):
            print(i, ": ", self.arrayCapacidade[i]/self.Escalonador.tempo, " | Tempo: ", self.arrayCapacidade[i])
        print("Tempo total: ", self.Escalonador.tempo)
        print("Perdas: ", self.loss)

class Escalonador:
    
    def __init__(self):
        self.eventos = []
        self.tempo = 0
        self.filas = []

    def add_fila(self, fila):
        self.filas.append(fila)
        
    def add_evento(self, evento):
        self.eventos.append(evento)

    def execute_event(self):
        if not self.eventos:
            return None
        next_event = min(self.eventos, key=lambda evento: evento.tempo)
        # print("Executando: ", next_event.toString())
        self.eventos.remove(next_event)
        self.tempo = next_event.tempo

        if next_event.tipo == 'chegada':
            next_event.filaOrigem.chegada(next_event.tempo)
        elif next_event.tipo == 'passagem':
            next_event.filaDestino.passagem(next_event.tempo, filaDestino=next_event.filaDestino)
        elif next_event.tipo == 'saida':
            next_event.filaOrigem.saida(next_event.tempo)

        # print("Executou")
        

def main():
    escalonador = Escalonador()
    # Fila G/G/2/3  
    fila = Fila(
        server=2, 
        capacidade=3, 
        minArrival=1,
        maxArrival=4, 
        minService=3, 
        maxService=4, 
        Escalonador=escalonador
        )
    escalonador.add_fila(fila)
    
    # Fila G/G/1/5
    fila = Fila(
        server=1, 
        capacidade=5, 
        minService=2, 
        maxService=3,
        Escalonador=escalonador
        )
    escalonador.add_fila(fila)
    # Fila G/G/2/3 envia para Fila G/G/1/5  
    escalonador.filas[0].filaDestino = escalonador.filas[1]
    escalonador.filas[1].filaOrigem = escalonador.filas[0]
    
    print(f"Fila1 instanciada: {escalonador.filas[0].toString()} | Fila Origem: {escalonador.filas[0].filaOrigem.toString()} | Fila Destino: {escalonador.filas[0].filaDestino.toString()}")
    print(f"Fila2 instanciada: {escalonador.filas[1].toString()} | Fila Origem: {escalonador.filas[1].filaOrigem.toString()} | Fila Destino: {escalonador.filas[1].filaDestino.toString() if escalonador.filas[1].filaDestino != None else 'None'}")
    escalonador.add_evento(Evento('chegada', 1.5, escalonador.filas[0]))
    for i in range(count):
        escalonador.execute_event()
    
    print()
    print("Simulação finalizada")
    print("Resultados:")
    print(escalonador.filas[0].toString())
    escalonador.filas[0].status()
    print()
    print(escalonador.filas[1].toString())
    escalonador.filas[1].status()

if __name__ == "__main__":
    main()