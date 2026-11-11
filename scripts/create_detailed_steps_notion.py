"""
Script to create ultra-complete, encyclopedic step-by-step reference sub-pages inside:
'01 · Guia Passo a Passo: O que foi Feito, Objetivos e Próximos Passos (com os Porquês)'
in Notion for each milestone (DE-01 through DS-03), reading the exact live source code
of every file created in each step for future consultation.
"""

import pathlib
import time
import requests

TOKEN = "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"
PARENT_PAGE_ID = "414e585c-5796-813a-94a5-d4d9664d6771"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

ROOT = pathlib.Path(__file__).resolve().parent.parent


def read_repo_file(rel_path: str) -> str:
    p = ROOT / rel_path
    if not p.exists():
        return f"# [Arquivo não encontrado: {rel_path}]"
    return p.read_text(encoding="utf-8")


def chunk_text(text: str, max_len: int = 1900) -> list[dict]:
    if not text:
        return [{"type": "text", "text": {"content": ""}}]
    chunks = [text[i : i + max_len] for i in range(0, len(text), max_len)]
    return [{"type": "text", "text": {"content": c}} for c in chunks]


def h1(text: str):
    return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": chunk_text(text)}}


def h2(text: str):
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": chunk_text(text)}}


def h3(text: str):
    return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": chunk_text(text)}}


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


def code(content: str, language: str = "plain text"):
    return {
        "object": "block",
        "type": "code",
        "code": {
            "language": language,
            "rich_text": chunk_text(content),
        },
    }


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


def archive_existing_subpages():
    print("Limpando versões anteriores das sub-páginas para evitar duplicatas...")
    url = f"https://api.notion.com/v1/blocks/{PARENT_PAGE_ID}/children"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        for block in resp.json().get("results", []):
            if block["type"] == "child_page":
                cid = block["id"]
                ctitle = block["child_page"]["title"]
                del_resp = requests.patch(
                    f"https://api.notion.com/v1/pages/{cid}",
                    headers=HEADERS,
                    json={"archived": True},
                )
                if del_resp.status_code == 200:
                    print(f"  🗑️ Arquivada página antiga: {ctitle}")
                time.sleep(0.2)


def create_child_page(title: str, icon_emoji: str, blocks: list):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"page_id": PARENT_PAGE_ID},
        "icon": {"type": "emoji", "emoji": icon_emoji},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": title}}]}
        },
        "children": blocks[:100],
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        page_id = resp.json()["id"]
        print(f"✅ Criada página completa: '{title}' (ID: {page_id})")
        if len(blocks) > 100:
            url_append = f"https://api.notion.com/v1/blocks/{page_id}/children"
            for i in range(100, len(blocks), 100):
                chunk = blocks[i : i + 100]
                resp_app = requests.patch(url_append, headers=HEADERS, json={"children": chunk})
                if resp_app.status_code != 200:
                    print(f"❌ Erro ao anexar lote {i}: {resp_app.status_code} - {resp_app.text}")
        time.sleep(0.3)
    else:
        print(f"❌ Erro ao criar '{title}': {resp.status_code} - {resp.text}")


