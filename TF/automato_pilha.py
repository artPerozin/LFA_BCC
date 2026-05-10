"""
automato_pilha.py
Autômato com Pilha (PDA) com suporte a saídas (Mealy estendido).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class StatusProducao(Enum):
    EM_PRODUCAO = "Em Produção"
    FINALIZADO  = "Finalizado"
    FALHA       = "Falha na Produção"
    AGUARDANDO  = "Aguardando Início"


@dataclass
class Transicao:
    """
    Regra de transição: (estado_atual, simbolo, topo_pilha) →
                        (estado_destino, push_pilha, saida)
    push_pilha: símbolos a empilhar após pop. [] = só pop.
    topo_pilha: "ε" = qualquer topo.
    """
    estado_atual:   str
    simbolo:        str
    topo_pilha:     str
    estado_destino: str
    push_pilha:     list
    saida:          str  = ""
    pode_falhar:    bool = False


@dataclass
class InstanciaPDA:
    """Uma unidade de veículo sendo produzida."""
    id_veiculo:   str
    tipo_carro:   str
    modelo:       str
    estado_atual: str
    pilha:        list           = field(default_factory=list)
    historico:    list           = field(default_factory=list)
    status:       StatusProducao = StatusProducao.EM_PRODUCAO
    motivo_falha: str            = ""

    def topo(self) -> str:
        return self.pilha[-1] if self.pilha else "∅"


class AutomatoPilha:
    """PDA para um tipo/modelo de veículo."""

    def __init__(self, nome, estados, alfabeto, alfabeto_pilha,
                 transicoes, estado_inicial, pilha_inicial, estados_aceitacao):
        self.nome              = nome
        self.estados           = estados
        self.alfabeto          = alfabeto
        self.alfabeto_pilha    = alfabeto_pilha
        self.transicoes        = transicoes
        self.estado_inicial    = estado_inicial
        self.pilha_inicial     = list(pilha_inicial)
        self.estados_aceitacao = estados_aceitacao

    def nova_instancia(self, id_veiculo, tipo, modelo):
        inst = InstanciaPDA(
            id_veiculo=id_veiculo, tipo_carro=tipo, modelo=modelo,
            estado_atual=self.estado_inicial, pilha=list(self.pilha_inicial),
        )
        inst.historico.append((self.estado_inicial, f"[INÍCIO] {self.nome}"))
        return inst

    def _buscar_transicao(self, inst, simbolo):
        topo = inst.topo()
        for t in self.transicoes:
            if (t.estado_atual == inst.estado_atual and t.simbolo == simbolo
                    and (t.topo_pilha == topo or t.topo_pilha == "ε")):
                return t
        return None

    def processar_simbolo(self, inst, simbolo, falha_injetada=False):
        if inst.status != StatusProducao.EM_PRODUCAO:
            return f"[IGNORADO] {inst.id_veiculo} fora de produção."

        trans = self._buscar_transicao(inst, simbolo)
        if trans is None:
            inst.status = StatusProducao.FALHA
            inst.motivo_falha = (
                f"Sem transição p/ '{simbolo}' no estado "
                f"'{inst.estado_atual}', topo='{inst.topo()}'"
            )
            inst.historico.append((inst.estado_atual, f"[FALHA] {inst.motivo_falha}"))
            return f"[FALHA] {inst.motivo_falha}"

        if falha_injetada and trans.pode_falhar:
            inst.status = StatusProducao.FALHA
            inst.motivo_falha = f"Falha operacional: '{trans.saida}'"
            inst.historico.append(
                (inst.estado_atual, f"[FALHA OPERACIONAL] {inst.motivo_falha}"))
            return f"[FALHA OPERACIONAL] {inst.motivo_falha}"

        # pop + push
        if inst.pilha:
            inst.pilha.pop()
        for s in reversed(trans.push_pilha):
            inst.pilha.append(s)

        inst.estado_atual = trans.estado_destino
        saida = trans.saida or f"{trans.estado_atual}→{trans.estado_destino}"
        inst.historico.append((inst.estado_atual, saida))

        if inst.estado_atual in self.estados_aceitacao and not inst.pilha:
            inst.status = StatusProducao.FINALIZADO

        return f"[OK] {saida}"
