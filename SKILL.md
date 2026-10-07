---
name: cortes-criativos
description: >
  Transcreve vídeos localmente com Whisper (faster-whisper), escolhe os melhores cortes para criativos
  de mídia paga ou orgânico e cria 3–5 headlines por corte. Entrega uma lista de minutagem (início/fim
  ajustados às palavras reais, fala literal, nota, headlines) em Markdown; não corta os arquivos.
  Serve para qualquer marca e qualquer vídeo: podcast, live, entrevista, aula, depoimento, UGC,
  gravação de celular, anúncio já editado. Use SEMPRE que o usuário pedir "cortes", "melhores trechos",
  "decupagem", "decupar vídeo", "minutagem", "transcrever vídeo", "whisper", "cortes para criativo",
  "cortes da live/podcast", "headline para os cortes", ou enviar um vídeo pedindo o que dá para aproveitar.
version: 1.0.0
---

# Cortes para criativos

Fluxo: **vídeo → transcrição com tempo de cada palavra → escolha dos cortes → headlines → minutagem conferida pelo script → Markdown no chat**.

A entrega é a **lista de minutagem para o editor**. A skill não recorta nem renderiza vídeo.

Os caminhos abaixo são relativos à pasta desta skill (o "base directory" informado quando ela é carregada). Rode os scripts com o caminho completo.

Scripts:
- `scripts/transcrever.py`: Whisper local na CPU, sem enviar o vídeo para fora.
- `scripts/minutagem.py`: ajusta os tempos às palavras, extrai a fala literal, aponta erros e gera o `minutagem.md`.

Referências (ler antes das etapas 5 e 6):
- `references/criterios-cortes.md`: nota, ganchos, eliminatórios, regras por tipo de vídeo e formato.
- `references/headlines.md`: regras e ângulos das headlines.

Requisitos: Python 3.9+ e `pip install faster-whisper`, que já traz o PyAV para ler mp4/mov sem ffmpeg. Na primeira execução o modelo `small` é baixado (~500 MB).

---

## 1. Entrada

Colete da mensagem do usuário (pergunte só o que faltar e não der para inferir):

| Item | Obrigatório | Padrão se não vier |
|---|---|---|
| Vídeo(s): caminho local, pasta ou link | sim | — |
| Marca / cliente | sim | — |
| Objetivo do criativo (lead, venda, inscrição, awareness…) | sim | inferir do material da campanha |
| Persona(s) | não | as personas do material da marca |
| Formato | não | Reels/TikTok 9:16 |
| Quantidade de cortes | não | a da tabela em `criterios-cortes.md` |

Se o objetivo não estiver na mensagem nem no material da marca, faça **uma** pergunta. Fora isso, siga direto.

## 2. Contexto da marca

1. Procure no projeto o material da marca ou do cliente: `CLAUDE.md`, briefing da campanha, personas, guia de marca ou de tom de voz.
2. Anote:
   - termos oficiais e proibidos;
   - nomes exatos de produto e marca;
   - números oficiais;
   - oferta, data e CTA;
   - personas.

   Isso alimenta o `--vocabulario` do Whisper, os eliminatórios e as headlines.
3. Não trave a entrega por falta de contexto: siga e diga o que ficou genérico.

**Pasta de saída:** uma pasta `cortes/` dentro da pasta da marca no projeto. Se não houver uma, crie `cortes/` na raiz. Cada vídeo vira uma subpasta com o nome do arquivo.

## 3. Obter o vídeo

- **Arquivo ou pasta local:** use direto. Aceita mp4, mov, m4v, mkv, webm, avi e áudio (mp3, wav, m4a…).
- **YouTube, Instagram, TikTok, Vimeo:** se o `yt-dlp` estiver instalado, baixe com `yt-dlp -o "<saida>/_fonte/%(title).60s.%(ext)s" "<url>"`. Se não estiver, peça o arquivo.
- **Drive, Dropbox e afins:** peça o arquivo baixado ou o caminho da pasta sincronizada.

## 4. Transcrever

```bash
python "<pasta-da-skill>/scripts/transcrever.py" "<video-ou-pasta>" --saida "<pasta>/cortes" --vocabulario "<marca, produtos, nomes próprios>"
```

