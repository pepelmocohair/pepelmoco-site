# pepel moco 2台開発運用

店ThinkPadと家ChromebookでGitHubをソースコードの中央の正本にする。
CodexセッションではなくGit履歴と各CHECKPOINT.mdから作業を継続する。
2026年10月の営業日設定は本番修正・全31日のGET照合を完了済み。

## pepel-syncの設置

必要環境：Git、Python 3.8以上、GitHubへの読み取り認証。
本体はこのリポジトリの` scripts/pepel-sync `。
サイトrepoの場所をGit remoteで確認してから、そのGitルートで実行する：

```sh
python3 --version
mkdir -p "$HOME/.local/bin"
# 既存コマンドがある場合は内容を確認し、勝手に上書きしない。
ln -s "$(git rev-parse --show-toplevel)/scripts/pepel-sync" "$HOME/.local/bin/pepel-sync"
command -v pepel-sync
pepel-sync --help
```

`~/.local/bin`がPATHにない端末では、まず現在のシェルで
`export PATH="$HOME/.local/bin:$PATH"`として確認する。
永続設定は既存シェル設定を読んで必要な箇所だけ追加する。
この端末の.bashrcには設定済みで、変更不要。

## リポジトリの発見

対象は次の3件。フォルダ名ではなく設定されたGit remote URLとGitルートで識別する。

- pepelmocohair/reservation
- pepelmocohair/reservation-gas
- pepelmocohair/pepelmoco-site

SSH（git@github.com:、ssh://git@github.com/）とHTTPSのURLに対応する。
通常はホーム配下を探索する。隠しディレクトリ・node_modules・仮想環境は除外し、
シンボリックリンクのディレクトリは再帰しない。Git repo内の入れ子は探索しない。
`.git`がファイルのworktreeにも対応する。
ホーム外や除外範囲は探索ルートを明示する：

```sh
pepel-sync --root /実際の開発フォルダ --root /別の開発フォルダ
```

1件でも欠落した場合、複数コピーを発見した場合、探索エラーの場合は更新しない。
対象外の無効な.gitマーカーは警告して除外し、その配下の探索を続ける。
複数コピーの選択や探索対象外の配置は`--repo NAME=PATH`で明示できる。
毎回指定したくない場合は端末固有の`~/.config/pepel-sync/repos.json`に配置を設定する。
この設定はGitへ保存しない。例のパスは各端末で確認した実際のパスへ置き換える：

```json
{
  "reservation": "/実際のフロントGitルート",
  "reservation-gas": "/実際のGAS Gitルート",
  "pepelmoco-site": "/実際のサイトGitルート"
}
```

明示配置でもGitルート・origin URLを検証する。--repoは設定ファイルより優先する。

## 作業開始

```sh
pepel-sync
```

1. 全3件の存在、Gitルート、origin、main、clean、進行中Git操作なしを確認する。
2. 全件のローカル検査が通った場合だけ全3件のorigin/mainをfetchする。
3. 全件のahead/behind/divergedを比較する。
4. 全件合格した場合だけ、behindのrepoを検査済みコミットへfast-forwardする。
5. HEAD一致・cleanを確認し、OK / UPDATED / STOPを一覧表示する。

Git操作はフック・fsmonitor・自動stashを無効にして実行する。
`git merge --ff-only`によるfast-forwardのみで、マージコミットは作らない。
通常のmerge、rebase、reset、stash、force push、commit、pushは行わない。
fetchは追跡参照・FETCH_HEADなどのGitメタデータを更新するが、作業ツリーを変更しない。

dirty、ahead、diverged、detached HEAD、main以外、想定外origin、fetch失敗はSTOP・非ゼロ終了。
全件の検査が終わるまで作業ツリーを1件も更新しない。
更新途中の失敗も非ゼロで停止し、先に更新済みのrepoはUPDATEDと表示する。
複数repoを一括でロールバックはしない。途中停止時には表示された状態を確認する。
実行中に別のGit操作やファイル編集を並行して行わない。

検査だけの場合：

```sh
pepel-sync --check
```

--checkもfetchを行うが、作業ツリーのfast-forwardは行わない。
ローカル検査で止まった場合はfetch・ahead/behindの最新確認は未実施と表示する。
STOP時に自動修復しない。原因を確認してユーザーと対処を決める。

## SSHの注意

この端末では通常SSHがシステム設定ファイルの所有権/権限エラーで失敗した。
恒久的なSSH設定修復はこの同期スクリプト整備に含めていない。
監査で成功した一時指定（GitHubのhost key検証は有効のまま）：

```sh
GIT_SSH_COMMAND='ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=yes' pepel-sync --check
```

この指定はSSH設定を読み込まないため、端末固有の鍵・proxy設定が必要な端末へ無条件で適用しない。
通常コマンドがfetch失敗する場合は成功扱いにならずSTOPする。

## 作業終了・端末切り替え

テスト・差分・CHECKPOINTを確認し、対象変更だけをcommitしてpushする。
ローカルHEADとGitHub mainの一致・working tree cleanを確認してから端末を切り替える。
片方に未pushの変更を残したままもう片方で開発しない。
別端末の未push変更はpepel-syncから検知できないため、終了確認は必須。

関連`pepel-publish`には自動rebaseがある。pepel-syncとは別の既存コマンドであり、
今回変更していない。安全な開始確認の代わりに使わない。

## 安全性テスト

```sh
python3 scripts/tests/test_pepel_sync.py
```

一時ディレクトリ内の架空repo・bare remoteだけでGit履歴を作り、
本番GitHub・実開発repoへcommit/pushや作業ツリー変更を行わない。
ネットワーク不要。clean、dirty、ahead、behind、diverged、欠落、想定外origin、
fetch失敗、detached、別ブランチ、複数コピー、--check、worktree、端末設定、
更新途中失敗、フック抑止を検証する。
