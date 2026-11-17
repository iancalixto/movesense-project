"""Script to update the master Step-by-Step Guide page in Notion ('01 · Guia Passo a Passo')."""

import time
import requests

TOKEN = "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"
GUIDE_PAGE_ID = "414e585c-5796-813a-94a5-d4d9664d6771"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def chunk_text(text: str, max_len: int = 1900) -> list[dict]:
    if not text:
        return [{"type": "text", "text": {"content": ""}}]
    chunks = [text[i : i + max_len] for i in range(0, len(text), max_len)]
    return [{"type": "text", "text": {"content": c}} for c in chunks]


def h1(text: str):
    return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": chunk_text(text)}}


def h2(text: str):
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": chunk_text(text)}}


def p(text: str):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": chunk_text(text)}}


def callout(text: str, emoji: str = "💡"):
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": emoji},
            "rich_text": chunk_text(text),
        },
    }


def bullet(text: str):
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": chunk_text(text)},
    }


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


def notion_table(rows: list[list[str]], has_column_header: bool = True) -> dict:
    table_width = len(rows[0]) if rows else 1
    children = [
        {
            "object": "block",
            "type": "table_row",
            "table_row": {
                "cells": [[{"type": "text", "text": {"content": str(cell)}}] for cell in row]
            },
        }
        for row in rows
    ]
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": table_width,
            "has_column_header": has_column_header,
            "has_row_header": False,
            "children": children,
        },
    }


