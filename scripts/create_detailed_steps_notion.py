"""
Script to create ultra-complete, didactic, encyclopedic step-by-step reference sub-pages inside:
'01 · Guia Passo a Passo: O que foi Feito, Objetivos e Próximos Passos (com os Porquês)'
in Notion for each milestone (DE-01 through DS-03).

Each page includes:
1. Detailed step-by-step instructions (commands, TDD Red->Green->Execution flow, Git flow).
2. Explicit explanation of WHY each file was created and its EXACT function/responsibility.
3. Full, verbatim source code for every file in that milestone.
4. Expected outputs, scientific takeaways, and validation results.
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


def numbered(text: str):
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": chunk_text(text)},
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


def file_section(
    file_path: str,
    why_created: str,
    exact_function: str,
    language: str = "python",
    override_content: str | None = None,
) -> list[dict]:
    content = override_content if override_content is not None else read_repo_file(file_path)
    return [
        h2(f"📄 {file_path}"),
        bullet(f"Por que este arquivo foi criado: {why_created}"),
        bullet(f"Função exata no sistema: {exact_function}"),
        code(content, language),
    ]


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
        print(f"✅ Criada página detalhada: '{title}' (ID: {page_id})")
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
    print("\nPublicando guia passo a passo completo com explicação de cada arquivo no Notion...")

    # =========================================================================
    # 1. DE-01: Scaffold e uv
    # =========================================================================
    de01_blocks = [
        callout(
            "DE-01 · Fundação de Engenharia: Como criamos um projeto Python moderno, profissional, isolado e reprodutível usando o layout src/ e o gerenciador uv.",
            "🏗️",
        ),
        divider(),
        h1("1. O Problema que Precisávamos Resolver"),
        p(
            "Projetos universitários frequentemente quebram porque cada aluno instala bibliotecas diretamente no Python global da máquina, usa pastas soltas sem estrutura de pacote e sobe arquivos gigantes (vídeos, pesos de IA, cache) para o Git. A etapa DE-01 resolve isso antes mesmo de escrever a primeira linha de Visão Computacional."
        ),
        h1("2. Passo a Passo Executado (Na Ordem Exata)"),
        numbered("Criar e trocar para a branch de trabalho 'chore/DE-01-scaffold' (nunca trabalhamos direto na branch main protegida)."),
        numbered("Criar o ambiente virtual Python 3.11 isolado dentro da pasta '.venv' usando 'uv venv --python 3.11' (o Python 3.11 garante 100% de compatibilidade com PyTorch, Ultralytics e OpenCV no macOS e Linux)."),
        numbered("Ativar o ambiente virtual com 'source .venv/bin/activate' para que o terminal use apenas as bibliotecas do projeto."),
        numbered("Definir os metadados e dependências do projeto no arquivo 'pyproject.toml' utilizando o padrão moderno 'layout src/'."),
        numbered("Blindar o Git criando o '.gitignore' para evitar vazamento de vídeos, pesos '.pt' e lixo de sistema operacional."),
        numbered("Criar o pacote mínimo 'src/movesense/__init__.py' e o primeiro teste de fumaça 'tests/test_imports.py'."),
        numbered("Instalar o pacote localmente em modo editável ('uv pip install -e \".[dev]\"') para que qualquer alteração em 'src/movesense/' seja refletida imediatamente nos testes e scripts sem precisar reinstalar."),
        numbered("Criar o 'Makefile' padronizando os comandos da equipe ('make install', 'make test')."),
        code(
"""# Sequência de comandos executada no terminal:
git checkout -b chore/DE-01-scaffold
uv venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[dev]"
python -m pytest tests/test_imports.py
git add .
git commit -m "chore: setup project scaffold with uv and src layout (DE-01)" """,
            "shell",
        ),
        h1("3. Cada Arquivo Criado, Por que Existe e Sua Função Exata"),
        *file_section(
            "pyproject.toml",
            "Substitui os antigos 'setup.py' e 'requirements.txt' por um único arquivo oficial (padrão PEP 621) que define o projeto Python.",
            "Declara o nome e versão do pacote ('movesense 0.1.0'), especifica a versão mínima do Python (>=3.10), lista todas as dependências científicas (numpy, pandas, opencv, scipy, scikit-learn, tqdm) e de desenvolvimento (pytest, ruff), e instrui o setuptools a procurar o código dentro da pasta 'src/'.",
            language="toml",
        ),
        *file_section(
            ".gitignore",
            "Sem ele, comandos como 'git add .' subiriam centenas de megabytes de vídeos (.avi), pesos de redes neurais (.pt), a pasta .venv inteira e arquivos ocultos do Mac (.DS_Store) para o GitHub.",
            "Lista padrões de arquivos e diretórios que o Git deve ignorar permanentemente (data/, weights/, *.pt, *.onnx, .venv/, __pycache__/, .pytest_cache/).",
            language="plain text",
        ),
        *file_section(
            "src/movesense/__init__.py",
            "Em Python, colocar códigos soltos na raiz gera confusão nos imports. Uma pasta só é reconhecida oficialmente como pacote importável ('import movesense') quando possui este arquivo.",
            "Inicializa o pacote 'movesense' e expõe a constante '__version__ = \"0.1.0\"' para validação e auditoria.",
            language="python",
        ),
        *file_section(
            "tests/test_imports.py",
            "Precisávamos de uma prova rápida (Smoke Test) de que a instalação em modo editável funcionou e que o pytest encontra os módulos dentro de 'src/'.",
            "Importa o módulo 'movesense' e verifica se o atributo '__version__' existe. É o teste #1 da nossa suíte.",
            language="python",
        ),
        *file_section(
            "Makefile",
            "Cada membro do time usa flags diferentes no terminal (ex: 'python3 -m pytest' vs 'pytest -q'). Precisávamos de atalhos universais.",
            "Define alvos curtos e padronizados ('make install', 'make test') para que todos rodem os mesmos comandos localmente e no servidor de CI.",
            language="makefile",
            override_content=""".PHONY: install test\n\ninstall:\n\tuv pip install -e ".[dev]"\n\ntest:\n\tpython -m pytest -q""",
        ),
        divider(),
        h1("4. Resultado Final e Como Validar"),
        bullet("28 dependências instaladas pelo uv em apenas 1.02 segundo."),
        bullet("Teste 'tests/test_imports.py' aprovado (1 passed)."),
        bullet("Pull Request #1 mergeado na 'main'."),
    ]
    create_child_page("DE-01 · Scaffold do Projeto e Gerenciamento com uv", "🏗️", de01_blocks)

    # =========================================================================
    # 2. DE-02: PR Template
    # =========================================================================
    de02_blocks = [
        callout(
            "DE-02 · Governança de Equipe: Como institucionalizamos a qualidade de código e segurança usando um Pull Request Template automático.",
            "📋",
        ),
        divider(),
        h1("1. O Problema que Precisávamos Resolver"),
        p(
            "Quando várias pessoas trabalham juntas em Git, é muito comum alguém abrir um Pull Request sem explicar o que mudou, qual tarefa do backlog está resolvendo, ou sem comprovar que rodou os testes. Pior ainda: alguém pode esquecer uma chave de API ou imagem pesada no commit."
        ),
        h1("2. Passo a Passo Executado"),
        numbered("Criar a branch 'chore/DE-02-pr-template' a partir da main."),
        numbered("Criar a pasta oculta '.github/' na raiz (pasta especial lida automaticamente pelo GitHub)."),
        numbered("Escrever o formulário padrão em '.github/pull_request_template.md' em inglês (idioma padrão de engenharia do time)."),
        numbered("Comitar, subir para o GitHub e fazer o merge via PR."),
        code(
"""git checkout -b chore/DE-02-pr-template
mkdir -p .github
# Criar e preencher .github/pull_request_template.md
git add .github/pull_request_template.md
git commit -m "chore: add standardized pull request template (DE-02)"
git push origin chore/DE-02-pr-template""",
            "shell",
        ),
        h1("3. Arquivo Criado, Por que Existe e Sua Função Exata"),
        *file_section(
            ".github/pull_request_template.md",
            "Para obrigar todo autor de Pull Request a documentar suas mudanças e passar por um checklist de qualidade e segurança antes do Code Review.",
            "Sempre que alguém clica em 'New Pull Request' no GitHub, este texto preenche automaticamente a descrição do PR cobrando: Backlog ID, resumo das alterações, evidência do 'make test' verde e verificação de que não há datasets/segredos commitados.",
            language="markdown",
        ),
        divider(),
        h1("4. Resultado Final"),
        bullet("Todos os PRs subsequentes do repositório já nasceram padronizados e auditáveis."),
    ]
    create_child_page("DE-02 · Template Padronizado de Pull Request", "📋", de02_blocks)

    # =========================================================================
    # 3. DE-03: Synthetic Generator
    # =========================================================================
    de03_blocks = [
        callout(
            "DE-03 · Primeiro Ciclo TDD Completo: Como construímos um simulador matemático de pedestres no formato internacional MOTChallenge.",
            "🧪",
        ),
        divider(),
        h1("1. O Problema que Precisávamos Resolver"),
        p(
            "Vídeos reais do benchmark MOT17 têm vários gigabytes. Se dependêssemos deles para cada teste unitário ou execução no GitHub Actions, o desenvolvimento seria lentíssimo. Precisávamos de um gerador sintético leve, rápido e 100% reproduzível (sempre gera os mesmos números com a mesma semente)."
        ),
        h1("2. Passo a Passo Executado (Ciclo TDD: Red ➔ Green ➔ Execution)"),
        numbered("Criar branch 'feat/DE-03-synthetic-generator'."),
        numbered("FASE RED (Teste Primeiro): Criar 'tests/test_synthetic.py' cobrando que o gerador crie o arquivo 'gt.txt' e que cada linha possua exatamente 9 colunas separadas por vírgula. Rodar 'pytest' e confirmar a falha esperada (ModuleNotFoundError)."),
        numbered("FASE GREEN (Implementação): Criar 'src/movesense/synthetic.py' implementando a física simulada de caminhada com semente determinística (seed=2026) até os testes ficarem verdes."),
        numbered("FASE EXECUTION (Script para o Usuário): Criar 'scripts/generate_synthetic.py' e adicionar o atalho 'make step-02' no Makefile."),
        numbered("Rodar 'make step-02' para gerar o arquivo real 'data/synthetic/gt.txt' e validar."),
        code(
"""git checkout -b feat/DE-03-synthetic-generator
python -m pytest tests/test_synthetic.py  # Fase RED (falha esperada)
# Após implementar src/movesense/synthetic.py:
python -m pytest                          # Fase GREEN (3 passed)
make step-02                              # Gera data/synthetic/gt.txt""",
            "shell",
        ),
        h1("3. Cada Arquivo Criado, Por que Existe e Sua Função Exata"),
        *file_section(
            "tests/test_synthetic.py",
            "No TDD, escrevemos o teste antes do código para definir o 'contrato' técnico: como a função será chamada e o que ela é obrigada a entregar.",
            "Contém dois testes automatizados: 'test_generate_creates_file' (garante que o arquivo é salvo em disco) e 'test_mot_format_nine_columns' (verifica linha por linha se a especificação de 9 campos do MOTChallenge foi respeitada).",
            language="python",
        ),
        *file_section(
            "src/movesense/synthetic.py",
            "Contém a regra de negócio pura e reutilizável da simulação, isolada de scripts CLI para poder ser importada tanto por testes quanto por outros scripts.",
            "A função 'generate_synthetic_mot()' usa 'np.random.default_rng(seed)' para posicionar N pedestres em uma tela 1920x1080, aplica vetores de velocidade constantes + pequeno ruído gaussiano por frame (mantendo dentro dos limites com 'np.clip'), ordena por (frame, id) e salva no padrão 'frame, id, x, y, w, h, conf, class, visibility'.",
            language="python",
        ),
        *file_section(
            "scripts/generate_synthetic.py",
            "Um arquivo dentro de 'src/' funciona apenas como biblioteca (ele define funções, mas não faz nada se executado diretamente). Precisamos de um arquivo executável na pasta 'scripts/' para o usuário rodar no dia a dia.",
            "Ponto de entrada CLI que invoca 'generate_synthetic_mot' com os parâmetros padrão do projeto (5 pedestres, 100 frames, seed 2026) e grava o resultado em 'data/synthetic/gt.txt'. Conectado ao atalho 'make step-02'.",
            language="python",
        ),
        divider(),
        h1("4. Resultado Final e Exemplo de Saída"),
        bullet("Arquivo 'data/synthetic/gt.txt' gerado em milissegundos com 500 linhas (5 pedestres × 100 frames)."),
        bullet("Suíte de testes avançou para 3 testes verdes."),
        code(
"""# Primeiras 5 linhas reais geradas em data/synthetic/gt.txt:
1,1,1583,170,64,128,1,1,1.0
1,2,673,258,64,128,1,1,1.0
1,3,1646,274,64,128,1,1,1.0
1,4,764,881,64,128,1,1,1.0
1,5,1142,793,64,128,1,1,1.0""",
            "plain text",
        ),
    ]
    create_child_page("DE-03 · Gerador Sintético de Trajetórias MOT (gt.txt)", "🧪", de03_blocks)

    # =========================================================================
    # 4. DE-04: Video Renderer
    # =========================================================================
    de04_blocks = [
        callout(
            "DE-04 · Transformando Números em Vídeo: Como renderizamos o arquivo gt.txt em um vídeo .avi Full HD usando OpenCV.",
            "🎬",
        ),
        divider(),
        h1("1. O Problema que Precisávamos Resolver"),
        p(
            "No passo anterior criamos apenas uma tabela de texto ('gt.txt'). Porém, modelos de Visão Computacional (como o YOLO no DS-01) e ferramentas visuais de avaliação consomem fluxos de vídeo (frames de pixels), e não arquivos CSV. Além disso, o olho humano precisa enxergar o movimento para validar o simulador."
        ),
        h1("2. Passo a Passo Executado (Ciclo TDD)"),
        numbered("Criar branch 'feat/DE-04-synthetic-video'."),
        numbered("FASE RED: Criar 'tests/test_render.py' exigindo que o renderizador gere um arquivo '.avi' não vazio e legível pelo 'cv2.VideoCapture' com o número exato de frames."),
        numbered("FASE GREEN: Implementar 'src/movesense/render.py' utilizando OpenCV ('cv2.VideoWriter' com codec MJPG)."),
        numbered("FASE EXECUTION: Criar 'scripts/render_video.py' e adicionar o alvo 'step-04' ao Makefile."),
        numbered("Executar 'make step-04' e verificar que o vídeo foi gerado em 'data/synthetic/synthetic_video.avi' (sem ir para o Git graças ao .gitignore)."),
        code(
"""git checkout -b feat/DE-04-synthetic-video
python -m pytest tests/test_render.py  # Fase RED -> Fase GREEN
make step-04                           # Renderiza synthetic_video.avi (2.5 MB)""",
            "shell",
        ),
        h1("3. Cada Arquivo Criado, Por que Existe e Sua Função Exata"),
        *file_section(
            "tests/test_render.py",
            "Testa automaticamente se o arquivo de vídeo gerado não está corrompido (comum ao errar codecs de vídeo ou ordem de largura/altura no OpenCV).",
            "Gera um mini 'gt.txt' temporário (2 pedestres, 5 frames), chama 'render_synthetic_video()', abre o arquivo resultante com 'cv2.VideoCapture' e valida se 'CAP_PROP_FRAME_COUNT == 5'.",
            language="python",
        ),
        *file_section(
            "src/movesense/render.py",
            "Encapsula a lógica gráfica de desenho OpenCV em uma função testável e parametrizável.",
            "Lê o arquivo 'gt.txt', agrupa as caixas por frame num dicionário, instancia um gravador 'cv2.VideoWriter' (MJPG, 25 FPS, 1920x1080) e, para cada frame, desenha um fundo cinza escuro (valor 40), escreve o timestamp do frame, desenha retângulos verdes brilhantes para cada pedestre e estampa o label 'ID: X' acima da caixa.",
            language="python",
        ),
        *file_section(
            "scripts/render_video.py",
            "Fornece o comando executável direto para a equipe transformar 'data/synthetic/gt.txt' em vídeo sem precisar escrever código Python.",
            "Verifica se 'gt.txt' já existe (senão orienta o usuário a rodar 'make step-02' antes) e invoca 'render_synthetic_video' em Full HD (1920x1080 @ 25 FPS). Conectado ao 'make step-04'.",
            language="python",
        ),
        divider(),
        h1("4. Resultado Final"),
        bullet("Vídeo 'data/synthetic/synthetic_video.avi' gerado (2.5 MB, 100 frames, 4 segundos)."),
        bullet("Suíte de testes avançou para 4 testes verdes."),
    ]
    create_child_page("DE-04 · Renderizador de Vídeo Sintético com OpenCV (.avi)", "🎬", de04_blocks)

    # =========================================================================
    # 5. DE-05: MOT Loader
    # =========================================================================
    de05_blocks = [
        callout(
            "DE-05 · Engenharia de Dados Tipada: Como unificamos a leitura do formato MOTChallenge com Pandas (e resolvemos o Issue #8 do GitLab!).",
            "📊",
        ),
        divider(),
        h1("1. O Problema que Precisávamos Resolver"),
        p(
            "Ler arquivos '.txt' manualmente com 'open()' e 'split(\",\")' em vários scripts diferentes gera bugs silenciosos (números lidos como string, colunas trocadas, dados desordenados). Além disso, o Project Manager Daniel Konrad criou o Issue #8 no GitLab pedindo exatamente um 'Einheitliches Datenformat und Dataset-Loader'."
        ),
        h1("2. Passo a Passo Executado (Ciclo TDD)"),
        numbered("Criar branch 'feat/DE-05-mot-loader'."),
        numbered("FASE RED: Criar 'tests/test_loader.py' validando o esquema exato de 9 colunas, os tipos de dados (inteiros para frame/id) e o tratamento de erro quando o arquivo não existe."),
        numbered("FASE GREEN: Implementar 'src/movesense/loader.py' usando Pandas com dicionário estrito de 'dtype'."),
        numbered("FASE EXECUTION: Criar o script de inspeção 'scripts/inspect_dataset.py' e o comando 'make step-05'."),
        code(
"""git checkout -b feat/DE-05-mot-loader
python -m pytest tests/test_loader.py
make step-05  # Exibe relatório executivo de inspeção no terminal""",
            "shell",
        ),
        h1("3. Cada Arquivo Criado, Por que Existe e Sua Função Exata"),
        *file_section(
            "tests/test_loader.py",
            "Garante a integridade do esquema de dados (Schema Validation), evitando que alterações futuras quebrem o Tracker ou Extrator de Features.",
            "Executa dois testes: 'test_load_mot_file_schema' (confere se retorna DataFrame Pandas, se as 9 colunas batem com MOT_COLUMNS e se frame/id são inteiros) e 'test_load_mot_file_not_found' (garante erro explícito se passar caminho inválido).",
            language="python",
        ),
        *file_section(
            "src/movesense/loader.py",
            "É a fonte única da verdade (Single Source of Truth) para leitura de anotações MOT em todo o projeto MoveSense.",
            "Exporta a lista 'MOT_COLUMNS' e a função 'load_mot_file()'. Valida se o caminho existe, lê via 'pd.read_csv' sem cabeçalho forçando tipagem estrita (int para frame/id/class_id; float para x/y/w/h/conf/visibility) e ordena cronologicamente por frame e id.",
            language="python",
        ),
        *file_section(
            "scripts/inspect_dataset.py",
            "Na Ciência de Dados, sempre precisamos de uma ferramenta rápida de Análise Exploratória (EDA) no terminal para checar um dataset antes de modelar (atendendo também ao Issue #5 do GitLab).",
            "Carrega 'data/synthetic/gt.txt' usando o loader oficial e imprime um resumo executivo: total de detecções, intervalo de frames, quantidade de pedestres únicos e prévia das 5 primeiras linhas.",
            language="python",
        ),
        divider(),
        h1("4. Resultado Final"),
        bullet("Inspeção confirmou: 500 detecções, 100 frames (1 a 100), 5 pedestres únicos."),
        bullet("Suíte de testes avançou para 6 testes verdes."),
    ]
    create_child_page("DE-05 · Loader MOT Tipado com Validação de Esquema (Pandas)", "📊", de05_blocks)

    # =========================================================================
    # 6. DE-06: CI GitHub Actions
    # =========================================================================
    de06_blocks = [
        callout(
            "DE-06 · Integração Contínua (CI): Como colocamos um robô auditor no GitHub para rodar todos os testes automaticamente na nuvem.",
            "🤖",
        ),
        divider(),
        h1("1. O Problema que Precisávamos Resolver"),
        p(
            "De nada adianta ter testes automatizados se alguém da equipe esquecer de rodá-los e fizer push de código quebrado na branch principal. Precisávamos que o próprio GitHub testasse o código em um computador limpo na nuvem toda vez que um commit ou PR acontecesse."
        ),
        h1("2. Passo a Passo Executado"),
        numbered("Criar branch 'chore/DE-06-ci'."),
        numbered("Criar o diretório especial '.github/workflows/' que o GitHub Actions monitora."),
        numbered("Configurar o pipeline no arquivo '.github/workflows/ci.yml' usando a action oficial 'astral-sh/setup-uv@v5' com cache ativado."),
        numbered("Fazer o push, observar os logs no GitHub Actions, corrigir a ativação de ambiente virtual no CI e obter o selo verde (Passing) em ~13 segundos."),
        code(
"""git checkout -b chore/DE-06-ci
mkdir -p .github/workflows
git add .github/workflows/ci.yml
git commit -m "chore: setup GitHub Actions CI pipeline with uv (DE-06)" """,
            "shell",
        ),
        h1("3. Arquivo Criado, Por que Existe e Sua Função Exata"),
        *file_section(
            ".github/workflows/ci.yml",
            "Automatiza o processo de Build e Teste na nuvem (Continuous Integration) garantindo que a branch 'main' nunca quebre.",
            "Define os gatilhos ('push' e 'pull_request' na main). Provisiona uma VM 'ubuntu-latest', instala o gerenciador 'uv', baixa o Python 3.11, executa 'make install' e por fim roda 'make test'. Se qualquer teste falhar, o workflow retorna vermelho e bloqueia o PR.",
            language="yaml",
        ),
        divider(),
        h1("4. Resultado Final"),
        bullet("Pipeline executando de ponta a ponta na nuvem em ~13 segundos com 100% de aprovação."),
        bullet("Base de Engenharia de Dados (DE-01 a DE-06) oficialmente concluída!"),
    ]
    create_child_page("DE-06 · Integração Contínua (CI) com GitHub Actions", "🤖", de06_blocks)

    # =========================================================================
    # 7. DS-01: YOLO Detector
    # =========================================================================
    ds01_blocks = [
        callout(
            "DS-01 · Visão Computacional Espacial: Como integramos a rede neural YOLOv8 para detectar pedestres frame a frame (e descobrimos por que ela ignorou o vídeo sintético!).",
            "👁️",
        ),
        divider(),
        h1("1. O Problema que Precisávamos Resolver"),
        p(
            "Um computador vendo um vídeo enxerga apenas uma matriz gigante de pixels coloridos. A primeira etapa de Inteligência Artificial do MoveSense é localizar onde estão os pedestres em cada imagem isolada. Escolhemos o YOLOv8 Nano ('yolov8n.pt') pela altíssima velocidade e compatibilidade futura com o acelerador Hailo-8L no Raspberry Pi 5 (atendendo ao Issue #9 do GitLab)."
        ),
        h1("2. Passo a Passo Executado (TDD + Prática Visual)"),
        numbered("Criar branch 'feat/DS-01-yolo-detector' a partir da main."),
        numbered("FASE RED: Criar 'tests/test_detector.py' definindo o contrato de 'Detection' e 'PedestrianDetector'. Confirmar a falha esperada ('No module named movesense.detector')."),
        numbered("FASE GREEN: Criar 'src/movesense/detector.py' carregando o modelo 'YOLO(model_name)', filtrando apenas a classe 0 ('person') e convertendo caixas de 'xyxy' para 'xywh'. Rodar pytest (3 passed!)."),
        numbered("FASE EXECUTION: Criar 'scripts/run_detector.py' e adicionar 'make step-06' ao Makefile."),
        numbered("Rodar 'make step-06' no vídeo sintético e investigar por que retornou 0 detecções."),
        numbered("Validar o detector em uma fotografia urbana real de Sevilha ('ultralytics/assets/bus.jpg') e renderizar as caixas verdes em 'outputs_local/detected_pedestrians.jpg'."),
        numbered("Fazer commit e merge na main."),
        code(
"""git checkout -b feat/DS-01-yolo-detector
python -m pytest tests/test_detector.py  # RED -> GREEN (3 passed)
python -m pytest                         # Total: 9 passed
make step-06                             # Roda YOLO no vídeo sintético""",
            "shell",
        ),
        h1("3. Cada Arquivo Criado, Por que Existe e Sua Função Exata"),
        *file_section(
            "tests/test_detector.py",
            "Garante que a interface do nosso detector funcione independentemente da versão da biblioteca Ultralytics e que aceite imagens no formato NumPy do OpenCV.",
            "Testa 3 coisas: se 'Detection' armazena x, y, w, h, conf corretamente; se 'PedestrianDetector' inicializa com o class ID 0 (pessoa); e se uma imagem preta (sem pessoas) retorna uma lista vazia sem quebrar o código.",
            language="python",
        ),
        *file_section(
            "src/movesense/detector.py",
            "Padrão de projeto Adapter/Wrapper: isola toda a complexidade interna da biblioteca YOLO/PyTorch do resto do nosso pipeline. Se depois quisermos trocar YOLOv8 por RT-DETR, mudamos apenas este arquivo.",
            "Define a dataclass 'Detection' (padronizando a saída) e a classe 'PedestrianDetector'. O método '.detect(frame)' passa o frame BGR para a rede neural, ignora classes que não sejam 'person' (cls_id != 0), transforma cantos (x1, y1, x2, y2) em (x, y, largura, altura) e retorna a lista limpa de detecções.",
            language="python",
        ),
        *file_section(
            "scripts/run_detector.py",
            "Permite rodar o detector em lote sobre qualquer arquivo de vídeo completo com barra de progresso e exportar as detecções no padrão MOT.",
            "Abre 'data/synthetic/synthetic_video.avi' com 'cv2.VideoCapture', itera frame por frame com 'tqdm', chama 'detector.detect(frame)' e grava em 'data/synthetic/detections_yolo.txt' usando '-1' na coluna de Track ID (pois detecção espacial pura ainda não possui identidade temporal).",
            language="python",
        ),
        divider(),
        h1("4. Grande Lição Científica Aprendida"),
        callout(
            "Por que o YOLO detectou 0 pessoas no 'synthetic_video.avi'?\n"
            "Porque o vídeo sintético contém apenas retângulos verdes desenhados em fundo cinza! O YOLOv8 foi treinado em milhares de fotografias reais do dataset COCO; ele procura cabeças, troncos, pernas e texturas humanas. Isso provou que nosso detector não 'alucina' humanos onde só há geometria. Ao testar na foto real de Sevilha ('bus.jpg'), o modelo detectou imediatamente 4 pedestres com até 86.5% de confiança!",
            "🧠",
        ),
    ]
    create_child_page("DS-01 · Detector de Pedestres YOLOv8 (Ultralytics)", "👁️", ds01_blocks)

    # =========================================================================
    # 8. DS-02: IoU Tracker
    # =========================================================================
    ds02_blocks = [
        callout(
            "DS-02 · Memória Temporal: Como criamos um Tracker IoU do zero para conectar caixas entre frames e manter a identidade contínua de cada pedestre.",
            "🎯",
        ),
        divider(),
        h1("1. O Problema que Precisávamos Resolver"),
        p(
            "Um detector (DS-01) sofre de amnésia temporal: ele olha para cada frame isoladamente e devolve caixas sem ID. Para saber a velocidade ou o comportamento de uma pessoa, precisamos acompanhar exatamente o mesmo indivíduo do frame 1 até o frame 100 mantendo um identificador único ('track_id')."
        ),
        h1("2. Passo a Passo Executado (TDD + Ajuste de Integração)"),
        numbered("Criar branch 'feat/DS-02-iou-tracker' a partir da main."),
        numbered("FASE RED: Criar 'tests/test_tracker.py' testando atribuição do ID 1, manutenção do ID 1 quando a caixa anda ligeiramente no próximo frame, e separação de IDs {1, 2} para pessoas distantes."),
        numbered("FASE GREEN: Criar 'src/movesense/tracker.py' implementando a matemática de IoU (Intersection over Union) e o gerenciador de estado 'SimpleTracker'."),
        numbered("Rodar 'python -m pytest tests/test_tracker.py' (3 passed!) e depois 'python -m pytest' (12 passed!)."),
        numbered("FASE EXECUTION: Criar 'scripts/run_tracker.py' e 'make step-07'. Corrigimos inclusive o acesso às colunas ('x', 'y', 'w', 'h' em vez de 'bb_left') integrando perfeitamente com o nosso loader do DE-05!"),
        numbered("Rodar 'make step-07' e gerar o arquivo 'data/synthetic/tracks.txt'."),
        numbered("Fazer commit e merge na main."),
        code(
"""git checkout -b feat/DS-02-iou-tracker
python -m pytest tests/test_tracker.py  # RED -> GREEN (3 passed)
python -m pytest                        # Total: 12 passed
make step-07                            # Gera data/synthetic/tracks.txt""",
            "shell",
        ),
        h1("3. Cada Arquivo Criado, Por que Existe e Sua Função Exata"),
        *file_section(
            "tests/test_tracker.py",
            "Valida o algoritmo de associação espacial sem precisar de vídeo pesado, usando caixas coordenadas simuladas frame a frame.",
            "Garante que o tracker cria IDs sequenciais (1, 2...), mantém o mesmo ID quando duas caixas têm sobreposição espacial suficiente (IoU >= 0.3) e não confunde duas pessoas em cantos opostos da imagem.",
            language="python",
        ),
        *file_section(
            "src/movesense/tracker.py",
            "Implementa a camada de associação temporal do pipeline MoveSense usando matemática geométrica pura (base conceitual do algoritmo SORT).",
            "Contém 3 componentes: (1) Dataclass 'Track' que guarda o histórico de cada pessoa (ID, posição atual, idade e contador 'misses'); (2) Função 'calculate_iou()' que calcula a área de intersecção dividida pela união de dois retângulos; e (3) Classe 'SimpleTracker' que, no método '.update()', casa tracks antigos com novas detecções pelo maior IoU, tolera até 3 frames de sumiço (oclusão) antes de descartar um track e cria novos IDs para detecções inéditas.",
            language="python",
        ),
        *file_section(
            "scripts/run_tracker.py",
            "Liga o Data Engineering (loader do DE-05) ao Tracker (DS-02) em um fluxo completo executável via terminal.",
            "Lê o arquivo 'data/synthetic/gt.txt' via 'load_mot_file()', extrai as caixas por frame simulando detecções sem ID, alimenta o 'SimpleTracker' frame a frame e grava as trajetórias rastreadas em 'data/synthetic/tracks.txt' no formato oficial MOT.",
            language="python",
        ),
        divider(),
        h1("4. Resultado Final"),
        bullet("Processou 100 frames a ~28.000 iterações por segundo!"),
        bullet("Rastreou todos os 5 pedestres (IDs [1, 2, 3, 4, 5]) com ZERO trocas de identidade (ID switches)."),
        bullet("Suíte completa atingiu 12 testes verdes."),
    ]
    create_child_page("DS-02 · Tracker de Pedestres (Associação Espacial IoU)", "🎯", ds02_blocks)

    # =========================================================================
    # 9. DS-03: Trajectory Features
    # =========================================================================
    ds03_blocks = [
        callout(
            "DS-03 · Engenharia de Features Cinemáticas: Como transformamos trajetórias de pixels em variáveis físicas (Velocidade, Aceleração e Raio de Confinamento) para Machine Learning.",
            "📈",
        ),
        divider(),
        h1("1. O Problema que Precisávamos Resolver"),
        p(
            "Classificadores de Machine Learning (como Random Forest no DS-04) não entendem sequências cruas de coordenadas x, y ao longo de 100 frames. Eles precisam de uma tabela resumida onde cada linha representa um pedestre (track_id) e cada coluna representa uma grandeza física discriminativa capaz de distinguir quem está parado, andando, correndo ou vadiando (loitering)."
        ),
        h1("2. Passo a Passo Executado (Ciclo TDD)"),
        numbered("Criar branch 'feat/DS-03-trajectory-features' a partir da main."),
        numbered("FASE RED: Criar 'tests/test_features.py' validando contas físicas conhecidas: (1) um pedestre andando 10 px/frame a 25 FPS deve ter exatamente velocidade média de 250.0 px/s e aceleração 0.0; (2) um pedestre parado deve ter velocidade e raio de confinamento 0.0."),
        numbered("FASE GREEN: Implementar 'src/movesense/features.py' usando NumPy e Pandas para vetorização matemática rápida."),
        numbered("Rodar 'python -m pytest' e comprovar 15 testes verdes passando em 3.48s!"),
        numbered("FASE EXECUTION: Criar 'scripts/extract_features.py' e adicionar 'make step-08' no Makefile."),
        numbered("Rodar 'make step-08', visualizar a tabela executiva por pedestre no terminal e salvar a base final 'data/synthetic/trajectory_features.csv'."),
        numbered("Fazer commit e merge na main."),
        code(
"""git checkout -b feat/DS-03-trajectory-features
python -m pytest tests/test_features.py  # RED -> GREEN (3 passed)
python -m pytest                         # Total: 15 passed
make step-08                             # Extrai trajectory_features.csv""",
            "shell",
        ),
        h1("3. Cada Arquivo Criado, Por que Existe e Sua Função Exata"),
        *file_section(
            "tests/test_features.py",
            "Fórmulas de física e estatística em arrays NumPy podem esconder erros de índice ('off-by-one') ou de escala de FPS. Este teste prova a exatidão matemática.",
            "Contém 3 testes unitários: velocidade constante (250 px/s a 25 FPS), pedestre estático (tudo zerado) e agregação de múltiplos pedestres num único DataFrame tabular.",
            language="python",
        ),
        *file_section(
            "src/movesense/features.py",
            "É a ponte matemática entre a Visão Computacional (tracking) e a Ciência de Dados tabular (classificação de comportamentos dos Issues #3 e #6 do GitLab).",
            "A função 'extract_track_kinematics()' calcula o centroide (cx, cy), distâncias euclidianas passo a passo com 'np.diff', velocidades instantâneas multiplicando pelo FPS, aceleração média e o raio de confinamento (distância máxima percorrida em relação à origem). A função 'extract_trajectory_features()' agrupa todos os tracks do vídeo e devolve um DataFrame estruturado (1 linha por pessoa).",
            language="python",
        ),
        *file_section(
            "scripts/extract_features.py",
            "Executa todo o extrator sobre os dados reais rastreados ('tracks.txt'), aplica regras cinemáticas preliminares para diagnóstico visual e gera o dataset tabular para o DS-04.",
            "Lê 'data/synthetic/tracks.txt', extrai a tabela com 'extract_trajectory_features()', aplica a heurística 'classify_preliminary_behaviour' (standing / loitering / walking / running), imprime o relatório no terminal e exporta 'data/synthetic/trajectory_features.csv'.",
            language="python",
        ),
        *file_section(
            "Makefile",
            "Versão consolidada do painel de comandos do projeto até a etapa DS-03.",
            "Centraliza toda a esteira reproduzível do MoveSense: install, test, step-02 (gerar dados), step-04 (renderizar vídeo), step-05 (inspecionar), step-06 (detector YOLO), step-07 (tracker IoU) e step-08 (extrator de features).",
            language="makefile",
        ),
        divider(),
        h1("4. Resultado Final"),
        bullet("Base tabular 'data/synthetic/trajectory_features.csv' criada e pronta para alimentar modelos de Machine Learning no DS-04."),
        bullet("15 testes automatizados verdes aprovados em 3.48s."),
        bullet("Integrado na branch 'main' com histórico Git limpo!"),
    ]
    create_child_page("DS-03 · Extrator de Features Cinemáticas de Trajetória", "📈", ds03_blocks)

    print("\n🎉 Todas as 9 páginas detalhadas foram atualizadas com sucesso no Notion!")


if __name__ == "__main__":
    main()
