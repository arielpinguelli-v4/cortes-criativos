# Critérios para escolher cortes

Um corte bom para criativo é um trecho que **prende nos 3 primeiros segundos, se entende sozinho e entrega uma ideia completa** que leva a persona até o objetivo da campanha.

## Nota de 0 a 10

Dê nota a cada candidato e ordene do maior para o menor. Os 3 primeiros viram prioridade (⭐).

| Critério | Peso | Pergunta |
|---|---|---|
| Gancho | 3 | A primeira frase prende sozinha, sem contexto? |
| Autossuficiência | 2 | Quem nunca viu o vídeo entende? |
| Payoff | 2 | Entrega uma ideia completa e fecha com conclusão, virada ou frase de efeito? |
| Prova / especificidade | 1,5 | Tem número, caso, nome, antes/depois ou demonstração? |
| Aderência | 1,5 | Fala com a dor/desejo da persona e aponta para o objetivo (lead, venda, inscrição)? |

Nota = soma(critério 0–10 × peso) ÷ 10. Descarte o que ficar abaixo de 6.

### Ganchos que funcionam

- Afirmação contraintuitiva: "Contratar mais gente não resolve."
- Número concreto: "Em 90 dias a gente dobrou a margem."
- Dor nomeada do jeito que a persona fala: "Eu faturava bem e não sobrava nada."
- Pergunta que a persona já se faz: "Por que minha agência não passa de 20 clientes?"
- Confissão ou erro: "O maior erro que eu cometi foi…"
- Resultado ou cena forte: "No dia que eu demiti meu melhor cliente…"
- A pergunta do entrevistador, quando ela já é o gancho. Nesse caso o corte começa nela.

### Inícios que matam o corte

"Então…", "Bom, como eu falei…", "É…", saudação, "Isso que ele falou", contexto antes da ideia, referência a slide ou tela ("como vocês estão vendo aqui").

## Eliminatórios (descarta mesmo com nota alta)

- Contraria a governança do cliente: termos proibidos, claims regulados, promessa de resultado que o cliente não autoriza.
- Número diferente do oficial. Confira com o material da campanha e, se houver divergência, não use o número na headline e avise.
- Erro factual, menção a concorrente, informação interna ou sensível.
- Fala truncada, muito gaguejada ou com transcrição suspeita (palavras sem sentido costumam indicar ruído ou duas pessoas falando junto). Avise o editor para conferir o áudio.

## Por tipo de vídeo

Classifique o vídeo antes de procurar cortes. A skill é usada com qualquer tipo de material.

### Longo (podcast, entrevista, live, aula, palestra; mais de 10 min)

- Cortes **contínuos** de 20–60 s (até 90 s se for uma história que segura).
- Procure respostas a perguntas, histórias com virada, listas ("3 erros que…"), opiniões fortes, números e frases de efeito que fecham um raciocínio.
- Cubra **temas diferentes**. Cinco cortes do mesmo assunto disputam a mesma persona e o mesmo leilão.
- Quantidade: 8–15 candidatos ranqueados para vídeos de 30 min ou mais; 5–8 para 10–30 min.
- Na live ou aula, o melhor momento costuma vir depois de uma pergunta do público ou de uma pausa ("deixa eu contar uma coisa").

### Curto e cru (UGC, depoimento, selfie, gravação de celular; 1–10 min, com várias tomadas)

- Frases quase iguais em sequência são **takes repetidos**. Escolha o mais fluente, que costuma ser o último, mas confira.
- Cortes **compostos** são esperados: gancho de um trecho + desenvolvimento de outro + CTA de outro. No máximo 4 trechos por corte, para o editor não se perder.
- Gere **variações A/B de gancho** com o mesmo corpo. É o maior ganho com material curto.
- Quantidade: 3–6 cortes.

### Já editado (anúncio pronto, VSL, vídeo institucional)

- Procure recortes de 6–15 s para Stories e bumper, além de ganchos alternativos para reabrir o mesmo vídeo.
- Quantidade: 3–5 recortes.

### Muito curto (menos de 1 min)

- Normalmente cabe só 1 corte e 1–2 variações de gancho, ou um recorte de 6–15 s. Não force quantidade.

## Duração por formato

| Formato | Ideal | Teto |
|---|---|---|
| Reels / TikTok / Shorts (anúncio) | 15–45 s | 60 s |
| Stories | 6–15 s | 15 s por card |
| Feed (vídeo) | 15–60 s | 90 s |
| Bumper YouTube | 6 s | 6 s |
| Corte orgânico de podcast/live | 30–90 s | 90 s |

Se o usuário não disser o formato, use **Reels/TikTok 9:16** como padrão e indique Stories quando o corte tiver menos de 15 s.

## Regras de minutagem

- O corte começa na **primeira palavra do gancho**. Pule respiração, muleta e "então".
- O corte termina **depois** do fim da frase. O `minutagem.py` acrescenta a folga sozinho.
- Use a `transcricao.md` para achar os tempos. As linhas `··· pausa` são os pontos de corte mais limpos.
- Em corte composto, dê um papel a cada trecho: `gancho`, `desenvolvimento`, `prova`, `cta`.
- Cortes diferentes não se sobrepõem, exceto variações A/B declaradas (mesmo corpo, gancho diferente).
- Em entrevista, diga no `obs_editor` quem fala em cada trecho quando isso não for óbvio.
