from src.config import np, njit
from src.simulations import gen_events


@njit
def AAoI_PAoI_sim(arrival_prob, send_prob, time, threshold=1):

    # rolagem de todos os dados
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    successes = 0
    AAoI = 0
    PAoI = 0

    # Variáveis dos transmissores
    Age_A = 0
    Age_B = 0
    t_arrival_A = 0
    t_arrival_B = 0
    A_have = False
    B_have = False

    for t in range(time):

        # 1. Lógica de Transmissão

        A_tries = A_have and sends_A[t] and Age_A >= threshold
        B_tries = B_have and sends_B[t] and Age_B >= threshold

        # 2. Updates

        # Sucesso de A
        if A_tries and not B_tries:
            PAoI += Age_A - 1
            Age_A = (t - t_arrival_A) + 1
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not A_tries:
            Age_B = (t - t_arrival_B) + 1
            B_have = False

        # 3. Arrivals and Ages

        if arrivals_A[t]:
            t_arrival_A = t
            A_have = True
        if arrivals_B[t]:
            t_arrival_B = t
            B_have = True

        AAoI += Age_A
        Age_A += 1
        Age_B += 1

    if successes > 0:
        AAoI = AAoI / time + 1/2
        PAoI = PAoI / successes
    else:
        AAoI = np.nan
        PAoI = np.nan
    return (AAoI, PAoI)