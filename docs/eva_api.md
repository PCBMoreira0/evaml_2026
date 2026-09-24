# Documentação da API (`eva_api.py`) e da Interface Web

Este documento explica a camada que expõe o simulador (ver [`simulador.md`](./simulador.md)) para um navegador. **O motor de execução não depende desta camada** — ela apenas o controla passo a passo através de uma API HTTP.

## Visão geral

```
┌──────────────┐   HTTP (fetch)   ┌─────────────┐   chama métodos   ┌───────────────┐
│  Navegador   │ ───────────────▶ │  eva_api.py │ ─────────────────▶│  ScriptEngine  │
│ (index.html) │ ◀─────────────── │   (Flask)   │ ◀──────────────── │ (script_engine)│
└──────────────┘   JSON (estado)  └─────────────┘   estado atual    └───────────────┘
```

- A interface nunca executa lógica do script: ela só chama endpoints (`/api/step`, `/api/back`...) e desenha o JSON de estado que volta.
- O `eva_api.py` é **um cliente do motor**, igual poderia ser um script Python simples (veja o final de [`simulador.md`](./simulador.md)). Substituí-lo por outra API não exige mudar o motor.

## Um passo por vez: por que a execução é "passo a passo"

O motor (`ScriptEngine`) não tem um "rodar até o fim" — ele expõe `play_next()`, que executa **exatamente um nó do XML** e retorna. A API expõe isso como o endpoint `/api/step` ("Avançar"). O "modo automático" da interface é só um laço no JavaScript que chama `/api/step` repetidamente com um intervalo entre chamadas — não existe um modo automático dentro do motor.

## Os endpoints

| Endpoint | Ação no motor | Quando usar |
|---|---|---|
| `POST /api/load` | `ScriptEngine()` + `load_script()` + `initialize()` | Carrega um arquivo `.xml` da pasta `eva_scripts/`. |
| `POST /api/start` | `start_script(modo)` | Executa a seção `<settings>` e posiciona o cursor no primeiro nó do `<script>`. |
| `POST /api/step` | `play_next()` | Executa o nó atual e avança o cursor. |
| `POST /api/repeat` | `previous()` + `play_next()` | Desfaz o último passo e o executa de novo (útil quando o robô não fez o esperado). |
| `POST /api/back` | `previous()` | Desfaz o último passo, sem reexecutar. |
| `POST /api/reset` | `reset()` | Volta ao início do `<script>`, com a memória limpa. |
| `POST /api/input` | Só alimenta uma fila | Entrega o texto digitado a um `<listen>`/`<qrRead>`/`<userEmotion>` que está esperando, em modo `terminal`. |
| `GET /api/scripts` | — | Lista os arquivos `*_evaml.xml` disponíveis em `eva_scripts/`. |
| `POST /api/log/start`, `/stop`, `GET /api/log/status`, `/api/log/path` | — | Controlam o `LogCollector` (grava os `<log>` do script em CSV), independente do motor. |

Toda resposta (função `result()`) devolve o mesmo formato de estado: `state`, `previous`/`current`/`upcoming` (os três últimos nós, para a interface desenhar os três "slots"), `history` (quantos passos dá pra voltar), `log` (linhas novas impressas desde a última chamada) e `error`.

## Truques para lidar com comandos que bloqueiam (MQTT_PUB_SUB)

Como vimos em `simulador.md`, um `<talk>` ou `<qrRead>` pode ficar **minutos** esperando resposta do robô. Isso cria dois problemas que a API resolve:

### 1. Só uma operação por vez (trava de exclusividade)

Enquanto um `/api/step` está esperando o robô responder, outra requisição não pode alterar o motor no meio do caminho (ex.: um "Repetir" clicado por engano enquanto o "Avançar" anterior ainda não voltou). Por isso `/api/load`, `/api/start` e `/api/step` usam o decorador `@exclusive`: se o motor já está ocupado, a requisição é recusada com HTTP 409 (`"Ocupado: aguarde..."`) em vez de interferir.

