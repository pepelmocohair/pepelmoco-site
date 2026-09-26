# pepel moco — static site v0.1

生成り背景・1カラム・大きな余白を基調とした、HTML/CSSだけの固定サイトです。
外部フォント、JavaScript、フレームワーク、パッケージのインストール、ビルドは不要です。

## ファイル

- `index.html`: トップ、INFORMATION、InstagramとLINE予約の案内
- `menu.html`: メニュー・料金
- `access.html`: 店舗情報
- `assets/style.css`: 全ページ共通のCSS
- `.nojekyll`: GitHub PagesのJekyll処理を無効化

## 毎月のお知らせ

`index.html` 内の `INFORMATION EDIT START` から `INFORMATION EDIT END` までを編集します。
対象年月・休業日・連休の案内を置き換えてください。

**2026年10月の日程は仮データです。実際の営業予定ではありません。**
公開前に確定した日程へ変更し、仮データの注意書きを外してください。
MENU/ACCESSも未確定情報を「準備中」としてあります。店舗情報は作成していません。

## 外部URLを一か所で変更する

全ページの固定RESERVATIONは `index.html#reservation` へ、フッターのInstagramは
`index.html#instagram` へ案内します。URLはトップページの各案内内だけに記載します。
JavaScriptやビルドを使わず一か所で管理するため、各ページから案内を経由する方式です。
固定RESERVATIONから外部サイトへ直接飛ぶ構成ではありません。

### Instagram

`index.html` の `INSTAGRAM URL` コメント直下にある `span` を次の形式へ置き換えます。
`確定したHTTPSのURL` は実際のURLに変更してください。

```html
<a class="text-link" href="確定したHTTPSのURL">Instagramを見る ↗</a>
```

### LINE予約

同じく `RESERVATION URL` コメント直下の `span` を置き換えます。

```html
<a class="text-link" href="確定したHTTPSのURL">LINEで予約する ↗</a>
```

設定後は各 `href` 一か所の変更だけで済みます。未設定時はリンクを表示しません。
URLのクエリに `&` が含まれる場合、HTML内では `&amp;` と記述します。

## ローカル確認

`index.html` をブラウザで開けます。静的HTTP配信を確認する場合は、Pythonがある環境で
このディレクトリから以下を実行します（Pythonはサイトの動作には不要です）。

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

`http://127.0.0.1:8000/` を開きます。終了は Ctrl+C です。
スマホ幅で横スクロールが出ないこと、ナビゲーション、固定予約ボタン、ページ末尾の表示を確認します。

## GitHub Pagesへの公開（今回は未実施）

専用リポジトリへpush後、Settings → Pagesで `main` ブランチのルートを公開元に設定します。
`.nojekyll` によりJekyllを使用せず公開します。内部参照はすべて相対パスです。
独自ドメイン用の設定、GitHubへのpush、Pagesの設定はまだ行っていません。

## 管理方針

Tumblr版 `/home/ysk/pepelmoco-tumblr/` とは別管理です。
このサイトの更新時にTumblr版を変更・削除する必要はありません。
