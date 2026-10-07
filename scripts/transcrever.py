"""Transcreve video/audio com faster-whisper e grava a transcricao com minutagem.

Uso:
  python transcrever.py <arquivo|pasta> --saida <pasta-cortes> [--modelo small] [--idioma pt]
                        [--vocabulario "Marca, Produto, Nome Proprio"] [--refazer]

Para cada arquivo cria <saida>/<slug-do-arquivo>/ com:
  transcricao.json  segmentos + palavras com tempo (fonte da verdade do minutagem.py)
  transcricao.md    uma frase por linha com [inicio -> fim] e pausas marcadas (para analise)
  transcricao.srt   legenda padrao
"""
import argparse, json, os, re, sys, time, unicodedata
from pathlib import Path

os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

EXTS = {'.mp4', '.mov', '.m4v', '.mkv', '.webm', '.avi', '.mp3', '.wav', '.m4a', '.aac', '.ogg', '.opus', '.flac'}
FIM_FRASE = re.compile(r'[.!?…]["\')\]]?$')
PAUSA_MARCADA = 1.5   # silencio que vira linha "pausa" no .md
PAUSA_QUEBRA = 0.7    # silencio que quebra frase mesmo sem pontuacao
MAX_PALAVRAS = 30     # frase longa demais quebra na proxima virgula


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()[:60] or 'video'


def ts(t, longo=False):
    d = int(round(max(0.0, t) * 10))
    h, m, s = d // 36000, (d // 600) % 60, (d % 600) / 10
    return f'{h:02d}:{m:02d}:{s:04.1f}' if longo else f'{m + h * 60:02d}:{s:04.1f}'


def ts_srt(t):
    ms = int(round(t * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def duracao(path):
    import av
    with av.open(str(path)) as c:
        if c.duration:
            return c.duration / 1_000_000
        st = next((s for s in c.streams if s.type == 'audio'), None)
        if st is not None and st.duration and st.time_base:
            return float(st.duration * st.time_base)
    return None


_modelos = {}


def carregar(nome):
    from faster_whisper import WhisperModel
    if nome not in _modelos:
        try:
            print(f'  carregando modelo {nome}...', flush=True)
            # nucleos fisicos: com hyperthreading (8 logicos) fica mais lento
            _modelos[nome] = WhisperModel(nome, device='cpu', compute_type='int8', cpu_threads=max(1, (os.cpu_count() or 8) // 2))
        except Exception as e:
            if nome == 'small':
                raise
            print(f'  ! modelo {nome} indisponivel ({e.__class__.__name__}: {e}); usando small', flush=True)
            return carregar('small')
    return _modelos[nome], nome


def frases(segmentos):
    """Reagrupa as palavras em frases curtas (pontuacao, pausa ou tamanho)."""
    out, atual = [], []
    palavras = [w for s in segmentos for w in s['palavras']]
    for k, w in enumerate(palavras):
        atual.append(w)
        prox = palavras[k + 1] if k + 1 < len(palavras) else None
        gap = (prox[0] - w[1]) if prox else 99
        quebra = FIM_FRASE.search(w[2]) or gap >= PAUSA_QUEBRA or \
            (len(atual) >= MAX_PALAVRAS and w[2].endswith(','))
        if quebra or prox is None:
            out.append(dict(ini=atual[0][0], fim=atual[-1][1], texto=' '.join(x[2] for x in atual), gap=gap))
            atual = []
    return out


def gravar(pasta, nome, dur, modelo, idioma, segmentos):
    longo = dur >= 3600
    dados = dict(arquivo=nome, duracao=round(dur, 2), modelo=modelo, idioma=idioma, segmentos=segmentos)
    (pasta / 'transcricao.json').write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding='utf-8')

    fr = frases(segmentos)
    linhas = [f'# Transcricao — {nome}', '',
              f'Duracao {ts(dur, longo)} · modelo {modelo} · idioma {idioma} · {len(fr)} frases', '',
              'Formato: `[inicio → fim] fala`. Linhas `··· pausa` marcam silencio de 1,5 s ou mais (bons pontos de corte).',
              'Whisper nao separa falantes; quem fala se deduz pelo conteudo.', '']
    bloco = -1
    for f in fr:
        if dur > 1200 and int(f['ini'] // 300) != bloco:
            bloco = int(f['ini'] // 300)
            linhas += ['', f'## {ts(bloco * 300, longo)}', '']
        linhas.append(f"[{ts(f['ini'], longo)} → {ts(f['fim'], longo)}] {f['texto']}")
        if PAUSA_MARCADA <= f['gap'] < 99:
            linhas.append(f"··· pausa {f['gap']:.1f} s")
    (pasta / 'transcricao.md').write_text('\n'.join(linhas) + '\n', encoding='utf-8')

    srt = []
    for k, s in enumerate(segmentos, 1):
        srt += [str(k), f"{ts_srt(s['ini'])} --> {ts_srt(s['fim'])}", s['texto'], '']
    (pasta / 'transcricao.srt').write_text('\n'.join(srt), encoding='utf-8')


def transcrever(path, saida, args):
    pasta = saida / slug(path.stem)
    if (pasta / 'transcricao.json').exists() and not args.refazer:
        print(f'= {path.name}: ja transcrito em {pasta} (use --refazer para refazer)', flush=True)
        return pasta
    pasta.mkdir(parents=True, exist_ok=True)

    dur = duracao(path) or 0.0
    modelo, nome_modelo = carregar(args.modelo)
    print(f'> {path.name} ({ts(dur, dur >= 3600)}) · modelo {nome_modelo}', flush=True)

    t0 = time.time()
    segs, info = modelo.transcribe(
        str(path), language=None if args.idioma == 'auto' else args.idioma,
        vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500),
        word_timestamps=True, beam_size=5, condition_on_previous_text=False,
        hotwords=args.vocabulario or None)
    segmentos, ultimo = [], time.time()
    for s in segs:
        palavras = [[round(w.start, 2), round(w.end, 2), w.word.strip()] for w in (s.words or []) if w.word.strip()]
        if not palavras:
            continue
        segmentos.append(dict(i=len(segmentos), ini=round(s.start, 2), fim=round(s.end, 2),
                              texto=s.text.strip(), palavras=palavras))
        if time.time() - ultimo > 20 and dur:
            print(f'  {ts(s.end)} de {ts(dur)} ({s.end / dur:.0%})', flush=True)
            ultimo = time.time()

    gravar(pasta, path.name, dur or (segmentos[-1]['fim'] if segmentos else 0), nome_modelo, info.language, segmentos)
    print(f'  ok em {time.time() - t0:.0f} s · {len(segmentos)} segmentos → {pasta}', flush=True)
    return pasta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('entrada')
    ap.add_argument('--saida', required=True, help='pasta cortes/ do cliente; cada video vira uma subpasta')
    ap.add_argument('--modelo', default='small', help='small (padrao) | medium (~7x mais lento na CPU) | large-v3')
    ap.add_argument('--idioma', default='pt', help='pt | en | es | auto')
    ap.add_argument('--vocabulario', default='', help='nomes de marca/produto/pessoas para o Whisper acertar a grafia')
    ap.add_argument('--refazer', action='store_true')
    args = ap.parse_args()

    entrada, saida = Path(args.entrada), Path(args.saida)
    arquivos = sorted(p for p in entrada.iterdir() if p.suffix.lower() in EXTS) if entrada.is_dir() else [entrada]
    if not arquivos:
        sys.exit(f'Nenhum video/audio encontrado em {entrada}')
    for p in arquivos:
        transcrever(p, saida, args)


if __name__ == '__main__':
    main()
