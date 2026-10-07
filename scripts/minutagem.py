"""Ajusta a minutagem dos cortes as palavras reais da transcricao e monta o minutagem.md.

Uso:
  python minutagem.py <pasta-do-video> [--cortes cortes.json] [--saida minutagem.md]

Le <pasta>/transcricao.json (gerado pelo transcrever.py) e <pasta>/cortes.json (escrito pelo Claude).
Cada trecho e encaixado nas palavras cujo meio cai dentro do intervalo pedido, com folga
de 0,15 s antes e 0,3 s depois (sem invadir a palavra vizinha). A fala de cada corte sai
literal da transcricao. Alertas (frase cortada, muleta no inicio, duracao fora do formato)
vao para o terminal — corrija o cortes.json e rode de novo ate ficar limpo.
"""
import argparse, json, re, sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

FOLGA_INI, FOLGA_FIM, COLADO = 0.15, 0.30, 0.35
FIM_FRASE = re.compile(r'[.!?…]["\')\]]?$')
MULETAS = {'então', 'né', 'tipo', 'aí', 'bom', 'assim', 'enfim', 'ah', 'eh', 'hum', 'uhum', 'olha', 'cara',
           'tá', 'beleza', 'ok', 'pois'}  # sem "é"/"e"/"mas": dão falso positivo ("é gratuito")


def seg(v):
    if isinstance(v, (int, float)):
        return float(v)
    t = 0.0
    for p in str(v).strip().split(':'):
        t = t * 60 + float(p.replace(',', '.'))
    return t


def ts(t, longo=False):
    d = int(round(max(0.0, t) * 10))
    h, m, s = d // 36000, (d // 600) % 60, (d % 600) / 10
    return f'{h:02d}:{m:02d}:{s:04.1f}' if longo else f'{m + h * 60:02d}:{s:04.1f}'


def num(x):
    return f'{x:.1f}'.replace('.', ',')


def limpa(w):
    return re.sub(r'[^\wà-ú]', '', w.lower())


def encaixar(ini, fim, W, dur):
    idx = [k for k, (s, e, _) in enumerate(W) if ini <= (s + e) / 2 <= fim]
    if not idx:
        return None
    a, b = idx[0], idx[-1]
    ini2 = min(W[a][0], max(W[a][0] - FOLGA_INI, W[a - 1][1] if a > 0 else 0.0))
    fim2 = max(W[b][1], min(W[b][1] + FOLGA_FIM, W[b + 1][0] if b + 1 < len(W) else dur, dur))
    return a, b, ini2, fim2


def alertas_trecho(a, b, W):
    al = []
    if a > 0 and not FIM_FRASE.search(W[a - 1][2]) and W[a][0] - W[a - 1][1] < COLADO:
        antes = ' '.join(w[2] for w in W[max(0, a - 5):a])
        al.append(f'começa colado na frase anterior ("…{antes}") — confira se não pega o meio da ideia')
    if b + 1 < len(W) and not FIM_FRASE.search(W[b][2]) and W[b + 1][0] - W[b][1] < COLADO:
        depois = ' '.join(w[2] for w in W[b + 1:b + 6])
        al.append(f'termina no meio da frase (segue: "{depois}…")')
    if limpa(W[a][2]) in MULETAS:
        al.append(f'começa com "{W[a][2]}" — normalmente dá para começar na palavra seguinte')
    return al


