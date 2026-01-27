from src.config import np, njit


@njit
def throughput(arrival_prob, send_prob, time=10000):
    """Gera todas as decisões aleatórias de uma vez
    (economiza tempo de chamada de função)"""
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
