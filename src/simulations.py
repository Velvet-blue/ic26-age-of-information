from src.config import np, njit


@njit
def gen_events(a, p, time):
    """
    Gera todas as decisões aleatórias de uma vez
    """
    arrivals_A = np.random.random(time) < a
    arrivals_B = np.random.random(time) < a
    sends_A = np.random.random(time) < p
    sends_B = np.random.random(time) < p
    return arrivals_A, arrivals_B, sends_A, sends_B


@njit
def throughput(arrival_prob, send_prob, time):
    """
    Throughput total do sistema (soma de todos os nós)
    """
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    total_thr = 0
    A_have = False
    B_have = False

    # O loop ainda existe, mas os acessos ao array NumPy são otimizados
    for t in range(time):

        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        # Sucesso A
        if A_willsend and not B_willsend:
            total_thr += 1
            A_have = False
        # Sucesso B
        elif B_willsend and not A_willsend:
            B_have = False

        # Chegada
        if arrivals_A[t]:
            A_have = True
        if arrivals_B[t]:
            B_have = True

    return total_thr / time


@njit
def disposal_rate(arrival_prob, send_prob, time):
    """
    Taxa de descarte de pacotes no nó de update
    """
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    total_disposal = 0
    A_have = False
    B_have = False

    # O loop ainda existe, mas os acessos ao array NumPy são otimizados
    for t in range(time):

        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        # Sucesso A
        if A_willsend and not B_willsend:
            A_have = False

        # Sucesso B
        elif B_willsend and not A_willsend:
            B_have = False

        # Chegada
        if arrivals_A[t]:
            if A_have:
                total_disposal += 1
            A_have = True

        if arrivals_B[t]:
            B_have = True

    return total_disposal / time


@njit
def W_up_cdot_I(arrival_prob, send_prob, time):
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    total_W_I = 0
    number_successes = 0

    t_arrival = 0
    t_update = 0
    A_have = False
    B_have = False
    for t in range(time):

        # 2. Lógica de Transmissão (acontece no final do slot de tempo)
        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        if A_willsend and not B_willsend: # Sucesso de A
            total_W_I += (t - t_arrival)*(t - t_update)
            t_update = t
            number_successes += 1
            A_have = False
            t_arrival = 0
        if B_willsend and not A_willsend:
            B_have = False

        # 3. Lógica de Chegada
        if arrivals_A[t]:
            A_have = True
            t_arrival = t
        if arrivals_B[t]:
            B_have = True

    return (total_W_I / number_successes) if number_successes > 0 else None


@njit
def I_squared(arrival_prob, send_prob, time):

    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    sum_I_sq = 0
    number_successes = 0

    t_update = 0
    A_have = False
    B_have = False
    for t in range(time):

        # 2. Lógica de Transmissão (acontece no final do slot de tempo)
        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        if A_willsend and not B_willsend: # Sucesso de A
            sum_I_sq += (t - t_update)**2
            t_update = t
            number_successes += 1
            A_have = False
        if B_willsend and not A_willsend:
            B_have = False

        # 3. Lógica de Chegada
        if arrivals_A[t]:
            A_have = True
            t_arrival = t
        if arrivals_B[t]:
            B_have = True

    return (sum_I_sq / number_successes) if number_successes > 0 else None


@njit
def X0_dot_X1(arrival_prob, send_prob, time):

    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    sum_X0X1 = 0
    number_successes = 0

    t_update = 0
    t_arrival = 0
    A_have = False
    B_have = False
    for t in range(time):

        # 2. Lógica de Transmissão (acontece no final do slot de tempo)
        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        if A_willsend and not B_willsend: # Sucesso de A
            sum_X0X1 += (t - t_arrival)*(t_arrival - t_update)
            t_update = t
            number_successes += 1
            A_have = False
        if B_willsend and not A_willsend:
            B_have = False

        # 3. Lógica de Chegada
        if arrivals_A[t] and not A_have:
            A_have = True
            t_arrival = t
        if arrivals_B[t]:
            B_have = True

    return (sum_X0X1 / number_successes) if number_successes > 0 else None


@njit
def X0_sqr(arrival_prob, send_prob, time):

    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    sum_X0_sqr = 0
    number_successes = 0

    t_update = 0
    t_arrival = 0
    A_have = False
    B_have = False
    for t in range(time):

        # 2. Lógica de Transmissão (acontece no final do slot de tempo)
        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        if A_willsend and not B_willsend: # Sucesso de A
            sum_X0_sqr += (t_arrival - t_update)**2
            t_update = t
            number_successes += 1
            A_have = False
        if B_willsend and not A_willsend:
            B_have = False

        # 3. Lógica de Chegada
        if arrivals_A[t] and not A_have:
            A_have = True
            t_arrival = t
        if arrivals_B[t]:
            B_have = True

    return (sum_X0_sqr / number_successes) if number_successes > 0 else None


@njit
def X1_sqr(arrival_prob, send_prob, time):

    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    sum_X1_sqr = 0
    number_successes = 0

    # t_update = 0
    t_arrival = 0
    A_have = False
    B_have = False
    for t in range(time):

        # 2. Lógica de Transmissão (acontece no final do slot de tempo)
        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        if A_willsend and not B_willsend: # Sucesso de A
            sum_X1_sqr += (t - t_arrival)**2
            # t_update = t
            number_successes += 1
            A_have = False
        if B_willsend and not A_willsend:
            B_have = False

        # 3. Lógica de Chegada
        if arrivals_A[t] and not A_have:
            A_have = True
            t_arrival = t
        if arrivals_B[t]:
            B_have = True

    return (sum_X1_sqr / number_successes) if number_successes > 0 else None