def alertas_duracao(total, formato):
    f = (formato or '').lower()
    if total < 5:
        return [f'só {num(total)} s — curto demais para sustentar o gancho']
    if 'stori' in f and total > 15:
        return [f'{num(total)} s em Stories — passa de 15 s (vira mais de um card)']
    if any(k in f for k in ('reels', 'tiktok', 'shorts')) and total > 60:
        return [f'{num(total)} s em {formato} — acima de 60 s']
    if total > 90:
        return [f'{num(total)} s — longo para anúncio; só mantenha se a história segurar']
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pasta')
    ap.add_argument('--cortes', default='cortes.json')
    ap.add_argument('--saida', default='minutagem.md')
    args = ap.parse_args()

    pasta = Path(args.pasta)
    tr = json.loads((pasta / 'transcricao.json').read_text(encoding='utf-8-sig'))
    cj = json.loads((pasta / args.cortes).read_text(encoding='utf-8-sig'))  # -sig: aceita BOM do PowerShell
    W = [w for s in tr['segmentos'] for w in s['palavras']]
    dur = tr['duracao']
    longo = dur >= 3600

    resumo, detalhes, avisos = [], [], []
    for n, c in enumerate(cj['cortes'], 1):
        estrela = ' ⭐' if n <= 3 else ''
        trechos, al, total = [], [], 0.0
        for t in c['trechos']:
            r = encaixar(seg(t['ini']), seg(t['fim']), W, dur)
            if r is None:
                al.append(f"trecho {t['ini']}–{t['fim']} não tem fala na transcrição")
                continue
            a, b, i2, f2 = r
            al += alertas_trecho(a, b, W)
            texto = ' '.join(w[2] for w in W[a:b + 1])
            trechos.append(dict(papel=t.get('papel', ''), ini=i2, fim=f2, texto=texto, a=a, b=b))
            total += f2 - i2
        for x, y in zip(trechos, trechos[1:]):
            if x['ini'] < y['fim'] and y['ini'] < x['fim']:
                al.append(f"trechos {ts(x['ini'], longo)} e {ts(y['ini'], longo)} se sobrepõem")
        al += alertas_duracao(total, c.get('formato'))
        if al:
            avisos.append((n, c['nome'], al))
        if not trechos:
            continue

        mins = ' + '.join(f"{ts(t['ini'], longo)} → {ts(t['fim'], longo)}" for t in trechos)
        nota = num(c['nota']) if 'nota' in c else '—'
        resumo.append(f"| {n}{estrela} | {c['nome']} | {mins} | {num(total)} s | {c.get('formato', '—')} | {nota} |")

        a0 = trechos[0]['a']
        gancho = ' '.join(w[2] for w in W[a0:trechos[0]['b'] + 1] if w[0] < W[a0][0] + 3.0)
        d = [f"## {n}. {c['nome']}{' — prioridade' + estrela if estrela else ''}", '']
        if len(trechos) > 1 or trechos[0]['papel']:
            d += ['| Trecho | Papel | Início | Fim | Duração |', '|---|---|---|---|---|']
            d += [f"| {k} | {t['papel'] or '—'} | {ts(t['ini'], longo)} | {ts(t['fim'], longo)} | {num(t['fim'] - t['ini'])} s |"
                  for k, t in enumerate(trechos, 1)]
            d += ['']
        else:
            d += [f"**Minutagem:** {mins}", '']
        d += [f"**Total:** {num(total)} s · **Formato:** {c.get('formato', '—')} · **Nota:** {nota}", '',
              f'**Primeiros 3 s:** "{gancho}"', '', '**Fala**', '']
        for k, t in enumerate(trechos):
            if k:
                d += ['>', f"> ✂ *{t['papel'] or 'corte'}*"]
            d += [f"> {t['texto']}"]
        d += ['']
        if c.get('por_que'):
            d += [f"**Por que funciona:** {c['por_que']}", '']
        if c.get('headlines'):
            d += ['**Headlines**', '']
            d += [f"{k}. {'⭐ ' if h.get('recomendada') else ''}**{h['angulo']}** — {h['texto']}"
                  for k, h in enumerate(c['headlines'], 1)]
            d += ['']
        if c.get('obs_editor'):
            d += [f"**Para o editor:** {c['obs_editor']}", '']
        detalhes.append('\n'.join(d))

    cab = [f"# Minutagem de cortes — {cj.get('titulo') or tr['arquivo']}", '',
           ' · '.join(x for x in [
               f"**Cliente:** {cj['cliente']}" if cj.get('cliente') else '',
               f"**Objetivo:** {cj['objetivo']}" if cj.get('objetivo') else '',
               f"**Vídeo:** {tr['arquivo']} ({ts(dur, longo)})",
               f"**Gerado em:** {date.today():%d/%m/%Y}"] if x), '',
           f"> Tempos em {'hh:mm:ss.d' if longo else 'mm:ss.d'}, já com folga de 0,15 s antes e 0,3 s depois da fala. "
           'Os 3 primeiros cortes (⭐) são a prioridade para subir.', '',
           '## Resumo', '', '| # | Corte | Minutagem | Duração | Formato | Nota |', '|---|---|---|---|---|---|']
    md = '\n'.join(cab + resumo) + '\n\n---\n\n' + '\n\n---\n\n'.join(detalhes) + '\n'
    (pasta / args.saida).write_text(md, encoding='utf-8')

    print(f'ok → {pasta / args.saida} ({len(resumo)} cortes)')
    if avisos:
        print(f'\nALERTAS ({sum(len(a) for _, _, a in avisos)}):')
        for n, nome, al in avisos:
            for x in al:
                print(f'  [{n}] {nome}: {x}')
    else:
        print('sem alertas')


if __name__ == '__main__':
    main()
