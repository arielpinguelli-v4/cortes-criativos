# cortes-criativos

Skill para o [Claude Code](https://claude.com/claude-code) que transforma um vídeo bruto em **lista de minutagem de cortes para criativos**. Ela transcreve localmente com Whisper, escolhe e ranqueia os melhores trechos e escreve de 3 a 5 headlines para cada corte.

Serve para podcast, live, entrevista, aula, depoimento, UGC, gravação de celular ou anúncio já editado, de qualquer marca.

> *Claude Code skill: local Whisper transcription → ranked clip timestamps + on-screen headlines for ad creatives (Portuguese).*

## O que você recebe

Para cada vídeo, um `minutagem.md` com:

- **Resumo** dos cortes, em ordem de prioridade, com minutagem, duração, formato e nota de 0 a 10.
- **Minutagem ajustada às palavras reais** da transcrição, já com folga, inclusive em cortes montados com trechos de partes diferentes (gancho de um ponto + CTA de outro).
- **Fala literal** de cada corte e o texto dos **primeiros 3 segundos**, para checar o gancho.
- **3 a 5 headlines por corte**, cada uma num ângulo (dor, desejo, curiosidade, prova, contraintuitivo, chamada de público, oferta), com uma recomendada.
- Observações para o editor.

A skill **não recorta nem renderiza** o vídeo. A entrega é a lista para o editor.

## Instalação

```bash
pip install -r requirements.txt   # faster-whisper (traz o PyAV; não precisa de ffmpeg)

# para todos os projetos
git clone https://github.com/arielpinguelli-v4/cortes-criativos ~/.claude/skills/cortes-criativos

# ou só para um projeto
git clone https://github.com/arielpinguelli-v4/cortes-criativos .claude/skills/cortes-criativos
```

Na primeira transcrição o modelo `small` do Whisper é baixado (~500 MB). Para baixar vídeos de YouTube, Instagram ou TikTok direto pelo link, instale também o [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) (opcional).

## Uso

No Claude Code, rode `/cortes-criativos` ou peça em linguagem natural:

> Faz a decupagem desse vídeo: `C:\videos\live-lancamento.mp4`. Cliente: Clínica Exemplo, objetivo: agendamento de avaliação. Quero cortes para Reels e headlines.

O Claude:

1. lê o contexto da marca no projeto (personas, termos, oferta);
2. transcreve o vídeo;
3. escolhe os cortes;
4. confere a minutagem com o script e entrega o resumo no chat.

O resultado fica em `cortes/<nome-do-video>/`.

## Scripts (também funcionam sozinhos)

```bash
# 1. transcrição com tempo de cada palavra → transcricao.json / .md / .srt
python scripts/transcrever.py video.mp4 --saida cortes --vocabulario "Marca, Produto"

# 2. depois de escrever cortes/<video>/cortes.json (formato no SKILL.md)
python scripts/minutagem.py cortes/<video>
```

| Opção | Padrão | Notas |
|---|---|---|
| `--modelo` | `small` | `medium` é cerca de 7x mais lento na CPU; use só se o `small` errar muito |
| `--idioma` | `pt` | `auto` detecta |
| `--vocabulario` | — | nomes de marca e pessoas, para o Whisper acertar a grafia |
| `--refazer` | — | transcreve de novo um vídeo já processado |

Referência de tempo: num notebook de 4 núcleos, o `small` leva cerca de metade da duração do vídeo.

## Estrutura

```
SKILL.md                         fluxo que o Claude segue
scripts/transcrever.py           Whisper local → transcrição com tempo de cada palavra
scripts/minutagem.py             ajusta os cortes às palavras, aponta erros e gera o minutagem.md
references/criterios-cortes.md   nota, ganchos, eliminatórios, regras por tipo de vídeo e formato
references/headlines.md          regras e ângulos de headline
```

## Licença

[MIT](LICENSE)
