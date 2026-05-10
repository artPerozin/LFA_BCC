"""
modelos_carros.py
Define 4 tipos de carros e seus modelos, cada um com seu PDA específico.

  SEDAN  – BASE / GL / GLS / SPORT   (4 modelos)
  SUV    – ENTRY / AWD / PREMIUM     (3 modelos)
  PICKUP – CS / CD / CD-TURBO        (3 modelos)
  HATCH  – POP / CITY / RS           (3 modelos)

Cada modelo tem etapas próprias.  O PDA usa a pilha como "checklist"
sequencial: topo da pilha indica a etapa esperada; ao concluir uma etapa
o marcador correspondente é retirado e o próximo é empilhado.
Quando a pilha fica vazia no estado de aceitação, a produção está finalizada.
"""

from automato_pilha import AutomatoPilha, Transicao


# ────────────────────────────────────────────────────────────────
# Construtor genérico de PDA linear
# ────────────────────────────────────────────────────────────────

def _fazer_pda(nome: str, etapas: list) -> AutomatoPilha:
    """
    etapas: lista de (simbolo, descricao, pode_falhar)
    Constrói PDA determinístico sequencial.

    Convenção de pilha:
      - Pilha inicial: ['Z']   (Z = fundo de pilha / marcador global)
      - A cada etapa i, a transição espera topo == 'Z' (pilha com apenas Z),
        executa e empilha 'Z' novamente, avançando o estado.
      - Na última transição (FIM), o pop de Z deixa a pilha vazia → aceitação.
    Isso é simples, correto e verificável — a pilha garante que a sequência
    não "pula" para o final sem percorrer todos os estados intermediários.
    """
    n = len(etapas)
    estados = {f"q{i}" for i in range(n + 1)} | {f"q{n}_fim"}
    transicoes = []

    for i, (simbolo, descricao, pode_falhar) in enumerate(etapas):
        estado_src = f"q{i}"
        estado_dst = f"q{i+1}"
        # Última etapa real: no destino ainda haverá Z na pilha
        # A transição FIM especial tirará o Z.
        transicoes.append(Transicao(
            estado_atual=estado_src,
            simbolo=simbolo,
            topo_pilha="Z",
            estado_destino=estado_dst,
            push_pilha=["Z"],   # mantém Z (pop + push de Z = não muda tamanho)
            saida=descricao,
            pode_falhar=pode_falhar,
        ))

    # Transição de encerramento: consome FIM, retira Z → pilha vazia → aceitação
    transicoes.append(Transicao(
        estado_atual=f"q{n}",
        simbolo="FIM",
        topo_pilha="Z",
        estado_destino=f"q{n}_fim",
        push_pilha=[],          # pop de Z, sem push → pilha vazia
        saida="Inspeção final e liberação do veículo ✓",
        pode_falhar=False,
    ))

    return AutomatoPilha(
        nome=nome,
        estados=estados,
        alfabeto={e[0] for e in etapas} | {"FIM"},
        alfabeto_pilha={"Z"},
        transicoes=transicoes,
        estado_inicial="q0",
        pilha_inicial=["Z"],
        estados_aceitacao={f"q{n}_fim"},
    )


def _fita(etapas: list) -> list:
    """Retorna a fita de entrada na ordem correta (inclui FIM)."""
    return [s for s, _, _ in etapas] + ["FIM"]


# ────────────────────────────────────────────────────────────────
# 1. SEDAN  (4 modelos)
# ────────────────────────────────────────────────────────────────

_SEDAN_BASE = [
    ("CHASSI",   "Estampagem e solda do chassi sedan",          True),
    ("MOTOR",    "Motor 1.0 aspirado flex",                     True),
    ("CAMBIO",   "Câmbio manual 5 marchas",                     False),
    ("ELETRICA", "Instalação elétrica básica",                  True),
    ("PINTURA",  "Pintura monocromática padrão",                False),
    ("INTERIOR", "Acabamento interno básico (tecido cinza)",    False),
]

