"""
fabrica.py
Motor de simulação da fábrica com linhas de produção baseadas em PDA.
"""

import random
from collections import defaultdict
from dataclasses import dataclass, field

from automato_pilha import InstanciaPDA, StatusProducao
from modelos_carros import CATALOGO, get_pda, get_fita


@dataclass
class LinhaProd:
    tipo:    str
    modelo:  str
    _count:  int = 0

    def novo_id(self) -> str:
        self._count += 1
        tipo_ab  = self.tipo[:2].upper()
        mod_ab   = self.modelo[:3].upper()
        return f"{tipo_ab}-{mod_ab}-{self._count:04d}"


class Fabrica:
    def __init__(self, nome: str, taxa_falha: float = 0.10,
                 seed: int | None = None):
        self.nome       = nome
        self.taxa_falha = taxa_falha
        self.linhas: dict[tuple, LinhaProd] = {}
        self.dia_atual  = 0
        self.historico_dias: list[dict] = []
        if seed is not None:
            random.seed(seed)

    # ── setup ──────────────────────────────────────────────────

    def _garantir_linha(self, tipo: str, modelo: str) -> LinhaProd:
        chave = (tipo, modelo)
        if chave not in self.linhas:
            self.linhas[chave] = LinhaProd(tipo=tipo, modelo=modelo)
            pda = get_pda(tipo, modelo)
            print(f"  [LINHA CRIADA] {tipo} {modelo}  —  PDA: '{pda.nome}'  "
                  f"({len(pda.transicoes)-1} etapas)")
        return self.linhas[chave]

    # ── produção de uma unidade ────────────────────────────────

    def _produzir(self, tipo: str, modelo: str,
                  linha: LinhaProd, verbose: bool) -> InstanciaPDA:
        pda  = get_pda(tipo, modelo)
        fita = get_fita(tipo, modelo)
        vid  = linha.novo_id()
        inst = pda.nova_instancia(vid, tipo, modelo)

        if verbose:
            print(f"\n  ┌─ Iniciando {vid}  [{pda.nome}]")

        for simbolo in fita:
            falha = random.random() < self.taxa_falha
            saida = pda.processar_simbolo(inst, simbolo, falha)
            if verbose:
                if "[OK]" in saida:
                    icone = "✓"
                    texto = saida[5:]
                elif "[FALHA" in saida:
                    icone = "✗"
                    texto = saida.split("] ", 1)[-1]
                else:
                    icone = "·"
                    texto = saida
                print(f"  │  [{icone}] {texto}")
            if inst.status == StatusProducao.FALHA:
                break

        if inst.status == StatusProducao.FINALIZADO:
            if verbose:
                print(f"  └─ ✅ {vid} FINALIZADO com sucesso")
        elif inst.status == StatusProducao.FALHA:
            if verbose:
                print(f"  └─ ❌ {vid} FALHOU — {inst.motivo_falha}")
        else:
            # fim de expediente: veículo incompleto
            inst.status = StatusProducao.EM_PRODUCAO
            if verbose:
                print(f"  └─ ⏸  {vid} NÃO CONCLUÍDO (fim de expediente)")

        return inst

    # ── simulação de um dia ────────────────────────────────────

    def simular_dia(self, ordens: list[tuple], verbose: bool = True) -> dict:
        """ordens: [(tipo, modelo, quantidade), ...]"""
        self.dia_atual += 1
        resumo = {
            "dia":         self.dia_atual,
            "finalizados": defaultdict(int),
            "falhas":      defaultdict(int),
            "em_producao": defaultdict(int),
            "instancias":  [],
        }

        if verbose:
            print(f"\n{'═'*64}")
            print(f"  🏭  {self.nome}  ——  DIA {self.dia_atual:02d}")
            print(f"{'═'*64}")

        for tipo, modelo, qtd in ordens:
            linha = self._garantir_linha(tipo, modelo)
            chave = f"{tipo} {modelo}"
            if verbose:
                print(f"\n▶  Linha: {tipo} {modelo}  ({qtd} un.)")
            for _ in range(qtd):
                inst = self._produzir(tipo, modelo, linha, verbose)
                resumo["instancias"].append(inst)
                if inst.status == StatusProducao.FINALIZADO:
                    resumo["finalizados"][chave] += 1
                elif inst.status == StatusProducao.FALHA:
                    resumo["falhas"][chave] += 1
                else:
                    resumo["em_producao"][chave] += 1

        self.historico_dias.append(resumo)
        return resumo

    # ── relatório de um dia ────────────────────────────────────

    def relatorio_dia(self, resumo: dict) -> str:
        sep  = "─" * 64
        sep2 = "═" * 64
        L    = []

        L.append(f"\n{sep2}")
        L.append(f"  📋  RELATÓRIO DIÁRIO — {self.nome}  |  DIA {resumo['dia']:02d}")
        L.append(sep2)

        # Finalizados
        total_fin = sum(resumo["finalizados"].values())
        L.append(f"\n  ✅  VEÍCULOS FINALIZADOS         ({total_fin} total)")
        L.append(f"  {sep}")
        if resumo["finalizados"]:
            for k, v in sorted(resumo["finalizados"].items()):
                L.append(f"       {k:<26}  {v:>3} unidade(s)")
        else:
            L.append("       Nenhum veículo finalizado neste dia.")

        # Falhas
        total_fal = sum(resumo["falhas"].values())
        L.append(f"\n  ❌  FALHAS NA PRODUÇÃO           ({total_fal} total)")
        L.append(f"  {sep}")
        if resumo["falhas"]:
            for k, v in sorted(resumo["falhas"].items()):
                L.append(f"       {k:<26}  {v:>3} unidade(s)")
            L.append(f"\n       Detalhes:")
            for inst in resumo["instancias"]:
                if inst.status == StatusProducao.FALHA:
                    L.append(f"         • {inst.id_veiculo}: {inst.motivo_falha}")
        else:
            L.append("       Nenhuma falha registrada.")

        # Incompletos
        total_ep = sum(resumo["em_producao"].values())
        L.append(f"\n  ⏸   NÃO CONCLUÍDOS (expediente)  ({total_ep} total)")
        L.append(f"  {sep}")
        if resumo["em_producao"]:
            for k, v in sorted(resumo["em_producao"].items()):
                L.append(f"       {k:<26}  {v:>3} unidade(s)")
        else:
            L.append("       Todos os veículos foram concluídos ou falharam.")

        total = total_fin + total_fal + total_ep
        taxa  = (total_fin / total * 100) if total else 0
        L.append(f"\n  {sep}")
        L.append(f"  Total processado : {total}    |    Taxa de sucesso : {taxa:.1f}%")
        L.append(sep2)

        texto = "\n".join(L)
        print(texto)
        return texto

    # ── relatório acumulado ────────────────────────────────────

    def relatorio_acumulado(self) -> str:
        sep2 = "═" * 64
        sep  = "─" * 64
        af, afa, aep = defaultdict(int), defaultdict(int), defaultdict(int)
        for r in self.historico_dias:
            for k, v in r["finalizados"].items():  af[k]  += v
            for k, v in r["falhas"].items():        afa[k] += v
            for k, v in r["em_producao"].items():   aep[k] += v

        tf, tfa, tep = sum(af.values()), sum(afa.values()), sum(aep.values())
        total = tf + tfa + tep
        taxa  = (tf / total * 100) if total else 0

        L = []
        L.append(f"\n{sep2}")
        L.append(f"  📊  RELATÓRIO ACUMULADO — {self.nome}")
        L.append(f"       Período: {self.dia_atual} dia(s)  |  "
                  f"Total geral: {total}  |  Taxa de sucesso: {taxa:.1f}%")
        L.append(sep2)

        L.append(f"\n  ✅ Finalizados: {tf}")
        for k, v in sorted(af.items()):
            pct = v / total * 100 if total else 0
            L.append(f"       {k:<26}  {v:>4}   ({pct:.1f}%)")

        L.append(f"\n  ❌ Com falha  : {tfa}")
        for k, v in sorted(afa.items()):
            pct = v / total * 100 if total else 0
            L.append(f"       {k:<26}  {v:>4}   ({pct:.1f}%)")

        L.append(f"\n  ⏸  Incompletos: {tep}")
        for k, v in sorted(aep.items()):
            pct = v / total * 100 if total else 0
            L.append(f"       {k:<26}  {v:>4}   ({pct:.1f}%)")

        L.append(f"\n{sep2}")
        texto = "\n".join(L)
        print(texto)
        return texto
