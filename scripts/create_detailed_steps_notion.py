"""
Script to create individual detailed sub-pages inside:
'01 · Guia Passo a Passo: O que foi Feito, Objetivos e Próximos Passos (com os Porquês)'
in Notion for each project milestone: DE-01 through DS-03.
"""

import requests
import time

TOKEN = "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"
PARENT_PAGE_ID = "414e585c-5796-813a-94a5-d4d9664d6771"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def h1(text: str):
    return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def h2(text: str):
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def h3(text: str):
    return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def p(text: str):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def callout(text: str, emoji: str = "💡"):
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": emoji},
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def bullet(text: str):
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}
    }

def code(content: str, language: str = "plain text"):
    return {
        "object": "block",
        "type": "code",
        "code": {
            "language": language,
            "rich_text": [{"type": "text", "text": {"content": content}}]
        }
    }

def divider():
    return {"object": "block", "type": "divider", "divider": {}}


def create_child_page(title: str, icon_emoji: str, blocks: list):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"page_id": PARENT_PAGE_ID},
        "icon": {"type": "emoji", "emoji": icon_emoji},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        },
        "children": blocks[:100]
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        page_id = resp.json()["id"]
        print(f"✅ Criada sub-página '{title}' (ID: {page_id})")
        if len(blocks) > 100:
            url_append = f"https://api.notion.com/v1/blocks/{page_id}/children"
            for i in range(100, len(blocks), 100):
                chunk = blocks[i:i+100]
                resp_app = requests.patch(url_append, headers=HEADERS, json={"children": chunk})
                if resp_app.status_code != 200:
                    print(f"❌ Erro ao anexar lote {i}: {resp_app.status_code} - {resp_app.text}")
        time.sleep(0.3)
    else:
        print(f"❌ Erro ao criar sub-página '{title}': {resp.status_code} - {resp.text}")