- O modelo padrão é o `small`. Na CPU ele foi cerca de 7x mais rápido que o `medium` e transcreveu igual ou melhor. Só use `--modelo medium` se o `small` errar muito (áudio ruim, sotaque forte, termo técnico) e o vídeo for curto.
- O idioma padrão é `pt`. Use `--idioma auto` se o vídeo tiver outra língua.
- **Tempo de referência:** num notebook de 4 núcleos, o `small` leva cerca de **metade da duração do vídeo**. Uma live de 80 min leva uns 40 min.
- **Vídeo acima de 5 min:** rode em background, se o ambiente permitir, e avise o usuário quanto tempo deve levar.
- Vídeo já transcrito é pulado. Use `--refazer` para transcrever de novo.

Saídas na subpasta do vídeo: `transcricao.json` (fonte da verdade), `transcricao.md` (uma frase por linha com `[início → fim]` e pausas marcadas) e `transcricao.srt`.

## 5. Ler e mapear

1. Leia a `transcricao.md` inteira. Em vídeo longo, leia em partes pelos blocos `## mm:ss`.
2. Classifique o vídeo: longo, curto e cru, já editado ou muito curto (ver `criterios-cortes.md`).
3. Monte para você um mapa dos momentos: tema, tempo, frase-gancho candidata e prova. Em material cru, marque os takes repetidos.
4. Se a transcrição tiver trechos sem sentido (ruído, falas sobrepostas), não use esses trechos e avise.

## 6. Escolher os cortes e criar as headlines

Siga `references/criterios-cortes.md` (nota, eliminatórios, duração) e `references/headlines.md` (3–5 headlines por corte em ângulos diferentes, uma recomendada).

Escreva `<subpasta-do-video>/cortes.json` **já em ordem de prioridade** (o primeiro é o melhor):

```json
{
  "titulo": "Podcast — episódio 12",
  "cliente": "Clínica Exemplo",
  "objetivo": "Agendamento de avaliação",
  "cortes": [
    {
      "nome": "Agenda cheia e caixa vazio",
      "formato": "Reels/TikTok 9:16",
      "nota": 8.7,
      "trechos": [
        {"ini": "12:04.2", "fim": "12:41.0", "papel": "gancho"},
        {"ini": "14:10.0", "fim": "14:22.5", "papel": "cta"}
      ],
      "por_que": "Abre com a dor nomeada pela persona e fecha com o número do caso.",
      "headlines": [
        {"angulo": "Dor", "texto": "Agenda cheia e o caixa não fecha?", "recomendada": true},
        {"angulo": "Contraintuitivo", "texto": "Mais pacientes não é a solução"},
        {"angulo": "Chamada de público", "texto": "Dono de clínica com 3+ profissionais:"}
      ],
      "obs_editor": "Quem fala no trecho 2 é o entrevistador."
    }
  ]
}
```

- Os tempos podem ser `"mm:ss.d"`, `"hh:mm:ss.d"` ou segundos. Copie da `transcricao.md`; o script faz o ajuste fino.
- Corte contínuo = 1 trecho, sem `papel`. Corte composto = 2–4 trechos com `papel`.
- Variação A/B de gancho = corte separado com o nome `"… (gancho B)"`.

## 7. Conferir a minutagem

```bash
python "<pasta-da-skill>/scripts/minutagem.py" "<subpasta-do-video>"
```

O script encaixa cada trecho nas palavras reais (0,15 s de folga antes e 0,3 s depois), copia a fala literal e lista alertas:
- frase cortada no meio;
- muleta no início ("então", "né", "tipo");
- duração fora do formato;
- trechos sobrepostos;
- trecho sem fala.

**Corrija o `cortes.json` e rode de novo até sobrar só alerta intencional.** Depois leia o `minutagem.md` e confira:
- a fala de cada corte sustenta a headline;
- os "Primeiros 3 s" são de fato um gancho.

## 8. Entregar

No chat, em Markdown:
1. Uma linha de contexto: vídeo, duração, tipo, quantos cortes, objetivo.
2. A tabela de **Resumo** do `minutagem.md`.
3. Para cada corte: minutagem, os primeiros 3 s, as headlines (com a recomendada marcada) e, se houver, a observação para o editor. A fala completa fica no arquivo, para não lotar o chat.
4. Avisos: alertas que ficaram, número divergente do oficial, trecho de áudio duvidoso, contexto que faltou.
5. O caminho do `minutagem.md`.

Se o usuário pedir ajuste ("troca o corte 3", "mais curto", "headline mais agressiva"), edite o `cortes.json`, rode o `minutagem.py` de novo e mostre só o que mudou.
