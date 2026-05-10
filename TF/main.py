"""
main.py  —  Simulação da Fábrica AutoTF
─────────────────────────────────────────────────────────────
Uso:
  python main.py                   → log completo de cada etapa
  python main.py --silencioso      → apenas relatórios finais
  python main.py --seed 42         → resultado reprodutível
  python main.py --taxa-falha 0.05 → 5% de chance de falha por etapa
─────────────────────────────────────────────────────────────
"""

import argparse
from fabrica import Fabrica


def main():
    parser = argparse.ArgumentParser(description="Fábrica de carros com PDA")
    parser.add_argument("--silencioso",  action="store_true",
                        help="Suprime log passo-a-passo; mostra só relatórios")
    parser.add_argument("--seed",       type=int,   default=7,
                        help="Semente aleatória (padrão: 7)")
    parser.add_argument("--taxa-falha", type=float, default=0.10,
                        help="Taxa de falha por etapa (padrão: 0.10)")
    args = parser.parse_args()
    verbose = not args.silencioso

    # ── Criação da fábrica ─────────────────────────────────────
    print("\n" + "═"*64)
    print("  🏭  AutoTF — Simulador de Produção com Autômatos com Pilha")
    print("  Teoria da Computação — TF Semestral")
    print("═"*64)

    fab = Fabrica(nome="AutoTF Joinville",
                  taxa_falha=args.taxa_falha,
                  seed=args.seed)

    # ── DIA 1: produção variada ────────────────────────────────
    r1 = fab.simular_dia([
        ("SEDAN",  "BASE",    2),
        ("SEDAN",  "GL",      2),
        ("SEDAN",  "GLS",     1),
        ("SEDAN",  "SPORT",   1),
        ("SUV",    "ENTRY",   2),
        ("SUV",    "AWD",     1),
        ("SUV",    "PREMIUM", 1),
        ("PICKUP", "CS",      2),
        ("PICKUP", "CD",      1),
        ("HATCH",  "POP",     3),
        ("HATCH",  "CITY",    2),
        ("HATCH",  "RS",      1),
    ], verbose=verbose)
    fab.relatorio_dia(r1)

    # ── DIA 2: foco em premium ─────────────────────────────────
    r2 = fab.simular_dia([
        ("SEDAN",  "GLS",      2),
        ("SEDAN",  "SPORT",    2),
        ("SUV",    "PREMIUM",  3),
        ("SUV",    "AWD",      2),
        ("PICKUP", "CD-TURBO", 2),
        ("PICKUP", "CD",       2),
        ("HATCH",  "RS",       2),
        ("HATCH",  "CITY",     1),
    ], verbose=verbose)
    fab.relatorio_dia(r2)

    # ── DIA 3: produção em massa de populares ──────────────────
    r3 = fab.simular_dia([
        ("HATCH",  "POP",   4),
        ("HATCH",  "CITY",  3),
        ("SEDAN",  "BASE",  3),
        ("SEDAN",  "GL",    3),
        ("PICKUP", "CS",    3),
        ("SUV",    "ENTRY", 2),
    ], verbose=verbose)
    fab.relatorio_dia(r3)

    # ── Relatório acumulado ────────────────────────────────────
    fab.relatorio_acumulado()

    # ── Exibe histórico completo de um veículo do Dia 1 ────────
    print("\n" + "═"*64)
    print("  🔍  HISTÓRICO DE ETAPAS — última unidade do Dia 1")
    print("═"*64)
    ultimo = r1["instancias"][-1]
    print(f"\n  Veículo : {ultimo.id_veiculo}")
    print(f"  Modelo  : {ultimo.tipo_carro} {ultimo.modelo}")
    print(f"  Status  : {ultimo.status.value}")
    if ultimo.motivo_falha:
        print(f"  Falha   : {ultimo.motivo_falha}")
    print(f"\n  {'Nº':>3}  {'Estado':<22}  Saída (etapa executada)")
    print(f"  {'─'*60}")
    for i, (estado, saida) in enumerate(ultimo.historico):
        print(f"  {i:>3}. [{estado:<20}]  {saida}")
    print()


if __name__ == "__main__":
    main()
