from src.config import np, njit
from src.simulations import gen_events


@njit
def AAoI_PAoI_sim(arrival_prob, send_prob, time):

    # rolagem de todos os dados
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    current_aoi_A = 0
    successes = 0
    AAoI = 0
    PAoI = 0

    # Variáveis dos transmissores
    tA_arrival = 0
    A_have = False
    B_have = False

    for t in range(time):

        # 1. A idade no destino sempre aumenta em 1 a cada time step
        current_aoi_A += 1

        # 2. Lógica de Transmissão (acontece no slot)
        A_tries = A_have and sends_A[t]
        B_tries = B_have and sends_B[t]

        # Sucesso de A
        if A_tries and not B_tries:
            PAoI += current_aoi_A - 1
            current_aoi_A = (t - tA_arrival) + 1
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not A_tries:
            B_have = False

        # 3. Lógica de Chegada (com substituição). Desde o tempo 0, pode ter pacotes.
        # aqui, ficou mais fácil deixar as chegadas neste ponto
        if arrivals_A[t]:
            tA_arrival = t
            A_have = True

        if arrivals_B[t]:
            B_have = True

        # 4. Armazena o estado do AoI no final do processo
        AAoI += current_aoi_A

    if successes > 0:
        AAoI = AAoI / time
        PAoI = PAoI / successes
    else:
        AAoI = None
        PAoI = None
    return (AAoI, PAoI)


@njit
def generate_traces(arrival_prob, send_prob, time, threshold):
    # Coluna 0: Tempo de Saída (t_up)
    # Coluna 1: Tempo de Geração (t_a)
    successful_packets = np.zeros((time, 2), dtype=np.int64)
    success_count = 0
    
    # Para descartes, só precisamos saber QUAIS foram descartados ou quantos
    disposal_count = 0
    
    # Para ocupação, como é uma integral no tempo, é melhor somar logo aqui
    # pois salvar o estado de fila a cada t gastaria muita memória.
    total_occupation = 0
    
    # --- Estado ---
    t_arrival_A = -1
    t_arrival_B = -1
    Age_A = 0
    Age_B = 0
    A_have = False
    B_have = False

    for t in range(time):
        # Geradores (mesma otimização anterior)
        rnd_arr_A = np.random.random()
        rnd_arr_B = np.random.random()
        rnd_send_A = np.random.random()
        rnd_send_B = np.random.random()
        
        try_A = A_have and (rnd_send_A < send_prob) and Age_A >= threshold
        try_B = B_have and (rnd_send_B < send_prob) and Age_B >= threshold

        # Transmissão
        success_A = try_A and not try_B
        success_B = try_B and not try_A

        if success_A:
            successful_packets[success_count, 0] = t    # momento de update
            successful_packets[success_count, 1] = t_arrival_A  # momento de geração
            Age_A = (t - t_arrival_A)
            success_count += 1

            A_have = False 
        elif success_B:
            Age_B = (t - t_arrival_B)
            B_have = False

        # Ocupação (acumulada in-loop pois é barato)
        if A_have: 
            total_occupation += 1

        # Chegada
        arr_A = rnd_arr_A < arrival_prob
        arr_B = rnd_arr_B < arrival_prob

        if arr_A:
            if A_have:
                disposal_count += 1
            A_have = True
            t_arrival_A = t

        if arr_B:
            B_have = True
            t_arrival_B = t

        Age_A += 1
        Age_B += 1

    # Cortamos os arrays para o tamanho real preenchido e retornamos
    return (
        successful_packets[:success_count], 
        disposal_count, 
        total_occupation
    )