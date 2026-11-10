"""Script to populate MoveSense Project documentation in Notion."""

import json
import requests

TOKEN = "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"
PARENT_PAGE_ID = "414e585c-5796-80d1-8a0b-f75e01eb905e"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def create_subpage(title: str, icon_emoji: str, blocks: list) -> str:
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"page_id": PARENT_PAGE_ID},
        "icon": {"type": "emoji", "emoji": icon_emoji},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": title}}]}
        },
        "children": blocks[:100],  # Notion API allows up to 100 blocks on creation
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        page_id = resp.json()["id"]
        print(f"✅ Criada página: {title} (ID: {page_id})")
        # If there are more than 100 blocks, append remaining
        if len(blocks) > 100:
            append_blocks(page_id, blocks[100:])
        return page_id
    else:
        print(f"❌ Erro ao criar {title}: {resp.status_code} - {resp.text}")
        return ""


def append_blocks(page_id: str, blocks: list):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    for i in range(0, len(blocks), 100):
        chunk = blocks[i : i + 100]
        resp = requests.patch(url, headers=HEADERS, json={"children": chunk})
        if resp.status_code != 200:
            print(f"⚠️ Erro ao anexar blocos: {resp.text}")


# Block helper functions
def h1(text: str):
    return {
        "object": "block",
        "type": "heading_1",
        "heading_1": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def h2(text: str):
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def h3(text: str):
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def p(text: str):
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def callout(text: str, emoji: str = "💡"):
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": emoji},
            "rich_text": [{"type": "text", "text": {"content": text}}],
        },
    }


def bullet(text: str):
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }


def code(content: str, language: str = "python"):
    return {
        "object": "block",
        "type": "code",
        "code": {
            "language": language,
            "rich_text": [{"type": "text", "text": {"content": content}}],
        },
    }


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


