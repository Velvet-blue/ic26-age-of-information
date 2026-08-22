import numpy as np

from src.simulations import gen_events

time = 100
arrival_prob = 1
send_prob = 0.7
threshold = 1

ev_aoi_A = np.empty(time)
ev_aoi_B = np.empty(time)
arrivals_succes_pack = np.empty(time)
updates = np.empty(time)

# rolagem de todos os dados
(arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
    a=arrival_prob, p=send_prob, time=time)

# Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
current_aoi_A = 0
current_aoi_B = 0
successes = 0
PAoI = 0
AAoI = 0

# Variáveis dos transmissores
tA_arrival = 0
tB_arrival = 0
A_have = False
B_have = False

for t in range(time):
    
    # 1. A idade no destino sempre aumenta em 1 a cada time step

    # 2. Lógica de Transmissão (acontece no slot)
    A_tries = A_have and sends_A[t] and current_aoi_A > threshold # não é >= pois já estamos no tempo t+1, depois do update
    B_tries = B_have and sends_B[t] and current_aoi_B > threshold

    # Sucesso de A
    if A_tries and not B_tries:
        PAoI += current_aoi_A
        current_aoi_A = (t - tA_arrival)
        arrivals_succes_pack[successes] = tA_arrival
        updates[successes] = t
        successes += 1
        A_have = False

    # Sucesso de B
    if B_tries and not A_tries:
        current_aoi_B = (t - tB_arrival)
        B_have = False

    # 3. Lógica de Chegada (com substituição). Desde o tempo 0, pode ter pacotes.
    # aqui, ficou mais fácil deixar as chegadas neste ponto
    if arrivals_A[t]:
        tA_arrival = t
        A_have = True

    if arrivals_B[t]:
        tB_arrival = t
        B_have = True

    AAoI += current_aoi_A

    ev_aoi_A[t] = current_aoi_A
    ev_aoi_B[t] = current_aoi_B

    current_aoi_A += 1
    current_aoi_B += 1