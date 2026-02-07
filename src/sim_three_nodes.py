from src.config import np, njit


@njit
def AAoI_PAoI_het_sim(arrival_prob, send_prob, time, threshold=0):

    # rolagem de todos os dados
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    arrivals_C = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < 1 - send_prob #send_prob_array[0]
    sends_B = np.random.random(time) < send_prob #send_prob_array[1]
    sends_C = np.random.random(time) < 0 #send_prob_array[2]

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    successes = 0
    AAoI = 0
    PAoI = 0

    # Variáveis dos transmissores
    Age_A = 0
    Age_B = 0
    Age_C = 0
    t_arrival_A = 0
    t_arrival_B = 0
    t_arrival_C = 0
    A_have = False
    B_have = False
    C_have = False

    for t in range(time):

        # 1. Lógica de Transmissão

        A_tries = A_have and sends_A[t] and Age_A >= threshold
        B_tries = B_have and sends_B[t] and Age_B >= threshold
        C_tries = C_have and sends_C[t] and Age_C >= threshold

        # 2. Updates

        # Sucesso de A
        if A_tries and not (B_tries or C_tries):
            PAoI += Age_A - 1
            Age_A = (t - t_arrival_A) + 1
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not (A_tries or C_tries):
            Age_B = (t - t_arrival_B) + 1
            B_have = False

        # Sucesso de C
        if C_tries and not (A_tries or B_tries):
            Age_C = (t - t_arrival_C) + 1
            C_have = False

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
        AAoI = AAoI / time
        PAoI = PAoI / successes
    else:
        AAoI = np.nan
        PAoI = np.nan
    return (AAoI, PAoI)


@njit
def AAoI_PAoI_hom_sim(arrival_prob, send_prob, time, threshold=0):

    # rolagem de todos os dados
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    arrivals_C = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob
    sends_C = np.random.random(time) < send_prob

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    successes = 0
    AAoI = 0
    PAoI = 0

    # Variáveis dos transmissores
    Age_A = 0
    Age_B = 0
    Age_C = 0
    t_arrival_A = 0
    t_arrival_B = 0
    t_arrival_C = 0
    A_have = False  # trocar por arrivals[0] em todos os arquivos
    B_have = False  # trocar por arrivals[0] em todos os arquivos
    C_have = False  # trocar por arrivals[0] em todos os arquivos

    for t in range(time):

        # 1. Lógica de Transmissão

        A_tries = A_have and sends_A[t] and Age_A >= threshold
        B_tries = B_have and sends_B[t] and Age_B >= threshold
        C_tries = C_have and sends_C[t] and Age_C >= threshold

        # 2. Updates

        # Sucesso de A
        if A_tries and not (B_tries or C_tries):
            PAoI += Age_A - 1
            Age_A = (t - t_arrival_A) + 1
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not (A_tries or C_tries):
            Age_B = (t - t_arrival_B) + 1
            B_have = False

        # Sucesso de C
        if C_tries and not (A_tries or B_tries):
            Age_C = (t - t_arrival_C) + 1
            C_have = False

        # 3. Arrivals and Ages

        if arrivals_A[t]:
            t_arrival_A = t
            A_have = True
        if arrivals_B[t]:
            t_arrival_B = t
            B_have = True
        if arrivals_C[t]:
            t_arrival_C = t
            C_have = True

        AAoI += Age_A
        Age_A += 1
        Age_B += 1
        Age_C += 1

    if successes > 0:
        AAoI = AAoI / time
        PAoI = PAoI / successes
    else:
        AAoI = np.nan
        PAoI = np.nan
    return (AAoI, PAoI)