def populate_all():
    print("Iniciando publicação do MoveSense no Notion...")

    # --- PÁGINA 1: VISÃO GERAL & ENGENHARIA ---
    blocks_p1 = [
        callout(
            "MoveSense: Pipeline reprodutível e modular para análise de fluxo e comportamento de pedestres a partir de vídeo. Projeto oficial do Mestrado em Data Science & Intelligent Analytics (FH Kufstein Tirol, Topic 06).",
            "🚶",
        ),
        divider(),
        h1("1. Filosofia de Engenharia e Boas Práticas"),
        p(
            "O desenvolvimento do MoveSense segue os mais altos padrões da indústria e pesquisa aplicada em Visão Computacional:"
        ),
        bullet(
            "Segregação de Papéis: Divisão formal entre Data Engineer (DE) (ingestão, esquemas contratuais, testes de fumaça, sanitização e CI) e Data Scientist (DS) (modelos, inferência, tracking e métricas)."
        ),
        bullet(
            "Git Flow Estrito: Branch main sagrada e protegida. Toda funcionalidade nasce em branch isolada (ex: chore/DE-01-scaffold) e só entra via Pull Request (PR) aprovado."
        ),
        bullet(
            "TDD (Test-Driven Development): Teste escrito primeiro (fase vermelha 🔴), código implementado em seguida (fase verde 🟢)."
        ),
        bullet(
            "uv Package Manager: Utilização do uv (escrito em Rust) para resolver dependências 10x mais rápido que o pip tradicional."
        ),
        bullet(
            "Higiene de Repositório: Bloqueio estrito de datasets (data/), vídeos pesados (*.avi) e pesos de redes neurais (*.pt, *.onnx) no .gitignore."
        ),
        h2("2. A Tríade de Papéis no Projeto"),
        bullet(
            "PM (Project Manager): Contato com o cliente/professor, backlog, aprovação de PRs e alinhamento de entregas."
        ),
        bullet(
            "DE (Data Engineer): Garante que a entrada é confiável. Se o dado não bater com o padrão MOT, é bug de engenharia."
        ),
        bullet(
            "DS (Data Scientist): Modela, rastreia e avalia. Extrai features físicas e classifica o comportamento final."
        ),
    ]
    create_subpage(
        "01 · Visão Geral & Filosofia de Engenharia", "🏛️", blocks_p1
    )

    # --- PÁGINA 2: DETECTORES ---
    blocks_p2 = [
        callout(
            "O Detector é o olho instantâneo do sistema: analisa cada quadro de vídeo de forma estática (sem memória) e gera Bounding Boxes [x, y, w, h, conf] das pessoas.",
            "👁️",
        ),
        divider(),
        h1("1. YOLO (You Only Look Once)"),
        p(
            "Arquitetura convolucional (CNN) em passo único (single-stage). Processa a imagem inteira de uma só vez prevendo caixas e probabilidades simultaneamente."
        ),
        bullet(
            "Vantagens: Velocidade extrema (60 a 150+ FPS), ultra-leve (família nano com apenas 6 MB), fácil integração via biblioteca ultralytics."
        ),
        bullet(
            "Desvantagens: Foco em padrões locais de textura; pode fundir ou perder pessoas sobrepostas em multidões densas."
        ),
        bullet(
            "Pós-processamento: Exige NMS (Non-Maximum Suppression) para apagar caixas duplicadas."
        ),
        bullet(
            "Papel no MoveSense: Detector padrão ultrarrápido ideal para dispositivos de borda (Raspberry Pi 5 + Hailo-8)."
        ),
        h2("2. RT-DETR (Real-Time Detection Transformer)"),
        p(
            "Primeiro detector baseado em Transformers capaz de rodar em tempo real. Utiliza mecanismos de Self-Attention e Cross-Attention."
        ),
        bullet(
            "Atenção Global: Compara cada pixel com todos os outros da imagem ao mesmo tempo, entendendo o contexto global da cena."
        ),
        bullet(
            "NMS-Free: A própria rede neural associa exatamente uma caixa única para cada pessoa real, eliminando o algoritmo NMS."
        ),
        bullet(
            "Vantagens: Superior em cenas complexas, aglomerações e pedestres sobrepostos."
        ),
        bullet(
            "Desvantagens: Modelo mais pesado, maior consumo de RAM e latência mais alta que o YOLO nano."
        ),
        h2("3. Comparação Direta: YOLO vs. RT-DETR"),
        code(
            """# Comparativo Arquitetural:
# YOLO    -> Convoluções locais -> Leve, veloz, exige NMS -> Pode apagar pessoas coladas
# RT-DETR -> Atenção global     -> NMS-Free, robusto em multidões -> Maior custo computacional""",
            "python",
        ),
    ]
    create_subpage("02 · Detectores de Pedestres: YOLO vs. RT-DETR", "🎯", blocks_p2)

    # --- PÁGINA 3: TRACKERS ---
    blocks_p3 = [
        callout(
            "O Tracker é a memória temporal: conecta as caixas soltas ao longo dos frames e garante que o Pedestre ID 1 mantenha a mesma identidade ao longo de todo o percurso.",
            "🧠",
        ),
        divider(),
        h1("1. A Tríade Fundamental do Tracking"),
        bullet(
            "Filtro de Kalman: Hipótese de movimento. Prediz onde a pessoa estará no próximo frame com base na velocidade atual."
        ),
        bullet(
            "ReID (Re-Identificação): Hipótese de aparência. Rede neural que extrai a assinatura visual (cor da roupa, silhueta)."
        ),
        bullet(
            "Algoritmo Húngaro: Decisão ótima. Resolve a matriz de custos e faz o casamento matemático entre predição e realidade."
        ),
        h2("2. SORT (Simple Online and Realtime Tracking)"),
        bullet("Mecanismo: Apenas Filtro de Kalman + IoU geométrico."),
        bullet("Vantagem: Velocidade absurda (>600 FPS)."),
        bullet(
            "Desvantagem: Não tem memória de aparência. Se a pessoa passa atrás de um poste por 2 frames, perde o ID (ID Switch catastrófico)."
        ),
        h2("3. DeepSORT"),
        bullet(
            "Mecanismo: Adiciona rede neural de ReID profunda ao SORT para lembrar a roupa e aparência do pedestre."
        ),
        bullet(
            "Problema: Processamento pesado de ReID para cada caixa e falha se pedestres usarem roupas parecidas."
        ),
        h2("4. ByteTrack (O Padrão de Alta Densidade)"),
        bullet(
            "A Sacada Genial: Quase todos os trackers jogavam fora caixas com baixa confiança (<0.5). O ByteTrack percebeu que pedestres ocluídos têm baixa confiança, mas ainda estão lá!"
        ),
        bullet(
            "Associação em 2 Etapas: 1) Associa caixas fortes (>0.6); 2) Pistas que sobraram tentam casar com as caixas fracas (0.1 a 0.6)."
        ),
        bullet(
            "Resultado: Excelente em multidões densas sem precisar de rede pesada de ReID."
        ),
        h2("5. BoT-SORT (Bag of Tricks for Tracking)"),
        bullet(
            "O Estado da Arte: Combina o ByteTrack com Compensação de Movimento de Câmera (CMC via fluxo óptico) e fusão elegante de ReID + IoU."
        ),
        bullet(
            "Resultado: Líder absoluto em métricas IDF1 e HOTA nos benchmarks mundiais."
        ),
    ]
    create_subpage(
        "03 · Trackers: SORT, DeepSORT, ByteTrack & BoT-SORT", "🔄", blocks_p3
    )

    # --- PÁGINA 4: MOT17 & MOT20 ---
    blocks_p4 = [
        callout(
            "MOT17 e MOT20 são os benchmarks oficiais internacionais do MOTChallenge para medir com rigor científico a qualidade dos algoritmos de rastreamento.",
            "📊",
        ),
        divider(),
        h1("1. O que são e qual a diferença?"),
        bullet(
            "MOT17: Densidade moderada (30 a 40 pessoas/frame). Cenários urbanos normais, ruas, praças e plataformas de trem. Oclusões breves."
        ),
        bullet(
            "MOT20: Densidade extrema (média de 170 pessoas/frame, picos de 246!). Mercados de Natal e calçadões hiperlotados. Oclusões severas e corpos encobertos."
        ),
        h2("2. Estrutura Padrão de uma Sequência MOT"),
        code(
            """MOT17-02-FRCNN/
├── seqinfo.ini   # Metadados (resolução 1920x1080, 30 FPS, total de frames)
├── img1/         # Imagens brutas do vídeo frame a frame (000001.jpg, 000002.jpg...)
├── det/det.txt   # Detecções públicas geradas pelo detector
└── gt/gt.txt     # O GROUND TRUTH oficial anotado por humanos""",
            "plain text",
        ),
        h2("3. O Contrato de 9 Colunas do Ground Truth (gt.txt)"),
        p("frame, id, x, y, w, h, conf, class_id, visibility"),
        bullet("frame: Número do quadro (1, 2, 3...)"),
        bullet("id: Identidade persistente do pedestre"),
        bullet("x, y, w, h: Coordenadas e dimensões da caixa"),
        bullet("conf: 1 para ground truth"),
        bullet("class_id: 1 para Pedestre"),
        bullet("visibility: Fração do corpo visível (0.0 a 1.0)"),
        h2("4. Como o MoveSense usa esses dados"),
        p(
            "No passo DE-05, o nosso loader `load_mot_file()` foi construído exatamente sobre essa especificação internacional de 9 colunas. Ele lê o MOT17 e MOT20 nativamente sem precisar de nenhuma alteração de código!"
        ),
    ]
    create_subpage("04 · Benchmarks Oficiais: MOT17 & MOT20", "🏆", blocks_p4)

    # --- PÁGINA 5: HOTA & PROPAGAÇÃO DE ERRO ---
    blocks_p5 = [
        callout(
            "O diferencial científico do MoveSense: demonstrar quantitativamente como as falhas de rastreamento (ID Switches) quebram trajetórias e corrompem a classificação final de comportamento.",
            "🔬",
        ),
        divider(),
        h1("1. A Métrica HOTA (Higher Order Tracking Accuracy)"),
        p(
            "Criada para balancear matematicamente a precisão de detecção (DetA) e a consistência de associação de IDs (AssA):"
        ),
        code("HOTA = sqrt(DetA * AssA)", "python"),
        bullet(
            "IDF1: Mede a porcentagem do tempo em que as identidades foram preservadas sem troca."
        ),
        bullet("MOTA: Foco em quantidade de caixas corretas e falsos positivos."),
        bullet(
            "IDSW (ID Switches): Quantidade absoluta de vezes em que o tracker confundiu e trocou as identidades."
        ),
        h2("2. A Matriz dos 4 Pares Exigida pelo Professor"),
        bullet(
            "Par 1: YOLO + ByteTrack no MOT17 -> Pipeline leve em tempo real para fluxo moderado."
        ),
        bullet(
            "Par 2: YOLO + BoT-SORT no MOT17 -> Mede se ReID e CMC melhoram a estabilidade de identidade."
        ),
        bullet(
            "Par 3: YOLO + ByteTrack no MOT20 -> Teste de estresse: recuperação de caixas fracas sob multidão."
        ),
        bullet(
            "Par 4: YOLO + BoT-SORT no MOT20 -> Teste supremo: o ReID consegue separar roupas parecidas em multidões?"
        ),
        h2("3. Propagação de Erro no Comportamento"),
        callout(
            "Cadeia de Erro: Oclusão severa -> ID Switch -> Trajetória contínua partida em 2 pedaços -> Cálculo de velocidade e aceleração corrompido com saltos irreais -> O classificador rotula erroneamente (ex: pedestre que só caminhava é classificado como 'parou e correu').",
            "⚠️",
        ),
        h2("4. Label Studio"),
        bullet(
            "O MOT17/20 traz caixas, mas não traz rótulos de comportamento (walking, standing, running, loitering)."
        ),
        bullet(
            "O Label Studio é a ferramenta open-source em Python onde anotamos manualmente o ground truth de comportamento para treinar o classificador Random Forest (DS-04)!"
        ),
    ]
    create_subpage(
        "05 · Avaliação HOTA, Propagação de Erros & Label Studio",
        "📈",
        blocks_p5,
    )

    # --- PÁGINA 6: RELATÓRIO PASSO A PASSO (DE-01 AO DS-02) ---
    blocks_p6 = [
        callout(
            "Registro histórico e cronológico de todas as tarefas de código desenvolvidas e testadas no repositório local e no GitHub.",
            "📝",
        ),
        divider(),
        h1("Resumo das Tarefas Entregues"),
        bullet(
            "DE-01: Scaffold do projeto com uv, .venv Python 3.11, pyproject.toml, Makefile e teste de importação. PR #1 mergeado."
        ),
        bullet(
            "DE-02: Template de Pull Request em inglês (.github/pull_request_template.md) com checklist de segurança."
        ),
        bullet(
            "DE-03: Gerador sintético de ground truth MOT (gt.txt com seed=2026 reprodutível) e make step-02. TDD vermelho -> verde."
        ),
        bullet(
            "DE-04: Renderizador OpenCV sintetizando vídeo synthetic_video.avi a 25 FPS com caixas e IDs estampados. make step-04."
        ),
        bullet(
            "DE-05: Loader MOT com Pandas (load_mot_file) com 9 colunas tipadas e script de inspeção executiva. make step-05."
        ),
        bullet(
            "DE-06: Pipeline de CI com GitHub Actions (setup-uv) rodando suíte de testes automática na nuvem em 13 segundos."
        ),
        bullet(
            "DS-01: Detector de pedestres com Ultralytics YOLOv8 (PedestrianDetector) filtrando classe 0 (person). PR #7 mergeado."
        ),
        bullet(
            "DS-02: Tracker temporal com cálculo de IoU, dataclass Track e persistência de IDs sequenciais. 12 testes verdes."
        ),
        h2("Roadmap das Próximas Entregas"),
        bullet(
            "DS-03: Extração de Trajectory Features (velocidade, aceleração, direção, dwell time)."
        ),
        bullet(
            "DS-04: Classificador de comportamento supervisionado (Random Forest) para walking, standing, running, loitering."
        ),
        bullet(
            "DS-05: Avaliação comparativa completa com HOTA, IDF1, MOTA e Macro-F1."
        ),
    ]
    create_subpage("06 · Relatório Passo a Passo (DE-01 a DS-02)", "🛠️", blocks_p6)

    print("\n🎉 Todas as 6 subpáginas foram criadas com sucesso no Notion!")


if __name__ == "__main__":
    populate_all()
