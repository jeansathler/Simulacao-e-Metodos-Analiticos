
# T1 - Desenvolvimento de Simulador para Rede de Filas

# Descrição 

Para a simulação, considere inicialmente as filas vazias e que o primeiro cliente chega no tempo 2,0. Realizem a simulação com 100.000 aleatórios, ou seja, ao se utilizar o 100.000 aleatório, a simulação deve se encerrar e a distribuição de probabilidades, bem como os tempos acumulados para os estados de cada fila devem ser reportados. Além disso, indique o número de perda de clientes (caso tenha havido perda) de cada fila e o tempo global da simulação.

# Como Executar

# 1. Clone ou baixe o repositório

```bash
git clone https://github.com/jeansathler/Simulacao-e-Metodos-Analiticos/tree/main/T1
cd simulador-filas
```

# 2. Abra o projeto no VS Code
```bash
code .
```

# 3. Edite o caminho de saída do arquivo `.txt`

No arquivo `simulador_filas.py`, localize esta linha (próximo do final):

```python
with open("/mnt/data/resultado_simulacao.txt", "w") as f:
```

**Substitua pelo caminho da rede que salvou o projeto. Ex.:**

```python
with open("C:\\Users\\jeancarlo.gomes\\Documentos\\resultado_simulacao.txt", "w") as f:
```

# 4. Execute o simulador

No terminal integrado do VS Code, rode:

```bash
python simulador_filas.py
```

# Verifique o Resultado

Após a execução, você verá no terminal algo como:

```
Simulação finalizada.
Fila1 teve 0 clientes na fila ao final.
Fila2 teve 11 clientes na fila ao final.
Fila3 teve 64 clientes na fila ao final.
```

O resultado completo estará no arquivo:
```
resultado_simulacao.txt
```
