"""Script to create the comprehensive Step-by-Step Guide in Notion."""

import requests

TOKEN = "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"
PARENT_PAGE_ID = "414e585c-5796-80d1-8a0b-f75e01eb905e"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


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


def code(content: str, language: str = "plain text"):
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


def main():
    print("Criando Guia Passo a Passo no Notion...")

    all_blocks = [
        callout(
            "Este documento consolida tudo o que foi construído passo a passo no projeto MoveSense, o objetivo técnico e científico de cada decisão, o que ainda falta fazer e o porquê detalhado de cada próxima etapa.",
            "🧭",
        ),
        divider(),
        h1("PARTE 1: O QUE FOI FEITO ATÉ AGORA (Passo a Passo com Objetivos)"),
        p(
            "Até o momento, foram concluídas 8 etapas técnicas completas (6 de Engenharia de Dados e 2 de Ciência de Dados), todas cobertas por testes automatizados (12 testes verdes) e integradas via Git Flow com proteção da main."
        ),
        # DE-01
        h2("1. DE-01: Scaffold do Projeto e Gerenciamento com uv"),
        bullet(
            "O que foi feito: Inicialização do repositório Git (main protegida), configuração do gerenciador uv (Rust), criação do ambiente isolado .venv com Python 3.11, escrita do pyproject.toml com layout src/, Makefile com comandos de equipe e primeiro teste de fumaça (test_imports.py)."
        ),
        bullet(
            "Qual era o objetivo: Garantir uma base de código estável, reprodutível e padronizada. O uv substitui o pip tradicional para resolver e instalar dependências 10x mais rápido (instalou 28 pacotes em apenas 1.02s). O .gitignore blindou o repositório contra dados pesados, caches e arquivos de sistema (.DS_Store)."
        ),
        bullet(
            "Resultado: Pacote movesense 0.1.0 instalado em modo editável (-e) e primeiro PR mergeado com sucesso."
        ),
        # DE-02
        h2("2. DE-02: Template Padronizado de Pull Request"),
        bullet(
            "O que foi feito: Criação do arquivo .github/pull_request_template.md inteiramente em inglês."
        ),
        bullet(
            "Qual era o objetivo: Institucionalizar a governança de código no time. Obriga qualquer pessoa que abra um PR no GitHub a preencher o ID da tarefa (Backlog ID), o resumo do que mudou (What Changed), a evidência de teste verde (make test) e um checklist de segurança (proibindo commit de datasets ou chaves de API)."
        ),
        bullet(
            "Resultado: Todos os PRs seguintes (#3, #4, #5, #6, #7) já abriram com o formulário profissional pré-preenchido."
        ),
        # DE-03
        h2("3. DE-03: Gerador Sintético de Trajetórias MOT (gt.txt)"),
        bullet(
            "O que foi feito: Aplicação de TDD estrito. O teste tests/test_synthetic.py foi escrito primeiro (vermelho 🔴), cobrando a especificação de 9 colunas do padrão MOT. Depois foi implementado src/movesense/synthetic.py (verde 🟢), script CLI scripts/generate_synthetic.py e atalho make step-02."
        ),
        bullet(
            "Qual era o objetivo: Permitir o desenvolvimento e teste de todo o pipeline sem depender do download lento de gigabytes de vídeos externos ou internet. A semente matemática fixa (seed=2026) garante reprodutibilidade científica exata em qualquer computador."
        ),
        bullet(
            "Resultado: Geração em milissegundos de 5 pedestres em 100 frames (500 anotações) em data/synthetic/gt.txt."
        ),
        # DE-04
        h2("4. DE-04: Renderizador de Vídeo Sintético com OpenCV (.avi)"),
        bullet(
            "O que foi feito: Módulo src/movesense/render.py usando cv2.VideoWriter com codec MJPG a 25 FPS, teste unitário tests/test_render.py, script scripts/render_video.py e make step-04."
        ),
        bullet(
            "Qual era o objetivo: Redes neurais de visão computacional (YOLO) consomem frames de vídeo, não tabelas de texto. O renderizador lê as anotações numéricas do gt.txt e desenha visualmente a cena: asfalto cinza, bounding boxes verdes brilhantes e carimbo de ID e timestamp."
        ),
        bullet(
            "Resultado: Produção de data/synthetic/synthetic_video.avi (validado pelo OpenCV). Verificado que o vídeo pesado ficou fora do Git graças ao .gitignore."
        ),
        # DE-05
        h2("5. DE-05: Loader MOT Tipado com Validação de Esquema (Pandas)"),
        bullet(
            "O que foi feito: Módulo src/movesense/loader.py com a função load_mot_file(), teste tests/test_loader.py, script scripts/inspect_dataset.py e make step-05."
        ),
        bullet(
            "Qual era o objetivo: Eliminar leituras manuais e frágeis de arquivos de texto. O loader converte qualquer arquivo MOT diretamente em um pd.DataFrame com tipos exatos (inteiros para frames e IDs, floats para coordenadas), garantindo integridade matemática para os próximos módulos."
        ),
        bullet(
            "Resultado: Inspeção executiva no terminal comprovando 500 detecções ativas, 100 frames e 5 pedestres rastreados."
        ),
        # DE-06
        h2("6. DE-06: Integração Contínua (CI) com GitHub Actions"),
        bullet(
            "O que foi feito: Workflow automatizado em .github/workflows/ci.yml utilizando astral-sh/setup-uv."
        ),
        bullet(
            "Qual era o objetivo: Ter um robô auditor na nuvem. A cada commit ou PR na main, o GitHub sobe uma máquina virtual Ubuntu, monta o ambiente virtual Python 3.11, instala o pacote com uv e roda a suíte de testes. Se algum teste quebrar, o merge é travado."
        ),
        bullet(
            "Resultado: Resolução do incidente de virtualenv e execução do CI com 100% de sucesso em apenas 13 segundos na nuvem."
        ),
        # DS-01
        h2("7. DS-01: Detector de Pedestres YOLOv8 (Ultralytics)"),
        bullet(
            "O que foi feito: Adição da biblioteca ultralytics no pyproject.toml (trazendo PyTorch e torchvision), dataclass Detection, classe PedestrianDetector em src/movesense/detector.py, testes unitários tests/test_detector.py, script scripts/run_detector.py e make step-06."
        ),
        bullet(
            "Qual era o objetivo: Integrar o detector espacial de Deep Learning em passo único (single-stage). O modelo analisa cada imagem estática e localiza caixas de pessoas filtrando estritamente a classe 0 (person do COCO dataset)."
        ),
        bullet(
            "Diagnóstico Científico: Ao rodar no vídeo sintético com retângulos vetoriais, o YOLO detectou 0 pessoas. Isso confirmou que a rede neural treinada em fotos reais procura texturas e anatomia humana real, validando o uso de detectores sintéticos ruidosos (DETA/DETB) para dados sintéticos e YOLO para vídeos reais."
        ),
        # DS-02
        h2("8. DS-02: Tracker de Pedestres (Associação Espacial IoU)"),
        bullet(
            "O que foi feito: Módulo src/movesense/tracker.py com a classe SimpleTracker, cálculo matemático de IoU (Intersection over Union), dataclass Track, testes unitários tests/test_tracker.py, script scripts/run_tracker.py e make step-07."
        ),
        bullet(
            "Qual era o objetivo: Dar memória temporal ao sistema. O detector gera caixas soltas sem saber quem é quem. O Tracker calcula a sobreposição geométrica entre o frame atual e o anterior: se IoU >= 0.3, preserva o ID; se a pessoa for nova, cria um novo ID; se ela sumir por até 3 frames (oclusão temporária), não apaga o ID imediatamente."
        ),
        bullet(
            "Resultado: Suíte completa alcançando 12 testes aprovados em 3.49s e geração de data/synthetic/tracks.txt com trajetórias contínuas."
        ),
        divider(),
        h1("PARTE 2: O QUE AINDA FALTA FAZER E O PORQUÊ DE CADA PASSO"),
        p(
            "Agora que a infraestrutura, o detector e o rastreador básico estão prontos, entramos na fase de inteligência comportamental e avaliação científica exigida pelo mestrado e pelo cliente:"
        ),
        # DS-03
        h2(
            "1. DS-03: Engenharia de Features de Trajetória (Trajectory Features)"
        ),
        bullet(
            "O que fazer: Implementar src/movesense/features.py para processar as trajetórias por track_id e calcular séries temporais de grandezas físicas: velocidade instantânea e média, aceleração, variação angular de direção (heading change) e tempo de permanência no mesmo raio (dwell time)."
        ),
        bullet(
            "POR QUE esse passo é necessário? Modelos de Machine Learning (classificadores) não entendem pixels nem coordenadas brutas (x, y). Para a IA saber se um pedestre está andando, correndo ou parado, ela precisa de dados físicos: 'Qual a velocidade dele? Ele está acelerando? A direção dele muda erraticamente? Quanto tempo ele ficou parado no mesmo metro quadrado?'."
        ),
        # DS-04
        h2(
            "2. DS-04: Classificador de Comportamento Supervisionado (Random Forest)"
        ),
        bullet(
            "O que fazer: Implementar src/movesense/classifier.py treinando um modelo Random Forest (e um classificador baseline majoritário) para mapear as features de trajetória em 4 classes de comportamento: walking (caminhando), standing (parado), running (correndo) e loitering (vadiando/rondando)."
        ),
        bullet(
            "POR QUE esse passo é necessário? Esta é a principal entrega final de inteligência do MoveSense exigida pelo cliente (Mohammadreza Mohebbi). O cliente não quer apenas contar pedestres em uma praça, ele quer entender a dinâmica do espaço público: saber se o fluxo é fluido (walking), se há aglomeração parada (standing) ou comportamento atípico/urgente (running / loitering)."
        ),
        # DS-05
        h2(
            "3. DS-05: Avaliação Científica HOTA, IDF1 e Propagação de Erro"
        ),
        bullet(
            "O que fazer: Implementar o cálculo das métricas oficiais de tracking (HOTA, IDF1, MOTA, ID Switches) e a métrica Macro-F1 com intervalo de confiança bootstrap para o classificador de comportamento. Gerar a matriz comparativa dos 4 pares oficiais exigidos pelo professor:"
        ),
        bullet(
            "Par 1: YOLO + ByteTrack no MOT17 | Par 2: YOLO + BoT-SORT no MOT17 | Par 3: YOLO + ByteTrack no MOT20 | Par 4: YOLO + BoT-SORT no MOT20."
        ),
        bullet(
            "POR QUE esse passo é necessário? É a resposta às 4 Perguntas Centrais de Pesquisa do projeto da FH Kufstein: 1) Qual par detector-tracker preserva identidades melhor sob oclusão? 2) Como os ID Switches propagam erro para os rótulos de comportamento? 3) Quais features de trajetória são mais úteis? 4) O custo extra de ReID no BoT-SORT se justifica frente à leveza do ByteTrack?"
        ),
        # Issue 5 do time
        h2("4. Issue #5 do Time: Exploração de Amostra Real do MOT17"),
        bullet(
            "O que fazer: Baixar localmente uma amostra leve do MOT17 (ex: sequência MOT17-09-FRCNN, ~20 MB), carregar com nosso load_mot_file(), extrair estatísticas (resolução, FPS, pessoas/frame, comprimento de tracks) e documentar em docs/data/exploration.md."
        ),
        bullet(
            "POR QUE esse passo é necessário? Cumprir o marco oficial de entrega do time no GitLab (Milestone: Training Data selected and labelled, aberto pelo Daniel Konrad com entrega para Nov 7, 2026)."
        ),
        # Issue 10/11 do time
        h2("5. Issue #10 & #11 do Time: Label Studio e Rótulos de Comportamento"),
        bullet(
            "O que fazer: Subir o Label Studio localmente, carregar o vídeo curto do MOT17 e rotular manualmente o comportamento de cada pedestre visível em trechos selecionados."
        ),
        bullet(
            "POR QUE esse passo é necessário? Os datasets MOT17 e MOT20 contêm apenas caixas e IDs de pessoas, mas NÃO contêm rótulos de comportamento. Para treinar o classificador Random Forest com aprendizado supervisionado, o time precisa criar esse Ground Truth de comportamento."
        ),
    ]

    # Criar a página no Notion
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"page_id": PARENT_PAGE_ID},
        "icon": {"type": "emoji", "emoji": "🧭"},
        "properties": {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": (
                                "01 · Guia Passo a Passo: O que foi Feito,"
                                " Objetivos e Próximos Passos (com os Porquês)"
                            )
                        },
                    }
                ]
            }
        },
        "children": all_blocks[:100],
    }

    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        new_page_id = resp.json()["id"]
        print(f"✅ Criada página principal do Guia com sucesso! ID: {new_page_id}")
        if len(all_blocks) > 100:
            url_append = f"https://api.notion.com/v1/blocks/{new_page_id}/children"
            requests.patch(
                url_append, headers=HEADERS, json={"children": all_blocks[100:]}
            )
            print("✅ Blocos adicionais anexados com sucesso!")
    else:
        print(f"❌ Erro ao criar página: {resp.status_code} - {resp.text}")


if __name__ == "__main__":
    main()
