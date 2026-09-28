# pepel moco 開発作業メモ

## 普段の開始

ThinkPad / Chromebook ともに最初に：

    pepel-sync

これでGitHubを確認し、ローカルがcleanなら最新版をpullする。

---

## ThinkPadで pepel-sync がまだ使えない場合

最初にサイトrepoを更新：

    cd ~/pepelmoco-site
    git pull

スクリプトを有効化：

    mkdir -p ~/.local/bin
    ln -sf ~/pepelmoco-site/scripts/pepel-sync ~/.local/bin/pepel-sync
    chmod +x ~/pepelmoco-site/scripts/pepel-sync

確認：

    pepel-sync

---

## Chromebookで pepel-sync がまだ使えない場合

    cd ~/dev/pepelmoco-site
    git pull

    mkdir -p ~/.local/bin
    ln -sf ~/dev/pepelmoco-site/scripts/pepel-sync ~/.local/bin/pepel-sync
    chmod +x ~/dev/pepelmoco-site/scripts/pepel-sync

確認：

    pepel-sync

---

## 作業終了時

まず確認：

    git status

変更をGitHubへ保存するとき：

    git add .
    git commit -m "変更内容"
    git push

※ pepel-sync は勝手にcommit/pushしない。

---

## リポジトリ

Chromebook:

    ~/dev/reservation
    ~/dev/reservation-gas
    ~/dev/pepelmoco-site

ThinkPad:

    ~/pepelmoco-reservation
    ~/pepelmoco-site

---

## 基本ルール

作業開始：
    pepel-sync

作業終了：
    git status
    git add .
    git commit
    git push

GitHubを共通のセーブポイントとして使う。
