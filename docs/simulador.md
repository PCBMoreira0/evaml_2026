# Documentação do Simulador EvaML

Este documento explica como o simulador executa um script EvaML e como cada comando se comunica com o robô (real ou simulado). Para a API web e a interface, veja [`eva_api.md`](./eva_api.md).

## Visão geral

Um script EvaML é um arquivo XML com uma seção `<settings>` (configurações globais) e uma seção `<script>` (a sequência de comandos). O simulador lê esse XML, carrega um módulo Python para cada tipo de comando usado, e executa os comandos um a um, avançando um cursor pela árvore XML.

```
arquivo .xml  →  evaml_parser.py  →  arquivo _evaml.xml  →  ScriptEngine executa
 (script fonte)   (valida + expande     (script final,        (script_engine.py)
                   loops + preenche      pronto para rodar)
                   atributos fixos)
```

**Por que existem dois arquivos XML?** O script fonte (`nome.xml`) é o que você edita, e pode usar atalhos como `<loop times="5">`. O `evaml_parser.py` valida esse arquivo contra o schema (`robot_package/xml_schema/`), preenche atributos fixos/padrão (como `pubTopic`) e expande `<loop>` em `<switch>`/`<counter>`/`<goto>` equivalentes, gerando `nome_evaml.xml`. É esse segundo arquivo que o simulador executa.

## As três peças principais

| Peça | Arquivo | Responsabilidade |
|---|---|---|
| Motor de execução | `script_engine.py` | Percorre o XML, mantém o estado (`PLAY`, `BLOCKED`, `IDLE`...) e despacha cada nó para o módulo certo. |
| Memória do robô | `robot_memory.py` | Guarda variáveis do script (`vars`, `$`), a pilha de retorno de laços/macros, e o modo de execução atual. |
| Carregador de módulos | `module_loader.py` | Para cada tag usada no script, importa `robot_package/<tag>_module/<tag>_module.py` e cria o objeto de comunicação (MQTT, HTTP ou nenhum) que aquele nó pediu. |

Cada comando (`<talk>`, `<audio>`, `<motion>`...) tem seu próprio módulo em `robot_package/`, todos implementando o mesmo contrato:

```python
class CommandHandler(BaseCommandHandler):
    def node_process(self, xml_node, memory):
        ...            # lê atributos do nó, manda mensagens, atualiza a memória
        return xml_node # ou outro nó, no caso de <goto>/<useMacro>/<switch>
```

## Os três modos de execução

O atributo `commMode` de cada nó, e o modo escolhido ao iniciar o script, decidem **como** um comando se comunica:

| Modo (`running_mode`) | Uso típico | O que os comandos fazem |
|---|---|---|
| `terminal` | Testar a lógica do script sem hardware | Comandos de entrada (`listen`, `qrRead`, `userEmotion`, `userid`) pedem um valor digitado no terminal. Comandos de saída (`talk`, `motion`...) só imprimem o que fariam. |
| `terminal-plus` | Igual ao terminal, mas para telas que mostram entrada | Mesmo comportamento do `terminal` (usado pela interface web). |
| `robot` | Executar de verdade, via MQTT | Cada comando publica e/ou espera resposta em um tópico MQTT (ver seção seguinte). |

Independentemente do modo de execução, cada **nó** também tem seu próprio `commMode`, que escolhe o comunicador daquele nó específico:

| `commMode` | Comunicador (`communicator_factory.py`) | Comportamento |
|---|---|---|
| `NULL` | `NullCommunicator` | Não comunica nada (ex.: `<counter>`, `<wait>`). |
| `MQTT_PUB` | `PubMqttCommunicator` | Publica uma mensagem e segue, sem esperar resposta ("dispare e esqueça"). |
| `MQTT_PUB_SUB` | `PubSubMqttComunicator` | Publica um comando **e bloqueia** esperando uma resposta em outro tópico. |
| `HTTP` | `HttpCommunicator` | Envia por HTTP em vez de MQTT. |

## Comunicação MQTT_PUB_SUB: o padrão pedido/resposta

