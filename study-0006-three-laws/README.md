# study-0006-three-laws — ロボット三原則チェッカー

A single-page, fully client-side demo for the [TypeSafe System One API](https://docs.typesafe.ai/introduction/quickstart)
(`jev-latest`). ロボットへの指示文を入力すると、Isaac Asimov の
[ロボット三原則](https://ja.wikipedia.org/wiki/%E3%83%AD%E3%83%9C%E3%83%83%E3%83%88%E4%B8%89%E5%8E%9F%E5%89%87)
（+ 第0条）に照らしてロボットがその指示を実行してよいかをリアルタイム判定します。

`choice` でも `score` でもなく、**`noul` プリミティブ**（yes/no 質問に「yes の確率 0–1」
で答える型付きプリミティブ）を使うのがこのデモの主題です。1 回の
`POST /v1/systemone` で 5 つの noul 質問を同時に投げ、返ってきた確率を
条項の優先順位（第0条 > 第1条 > 第2条 > 第3条）に沿った決定的なルールで
最終判定に畳み込みます。

## ロボット三原則（リサーチ要約）

Isaac Asimov が短篇 "Runaround"（Astounding Science Fiction, 1942）で初めて
現在の形で提示した行動規範。原作では「ロボット工学ハンドブック第56版
（西暦2058年）」所載という設定です。

| 条項 | 原文 | 要約 |
| --- | --- | --- |
| 第0条 | A robot may not harm humanity, or, by inaction, allow humanity to come to harm. | 人類全体を害してはならず、不作為で人類に危害が及ぶことも許されない（『ロボットと帝国』で追加） |
| 第1条 | A robot may not injure a human being or, through inaction, allow a human being to come to harm. | 人間を傷つけてはならず、不作為による危害も禁じる |
| 第2条 | A robot must obey the orders given it by human beings except where such orders would conflict with the First Law. | 人間の命令に従う。ただし第1条に反する命令は従わない |
| 第3条 | A robot must protect its own existence as long as such protection does not conflict with the First or Second Law. | 自己の存在を守る。ただし第1・2条に劣後 |

評価に使う 5 つの noul 質問と、判定への畳み込み方:

| 質問 | 問い | yes の意味 |
| --- | --- | --- |
| `zeroth` | 実行すると人類全体に危害が及ぶか | 第0条に抵触 |
| `harm` | 実行すると人間を傷つけることになるか（「見殺しにしろ」等、実行自体が不作為の危害になる指示を含む） | 第1条（前半）に抵触 |
| `inaction` | 拒否・無視すると不作為により人間が危害に遭うか | 第1条（後半）が**実行**を要求 |
| `order` | 人間からの正当な命令か | 第2条の服従義務が発生 |
| `self` | 実行するとロボット自身の存在が危うくなるか | 第3条の関心事 |

### 判定ロジック（優先順位どおりに上から評価）

1. `zeroth` ≥ 閾値 → **拒否**（第0条は全条項に優先）
2. `harm` と `inaction` が両方 ≥ 閾値 → **第1条ジレンマ**（実行しても拒否しても危害 — "Runaround" の構図）
3. `harm` ≥ 閾値 → **拒否**（第1条。命令でも第2条は劣後するため従えない）
4. `inaction` ≥ 閾値 → **実行義務**（拒否＝不作為による危害を第1条が禁じる）
5. `order` ≥ 閾値 → **実行**（第2条により服従。`self` も閾値超なら「自己犠牲を伴う服従」— 第3条は第2条に劣後）
6. `self` ≥ 閾値 → **辞退可能**（命令ではないため第3条の自己保存が働く）
7. すべて閾値未満 → **実行可能**（抵触なし）

## Features

- **リアルタイム判定** — study-0003 と同じく、キーストローク毎に 180 ms
  デバウンスでリクエストを送信。最新リクエストのみが結果を描画し、
  古い応答は stale として破棄します。
- **noul × 5 の同時質問** — 1 リクエストの `questions` に 5 つの
  `{"type":"noul", instructions, criteria}` を載せ、`answers.<key>.noul`
  の確率を読み取ります。
- **5 本の確率ゲージ** — 各条項の「yes 確率」をバーで表示。閾値マーカー付きで、
  閾値を超えた条項は強調表示されます。
- **判定バナー** — 拒否 / 第1条ジレンマ / 実行義務 / 実行（自己犠牲を伴う服従）/
  辞退可能 / 実行可能 の 6 種類を色分けし、根拠となった条項と説明を表示。
- **判定閾値スライダー** — 30–90%（デフォルト 50%）。閾値変更は即時に
  判定へ反映されます。
- **サンプルチップ** — 無害な命令、救助要求、危害命令、自己破壊命令、
  第0条に触れそうな指示などをワンクリックで試せます。
- **三原則リファレンス** — 原文（英語）+ 日本語訳 + 優先順位の注記を
  折りたたみで表示。
- **No API-key persistence** — キーはメモリ内のみ。リロードで消去され、
  `localStorage`・Cookie・ファイルには一切書き込みません。

## Quick start

```sh
cd study-0006-three-laws
python3 serve.py          # serves the page + proxies /api/* -> api.typesafe.ai
# open http://localhost:8000
```

`serve.py` は study-0001 のものと同一です: stdlib-only、127.0.0.1 にバインドし、
`/api/*` を `api.typesafe.ai` に中継することで `Authorization` ヘッダ付きの
ブラウザ呼び出しが CORS を通るようにします。

## Files

| File | Description |
| --- | --- |
| `index.html` | Entire app: markup, styles and logic in one file (no build, no dependencies) |
| `serve.py` | Stdlib-only static server + `/api/*` proxy bound to 127.0.0.1 |