def clear_non_subpage_blocks(page_id: str) -> None:
    print("Limpando blocos antigos da página principal (preservando sub-páginas)...")
    cursor = None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        resp = requests.get(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=HEADERS,
            params=params,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Erro ao ler blocos: {resp.status_code} - {resp.text}")

        data = resp.json()
        for block in data.get("results", []):
            if block["type"] == "child_page":
                continue
            del_resp = requests.delete(
                f"https://api.notion.com/v1/blocks/{block['id']}",
                headers=HEADERS,
            )
            if del_resp.status_code != 200:
                print(f"  ⚠️ Falha ao remover bloco {block['id']}: {del_resp.text}")
            time.sleep(0.1)

        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")


def append_blocks(page_id: str, blocks: list[dict]) -> None:
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    for i in range(0, len(blocks), 100):
        chunk = blocks[i : i + 100]
        resp = requests.patch(url, headers=HEADERS, json={"children": chunk})
        if resp.status_code != 200:
            raise RuntimeError(f"Erro ao anexar lote {i}: {resp.status_code} - {resp.text}")
        time.sleep(0.2)


def main():
    print("Atualizando página '01 · Guia Passo a Passo' no Notion...")

    all_blocks = [
        callout(
            "Estado Atual (11 Nov 2026): 15 etapas técnicas concluídas (DE-01 a DE-07 e DS-01 a DS-08), 30 testes automatizados verdes (make test em 4.97s), aplicação rodando em vídeo real (.mp4 e MOT17 img1/) e benchmark completo executado nas 7 sequências únicas do MOT17.",
            "🧭",
        ),
        divider(),
        h1("PARTE 1: O QUE FOI FEITO ATÉ AGORA (DE-01..DE-07 e DS-01..DS-08)"),
        p(
            "Todas as etapas abaixo foram implementadas seguindo TDD estrito (Red -> Green -> Execução), isoladas em branches feat/ ou chore/ e integradas na main. Abaixo está o mapa completo com os porquês; abra as sub-páginas no final para ver o código completo de cada arquivo."
        ),
        h2("Engenharia de Dados & Governança (DE-01 a DE-07)"),
        bullet("DE-01 · Scaffold & uv: estrutura src/movesense/, pyproject.toml, Makefile, .venv Python 3.11 e .gitignore protegendo data/, outputs_local/ e pesos."),
        bullet("DE-02 · Template de PR: .github/pull_request_template.md exigindo ID do backlog, evidência de make test e zero vazamento de dados/chaves."),
        bullet("DE-03 · Gerador Sintético MOT (step-02): src/movesense/synthetic.py gera data/synthetic/gt.txt reproduzível (seed=2026) no padrão de 9 colunas."),
        bullet("DE-04 · Renderizador OpenCV (step-04): src/movesense/render.py transforma gt.txt em vídeo .avi (MJPG, 25 FPS)."),
        bullet("DE-05 · Loader MOT Tipado (step-05): src/movesense/loader.py com load_mot_file() padronizando colunas e tipos (corrigido no DS-04 para 9 colunas exatas)."),
        bullet("DE-06 · CI no GitHub Actions: .github/workflows/ci.yml rodando make test automaticamente em cada PR/commit."),
        bullet("DE-07 · Benchmark Unificado MOT17 + MOT20 (step-13): configs/splits/mot_sequences.json + src/movesense/benchmark.py + scripts/run_mot_benchmark.py com bloqueio de leakage entre variantes DPM/FRCNN/SDP e relatórios separados por regime."),
        h2("Ciência de Dados, Tracking & Comportamento (DS-01 a DS-08)"),
        bullet("DS-01 · Detector YOLOv8 (step-06): src/movesense/detector.py filtrando classe 0 (person) e validado em imagem real (4 pedestres em bus.jpg)."),
        bullet("DS-02 · SimpleTracker IoU (step-07): src/movesense/tracker.py associando caixas entre frames (IoU >= 0.3, tolerância max_misses)."),
        bullet("DS-03 · Features Cinemáticas (step-08): src/movesense/features.py extraindo velocidade média/máxima/desvio, aceleração e raio de confinamento."),
        bullet("DS-04 · Classificador Random Forest (step-09): src/movesense/classifier.py atingindo 100% Accuracy e Macro-F1 no corpus sintético balanceado."),
        bullet("DS-05 · Métricas MOT & Propagação de Erros (step-10): src/movesense/evaluation.py (Algoritmo Húngaro) provou que ±5 px de jitter derruba % Walking de 100.0% para 0.0% mesmo com MOTA de 96.4%."),
        bullet("DS-06 · Pipeline Vídeo Real (step-11): src/movesense/pipeline.py + scripts/run_video.py processando .mp4 e img1/ em 2 passagens com uso mínimo de RAM."),
        bullet("DS-07 · Auditoria GT Real & Ablação MOT17-09 (step-12): descobertas 5.086 linhas ignoradas (48,8%) no gt.txt real; criado load_mot_gt(). Subir --conf de 0.25 -> 0.50 elevou MOTA de 34.7% para 57.2% e derrubou IDSW de 13 para 2."),
        bullet("DS-08 · Suavização Savitzky-Golay & Filtro de Micro-Tracks: smooth_trajectory(window=9) + delta real dt + min_frames=5 cortou tracks fragmentados do MOT17-09 de 53 para 11 e recuperou 5 caminhantes reais de falso RUNNING para WALKING."),
        divider(),
        h1("PARTE 2: RESULTADOS REAIS MEDIDOS (MOT17 & PROPAGAÇÃO DE ERROS)"),
        h2("1. Experimento de Propagação de Erros — Antes (Raw) vs. Depois (DS-08)"),
        notion_table([
            ["Cenário", "MOTA", "Recall", "IDSW", "Walk (Raw)", "Walk (DS-08)"],
            ["1. Ideal (Baseline)", "100.0%", "100.0%", "0", "100.0%", "40.0%*"],
            ["2. Ruído Leve (5% / 5 px)", "96.4%", "96.4%", "0", "0.0%", "80.0%"],
            ["3. Oclusão Moderada", "29.0%", "59.6%", "36", "1.8%", "60.0%"],
            ["4. Detector Degradado", "-25.4%", "22.8%", "38", "7.9%", "58.8%"],
        ]),
        h2("2. Benchmark Real nas 7 Sequências Únicas do MOT17 (make step-13 · 60 frames/cena, conf=0.50)"),
        notion_table([
            ["Dataset", "Sequência", "Split", "Câmera", "MOTA", "Precision", "Recall", "IDSW"],
            ["MOT17", "MOT17-02-FRCNN", "dev", "stationary", "17.8%", "91.7%", "19.7%", "2"],
            ["MOT17", "MOT17-04-FRCNN", "eval", "stationary", "23.0%", "88.3%", "26.9%", "10"],
            ["MOT17", "MOT17-05-FRCNN", "dev", "moving", "32.0%", "86.1%", "40.9%", "11"],
            ["MOT17", "MOT17-09-FRCNN", "dev", "stationary", "46.1%", "79.3%", "63.0%", "2"],
            ["MOT17", "MOT17-10-FRCNN", "dev", "moving", "23.7%", "92.7%", "27.4%", "18"],
            ["MOT17", "MOT17-11-FRCNN", "eval", "moving", "34.8%", "97.3%", "36.4%", "5"],
            ["MOT17", "MOT17-13-FRCNN", "eval", "moving", "22.0%", "96.9%", "23.2%", "7"],
        ]),
        notion_table([
            ["Regime Agregado", "Seqs", "Frames", "GT Boxes", "MOTA", "Precision", "Recall", "IDSW"],
            ["MOT17 Baseline", "7", "420", "8.287", "25.1%", "90.1%", "28.9%", "55"],
            ["MOT20 Stress Test", "Pendente download", "-", "-", "-", "-", "-", "-"],
        ]),
        divider(),
        h1("PARTE 3: PRÓXIMOS PASSOS E OS PORQUÊS"),
        h2("1. Baixar MOT20 e rodar Stress Test de Multidão (make step-13)"),
        bullet("O que fazer: Extrair MOT20 para data/MOT20/train/ e rodar make step-13 (sem mudar código!)."),
        bullet("Por quê: Completar a segunda linha da tabela de regimes comparando densidade normal (MOT17) vs. multidão severa (MOT20)."),
        h2("2. DS-09: Evoluir Tracker (Kalman / ByteTrack) & Normalizar Velocidade pela Altura (h)"),
        bullet("O que fazer: Substituir IoU puro em oclusões por Kalman/ByteTrack (atacar os 18 IDSW da MOT17-10 e o Recall de 28.9% testando imgsz maior / modelo S) e normalizar velocidade por px / altura_da_caixa (body-lengths/s)."),
        bullet("Por quê: Na MOT17-09, o pedestre ID #1 perto da câmera marcou 320.8 px/s (RUNNING) enquanto pedestres distantes marcaram 20–40 px/s. Normalizar pela altura elimina o viés de perspectiva 2D."),
        h2("3. Camada Real de Comportamento: Piloto JRDB-Act / VIRAT (ou subset MOT17 anotado)"),
        bullet("O que fazer: Executar o piloto de 1 sequência do JRDB-Act (validando impacto da câmera móvel 360° e 7 FPS) e manter VIRAT Ground (câmera fixa) em paralelo."),
        bullet("Por quê: MOT17 e MOT20 medem Tracking com perfeição, mas não possuem rótulos nativos de comportamento por pessoa (exigência central do MoveSense)."),
    ]

    clear_non_subpage_blocks(GUIDE_PAGE_ID)
    append_blocks(GUIDE_PAGE_ID, all_blocks)
    print(f"✅ Página '01 · Guia Passo a Passo' ({GUIDE_PAGE_ID}) atualizada com sucesso!")


if __name__ == "__main__":
    main()
