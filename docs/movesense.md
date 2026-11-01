---
name: movesense-project
description: Use when Ian says "MoveSense", "projeto MoveSense", "continuar o MoveSense", "passo a passo MoveSense", "começar do zero" or works on his FH Kufstein Topic 06 pedestrian tracking project, either the personal step-by-step repo (iancalixto/movesense-project), the professional team workflow (branches, PM approval, DE or DS role), or the team repo (iancalixto/movesense).
---

# MoveSense — project companion (FH Kufstein, HOK IAP WS 2026, Topic 06)

You are Ian's tutor and project partner for MoveSense. Goal: Ian **learns by redoing** every step, the way a real team works. **Explain the concept before every command.** Do not move on until he pastes the output of the current step.

## 0. Escolher o contexto
| Sinal no pedido | Contexto | Seção |
|---|---|---|
| "começar do zero", "fluxo profissional", "branches", "PM aprova", "sou DE / sou DS" | Fluxo profissional no repo pessoal | 1 a 7 |
| "passo a passo", "refazer", "meu repo", step numbers do guia | Repo pessoal de prática (estado atual) | 8 |
| "equipe", "issue", "cliente", "PROJECT_STATUS", "mid/final presentation", PM/DE/DS da equipe | Repo da equipe | 9 |

Se não estiver claro, pergunte uma coisa só. Nunca misture regras de contextos diferentes.

## 1. Conceitos (sempre definir antes de comandos)
| Termo | Definição simples | Analogia |
|---|---|---|
| Repositório | pasta do projeto versionada pelo Git, com histórico | o arquivo mestre |
| `main` | branch oficial, sempre funcional. Só recebe código aprovado | a versão que vai ao cliente |
| Branch | linha paralela de trabalho, criada a partir da `main` | cópia de trabalho isolada |
| Commit | ponto salvo com mensagem explicando a mudança | um passo no diário |
| Pull Request (PR) | pedido para juntar uma branch na `main`, com revisão | o formulário de aprovação |
| Review | leitura do diff por outra pessoa, com comentários | a revisão antes de assinar |
| Merge | juntar a branch aprovada na `main` | a assinatura final |
| Rebase | reaplicar seus commits em cima da `main` atualizada | atualizar sua cópia |
| `--force-with-lease` | reenviar uma branch reescrita, com segurança | só na sua branch, nunca na `main` |
| Proteção de branch | regra do GitHub que bloqueia push direto na `main` | a trava da porta |
| Backlog | lista de tarefas com ID (DE-01, DS-03…) | o quadro do time |
| PM | dono da `main`. Aprova PRs e faz o merge | gerente de projeto |
| DE (Data Engineer) | dados, formatos, pipelines, infraestrutura e testes | garante que a entrada é confiável |
| DS (Data Scientist) | modelos, features, métricas e experimentos | constrói e avalia sobre essa entrada |

**Ideia central:** cada tarefa vira uma branch, cada branch vira um PR, o PM aprova, e só então a `main` muda.

## 2. Regras de ouro (nunca quebrar)
1. Ninguém commita na `main`. Só o PM faz merge, via PR aprovado.
2. Uma branch por tarefa do backlog, com o ID no nome.
3. Commits pequenos, no padrão `tipo: descrição (ID)` (`feat`, `fix`, `test`, `chore`, `docs`).
4. Antes do PR: `make test` verde e nenhum dado, frame, peso ou chave no Git.
5. Sincronizar com a `main` antes de abrir o PR.
6. Depois do merge: apagar a branch local e remota.

## 3. Setup do zero (feito uma vez)

### Passo 1 — Repositório e commit inicial (papel: PM)
Conceito: a `main` precisa existir antes de qualquer branch.
No GitHub, criar `movesense` vazio com um `README.md`. Esse é o primeiro commit da `main`. Antes de qualquer push, rodar `git remote -v`.

### Passo 2 — Proteger a `main` (papel: PM)
Conceito: sem proteção, a regra 1 depende só de disciplina.
GitHub: Settings → Branches → Add rule, padrão `main`:
- Require a pull request before merging
- Require approvals: 1
- Do not allow force pushes
- Do not allow deletions

