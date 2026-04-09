def validar_afd(estados, alfabeto, transicoes, estado_inicial, estados_finais):
    if estado_inicial not in estados:
        return False, "Erro: Estado inicial não pertence ao conjunto de estados."
    
    if not estados_finais.issubset(estados):
        return False, "Erro: Existem estados de aceitação que não pertencem ao conjunto de estados."

    for estado in estados:
        if estado not in transicoes:
            return False, f"Erro: O estado {estado} não possui transições definidas."
        
        simbolos_mapeados = transicoes[estado]

        if set(simbolos_mapeados.keys()) != set(alfabeto):
            return False, f"Erro: O estado {estado} deve ter transições para TODOS os símbolos {alfabeto}."

        for simbolo, destino in simbolos_mapeados.items():
            if isinstance(destino, (list, set, tuple)):
                return False, f"Erro: No AFD, o símbolo '{simbolo}' no estado '{estado}' só pode levar a UM destino, mas levou a vários: {destino}."
            
            if destino not in estados:
                return False, f"Erro: O estado {estado} leva ao estado inexistente '{destino}' através do símbolo '{simbolo}'."
            
    return True, "Validado: É um AFD legítimo!"

afd_verdadeiro = {
    'estados': {'q0', 'q1'},
    'alfabeto': {'0', '1'},
    'inicial': 'q0',
    'finais': {'q1'},
    'transicoes': {
        'q0': {'0': 'q0', '1': 'q1'},
        'q1': {'0': 'q0', '1': 'q1'}
    }
}

afn_disfarcado = {
    'estados': {'A', 'B'},
    'alfabeto': {'0', '1'},
    'inicial': 'A',
    'finais': {'B'},
    'transicoes': {
        'A': {'0': ['A', 'B'], '1': 'A'},
        'B': {'0': 'B', '1': 'B'}
    }
}

print("--- Testando AFD Verdadeiro ---")
print(validar_afd(afd_verdadeiro['estados'], afd_verdadeiro['alfabeto'], afd_verdadeiro['transicoes'], afd_verdadeiro['inicial'], afd_verdadeiro['finais'])[1])

print("\n--- Testando AFN Disfarçado ---")
print(validar_afd(afn_disfarcado['estados'], afn_disfarcado['alfabeto'], afn_disfarcado['transicoes'], afn_disfarcado['inicial'], afn_disfarcado['finais'])[1])