def main():
    archive_existing_subpages()
    print("\nIniciando publicação da enciclopédia completa de passos no Notion...")

    # =========================================================================
    # 1. DE-01: Scaffold e uv
    # =========================================================================
    de01_blocks = [
        callout("DE-01 · Guia de Referência Completa: Scaffold do Projeto, Layout src/, Gerenciador uv e Primeiros Testes.", "🏗️"),
        divider(),
        h1("1. Por que fizemos este passo? (Objetivo Científico & Engenharia)"),
        p("Em projetos acadêmicos e profissionais de Ciência de Dados, o maior inimigo é o famoso 'na minha máquina funciona'. Ao estruturar o projeto como um pacote Python instalável (layout src/) gerenciado pelo uv (Rust) com ambiente virtual isolado (.venv), garantimos que qualquer integrante do grupo (Daniel, Ian, Leon, Jonas, Tamino) ou servidor na nuvem rode exatamente as mesmas versões com determinismo."),
        h1("2. Passo a Passo no Terminal (Como reproduzir do zero)"),
        code(
"""# 1. Criar branch de feature a partir da main
git checkout -b chore/DE-01-scaffold

# 2. Criar ambiente virtual Python 3.11 isolado usando uv
uv venv --python 3.11
source .venv/bin/activate

# 3. Instalar pacote local em modo editável (-e) com dependências de desenvolvimento
uv pip install -e ".[dev]"

# 4. Rodar o primeiro teste de fumaça
python -m pytest tests/test_imports.py""",
            "shell",
        ),
        h1("3. Arquivos Criados e Códigos Completos"),
        h2("📄 pyproject.toml"),
        p("Arquivo mestre de metadados, dependências do projeto (numpy, pandas, opencv, scikit-learn, ultralytics) e configuração do pytest."),
        code(read_repo_file("pyproject.toml"), "toml"),
        h2("📄 .gitignore"),
        p("Protege o repositório contra vazamento de vídeos pesados (data/), pesos de redes neurais (*.pt, *.onnx), caches Python e arquivos de sistema."),
        code(read_repo_file(".gitignore"), "plain text"),
        h2("📄 src/movesense/__init__.py"),
        p("Marca a pasta movesense como pacote Python oficial e define a versão atual."),
        code(read_repo_file("src/movesense/__init__.py"), "python"),
        h2("📄 tests/test_imports.py"),
        p("Smoke test inicial para provar que o pacote movesense foi instalado corretamente no ambiente virtual."),
        code(read_repo_file("tests/test_imports.py"), "python"),
        h2("📄 Makefile (Versão Inicial)"),
        code(
""".PHONY: install test

install:
\tuv pip install -e ".[dev]"

test:
\tpython -m pytest -q""",
            "makefile",
        ),
        h1("4. Resultado e Validação"),
        bullet("28 pacotes instalados em 1.02 segundos com uv."),
        bullet("1 teste verde aprovado (tests/test_imports.py)."),
        bullet("PR #1 mergeado na main."),
    ]
    create_child_page("DE-01 · Scaffold do Projeto e Gerenciamento com uv", "🏗️", de01_blocks)

    # =========================================================================
    # 2. DE-02: PR Template
    # =========================================================================
    de02_blocks = [
        callout("DE-02 · Guia de Referência Completa: Governança de Código e Template de Pull Request.", "📋"),
        divider(),
        h1("1. Por que fizemos este passo?"),
        p("Para garantir controle de qualidade e rastreabilidade em equipe. O template obriga todo colaborador a vincular o número da tarefa (Backlog ID), resumir o que mudou, comprovar que os testes passaram (make test) e garantir que nenhum dataset ou chave secreta foi incluído no commit."),
        h1("2. Passo a Passo no Terminal"),
        code(
"""git checkout -b chore/DE-02-pr-template
mkdir -p .github
# Criar .github/pull_request_template.md
git add .github/pull_request_template.md
git commit -m "chore: add standardized pull request template (DE-02)"
git push origin chore/DE-02-pr-template""",
            "shell",
        ),
        h1("3. Arquivo Criado e Código Completo"),
        h2("📄 .github/pull_request_template.md"),
        code(read_repo_file(".github/pull_request_template.md"), "markdown"),
        h1("4. Resultado e Validação"),
        bullet("Todos os Pull Requests abertos no GitHub a partir do PR #2 exibiram automaticamente o formulário de auditoria."),
    ]
    create_child_page("DE-02 · Template Padronizado de Pull Request", "📋", de02_blocks)

    # =========================================================================
    # 3. DE-03: Synthetic Generator
    # =========================================================================
    de03_blocks = [
        callout("DE-03 · Guia de Referência Completa: Gerador Sintético de Trajetórias MOT (gt.txt) via TDD.", "🧪"),
        divider(),
        h1("1. Por que fizemos este passo?"),
        p("Datasets reais de vídeo (como MOT17) têm gigabytes de tamanho. Criar um gerador sintético matemático com semente determinística (seed=2026) nos permite testar o pipeline completo de ponta a ponta em milissegundos, offline, tanto no notebook local quanto na nuvem do GitHub Actions."),
        h1("2. Passo a Passo (Ciclo TDD Red -> Green -> Refactor)"),
        code(
"""# 1. Criar branch
git checkout -b feat/DE-03-synthetic-generator

# 2. FASE RED: Escrever tests/test_synthetic.py primeiro e ver falhar
python -m pytest tests/test_synthetic.py  # -> ModuleNotFoundError

# 3. FASE GREEN: Implementar src/movesense/synthetic.py e ver passar
python -m pytest  # -> 3 passed

# 4. FASE EXECUTION: Criar scripts/generate_synthetic.py e rodar
make step-02""",
            "shell",
        ),
        h1("3. Arquivos Criados e Códigos Completos"),
        h2("📄 tests/test_synthetic.py (Contrato de Testes)"),
        p("Garante que o arquivo gt.txt é gerado e que cada linha contém exatamente as 9 colunas do padrão oficial MOTChallenge."),
        code(read_repo_file("tests/test_synthetic.py"), "python"),
        h2("📄 src/movesense/synthetic.py (Módulo Gerador)"),
        p("Simula trajetórias de pedestres com velocidade inicial e ruído gaussiano aleatório controlado (random walk) dentro da resolução 1920x1080."),
        code(read_repo_file("src/movesense/synthetic.py"), "python"),
        h2("📄 scripts/generate_synthetic.py (Script CLI)"),
        p("Script executável que instancia a função para gerar 5 pedestres ao longo de 100 frames em data/synthetic/gt.txt."),
        code(read_repo_file("scripts/generate_synthetic.py"), "python"),
        h1("4. Resultado e Validação"),
        bullet("Arquivo data/synthetic/gt.txt criado com 500 linhas válidas (5 pedestres × 100 frames)."),
        bullet("Suíte de testes: 3 testes verdes aprovados."),
    ]
    create_child_page("DE-03 · Gerador Sintético de Trajetórias MOT (gt.txt)", "🧪", de03_blocks)

    # =========================================================================
    # 4. DE-04: Video Renderer
    # =========================================================================
    de04_blocks = [
        callout("DE-04 · Guia de Referência Completa: Renderizador de Vídeo Sintético com OpenCV (.avi).", "🎬"),
        divider(),
        h1("1. Por que fizemos este passo?"),
        p("Redes neurais de detecção espacial (como YOLOv8 e RT-DETR) recebem frames de imagem/vídeo (matrizes NumPy RGB/BGR) e não tabelas de texto. Este módulo lê as caixas delimitadoras do gt.txt e desenha visualmente um arquivo de vídeo .avi em Full HD usando OpenCV."),
        h1("2. Passo a Passo (Ciclo TDD)"),
        code(
"""git checkout -b feat/DE-04-synthetic-video
# Escrever tests/test_render.py (RED) -> implementar src/movesense/render.py (GREEN)
python -m pytest
make step-04  # Renderiza data/synthetic/synthetic_video.avi""",
            "shell",
        ),
        h1("3. Arquivos Criados e Códigos Completos"),
        h2("📄 tests/test_render.py"),
        p("Valida se o arquivo .avi é gerado, possui mais de 0 bytes, pode ser aberto pelo cv2.VideoCapture e contém o número exato de frames esperado."),
        code(read_repo_file("tests/test_render.py"), "python"),
        h2("📄 src/movesense/render.py"),
        p("Usa cv2.VideoWriter com codec MJPG, fundo cinza escuro, estampa o timestamp do frame e desenha as bounding boxes verdes com o ID de cada pedestre."),
        code(read_repo_file("src/movesense/render.py"), "python"),
        h2("📄 scripts/render_video.py"),
        code(read_repo_file("scripts/render_video.py"), "python"),
        h1("4. Resultado e Validação"),
        bullet("Vídeo data/synthetic/synthetic_video.avi (2.5 MB, 100 frames, 1920x1080 @ 25 FPS) gerado com sucesso."),
        bullet("Suíte de testes: 4 testes verdes aprovados."),
    ]
    create_child_page("DE-04 · Renderizador de Vídeo Sintético com OpenCV (.avi)", "🎬", de04_blocks)

    # =========================================================================
    # 5. DE-05: MOT Loader
    # =========================================================================
    de05_blocks = [
        callout("DE-05 · Guia de Referência Completa: Loader MOT Tipado e Validação de Esquema com Pandas.", "📊"),
        divider(),
        h1("1. Por que fizemos este passo?"),
        p("Padroniza a leitura de arquivos no formato MOTChallenge em um DataFrame Pandas tipado. Evita que scripts futuros façam parsing frágil de texto e resolve integralmente o Issue #8 do GitLab ('Einheitliches Datenformat und Dataset-Loader implementieren')."),
        h1("2. Passo a Passo (Ciclo TDD)"),
        code(
"""git checkout -b feat/DE-05-mot-loader
python -m pytest tests/test_loader.py
make step-05  # Roda inspeção executiva do dataset""",
            "shell",
        ),
        h1("3. Arquivos Criados e Códigos Completos"),
        h2("📄 tests/test_loader.py"),
        p("Testa a integridade das 9 colunas canônicas, tipos numéricos (int/float) e o lançamento de FileNotFoundError para arquivos inexistentes."),
        code(read_repo_file("tests/test_loader.py"), "python"),
        h2("📄 src/movesense/loader.py"),
        p("Define MOT_COLUMNS = ['frame', 'id', 'x', 'y', 'w', 'h', 'conf', 'class_id', 'visibility'] e ordena automaticamente por frame e id."),
        code(read_repo_file("src/movesense/loader.py"), "python"),
        h2("📄 scripts/inspect_dataset.py"),
        code(read_repo_file("scripts/inspect_dataset.py"), "python"),
        h1("4. Resultado e Validação"),
        bullet("Inspeção confirmou: 500 detecções, 100 frames, 5 pedestres únicos (IDs [1, 2, 3, 4, 5])."),
        bullet("Suíte de testes: 6 testes verdes aprovados."),
    ]
    create_child_page("DE-05 · Loader MOT Tipado com Validação de Esquema (Pandas)", "📊", de05_blocks)

    # =========================================================================
    # 6. DE-06: CI GitHub Actions
    # =========================================================================
    de06_blocks = [
        callout("DE-06 · Guia de Referência Completa: Integração Contínua (CI) Automatizada na Nuvem.", "🤖"),
        divider(),
        h1("1. Por que fizemos este passo?"),
        p("Qualquer Pull Request ou push na branch principal precisa ser auditado por um ambiente limpo e imparcial. O GitHub Actions sobe uma máquina virtual Linux (Ubuntu), instala o uv, cria o ambiente Python 3.11, instala o projeto e executa toda a suíte pytest automaticamente."),
        h1("2. Passo a Passo"),
        code(
"""git checkout -b chore/DE-06-ci
mkdir -p .github/workflows
# Criar .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "chore: setup GitHub Actions CI pipeline with uv (DE-06)" """,
            "shell",
        ),
        h1("3. Arquivo Criado e Código Completo"),
        h2("📄 .github/workflows/ci.yml"),
        code(read_repo_file(".github/workflows/ci.yml"), "yaml"),
        h1("4. Resultado e Validação"),
        bullet("Pipeline verde rodando na nuvem do GitHub em ~13 segundos a cada PR."),
        bullet("Protege o repositório contra regressões de código."),
    ]
    create_child_page("DE-06 · Integração Contínua (CI) com GitHub Actions", "🤖", de06_blocks)

    # =========================================================================
    # 7. DS-01: YOLO Detector
    # =========================================================================
    ds01_blocks = [
        callout("DS-01 · Guia de Referência Completa: Detector de Pedestres YOLOv8 (Deep Learning).", "👁️"),
        divider(),
        h1("1. Por que fizemos este passo?"),
        p("Integra o detector de objetos em passo único (YOLOv8n, 3.2M parâmetros) focado na detecção de pedestres (classe 0 'person' no dataset COCO). Resolve o Issue #9 do GitLab ('X Detektoren auswählen') e serve como referência de detector Edge compatível com Raspberry Pi 5 + Hailo-8L."),
        h1("2. Passo a Passo (Ciclo TDD + Diagnóstico Empírico)"),
        code(
"""git checkout -b feat/DS-01-yolo-detector
# 1. RED: Escrever tests/test_detector.py -> ModuleNotFoundError
python -m pytest tests/test_detector.py
# 2. GREEN: Implementar src/movesense/detector.py -> 3 passed
python -m pytest tests/test_detector.py
# 3. EXECUTION: Criar scripts/run_detector.py e make step-06
make step-06""",
            "shell",
        ),
        h1("3. Arquivos Criados e Códigos Completos"),
        h2("📄 tests/test_detector.py"),
        code(read_repo_file("tests/test_detector.py"), "python"),
        h2("📄 src/movesense/detector.py"),
        p("Define a dataclass Detection(x, y, w, h, conf) e a classe PedestrianDetector que carrega o modelo YOLO, filtra apenas cls_id == 0 (person) e converte coordenadas de xyxy para xywh."),
        code(read_repo_file("src/movesense/detector.py"), "python"),
        h2("📄 scripts/run_detector.py"),
        code(read_repo_file("scripts/run_detector.py"), "python"),
        h1("4. Descoberta Científica Importante (Vídeo Sintético vs Foto Real)"),
        bullet("No vídeo sintético (apenas caixas verdes retangulares desenhadas), o YOLO retornou 0 detecções — provando que a rede neural treinada em imagens reais exige anatomia/texturas humanas e não alucina pessoas em figuras geométricas."),
        bullet("Ao rodar na foto real de rua de Sevilha (ultralytics/assets/bus.jpg), o detector identificou perfeitamente 4 pedestres com confianças de 86.5%, 85.4%, 82.5% e 26.7%, salvando visualização em outputs_local/detected_pedestrians.jpg."),
        bullet("Suíte completa: 9 testes verdes aprovados."),
    ]
    create_child_page("DS-01 · Detector de Pedestres YOLOv8 (Ultralytics)", "👁️", ds01_blocks)

    # =========================================================================
    # 8. DS-02: IoU Tracker
    # =========================================================================
    ds02_blocks = [
        callout("DS-02 · Guia de Referência Completa: Rastreador Multi-Objeto Temporal com IoU.", "🎯"),
        divider(),
        h1("1. Por que fizemos este passo?"),
        p("Um detector sofre de 'amnésia frame a frame': ele encontra caixas isoladas, mas não sabe quem é quem entre o frame t e t+1. O Tracker dá memória temporal ao sistema usando sobreposição geométrica IoU (Intersection over Union) e controle de tolerância a falhas (max_misses) para preservar os IDs dos pedestres no tempo."),
        h1("2. Passo a Passo (Ciclo TDD)"),
        code(
"""git checkout -b feat/DS-02-iou-tracker
# 1. RED: Escrever tests/test_tracker.py -> ModuleNotFoundError
python -m pytest tests/test_tracker.py
# 2. GREEN: Implementar src/movesense/tracker.py -> 3 passed
python -m pytest tests/test_tracker.py
# 3. EXECUTION: Criar scripts/run_tracker.py e make step-07
make step-07""",
            "shell",
        ),
        h1("3. Arquivos Criados e Códigos Completos"),
        h2("📄 tests/test_tracker.py"),
        code(read_repo_file("tests/test_tracker.py"), "python"),
        h2("📄 src/movesense/tracker.py"),
        code(read_repo_file("src/movesense/tracker.py"), "python"),
        h2("📄 scripts/run_tracker.py"),
        code(read_repo_file("scripts/run_tracker.py"), "python"),
        h1("4. Resultado e Validação"),
        bullet("Processou 100 frames a quase 28.000 iterações/s."),
        bullet("Identificou e manteve os 5 pedestres únicos (IDs [1, 2, 3, 4, 5]) com 0 trocas de identidade (ID switches)."),
        bullet("Gerou o arquivo oficial data/synthetic/tracks.txt no formato MOTChallenge."),
        bullet("Suíte completa: 12 testes verdes aprovados."),
    ]
    create_child_page("DS-02 · Tracker de Pedestres (Associação Espacial IoU)", "🎯", ds02_blocks)

    # =========================================================================
    # 9. DS-03: Trajectory Features
    # =========================================================================
    ds03_blocks = [
        callout("DS-03 · Guia de Referência Completa: Extrator de Features Cinemáticas de Trajetória.", "📈"),
        divider(),
        h1("1. Por que fizemos este passo?"),
        p("Modelos clássicos de Machine Learning (Random Forest, SVM, XGBoost) não entendem coordenadas soltas de caixas ao longo do tempo. Este módulo transforma cada trajetória em variáveis físicas concretas da cinemática: velocidade linear média/máxima (px/s), aceleração (px/s²) e raio de confinamento espacial (dwell radius), permitindo classificar comportamentos como standing, walking, running e loitering."),
        h1("2. Passo a Passo (Ciclo TDD)"),
        code(
"""git checkout -b feat/DS-03-trajectory-features
# 1. RED: Escrever tests/test_features.py -> ModuleNotFoundError
python -m pytest tests/test_features.py
# 2. GREEN: Implementar src/movesense/features.py -> 3 passed
python -m pytest tests/test_features.py
# 3. EXECUTION: Criar scripts/extract_features.py e make step-08
make step-08""",
            "shell",
        ),
        h1("3. Arquivos Criados e Códigos Completos"),
        h2("📄 tests/test_features.py"),
        code(read_repo_file("tests/test_features.py"), "python"),
        h2("📄 src/movesense/features.py"),
        code(read_repo_file("src/movesense/features.py"), "python"),
        h2("📄 scripts/extract_features.py"),
        code(read_repo_file("scripts/extract_features.py"), "python"),
        h2("📄 Makefile (Versão Consolidada até DS-03)"),
        code(read_repo_file("Makefile"), "makefile"),
        h1("4. Resultado e Validação"),
        bullet("Extraiu a tabela tabular completa de features e salvou em data/synthetic/trajectory_features.csv."),
        bullet("Suíte completa: 15 testes verdes aprovados em 3.48s."),
        bullet("Branch mergeada com sucesso na main!"),
    ]
    create_child_page("DS-03 · Extrator de Features Cinemáticas de Trajetória", "📈", ds03_blocks)

    print("\n🎉 Todas as 9 páginas enciclopédicas completas foram atualizadas no Notion com código integral!")


if __name__ == "__main__":
    main()