### 2. Interromper uma espera (`/api/back` e `/api/reset`)

"Voltar" e "Voltar ao início" usam o decorador `@interrupting` em vez de `@exclusive`: se o motor estiver esperando uma resposta (por exemplo, esperando alguém mostrar um QR code), esses dois **cancelam a espera em andamento** e seguem a operação. Isso é o que permite ao usuário desistir de um passo travado sem precisar reiniciar a página.

```
        thread do /api/step (esperando QR code)          thread do /api/back
                    │                                            │
                    │  bloqueado em receive()                    │  chama cancel_waits()
                    │                                            │
                    │◀── recebe uma marca "CANCEL" na fila ──────│
                    │                                            │
        levanta ResponseCancelled                                │
                    │                                            │
        run_step() desfaz o passo (engine.previous())            │
                    │                                            │  segue com engine.previous()
```

- O cancelamento é implementado no comunicador MQTT (`pub_sub_mqtt_communicator.py`): o método `cancel()` coloca uma marca especial na fila de respostas, que acorda o `receive()` bloqueado e faz ele levantar `ResponseCancelled`.
- Se a espera era por texto digitado (modo `terminal`), a mesma ideia se aplica à fila do `WebStdin`.
- Depois de cancelar, `run_step()` desfaz o passo (`engine.previous()`), então o motor nunca fica "preso" em `BLOCKED`.

### 3. Tempo limite (timeout)

Além de poder ser cancelado manualmente, todo `receive()` tem um tempo limite (configurado em `config.py`, com exceções por tópico). Se o robô nunca responder, o simulador desiste automaticamente depois desse tempo, e o passo é desfeito do mesmo jeito que numa interrupção manual — a diferença é só a mensagem de erro (`ResponseTimeout` em vez de `ResponseCancelled`).

## A interface (`templates/index.html`)

Uma única página, sem framework de front-end — HTML + um bloco `<script>` com funções simples que chamam `fetch()`.

```
Carrega/Inicia  →  [Avançar] → mostra o resultado
                  ↺ [Repetir]         │
                  ◂ [Voltar]  (funciona mesmo com Avançar em andamento)
                  [Modo automático] = repete "Avançar" com um intervalo, até
                                       o estado deixar de ser PLAY ou dar erro
```

Pontos que valem explicação:

- **Três "slots" (`previous`/`current`/`upcoming`):** a tela sempre mostra o nó anterior, o que acabou de ser executado, e o que será executado no próximo "Avançar" — isso ajuda a acompanhar onde o script está sem precisar abrir o XML.
- **Campo de entrada (`#inputBox`):** só aparece nos modos `terminal`/`terminal-plus`, para os comandos que pedem valor digitado (`listen`, `qrRead`, `userEmotion`). Nos modos com robô/simulador reais, o valor chega por MQTT, então esse campo fica escondido.
- **Modo automático:** um laço no JavaScript (`while (auto) { ...; await doStep(); ... }`) que só continua enquanto o estado voltar `PLAY` sem erro. Ele para sozinho ao fim do script, num erro, ou se o usuário clicar em "Pausar".
- **Ignorar resposta de um passo cancelado:** quando "Voltar" cancela um `/api/step` em andamento, as duas requisições respondem quase juntas. A tela ignora a resposta do passo cancelado (`error` começando com `ResponseCancelled`) para não mostrar por um instante o nó errado.

## Logs (aba "logs (csv)")

Independente da execução do script, a API pode ligar um `LogCollector` (`log_collector.py`), que escuta o tópico MQTT `EVA/LOG` e grava um arquivo `.csv` por nome de log (o atributo `name` de `<log>`). Isso serve para coletar dados de um experimento (por exemplo, respostas certas/erradas de um script como `teste_psicologia`) sem misturar essa gravação com a lógica de execução do script.
