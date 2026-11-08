# 編集型リデザイン試作（claude/redesign-editorial ブランチ）

本番（main / GitHub Pages）には未反映の試作です。ローカル確認：

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

## 方針

- 12列グリッド。左3列＝見出し、中央6列＝本文。見出しはPCで縦組み。
- 書体は端末標準のみ（明朝＝見出し・店名・日付、ゴシック＝本文・情報）。外部フォントなし。
- 色は生成り地＋墨＋罫線のみ。装飾的な色面は使わない。
- トップの最初の画面は「今月のお休み」と写真。巨大ロゴ・ヒーローコピーなし。
- メニューはカテゴリを左列、料金を右列に置く目録型。

## 写真の追加

`index.html` の `.plates` 内に `<figure class="plate">` を追加するだけで、
縦横比を保ったまま4枚周期で配置が巡回します（クラス指定不要）。
横長を大きく見せたい時だけ `plate--wide` を付けます。
`plate--placeholder` と `assets/images/placeholder-*.webp` は仮枠なので、写真差し替え時に削除してください。

## 維持したもの

- URL：index / menu / access / reservation.html
- アンカー：#information-title #news #instagram #reservation
- 編集マーカー：INFORMATION / NEWS / MENU / ACCESS EDIT START〜END と内側のHTML構造
- 予約・LINE・Instagramの全リンク先
