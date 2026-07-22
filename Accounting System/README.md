githubcopilotchatに会計システムを作ってと書いてその後uiも作ってと書いた結果がこのファイルです。
勘定は自分で書くので仕入れ勘定と仕入勘定で二つに分かれて書かれる可能性があったり、総勘定元帳が残高になって入て残高しかわからずそこからしわけに飛べるようにしたりとaiまかせにせず人間が考える必要があることが分かりました。
--ここからgithubcopilotchatがかいてくれました--
# Accounting System

シンプルなPythonベースの会計システム（CLI）です。

## 機能
- 仕訳の追加（複式簿記）
- 仕訳一覧の表示
- 勘定科目ごとの残高確認
- データをJSONファイルに永続化

## 要件
- Python 3.11+

## 使い方

データを保存するファイルを指定して仕訳を追加します:

```bash
python main.py add --file ledger.json --date 2026-07-22 --description "売上" --debit "Cash:100.00" --credit "Revenue:100.00"
```

仕訳一覧:

```bash
python main.py list --file ledger.json
```

勘定科目の残高確認:

```bash
python main.py balance --file ledger.json --account Cash
```
