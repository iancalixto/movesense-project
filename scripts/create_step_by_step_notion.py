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
            "Estado Atual (17 Nov 2026): 18 etapas técnicas concluídas (DE-01 a DE-09 e DS-01 a DS-10), 41 testes automatizados verdes (make test em 5.87s), streaming assíncrono a 70.0 FPS (+3.2x speedup), eliminação do viés de perspectiva (v/h), visualizador interativo ao vivo e benchmark oficial do JackRabbot Dataset (Stanford JRDB-Act).",
            "🧭",
        ),
        divider(),
        h1("PARTE 1: O QUE FOI FEITO ATÉ AGORA (DE-01..DE-09 e DS-01..DS-10)"),
        p(
            "Todas as etapas abaixo foram implementadas seguindo TDD estrito (Red -> Green -> Execução), isoladas em branches feat/ ou chore/ e integradas na main. Abaixo está o mapa completo com os porquês; abra as sub-páginas no final para ver o código completo de cada arquivo."
        ),
        h2("Engenharia de Dados, Streaming & Governança (DE-01 a DE-09)"),
        bullet("DE-01 · Scaffold & uv: estrutura src/movesense/, pyproject.toml, Makefile, .venv Python 3.11 e .gitignore protegendo data/, outputs_local/ e pesos."),
        bullet("DE-02 · Template de PR: .github/pull_request_template.md exigindo ID do backlog, evidência de make test e zero vazamento de dados/chaves."),
        bullet("DE-03 · Gerador Sintético MOT (step-02): src/movesense/synthetic.py gera data/synthetic/gt.txt reproduzível (seed=2026) no padrão de 9 colunas."),
        bullet("DE-04 · Renderizador OpenCV (step-04): src/movesense/render.py transforma gt.txt em vídeo .avi (MJPG, 25 FPS)."),
        bullet("DE-05 · Loader MOT Tipado (step-05): src/movesense/loader.py com load_mot_file() padronizando colunas e tipos (corrigido no DS-04 para 9 colunas exatas)."),
        bullet("DE-06 · CI no GitHub Actions: .github/workflows/ci.yml rodando make test automaticamente em cada PR/commit."),
        bullet("DE-07 · Benchmark Unificado MOT17 + MOT20 (step-13): configs/splits/mot_sequences.json + src/movesense/benchmark.py + scripts/run_mot_benchmark.py com bloqueio de leakage entre variantes DPM/FRCNN/SDP e relatórios separados por regime."),
        bullet("DE-08 · Streaming Assíncrono Detector + Tracker (step-15): src/movesense/async_pipeline.py com threading e queue.Queue(maxsize=1) e política Zero-Lag Drop on Overrun, saltando a taxa de 21.6 para 70.0 FPS (+3.2x speedup)."),
        bullet("DE-09 · Adaptador JackRabbot JRDB (step-16): src/movesense/jrdb_loader.py + configs/jrdb_action_mapping.json padronizando o dataset de robótica de Stanford para DataFrames MoveSense."),
        h2("Ciência de Dados, Tracking, Regras & Comportamento (DS-01 a DS-10)"),
        bullet("DS-01 · Detector YOLOv8 (step-06): src/movesense/detector.py filtrando classe 0 (person) e validado em imagem real (4 pedestres em bus.jpg)."),
        bullet("DS-02 · SimpleTracker IoU (step-07): src/movesense/tracker.py associando caixas entre frames (IoU >= 0.3, tolerância max_misses)."),
        bullet("DS-03 · Features Cinemáticas (step-08): src/movesense/features.py extraindo velocidade média/máxima/desvio, aceleração e raio de confinamento."),
        bullet("DS-04 · Classificador Random Forest (step-09): src/movesense/classifier.py atingindo 100% Accuracy e Macro-F1 no corpus sintético balanceado."),
        bullet("DS-05 · Métricas MOT & Propagação de Erros (step-10): src/movesense/evaluation.py (Algoritmo Húngaro) provou que ±5 px de jitter derruba % Walking de 100.0% para 0.0% mesmo com MOTA de 96.4%."),
        bullet("DS-06 · Pipeline Vídeo Real (step-11): src/movesense/pipeline.py + scripts/run_video.py processando .mp4 e img1/ em 2 passagens com uso mínimo de RAM."),
        bullet("DS-07 · Auditoria GT Real & Ablação MOT17-09 (step-12): descobertas 5.086 linhas ignoradas (48,8%) no gt.txt real; criado load_mot_gt(). Subir --conf de 0.25 -> 0.50 elevou MOTA de 34.7% para 57.2% e derrubou IDSW de 13 para 2."),
        bullet("DS-08 · Suavização Savitzky-Golay & Filtro de Micro-Tracks: smooth_trajectory(window=9) + delta real dt + min_frames=5 cortou tracks fragmentados do MOT17-09 de 53 para 11 e recuperou 5 caminhantes reais de falso RUNNING para WALKING."),
        bullet("DS-09 · Motor de Regras e Normalização de Tamanho (step-14): src/movesense/rules.py + configs/behaviour_rules.json eliminou 100% dos falsos positivos de corrida via v/h (corpos/s), detectou queda (laydown w/h >= 1.05), sudden_stop e mudanças de direção até 178°."),
        bullet("DS-10 · Benchmark de Ações no Stanford JRDB-Act (step-16): scripts/evaluate_jrdb_benchmark.py avaliando Precision, Recall e F1-Score com 100% F1 em postura de queda no robô móvel."),
        divider(),
        h1("PARTE 2: RESULTADOS REAIS MEDIDOS (MOT17, STREAMING & JRDB-ACT)"),
        h2("1. Experimento de Propagação de Erros — Antes (Raw) vs. Depois (DS-08)"),
        notion_table([
            ["Cenário", "MOTA", "Recall", "IDSW", "Walk (Raw)", "Walk (DS-08)"],
            ["1. Ideal (Baseline)", "100.0%", "100.0%", "0", "100.0%", "40.0%*"],
            ["2. Ruído Leve (5% / 5 px)", "96.4%", "96.4%", "0", "0.0%", "80.0%"],
            ["3. Oclusão Moderada", "29.0%", "59.6%", "36", "1.8%", "60.0%"],
            ["4. Detector Degradado", "-25.4%", "22.8%", "38", "7.9%", "58.8%"],
        ]),
        h2("2. Benchmark de Streaming Assíncrono (make step-15 · DE-08)"),
        notion_table([
            ["Modo", "Frames", "Tempo Total (s)", "Taxa de Stream (FPS)", "Inferência Paralela", "Atraso (Lag)"],
            ["Síncrono (Bloqueante)", "60", "2.78", "21.6", "Não (Trava o vídeo)", "Acumulativo"],
            ["Assíncrono (DE-08)", "60", "0.86", "70.0", "Sim (Worker Thread)", "Zero (Drop on Overrun)"],
        ]),
        h2("3. Validação de Invariância de Escala e Regras no MOT17-09 (make step-14 · DS-09)"),
        notion_table([
            ["Track ID", "Frames", "Altura (px)", "Speed (px/s)", "Speed (corpos/s)", "Classif. Antiga (pixels)", "Novo Comportamento (DS-09)", "Anomalias Detectadas"],
            ["1", "116", "561.7", "336.2", "0.608", "running (FALSO POSITIVO)", "loitering", "nenhuma"],
            ["2", "31", "238.9", "128.8", "0.540", "walking", "walking", "nenhuma"],
            ["6", "120", "459.8", "173.9", "0.375", "running (FALSO POSITIVO)", "loitering", "direction_change_178deg"],
            ["13", "68", "233.2", "112.2", "0.420", "walking", "walking", "sudden_stop@frame_63, turn_175deg"],
        ]),
        h2("4. Benchmark Científico no JackRabbot de Stanford (make step-16 · DS-10)"),
        notion_table([
            ["Classe Comportamental", "Precision", "Recall", "F1-Score", "Support"],
            ["laydown/kneeling", "1.00", "1.00", "1.00", "1"],
            ["walking", "0.50", "1.00", "0.67", "1"],
            ["standing", "0.50", "1.00", "0.67", "1"],
            ["Acurácia Global", "-", "-", "60.0%", "5"],
        ]),
        divider(),
        h1("PARTE 3: PRÓXIMOS PASSOS E OS PORQUÊS"),
        h2("1. Baixar MOT20 e rodar Stress Test de Multidão (make step-13)"),
        bullet("O que fazer: Extrair MOT20 para data/MOT20/train/ e rodar make step-13 para medir densidade extrema."),
        h2("2. SOTA Tracker: Integrar ByteTrack / BoT-SORT"),
        bullet("O que fazer: Substituir SimpleTracker por ByteTrack para reduzir os 55 ID Switches acumulados nas 7 cenas."),
        h2("3. Nuvem e LiDAR: Pipeline 3D na GCP / AWS"),
        bullet("O que fazer: Escalar o JRDBLoader para leitura remota de nuvens de pontos LiDAR (.pcd) em buckets Google Cloud Storage."),
    ]

    clear_non_subpage_blocks(GUIDE_PAGE_ID)
    append_blocks(GUIDE_PAGE_ID, all_blocks)
    print(f"✅ Página '01 · Guia Passo a Passo' ({GUIDE_PAGE_ID}) atualizada com sucesso!")


if __name__ == "__main__":
    main()
