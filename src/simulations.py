from src.config import np, njit


@njit
def throughput(arrival_prob, send_prob, time):
    """
    Throughput total do sistema (soma de todos os nós)
    """

    # Gera todas as decisões aleatórias de uma vez
    # (economiza tempo de chamada de função)
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob

    total_thr = 0
    A_have = False
    B_have = False

    # O loop ainda existe, mas os acessos ao array NumPy são otimizados
    for t in range(time):
        # Chegada
        if arrivals_A[t]:
            A_have = True
        if arrivals_B[t]:
            B_have = True

        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        # Sucesso A
        if A_willsend and not B_willsend:
            total_thr += 1
            A_have = False
        # Sucesso B
        elif B_willsend and not A_willsend:
            B_have = False

    return total_thr / time


@njit
def disposal_rate(arrival_prob, send_prob, time):
    """
    Taxa de descarte de pacotes no nó de update
    """

    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob

    total_disposal = 0
    A_have = False
    B_have = False

    # O loop ainda existe, mas os acessos ao array NumPy são otimizados
    for t in range(time):
        # Chegada
        if arrivals_A[t]:
            if A_have:
                total_disposal += 1
            A_have = True

        if arrivals_B[t]:
            B_have = True

        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        # Sucesso A
        if A_willsend and not B_willsend:
            A_have = False

        # Sucesso B
        elif B_willsend and not A_willsend:
            B_have = False

    return total_disposal / time

@njit
def occupation_up_pack(arrival_prob, send_prob, time):
    """L_up -> probabilidade de encontrar um pacote que será transmitido com
    sucesso, olhando para algum timeslot aleatório"""

    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob

    total_occupation = 0
    partial_occupation = 0
    A_have = False
    B_have = False

    for t in range(time):

        # 1. Lógica de Chegada
        if arrivals_A[t]:
            partial_occupation = 0
            A_have = True
        if arrivals_B[t]:
            B_have = True

        # # métrica ocupação
        partial_occupation += 1 if A_have else 0
        # mean_delay += (t - tA_arrival) if A_have else 0

        # 2. Lógica de Transmissão (acontece no final do slot de tempo)
        A_willsend = A_have and sends_A[t]
        B_willsend = B_have and sends_B[t]

        if A_willsend and not B_willsend:
            total_occupation += partial_occupation
            A_have = False
        elif B_willsend and not A_willsend:
            B_have = False


    return total_occupation/time


def mean_delay_up_pack(arrival_prob, send_prob, time):
    """
    tempo médio de permanência dos pacotes de uptade no nó (W_up)
    """
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob

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
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob

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
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob

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
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob

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