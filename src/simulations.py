from src.config import np, njit


@njit
def throughput(arrival_prob, send_prob, time=10000):
    """
    Throughput total do sistema (soma de todos os nós)
    """

    # Gera todas as decisões aleatórias de uma vez
    # (economiza tempo de chamada de função)
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob

    mean_thr = 0
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
            mean_thr += 1
            A_have = False
        # Sucesso B
        elif B_willsend and not A_willsend:
            mean_thr += 1
            B_have = False

    return mean_thr / time


@njit
def occupation_up_pack(arrival_prob, send_prob, time=100):
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


def mean_delay_up_pack(arrival_prob, send_prob, time=100):
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
            B_have = 0

        # 3. Lógica de Chegada
        if arrivals_A[t]:
            A_have = True
            t_arrival = t
        if arrivals_B[t]:
            B_have = True

    return total_delay / number_successes if number_successes > 0 else None