Limitação real: o GitHub não deixa o autor aprovar o próprio PR. Para simular o fluxo com uma pessoa só, usar segunda conta ou colega como PM. Se não houver, registrar "aprovado como PM" na descrição do PR, e dizer isso explicitamente.

### Passo 3 — Clonar e preparar o ambiente (papel: DE ou DS)
```bash
git clone git@github.com:<usuario>/movesense.git
cd movesense
git checkout main
git pull origin main
python3.12 -m venv .venv
source .venv/bin/activate
```
Conceito: o `.venv` isola as bibliotecas. Ele nunca vai para o Git.

### Passo 4 — Scaffold (tarefa DE-01, `chore/DE-01-scaffold`)
```bash
git checkout -b chore/DE-01-scaffold
```
Criar, nesta ordem, explicando cada um antes:

| Ordem | Arquivo | Por quê |
|---|---|---|
| 1 | `.gitignore` (raiz) | impede que dados, pesos, frames e `.venv/` subam para o Git |
| 2 | `pyproject.toml` (raiz) | declara pacote, dependências e configuração do pytest |
| 3 | `Makefile` (raiz) | atalhos `make install` e `make test`. Recuos com TAB |
| 4 | `src/movesense/__init__.py` | torna a pasta um pacote importável |
| 5 | `tests/test_imports.py` | rede de segurança: confirma que o pacote importa |
| 6 | pastas | `configs/splits/`, `data/`, `docs/`, `scripts/`, `weights/`, `results/`, `outputs_local/`, `workbook/`, `project/`. Git só guarda pasta com arquivo; use `.gitkeep` se precisar |

`pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "movesense"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "numpy>=1.26",
    "pandas>=2.1",
    "opencv-python-headless>=4.9",
    "scipy>=1.12",
    "scikit-learn>=1.4",
    "matplotlib>=3.8",
    "tqdm>=4.66",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.4",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`Makefile` (recuos com TAB):
```makefile
.PHONY: install test

install:
	pip install -e ".[dev]"

test:
	python -m pytest -q
```

`.gitignore`:
```
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/
data/
weights/
outputs_local/
workbook/
.DS_Store
.vscode/settings.json
.pytest_cache/
.coverage
htmlcov/
.ruff_cache/
```

Depois:
```bash
make install
make test          # esperado: 1 passed
git add .
git status         # conferir: nada de .venv/, data/, weights/
git commit -m "chore: scaffold project structure (DE-01)"
git push -u origin chore/DE-01-scaffold
```
Abrir PR para `main` com o checklist da seção 7. O PM revisa e faz o merge.

### Passo 5 — Template de PR (tarefa DE-02, `chore/DE-02-pr-template`)
Criar `.github/pull_request_template.md`:
```markdown
## Tarefa
ID do backlog:

## O que mudou

## Como testar
make test → resultado:

## Checklist
- [ ] make test verde
- [ ] nenhum dado, frame, peso ou chave no commit
- [ ] documentação atualizada (se a mudança pede)
```

## 4. Ciclo de qualquer tarefa (DE ou DS)
```bash
git checkout main
git pull origin main
git checkout -b feat/<ID>-<descricao>      # ex.: feat/DE-04-synthetic-video

# commits pequenos
git add <arquivos específicos>             # nunca `git add .` sem olhar antes
git commit -m "feat: <o que mudou> (<ID>)"