@njit
def occupation_up_pack(arrival_prob, send_prob, time):
    """L_up -> probabilidade de encontrar um pacote que será transmitido com
    sucesso, olhando para algum timeslot aleatório"""

    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    total_occupation = 0
    partial_occupation = 0
    A_have = False
    B_have = False

    for t in range(time):

        # # métrica ocupação
        partial_occupation += 1 if A_have else 0
        # mean_delay += (t - tA_arrival) if A_have else 0

        # Lógica de Transmissão (acontece no final do slot de tempo)
        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        if A_willsend and not B_willsend:
            total_occupation += partial_occupation
            A_have = False
        elif B_willsend and not A_willsend:
            B_have = False

        if arrivals_A[t]:
            partial_occupation = 0
            A_have = True
        if arrivals_B[t]:
            B_have = True


    return total_occupation/time


def mean_delay_up_pack(arrival_prob, send_prob, time):
    """
    tempo médio de permanência dos pacotes de uptade no nó (W_up)
    """
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    total_delay = 0
    number_successes = 0

    t_arrival = 0
    A_have = False
    B_have = False
    for t in range(time):

        # 2. Lógica de Transmissão (acontece no final do slot de tempo)
        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        if A_willsend and not B_willsend: # Sucesso de A
            total_delay += (t - t_arrival)
            number_successes += 1
            A_have = False
            t_arrival = 0
        if B_willsend and not A_willsend:
            B_have = False

        # 3. Lógica de Chegada
        if arrivals_A[t]:
            A_have = True
            t_arrival = t
        if arrivals_B[t]:
            B_have = True

    return total_delay / number_successes if number_successes > 0 else None


@njit
def mean_delay_disc_pack(arrival_prob, send_prob, time):
    """
    tempo médio de permanência de um pacote no nó até ser descartado
    """
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    total_delay = 0
    number_discards = 0

    t_arrival = 0
    A_have = False
    B_have = False
    for t in range(time):

        # 2. Lógica de Transmissão (acontece no final do slot de tempo)
        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        if A_willsend and not B_willsend: # Sucesso de A
            A_have = False
        if B_willsend and not A_willsend:
            B_have = False

        # 3. Lógica de Chegada
        if arrivals_A[t]:
            if A_have:
                total_delay += (t - t_arrival)
                number_discards += 1
            A_have = True
            t_arrival = t
        if arrivals_B[t]:
            B_have = True

    return total_delay / number_discards if number_discards > 0 else None


@njit
def mean_delay_any_pack(arrival_prob, send_prob, time):
    """
    tempo médio de permanência de um pacotes no nó
    até ser descartado ou transmitido com sucesso (W)
    """
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    total_delay = 0
    number_exits = 0

    t_arrival = 0
    A_have = False
    B_have = False
    for t in range(time):

        # 2. Lógica de Transmissão (acontece no final do slot de tempo)
        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        if A_willsend and not B_willsend: # Sucesso de A
            total_delay += (t - t_arrival)
            number_exits += 1
            A_have = False
            t_arrival = 0
        if B_willsend and not A_willsend:
            B_have = False

        # 3. Lógica de Chegada
        if arrivals_A[t]:
            if A_have:
                total_delay += (t - t_arrival)
                number_exits += 1
            A_have = True
            t_arrival = t
        if arrivals_B[t]:
            B_have = True

    return total_delay / number_exits if number_exits > 0 else None


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

        # 4. Armazena o estado do AoI no final do processo
        AAoI += current_aoi_A
        
        # 1. A idade no destino sempre aumenta em 1 a cada time step
        current_aoi_A += 1

        # 2. Lógica de Transmissão (acontece no slot)
        A_tries = A_have and sends_A[t]
        B_tries = B_have and sends_B[t]

        # Sucesso de A
        if A_tries and not B_tries:
            PAoI += current_aoi_A
            current_aoi_A = (t - tA_arrival)
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

    if successes > 0:
        AAoI = AAoI / time + 1/2
        PAoI = PAoI / successes
    else:
        AAoI = None
        PAoI = None
    return (AAoI, PAoI)


@njit
def evolution_AoI_sim(arrival_prob, send_prob, time=100):
    ev_aoi_A = np.empty(time)
    ev_aoi_B = np.empty(time)
    arrivals_succes_pack = np.empty(time)

    # rolagem de todos os dados
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob

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
      
        AAoI += current_aoi_A
      
        # 1. A idade no destino sempre aumenta em 1 a cada time step
        current_aoi_A += 1
        current_aoi_B += 1

        # 2. Lógica de Transmissão (acontece no slot)
        A_tries = A_have and sends_A[t]
        B_tries = B_have and sends_B[t]

        # Sucesso de A
        if A_tries and not B_tries:
            PAoI += current_aoi_A - 1
            current_aoi_A = (t - tA_arrival) + 1
            arrivals_succes_pack[successes] = tA_arrival
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not A_tries:
            current_aoi_B = (t - tB_arrival) + 1
            B_have = False

        # 3. Lógica de Chegada (com substituição). Desde o tempo 0, pode ter pacotes.
        # aqui, ficou mais fácil deixar as chegadas neste ponto
        if arrivals_A[t]:
            tA_arrival = t
            A_have = True

        if arrivals_B[t]:
            tB_arrival = t
            B_have = True

        # 4. Armazena o estado do AoI no final do processo
        ev_aoi_A[t] = current_aoi_A
        ev_aoi_B[t] = current_aoi_B

    return ev_aoi_A, ev_aoi_B, arrivals_succes_pack[:successes], PAoI/successes, AAoI/time, successes