_SEDAN_GL = _SEDAN_BASE[:4] + [
    ("DIRECAO",  "Direção hidráulica",                          True),
    ("PINTURA",  "Pintura metálica com primer extra",           False),
    ("INTERIOR", "Acabamento GL — tecido premium + console",    False),
]

_SEDAN_GLS = _SEDAN_GL[:5] + [
    ("AR",       "Ar-condicionado digital",                     True),
    ("MULTIM",   "Central multimídia 7\" + câmera de ré",       True),
    ("PINTURA",  "Pintura GLS + proteção UV",                   False),
    ("INTERIOR", "Acabamento GLS — couro sintético",            False),
]

_SEDAN_SPORT = _SEDAN_GLS[:5] + [
    ("MOTOR2",   "Upgrade motor 2.0 turbo 180cv",               True),
    ("AR",       "Ar-condicionado dual zone",                   True),
    ("MULTIM",   "Central multimídia 10\" + carregamento Qi",   True),
    ("SUSP",     "Suspensão esportiva rebaixada",                True),
    ("AEROD",    "Kit aerodônimico + rodas 18\" aro esportivo",  False),
    ("INTERIOR", "Acabamento SPORT — couro + bancos aquecidos",  False),
]


# ────────────────────────────────────────────────────────────────
# 2. SUV  (3 modelos)
# ────────────────────────────────────────────────────────────────

_SUV_ENTRY = [
    ("CHASSI",   "Chassi monocoque reforçado p/ SUV",           True),
    ("MOTOR",    "Motor 1.6 flex 130cv",                        True),
    ("CAMBIO",   "Câmbio CVT 7 velocidades",                    True),
    ("AR",       "Ar-condicionado de série",                    False),
    ("ELETRICA", "Instalação elétrica + iluminação LED DRL",    True),
    ("PINTURA",  "Pintura SUV com proteção UV",                 False),
    ("INTERIOR", "Interior Entry — tecido premium + tela 7\"",  False),
]

_SUV_AWD = _SUV_ENTRY[:4] + [
    ("TRACAO",   "Sistema de tração integral AWD eletrônico",   True),
    ("SUSP",     "Suspensão off-road com molas reforçadas",     True),
    ("ELETRICA", "Instalação elétrica ampliada",                True),
    ("PINTURA",  "Pintura metalizada bicamada",                 False),
    ("INTERIOR", "Interior AWD — couro + painel digital 12\"",  False),
]

_SUV_PREMIUM = _SUV_AWD[:7] + [
    ("MULTIM",   "Central multimídia MBUX 12\" + HUD",          True),
    ("PILOTO",   "Sistema ADAS — piloto adaptativo",            True),
    ("TETO",     "Teto solar panorâmico elétrico",              True),
    ("INTERIOR", "Interior Premium — couro Nappa + madeira",    False),
]


# ────────────────────────────────────────────────────────────────
# 3. PICKUP  (3 modelos)
# ────────────────────────────────────────────────────────────────

_PICKUP_CS = [
    ("CHASSI",   "Chassi ladder frame robusto (cabine simples)",True),
    ("MOTOR",    "Motor 2.5 diesel 150cv",                      True),
    ("CAMBIO",   "Câmbio manual 6 marchas 4x4",                 True),
    ("CACAMBA",  "Montagem e revestimento da caçamba",          False),
    ("ELETRICA", "Instalação elétrica básica",                  True),
    ("PINTURA",  "Pintura anti-ferrugem + acabamento externo",  False),
    ("INTERIOR", "Interior CS — bancos simples + rádio AM/FM",  False),
]

_PICKUP_CD = _PICKUP_CS[:3] + [
    ("CABINE",   "Extensão da carroceria para cabine dupla",    True),
    ("CACAMBA",  "Caçamba encurtada + grade separadora",        False),
    ("AR",       "Ar-condicionado digital",                     False),
    ("ELETRICA", "Instalação elétrica ampliada (4 portas)",     True),
    ("PINTURA",  "Pintura metalizada anti-ferrugem",            False),
    ("INTERIOR", "Interior CD — bancos traseiros + tela 8\"",   False),
]