Este é o padrão usado por comandos que precisam esperar o robô terminar algo: `talk`, `audio` (quando `block="TRUE"`), `listen`, `qrRead`, `userEmotion`, `userid`.

```
Simulador                         Broker MQTT                    Robô (ou simulador de robô)
    │                                  │                                  │
    │── publica em <pubTopic> ────────▶│── entrega ─────────────────────▶│
    │                                  │                                  │  (executa a ação:
    │                                  │                                  │   fala, ouve, lê QR...)
    │◀── espera em <subTopic> ─────────│◀── publica em <subTopic> ───────│
    │  (bloqueado até chegar           │                                  │
    │   ou até o tempo limite)         │                                  │
```

- **Tempo limite:** se a resposta não chegar dentro do limite configurado em `config.MQTT_RESPONSE_TIMEOUT` (ou de uma exceção por tópico em `MQTT_RESPONSE_TIMEOUTS`), o simulador desiste de esperar e sinaliza erro, em vez de travar para sempre.
- **Descarte de respostas antigas:** antes de publicar um novo pedido, o simulador descarta qualquer resposta que tenha sobrado na fila de uma execução anterior. Isso evita que uma resposta atrasada de um comando anterior seja confundida com a resposta do comando atual — importante porque, no robô físico, alguns comandos compartilham conceitualmente o mesmo sinal de "estou livre".

## Tabela de comandos

Nem toda linha da tabela usa MQTT — comandos de controle de fluxo (`switch`, `goto`, `useMacro`...) e os que ajustam apenas a memória local (`counter`, `random`...) não se comunicam com o robô.

| Comando | O que faz | Comunicação (modo `robot`) |
|---|---|---|
| `<talk>` | Robô fala um texto (com suporte a variáveis `#var`, `$`, e sorteio aleatório com `/`) | `MQTT_PUB_SUB`: publica `voz\|texto` em `TALK`, manda `LEDS SPEAK`, espera `TALK_RESPONSE`, manda `LEDS STOP`. |
| `<audio>` | Toca um efeito sonoro ou música | Se `block="TRUE"`: `MQTT_PUB_SUB`, publica `arquivo\|TRUE` em `AUDIO` e espera `AUDIO_RESPONSE`. Se `block="FALSE"`: publica e não espera. |
| `<motion>` | Move a cabeça (`YES`/`NO`/...) | `MQTT_PUB`: publica em `MOTION/HEAD`, sem esperar resposta. |
| `<led>` | Muda a cor/animação dos LEDs | `MQTT_PUB`: publica o nome mapeado (ex.: `HAPPY` → `green`) em `LEDS`. |
| `<evaEmotion>` | Muda a expressão facial do robô (tela) | `MQTT_PUB`: publica a emoção em `EVAEMOTION`. |
| `<listen>` | Ouve o usuário (fala → texto) | `MQTT_PUB_SUB`: manda `LEDS LISTEN`, publica idioma em `LISTEN`, espera `LISTEN_RESPONSE`, manda `LEDS STOP`. Em modo terminal, pede o texto digitado. |
| `<qrRead>` | Lê um QR code | `MQTT_PUB_SUB`: manda `LEDS LISTEN`, publica em `QRREAD`, espera `QRREAD_RESPONSE`, manda `LEDS STOP`. |
| `<userEmotion>` | Reconhece a emoção do usuário pela câmera | `MQTT_PUB_SUB`: manda `LEDS LISTEN`, publica em `USEREMOTION`, espera `USEREMOTION_RESPONSE`. |
| `<userid>` | Reconhece o usuário pela câmera | `MQTT_PUB_SUB`: publica em `USERID`, espera `USERID_RESPONSE`. |
| `<mqtt>` | Publica uma mensagem MQTT livre (com substituição de variáveis) | Publica no `pubTopic` indicado no nó, sem esperar resposta. |
| `<http>` | Envia uma requisição pelo comunicador HTTP | Usa `HttpCommunicator` em vez de MQTT. |
| `<voice>` / `<lightEffects>` / `<audioEffects>` | Ajustam configurações globais (`<settings>`) | Apenas atualizam a memória/log; `voice` grava a voz padrão usada por `<talk>`. |
| `<wait>` | Pausa a execução por N milissegundos | Não comunica; só espera com uma barra de progresso. |
| `<counter>` | Operações aritméticas (`=`, `+`, `-`, `*`, `/`, `^`, `%`) sobre uma variável ou sobre `$` | `NULL`, só memória. |
| `<random>` | Sorteia um inteiro entre `min` e `max` | `NULL`, só memória. |
| `<log>` | Envia uma linha para o coletor de logs (CSV) | `MQTT_PUB`: publica em `LOG`, sempre (mesmo em modo terminal). |
| `<switch>` / `<case>` / `<default>` | Estrutura condicional: compara uma variável e desvia a execução | Não comunicam; `<case>` aceita `eq`, `gt`, `gte`, `lt`, `lte`, `ne`, `exact`, `contain`. |
| `<goto>` | Salta para um nó com `id` correspondente | Não comunica; reorganiza a pilha de retorno do motor. |
| `<macro>` / `<useMacro>` | Define/chama um bloco reutilizável de comandos | `<useMacro>` desvia a execução para dentro da `<macro>` e organiza o retorno. |
| `<stop>` | Encerra o script imediatamente | Não comunica. |
| `<debug>` | Ferramentas de depuração (pausa manual, mostrar tabelas de variáveis) | Não comunica; usa `input()` direto no terminal. |
| `<llm>` / `<llmRobotProfile>` / `<robotAffectiveProfile>` | Integração com modelo de linguagem (Ollama) e perfil afetivo do robô | Chamam o LLM local; não usam MQTT_PUB_SUB. |