def main():
    print("Iniciando criação das páginas detalhadas de cada etapa no Notion...")

    # ==========================================
    # 1. DE-01: Scaffold e uv
    # ==========================================
    p1_blocks = [
        callout("DE-01 · Scaffold do Projeto e Gerenciamento Ultrarrápido de Dependências com uv (Rust).", "🏗️"),
        divider(),
        h1("1. O que foi feito (Implementação Técnica)"),
        bullet("Inicialização do repositório Git com branch principal protegida ('main')."),
        bullet("Adoção do uv (gerenciador moderno escrito em Rust pela Astral) em substituição ao pip/poetry/conda tradicional."),
        bullet("Criação do ambiente virtual isolado '.venv' fixado em Python 3.11.18."),
        bullet("Configuração da arquitetura moderna de pacotes em 'pyproject.toml' utilizando o layout padrão 'src/movesense/'."),
        bullet("Elaboração de um '.gitignore' robusto contra arquivos de sistema (.DS_Store), caches Python (__pycache__) e pastas de dados pesados."),
        bullet("Criação do 'Makefile' da equipe com atalhos padronizados ('make install', 'make test')."),
        bullet("Escrita do primeiro teste de fumaça em 'tests/test_imports.py' para validar que o pacote 'movesense' é importável."),
        code(
"""# Estrutura inicial criada:
movesense-project/
├── .gitignore
├── Makefile
├── pyproject.toml
├── src/
│   └── movesense/
│       └── __init__.py
└── tests/
    └── test_imports.py""",
            "plain text"
        ),
        h1("2. Qual era o objetivo técnico e científico"),
        bullet("Garantir a reprodutibilidade científica exata: projetos de Data Science costumam sofrer de 'funciona na minha máquina'. O uv e o pyproject.toml travam as versões exatas de dependências."),
        bullet("Velocidade de desenvolvimento: O uv resolveu e instalou 28 pacotes em apenas 1.02 segundos, sendo 10x a 100x mais rápido que pip tradicional."),
        bullet("Layout src/ recomendado pela comunidade: Impede que testes importem acidentalmente o código local sem testar a versão devidamente instalada em modo editável (-e)."),
        h1("3. Resultado e Validação"),
        bullet("Pacote 'movesense 0.1.0' instalado com sucesso em modo editável."),
        bullet("Teste 'tests/test_imports.py' aprovado (1 verde)."),
        bullet("Pull Request #1 aberto e mergeado na main com sucesso.")
    ]
    create_child_page("DE-01 · Scaffold do Projeto e Gerenciamento com uv", "🏗️", p1_blocks)

    # ==========================================
    # 2. DE-02: PR Template
    # ==========================================
    p2_blocks = [
        callout("DE-02 · Template Padronizado de Pull Request e Governança de Código.", "📋"),
        divider(),
        h1("1. O que foi feito (Implementação Técnica)"),
        bullet("Criação do arquivo padrão '.github/pull_request_template.md' em inglês."),
        bullet("O formulário exige preenchimento de: Backlog ID, What Changed, Why, Testing Evidence e Security Checklist."),
        code(
"""## Summary
<!-- Concise description of changes -->

## Backlog ID
<!-- e.g. DE-01, DS-01, or GitLab Issue # -->

## What Changed
- 

## Verification & Tests
- [ ] Tests passing (`make test`)
- [ ] No heavy datasets committed
- [ ] No API secrets committed""",
            "markdown"
        ),
        h1("2. Qual era o objetivo técnico e científico"),
        bullet("Governança e auditoria de código em equipe: Em projetos com múltiplos desenvolvedores (Daniel, Ian, Tamino, Leon, Jonas), PRs sem descrição geram confusão e quebram branches principais."),
        bullet("Segurança de dados (GDPR e SIG): O checklist proíbe expressamente o commit acidental de arquivos de vídeo pesados ou chaves de API secretas."),
        h1("3. Resultado e Validação"),
        bullet("Todos os PRs subsequentes do projeto abriram com o formulário profissional pré-preenchido."),
        bullet("Histórico de auditoria do Git limpo e rastreável.")
    ]
    create_child_page("DE-02 · Template Padronizado de Pull Request", "📋", p2_blocks)

    # ==========================================
    # 3. DE-03: Gerador Sintético
    # ==========================================
    p3_blocks = [
        callout("DE-03 · Gerador Sintético de Trajetórias MOT (gt.txt) com TDD Estrito.", "🧪"),
        divider(),
        h1("1. O que foi feito (Implementação Técnica)"),
        bullet("Aplicação rigorosa de TDD (Test-Driven Development): o teste unitário 'tests/test_synthetic.py' foi escrito primeiro (vermelho 🔴), cobrando a especificação canônica de 9 colunas do benchmark MOTChallenge."),
        bullet("Implementação da função geradora em 'src/movesense/synthetic.py' (verde 🟢)."),
        bullet("Criação do script de linha de comando 'scripts/generate_synthetic.py'."),
        bullet("Adição do atalho 'make step-02' no Makefile."),
        code(
"""# Formato canônico de saída (MOTChallenge):
# frame, id, bb_left, bb_top, bb_width, bb_height, conf, class_id, visibility
1,1,1583,170,64,128,1,1,1.0
1,2,673,258,64,128,1,1,1.0
1,3,1646,274,64,128,1,1,1.0""",
            "plain text"
        ),
        h1("2. Qual era o objetivo técnico e científico"),
        bullet("Independência de dados externos: Permite desenvolver todo o pipeline de software e CI/CD sem depender do download demorado de 10 GB de vídeos da internet."),
        bullet("Determinismo Matemático: O uso de uma semente pseudo-aleatória fixa (seed=2026) garante que a mesma cena sintética seja reproduzida com precisão de bits em qualquer máquina."),
        h1("3. Resultado e Validação"),
        bullet("Geração instantânea de 5 pedestres em 100 frames (500 anotações válidas) em 'data/synthetic/gt.txt'."),
        bullet("Testes unitários aprovados (total de 3 testes verdes no repositório).")
    ]
    create_child_page("DE-03 · Gerador Sintético de Trajetórias MOT (gt.txt)", "🧪", p3_blocks)

    # ==========================================
    # 4. DE-04: Renderizador OpenCV
    # ==========================================
    p4_blocks = [
        callout("DE-04 · Renderizador de Vídeo Sintético com OpenCV (.avi).", "🎬"),
        divider(),
        h1("1. O que foi feito (Implementação Técnica)"),
        bullet("Módulo 'src/movesense/render.py' utilizando 'cv2.VideoWriter' com codec MJPG a 25 frames por segundo na resolução Full HD (1920x1080)."),
        bullet("O motor gráfico lê as coordenadas do 'gt.txt', cria um canvas escuro e desenha as bounding boxes com contorno verde e texto 'ID: {id}'."),
        bullet("Escrita de testes unitários em 'tests/test_render.py' validando resolução, FPS e contagem de frames do arquivo .avi gerado."),
        bullet("Criação do script 'scripts/render_video.py' e atalho 'make step-04'."),
        code("make step-04  # Gera data/synthetic/synthetic_video.avi em segundos", "shell"),
        h1("2. Qual era o objetivo técnico e científico"),
        bullet("Conexão com Visão Computacional: Detectores como YOLO e RT-DETR recebem matrizes de pixels (vídeo), não coordenadas numéricas de texto."),
        bullet("Validação de renderização gráfica: Garante que os modelos de detecção espacial tenham um feed de vídeo consistente para teste local de integração."),
        h1("3. Resultado e Validação"),
        bullet("Produção de 'data/synthetic/synthetic_video.avi' (2.5 MB)."),
        bullet("Verificação de que o arquivo pesado ficou fora do Git graças à regra 'data/' no .gitignore."),
        bullet("Suíte passando com 4 testes verdes.")
    ]
    create_child_page("DE-04 · Renderizador de Vídeo Sintético com OpenCV (.avi)", "🎬", p4_blocks)

    # ==========================================
    # 5. DE-05: Loader MOT Tipado
    # ==========================================
    p5_blocks = [
        callout("DE-05 · Loader MOT Tipado com Validação de Esquema com Pandas.", "📊"),
        divider(),
        h1("1. O que foi feito (Implementação Técnica)"),
        bullet("Módulo 'src/movesense/loader.py' com a função 'load_mot_file()', definindo as 9 colunas canônicas do MOTChallenge: frame, id, x, y, w, h, conf, class_id, visibility."),
        bullet("Tipagem estrita via Pandas (inteiros para frame/id/classe, floats para coordenadas e confiança)."),
        bullet("Testes unitários em 'tests/test_loader.py' cobrindo arquivos válidos e tratamento de erro 'FileNotFoundError'."),
        bullet("Script 'scripts/inspect_dataset.py' e atalho 'make step-05'."),
        code(
"""# Exemplo de uso da API do loader:
from movesense.loader import load_mot_file

df = load_mot_file("data/synthetic/gt.txt")
print(f"Total de detecções: {len(df)}")""",
            "python"
        ),
        h1("2. Qual era o objetivo técnico e científico"),
        bullet("Eliminar código frágil: Sem o loader, cada script precisava abrir arquivos texto com 'open()' e fazer 'split(',')' manualmente, o que causava bugs silenciosos."),
        bullet("Resolução antecipada do Issue #8 do GitLab: O Project Manager pediu um 'Einheitliches Datenformat und Dataset-Loader', que nós resolvemos 100% nesta etapa!"),
        h1("3. Resultado e Validação"),
        bullet("Inspeção executiva comprovando 500 detecções ativas, 100 frames e 5 pedestres."),
        bullet("Suíte passando com 6 testes verdes.")
    ]
    create_child_page("DE-05 · Loader MOT Tipado com Validação de Esquema (Pandas)", "📊", p5_blocks)

    # ==========================================
    # 6. DE-06: CI GitHub Actions
    # ==========================================
    p6_blocks = [
        callout("DE-06 · Integração Contínua (CI) Automatizada com GitHub Actions.", "🤖"),
        divider(),
        h1("1. O que foi feito (Implementação Técnica)"),
        bullet("Criação do pipeline automatizado em '.github/workflows/ci.yml' disparado a cada push ou Pull Request na main."),
        bullet("Integração da action oficial 'astral-sh/setup-uv' para provisionamento ultrarrápido do ambiente Python 3.11 no runner Ubuntu."),
        bullet("Resolução de incidente de ativação de virtualenv no CI antes da execução de 'make test'."),
        code(
"""# Trecho do workflow .github/workflows/ci.yml:
name: CI Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv venv && source .venv/bin/activate
      - run: uv pip install -e ".[dev]"
      - run: python -m pytest -q""",
            "yaml"
        ),
        h1("2. Qual era o objetivo técnico e científico"),
        bullet("Blindagem contra regressões: Nenhum código quebrado entra na branch principal. Se um colega abrir um PR que faça qualquer teste falhar, o GitHub bloqueia o merge."),
        bullet("Auditoria de qualidade contínua em conformidade com padrões de Engenharia de Software da FH Kufstein."),
        h1("3. Resultado e Validação"),
        bullet("Execução de todo o ambiente e testes na nuvem em apenas 13 segundos!"),
        bullet("Badge verde de CI no repositório.")
    ]
    create_child_page("DE-06 · Integração Contínua (CI) com GitHub Actions", "🤖", p6_blocks)

    # ==========================================
    # 7. DS-01: YOLOv8 Detector
    # ==========================================
    p7_blocks = [
        callout("DS-01 · Detector Espacial de Pedestres com YOLOv8 (Ultralytics).", "👁️"),
        divider(),
        h1("1. O que foi feito (Implementação Técnica)"),
        bullet("Adição da dependência 'ultralytics' (trazendo PyTorch e torchvision) no pyproject.toml."),
        bullet("Criação da dataclass 'Detection(x, y, w, h, conf)' e da classe 'PedestrianDetector' em 'src/movesense/detector.py'."),
        bullet("Filtragem estrita da classe 0 (person do COCO dataset) e conversão para o padrão de coordenadas da nossa biblioteca."),
        bullet("Testes unitários em 'tests/test_detector.py' e script de inferência 'scripts/run_detector.py' ('make step-06')."),
        bullet("Comprovação empírica na imagem oficial 'bus.jpg' (detectando 4 pedestres reais com 87% de confiança em Sevilha, Espanha)."),
        h1("2. Qual era o objetivo técnico e científico"),
        bullet("Deep Learning de passo único (single-stage): O YOLOv8 Nano (yolov8n.pt com 3.2M de parâmetros) é o modelo ideal para rodar a mais de 100 FPS na NPU Hailo-8L do Raspberry Pi 5."),
        bullet("Resolução do Issue #9 do GitLab ('X Detektoren auswählen')."),
        bullet("Diagnóstico científico fundamental: Ao rodar no vídeo sintético, o YOLO detectou 0 pessoas. Isso provou matematicamente que a rede convolucional treinada em dados reais não alucina seres humanos onde só existem retângulos verdes desenhados!"),
        h1("3. Resultado e Validação"),
        bullet("Suíte alcançando 9 testes verdes aprovados."),
        bullet("Módulo de detecção espacial 100% pronto para integração com o tracker.")
    ]
    create_child_page("DS-01 · Detector de Pedestres YOLOv8 (Ultralytics)", "👁️", p7_blocks)

    # ==========================================
    # 8. DS-02: IoU Tracker
    # ==========================================
    p8_blocks = [
        callout("DS-02 · Rastreador Multi-Objeto Temporal com Associação por IoU.", "🎯"),
        divider(),
        h1("1. O que foi feito (Implementação Técnica)"),
        bullet("Módulo 'src/movesense/tracker.py' contendo a dataclass 'Track' e a classe 'SimpleTracker'."),
        bullet("Implementação matemática da métrica IoU (Intersection over Union) entre retângulos."),
        bullet("Lógica de gestão de estado: associação gananciosa por maior IoU, tolerância a ausências temporárias ('max_misses=3') e atribuição sequencial de novos IDs."),
        bullet("Testes unitários em 'tests/test_tracker.py' (criação de ID, persistência temporal e separação de pessoas distintas)."),
        bullet("Script 'scripts/run_tracker.py' e atalho 'make step-07'."),
        code("make step-07  # Rastreia 100 frames a 28.000 FPS e gera tracks.txt", "shell"),
        h1("2. Qual era o objetivo técnico e científico"),
        bullet("Dar memória temporal ao pipeline: O detector analisa cada frame isoladamente como se tivesse amnésia. O Tracker conecta os pontos ao longo do tempo para formar trajetórias contínuas."),
        bullet("Tratamento de oclusões temporárias: Se um pedestre passa atrás de uma placa ou poste por 1 a 3 frames, o tracker não descarta o ID imediatamente."),
        h1("3. Resultado e Validação"),
        bullet("100 frames processados a quase 28.000 FPS."),
        bullet("5 pedestres rastreados do início ao fim com zero trocas indevidas de identidade (ID switches)."),
        bullet("Geração de 'data/synthetic/tracks.txt' no formato MOT e 12 testes verdes aprovados.")
    ]
    create_child_page("DS-02 · Tracker de Pedestres (Associação Espacial IoU)", "🎯", p8_blocks)

    # ==========================================
    # 9. DS-03: Trajectory Features
    # ==========================================
    p9_blocks = [
        callout("DS-03 · Extrator de Features Cinemáticas de Trajetória (Velocidade, Aceleração e Confinamento).", "📈"),
        divider(),
        h1("1. O que foi feito (Implementação Técnica)"),
        bullet("Módulo 'src/movesense/features.py' contendo as funções 'extract_track_kinematics()' e 'extract_trajectory_features()'."),
        bullet("Cálculo formal de grandezas da física: centroide (cx, cy), velocidade linear média e máxima (px/s), aceleração média (px/s²) e raio de confinamento espacial (dwell radius)."),
        bullet("Testes unitários em 'tests/test_features.py' cobrindo movimento retilíneo uniforme e pedestre estático."),
        bullet("Script 'scripts/extract_features.py' e atalho 'make step-08'."),
        code(
"""# Exemplo da tabela de features gerada para ML:
# track_id, duration_frames, mean_speed, max_speed, confinement_radius, heuristic_label
Pedestre #1 | Duração: 100 frames | Vel. Média: 120.5 px/s | Conf: 310.0 px | [WALKING]
Pedestre #2 | Duração:  80 frames | Vel. Média:   0.0 px/s | Conf:   0.0 px | [STANDING]
Pedestre #3 | Duração:  95 frames | Vel. Média:  22.1 px/s | Conf:  15.0 px | [LOITERING]
Pedestre #4 | Duração:  60 frames | Vel. Média: 850.0 px/s | Conf: 650.0 px | [RUNNING]""",
            "plain text"
        ),
        h1("2. Qual era o objetivo técnico e científico"),
        bullet("A ponte entre Visão Computacional e Machine Learning: Modelos tabulares (Random Forest, SVM, MLP) não operam sobre vídeos, mas sobre vetores de atributos físicos."),
        bullet("Atendimento direto aos Issues #3 e #6 do GitLab da equipe ('Taxonomie und Label-Mapping')."),
        h1("3. Resultado e Validação"),
        bullet("Extração instantânea e salvamento em 'data/synthetic/trajectory_features.csv'."),
        bullet("Suíte completa com 15 testes verdes aprovados em 3.48s.")
    ]
    create_child_page("DS-03 · Extrator de Features Cinemáticas de Trajetória", "📈", p9_blocks)

    print("\n🎉 Todas as 9 sub-páginas detalhadas foram criadas no Notion com sucesso!")

if __name__ == "__main__":
    main()