_PICKUP_CDTURBO = _PICKUP_CD[:6] + [
    ("TURBO",    "Turbocompressor intercooler + recalibração",  True),
    ("ELETRICA", "Elétrica sport + iluminação Matrix LED",      True),
    ("PINTURA",  "Pintura bicamada + proteção cerâmica",        False),
    ("INTERIOR", "Interior Turbo — couro + aquecimento bancos", False),
]


# ────────────────────────────────────────────────────────────────
# 4. HATCH  (3 modelos)
# ────────────────────────────────────────────────────────────────

_HATCH_POP = [
    ("CHASSI",   "Estampagem chassi compacto hatchback",        True),
    ("MOTOR",    "Motor 1.0 8v flex 75cv",                      True),
    ("CAMBIO",   "Câmbio manual 5 marchas",                     False),
    ("ELETRICA", "Instalação elétrica básica",                  True),
    ("PINTURA",  "Pintura monocromática",                       False),
    ("INTERIOR", "Interior POP — tecido, rádio, vidros manuais",False),
]

_HATCH_CITY = _HATCH_POP[:4] + [
    ("DIRECAO",  "Direção elétrica progressiva",                True),
    ("AR",       "Ar-condicionado automático",                  False),
    ("SENSOR",   "Sensores de estacionamento dianteiros/trans.", True),
    ("PINTURA",  "Pintura CITY + friso lateral",                False),
    ("INTERIOR", "Interior CITY — premium + multimídia 8\"",    False),
]

_HATCH_RS = _HATCH_CITY[:6] + [
    ("MOTOR2",   "Motor 1.3 turbo 150cv + escape esportivo",    True),
    ("SUSP",     "Suspensão RS rebaixada + amortecedores Sachs", True),
    ("KIT",      "Kit RS: difusor, spoiler, rodas 17\" bicolor", False),
    ("INTERIOR", "Interior RS — couro + bancos tipo concha",    False),
]


# ────────────────────────────────────────────────────────────────
# CATÁLOGO PÚBLICO
# ────────────────────────────────────────────────────────────────

CATALOGO: dict[str, dict[str, tuple]] = {
    "SEDAN": {
        "BASE":  (_fazer_pda("Sedan BASE",    _SEDAN_BASE),  _fita(_SEDAN_BASE)),
        "GL":    (_fazer_pda("Sedan GL",      _SEDAN_GL),    _fita(_SEDAN_GL)),
        "GLS":   (_fazer_pda("Sedan GLS",     _SEDAN_GLS),   _fita(_SEDAN_GLS)),
        "SPORT": (_fazer_pda("Sedan SPORT",   _SEDAN_SPORT), _fita(_SEDAN_SPORT)),
    },
    "SUV": {
        "ENTRY":   (_fazer_pda("SUV ENTRY",   _SUV_ENTRY),   _fita(_SUV_ENTRY)),
        "AWD":     (_fazer_pda("SUV AWD",     _SUV_AWD),     _fita(_SUV_AWD)),
        "PREMIUM": (_fazer_pda("SUV PREMIUM", _SUV_PREMIUM), _fita(_SUV_PREMIUM)),
    },
    "PICKUP": {
        "CS":       (_fazer_pda("Pickup CS",       _PICKUP_CS),     _fita(_PICKUP_CS)),
        "CD":       (_fazer_pda("Pickup CD",       _PICKUP_CD),     _fita(_PICKUP_CD)),
        "CD-TURBO": (_fazer_pda("Pickup CD-TURBO", _PICKUP_CDTURBO),_fita(_PICKUP_CDTURBO)),
    },
    "HATCH": {
        "POP":  (_fazer_pda("Hatch POP",  _HATCH_POP),  _fita(_HATCH_POP)),
        "CITY": (_fazer_pda("Hatch CITY", _HATCH_CITY), _fita(_HATCH_CITY)),
        "RS":   (_fazer_pda("Hatch RS",   _HATCH_RS),   _fita(_HATCH_RS)),
    },
}


def get_pda(tipo: str, modelo: str) -> "AutomatoPilha":
    return CATALOGO[tipo][modelo][0]

def get_fita(tipo: str, modelo: str) -> list:
    return list(CATALOGO[tipo][modelo][1])