## Sequência completa de exemplo: `<talk>`

```
<talk commMode="MQTT_PUB_SUB" pubTopic="TALK" subTopic="TALK_RESPONSE">Olá!</talk>
```

1. O motor (`script_engine.py`) chama `talk_module.node_process()`.
2. O módulo resolve variáveis no texto (`#var`, `$`) e escolhe uma sentença aleatória se houver `/`.
3. Publica `"<voz>|Olá!"` no tópico `EVA/TALK`.
4. Publica `"SPEAK"` no tópico `EVA/LEDS` (o robô acende os LEDs de fala).
5. Bloqueia esperando uma mensagem em `EVA/TALK_RESPONSE` (com tempo limite).
6. Ao receber a resposta (o robô terminou de falar), publica `"STOP"` em `EVA/LEDS`.
7. Retorna o controle ao motor, que avança para o próximo nó.

## Variáveis do script

- **Variáveis nomeadas** (`memory.vars`): criadas por `<counter var="x" .../>`, `<random var="x" .../>`, ou pelo atributo `var` de comandos de entrada (`listen`, `qrRead`, `userEmotion`...). Usadas no texto com `#x`.
- **A pilha `$`** (`memory.var_dollar`): toda vez que um comando de entrada não tem o atributo `var`, o resultado é empilhado aqui. É referenciado com `$` (o último valor), `$n` (o n-ésimo, contando do início) ou `$-n` (contando do fim).

## Retrocesso (undo) e reinício

O motor mantém um histórico de snapshots (nó atual + estado + memória completa) a cada passo executado (`__push_history()`), o que permite:

- `previous()`: volta um passo, restaurando a memória exatamente como estava antes daquele passo ser executado.
- `reset()`: volta ao primeiro nó do `<script>`, limpando a memória (mas não a tabela de IDs).

Isso é o que possibilita os botões "Voltar" e "Voltar ao início" da interface web (veja [`eva_api.md`](./eva_api.md)).

## Rodando sem a API/interface

O motor não depende do Flask nem da interface web. Para rodar um script diretamente em Python:

```python
from script_engine import ScriptEngine

engine = ScriptEngine()
engine.load_script("eva_scripts/meu_script_evaml.xml")
engine.initialize()
engine.start_script("robot")   # ou "terminal" / "terminal-plus"

while engine.get_state() == "PLAY":
    engine.play_next()
```

Isso é útil para criar uma API alternativa ao `eva_api.py`, ou para rodar scripts em lote sem interface.