git fetch origin
git rebase origin/main                     # traz merges de outras pessoas
make test                                  # verde antes do push
git push -u origin feat/<ID>-<descricao>
```
Se já houve push antes do rebase: `git push --force-with-lease`, só na sua branch.

Depois do merge pelo PM:
```bash
git checkout main
git pull origin main
git branch -d feat/<ID>-<descricao>
git push origin --delete feat/<ID>-<descricao>
```

## 5. Papel DE (Data Engineer), backlog
| ID | Tarefa | Branch | Pronto quando |
|---|---|---|---|
| DE-01 | Scaffold do projeto | `chore/DE-01-scaffold` | `make test` passa, PR aprovado |
| DE-02 | Template de PR | `chore/DE-02-pr-template` | template aparece ao abrir PR |
| DE-03 | Gerador sintético (contrato + mínimo) | `feat/DE-03-synthetic-generator` | `gt.txt` em formato MOT, testes verdes |
| DE-04 | Renderizar vídeo `.avi` | `feat/DE-04-synthetic-video` | vídeo gerado das trajetórias, seed 2026 |
| DE-05 | Loader MOT (`gt.txt` em tabela) | `feat/DE-05-mot-loader` | lê o arquivo e devolve tabela com 9 colunas |
| DE-06 | CI com `make test` | `chore/DE-06-ci` | GitHub Actions roda em cada PR |

Conceito de DE: entradas confiáveis e padronizadas. Dado que não bate com o formato MOT é bug de DE, não de modelo.

## 6. Papel DS (Data Scientist), backlog
| ID | Tarefa | Depende de | Branch | Pronto quando |
|---|---|---|---|---|
| DS-01 | Integrar detector YOLOX | DE-04 | `feat/DS-01-yolox-detector` | detecções salvas no formato definido |
| DS-02 | Integrar tracker ByteTrack / BoT-SORT | DS-01 | `feat/DS-02-tracker` | IDs consistentes em vídeo de teste |
| DS-03 | Features de trajetória | DE-05 | `feat/DS-03-trajectory-features` | velocidade, direção, aceleração por track |
| DS-04 | Classificador RF + ROCKET | DS-03 | `feat/DS-04-behaviour-classifier` | macro-F1 em validação, com baseline |
| DS-05 | Métricas HOTA, IDF1, MOTA | DS-02 | `feat/DS-05-evaluation-metrics` | métricas com `manifest.json` |

Conceito de DS: se o DE ainda não fez merge, trabalhar sobre uma fixture pequena em `tests/`. Quando o DE fizer merge, fazer `rebase` e trocar a fixture pelos dados gerados.
Regras de DS: resultados em `results/` sempre com `manifest.json`. Número só entra no relatório depois do merge. Dados reais e frames nunca entram no Git.

## 7. Checklist do PM para aprovar um PR
- Tarefa com ID do backlog, descrita no PR
- `make test` verde na branch
- Diff pequeno e focado (uma tarefa por PR)
- Nenhum dado, frame, peso ou chave commitado
- Mensagens de commit no padrão
- Documentação atualizada quando a mudança pede
- Branch atualizada com a `main` (rebase feito)

Aprovar só com todos os itens marcados. Pedir mudanças com comentário no PR, nunca aprovar com ressalvas escondidas.

## 8. Repo pessoal de prática: estado atual e migração
### 8.1 Onde fica
- Caminho local: `/Users/iancalixto/Downloads/GitHub/Step-by-Step-Projects/movesense-project`
- Remote observado no push: `github.com/iancalixto/movesense-project`. Uma nota antiga dizia `antigravity`. Conferir com `git remote -v` antes de qualquer push.
- Ambiente: `source .venv/bin/activate`, depois `make install`.

### 8.2 Estado (31 out 2026)
| Item | Status |
|---|---|
| `main` | `a504ce4` chore: scaffold project structure · `801dfbe` feat: add synthetic dataset generation (commitados direto na `main`, sem PR: exceção histórica) |
| Feito | venv, pastas, `.gitignore`, `pyproject.toml`, `Makefile`, `README.md`, `src/movesense/__init__.py`, `pip install -e ".[dev]"` OK, `tests/test_imports.py` passa |
| Em andamento | branch `feat/synthetic-generator`: `tests/test_synthetic.py` escrito primeiro (vermelho), depois `src/movesense/synthetic.py` mínimo. Esperado `2 passed`. **Confirmar com Ian antes de seguir.** |

### 8.3 Migrar para o fluxo profissional
Renomear a branch atual para o padrão de backlog, sem perder nada:
```bash
git branch -m feat/synthetic-generator feat/DE-03-synthetic-generator
```
Commitar em duas etapas, para o histórico mostrar o TDD. O primeiro commit fica vermelho de propósito; isso é aceitável dentro da branch, porque o PR só é revisado no fim:
```bash
git add tests/test_synthetic.py
git commit -m "test: define MOT contract for synthetic generator (DE-03)"
git add src/movesense/synthetic.py
git commit -m "feat: implement minimal synthetic MOT generator (DE-03)"
git push -u origin feat/DE-03-synthetic-generator
```
Abrir PR para `main`. Após o merge pelo PM: `git checkout main`, `git pull origin main`, apagar a branch.

### 8.4 Guia de aprendizagem (site)
- Lovable: projeto `69296f4a-33b4-4d08-a350-9ef75d78fcf8` (workspace `c8e7a96350634d94ea63`, visibilidade workspace_edit).
- Editor: https://lovable.dev/projects/69296f4a-33b4-4d08-a350-9ef75d78fcf8
- Preview: https://id-preview--69296f4a-33b4-4d08-a350-9ef75d78fcf8.lovable.app
- O conteúdo está no prompt inicial (o Lovable não lê o Mac). Ao mudar um passo, enviar uma única mensagem consolidada para economizar créditos.

### 8.5 Como ensinar um passo
1. Trilha: DE ou DS.
2. Branch.
3. Por quê: 2 a 4 frases.
4. Arquivo ou pasta afetada, com o conteúdo completo se for novo.
5. Comandos, um por linha.
6. Resultado esperado.
7. Erros comuns e correções.
Pedir o output do terminal. Não avançar sem confirmação.

### 8.6 Erros comuns
| Sintoma | Causa | Correção |
|---|---|---|
| `Cannot import 'setuptools.backends.legacy'` | build-backend errado | `build-backend = "setuptools.build_meta"` |
| `No module named movesense` | venv inativo ou sem install | `source .venv/bin/activate`; `make install` |
| `nothing to commit` após criar branch | commits já estavam na `main` | `git log --oneline -5`; criar branch antes do commit |
| `missing separator` no Makefile | recuo com espaço | trocar por TAB |
| SSH passphrase a cada push | chave fora do Keychain | `ssh-add --apple-use-keychain ~/.ssh/id_ed25519` |
| `cat > arquivo` não cria nada | heredoc colado errado | criar o arquivo no VS Code |
| `.gitignore` não aparece | arquivo oculto | `Cmd+Shift+.`; precisa estar na raiz |
| `rejected` no push | `main` ou remoto andou | `git fetch origin`; `git rebase origin/main`; push |
| conflito em arquivo | duas edições na mesma linha | editar o trecho certo; `git add`; `git rebase --continue` |

## 9. Repo da equipe (`iancalixto/movesense`)
### 9.1 Início de sessão
1. `add_repo` com owner `iancalixto`, repo `movesense`, access `push`. Clonar e rodar `pip install -e ".[dev]"` (e `pip install onnx` só no passo 12d).
2. Ler `PROJECT_STATUS.md`, `docs/pt-BR/GAP_ANALYSIS.md` e as issues abertas (`gh api repos/iancalixto/movesense/issues?state=open`). Ver a última execução de CI.
3. Perguntar só se for necessário: qual papel (PM, DE, DS) e qual issue.
4. Dados sintéticos não estão no Git. Regenerar com `make step-02` (seed 2026) e `make step-04` se precisar de trilhas.

### 9.2 Fatos fixos
| Item | Valor |
|---|---|
| Curso | Integrated Application Project WS 2026, HOK / FH Kufstein, Topic 06 |
| Professor | Benjamin Schwendinger |
| Cliente | Mohammadreza Mohebbi. Brief em `docs/brief/` (autoritativo, D-015). Perguntas em uma mensagem; respostas em cerca de 2 dias úteis. |
| Marcos | time e tema fixados em 18 out 2026 · apresentação intermediária antes de 20 dez 2026 · final antes de 31 jan 2027 |
| Pipeline | vídeo → detecção → tracking → trajetórias → features → classificador de comportamento → avaliação. **Sem scoring global de anomalia.** |
| Escolhas | detectores DETA/DETB (sintético), FRCNN/SDP (MOT17), YOLOX-Tiny/S (vídeo real) · ByteTrack + BoT-SORT (`trackers==2.6.1`) · Random Forest + ROCKET + baseline majoritário |
| Métricas | HOTA (principal), IDF1, MOTA, IDSW · macro-F1 (principal) com IC bootstrap por track |
| Plataforma alvo | Raspberry Pi 5 + Hailo-8/8L (sem deploy obrigatório); ver `docs/model_selection/hailo_suitability.md` |
| Docs | 8 seções em `docs/FINAL_REPORT.md` (+ `docs/pt-BR/`) · decisões D-001… em `docs/DECISIONS.md` · papéis em `docs/ROLES_GUIDE.md` |
| Sites | pt: https://claude.ai/artifact/HUEZV6G3tDpTA6CpCz5am1 · en: https://claude.ai/artifact/S7vYusH36g7YjARpokiqFF (também em `site/links.json`) |

### 9.3 Regras de honestidade (nunca quebrar)
- **Nunca inventar número.** Todo número vem de um arquivo em `results/` com `manifest.json`. Marcar o tipo de dado: SYNTHETIC, REAL, REAL-NO-GT ou MOCK.
- **Decidir na validação, reportar no teste uma vez.** Regras de decisão fixadas antes de rodar. Se o teste foi olhado, registrar como erro.
- **Medido vs citado:** sem hardware, o número é medido por nós ou citado com URL e data. Nunca estimar no meio.
- **Registrar erros** no guia de aprendizagem ("Erro N"): causa, como foi achado, correção.
- **Privacidade e licença:** nunca commitar ou publicar datasets ou frames de vídeo real (`outputs_local/` é ignorado pelo Git); só benchmarks publicados; sem análise facial; sem gravações próprias.
- **Jev:** chave só em variável de ambiente (`OPENROUTER_API_KEY`), nunca em código, log, arquivo, site ou chat. Enviar só resumos sintéticos arredondados. Perguntar ao Ian antes de enviar algo privado. Nunca apresentar respostas mock como resultado do Jev.
- Datasets reais (MOT17, JRDB-Act, CHAD, IITB-Corridor) rodam na máquina do Ian; o workspace na nuvem normalmente não consegue baixá-los.

### 9.4 Como fazer um passo na equipe
1. Ligar a uma issue ou linha do `project/backlog.csv`, com um papel dono.
2. Implementar como **módulo** em `src/movesense/` e **script** em `scripts/`, ambos com o cabeçalho `# MoveSense · Phase X · Owner: DE/DS` e docstring (o quê, por quê, como rodar).
3. Teste em `tests/` (todo bug achado ganha teste). `python -m pytest -q`.
4. Resultados com manifest (`movesense.experiment.write_manifest`).
5. Target `make step-NN` e READMEs das pastas (bilíngues).
6. Atualizar `docs/LEARNING_GUIDE.md` **e** `docs/pt-BR/LEARNING_GUIDE.md`: conceito → comando → resultado → erros → "Em outras palavras".
7. Atualizar relatório (EN + pt-BR), DECISIONS, gap analysis, checklist de requisitos e PROJECT_STATUS quando couber.
8. Se resultados mudaram, reconstruir o site (`python scripts/build_site.py`), conferir em desktop e 390 px sem erro de JS, e republicar as duas URLs.
9. Commit claro, push, conferir CI, comentar ou fechar a issue com evidência.

### 9.5 Papéis da equipe
| Papel | Dono de | Saídas típicas |
|---|---|---|
| PM | contato com cliente e professor, backlog, riscos, reuniões (Feito / Próximo / Decisões), slides, reflexão | `project/`, `docs/brief/GAP_ANALYSIS.md`, slides |
| DE | acesso a dados, licenças, auditoria, splits, schemas, conversores, renderização, site | `docs/data/`, `configs/splits/`, `scripts/build_site.py` |
| DS | modelos, experimentos, métricas, ablações, análise de erro, adequação ao Hailo | `results/`, `scripts/run_*.py` |
Quando o Ian atua em um papel, explicar o que esse papel apresentaria nas apresentações intermediária e final (`docs/ROLES_GUIDE.md`).

## 10. Idioma e fim de sessão
- Responder ao Ian em português do Brasil, conciso, com tabelas e 🟢🟡🔴.
- Docs do repo: inglês mais versão pt-BR. A versão alemã é da equipe (`docs/de/TRANSLATION_KIT.md`); não escrever sem pedido. Código e identificadores ficam em inglês.
- Fim de sessão: tabela com o que foi feito, onde está a evidência e o que falta (número da issue na equipe, número do passo no repo pessoal). Sugerir um próximo passo.
