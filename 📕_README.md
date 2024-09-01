## Streamlit

Streamlitは、Pythonで書いたコードを、簡単にWebアプリケーションに変換してくれるツールです。Webアプリケーションとは、インターネット上で動作するアプリケーションのことです。例えば、GoogleマップやYouTubeなどもWebアプリケーションです。
Streamlitを使うと、複雑なWeb開発の知識がなくても、PythonのコードだけでインタラクティブなWebアプリケーションを作成することができます。

Python: 様々なことができる万能なプログラミング言語 (レゴブロック)
Cursor: データベースを操作するための指示棒 (図書館の検索システム)
Streamlit: Pythonコードを簡単にWebアプリケーションに変換するツール (魔法の杖)

これらのツールは、それぞれが独立して存在するのではなく、組み合わせて使うことでより強力な力を発揮します。例えば、Pythonでデータ分析を行い、Cursorでデータベースから必要なデータを取り出し、Streamlitで結果をWebアプリケーションとして表示する、といったことが可能です。

### Streamlitの仮想環境
仮想環境の名前：streamlit_env

my_streamlit_appのディレクトリで起動。
アクティブ化されると、ターミナルのプロンプトに (streamlit_env) のように表示され、仮想環境が有効であることがわかります。
source streamlit_env/bin/activate

作業が終わったら、仮想環境を無効化して通常のPython環境に戻る
deactivate

エイリアス：Streamlitの立ち上げ
stream
```bash
alias stream="cd /Users/shigikasumi/Dropbox/Projects/Projects/99_Automation_Scripts/my_streamlit_app && source streamlit_e$
 ```

エイリアス：Streamlit仮想環境の立ち上げ
streamenv
```bash
alias streamenv="source /Users/shigikasumi/Dropbox/Projects/Projects/99_Automation_Scripts/my_streamlit_app/streamlit_env/bin/activate"
 ```
 
### Project Structure

# プロジェクト構造

## ディレクトリツリー

```
my_streamlit_app/
├── .streamlit/
│   │   └── config.toml
├── css/
│   │   └── invoice_generator.css
├── modules/ #アプリケーション全体で再利用される共通のロジックやユーティリティ関数
│   │   ├── __init__.py      # 必須ファイル（空でもOK）
│   │   ├── image_url_generator.py # 画像URL生成のバックエンド機能
│   │   ├── notion_config.py #Notion API /請求書生成関連の設定
│   │   └── notion_integration.py
├── main.py
├── Home.py
├── dashboard.py  # サンプル
├── DataAnalysis.py  # サンプル
├── proposal.py  # サンプル
├── ImageUrlGenerator.py  # 画像URL生成のロジックをここに配置
├── content_planner.py
├── styles.css #全体のスタイルを記述する
├── invoice_generator.py  # 請求書生成ロジックとUI
├── invoice_output/  # 請求書生成
├── link_collection.py
├── notion_integration.py
├── run_streamlit.sh
├── search_db   # クライアント管理用
├── add_to_notion.py  # クライアント管理（追加）用
├── streamlit_env/  # 仮想環境ディレクトリ
├── task_manager.py
├── requirements.txt
├── 🌳_project_structure.md
└── 📕_README.md
```

### Notion

インテグレーションシークレット
secret_nGXGsWKzJLr1tpbR7kt3eTMVwbfjz9vL4NteDUg2tKc

クライアントリストDB
https://www.notion.so/shigi-k/ea4dfda2bf074b52a6a3a27a691153d5?v=1acb8a8b373347f6ae46c46b7d544579&pvs=4
ea4dfda2bf074b52a6a3a27a691153d5

見込みリストDB
https://www.notion.so/shigi-k/6ab51c8ae24d4ac49789e69123a42ffc?v=7be0340b1461464197c970838c6ea14b&pvs=4
6ab51c8ae24d4ac49789e69123a42ffc

TO DO用データベース

https://www.notion.so/shigi-k/6abab9c4a4374e3db48fcb22f14a1959?v=43a5d0223ed44069a37adfee636e4070&pvs=4
6abab9c4a4374e3db48fcb22f14a1959

プロジェクト管理データベース:
https://www.notion.so/shigi-k/097f9506e00b4b17b0d350bbdfe532d3?v=6da221d02a424edd8aa6a719c34ae24e&pvs=4
097f9506e00b4b17b0d350bbdfe532d3

Time Recordingデータベース：
https://www.notion.so/shigi-k/4dee3cbe43de46959b496bbb337344b0?v=70ed177c94214199aeeb755aea12b2c2&pvs=4
4dee3cbe43de46959b496bbb337344b0

接続先にStreamlitを入れるのを忘れないように！

将来的にどうしたいかというと、Difyとかも組み合わせながら、
LINEマーケティングに関する情報（クライアントのアカウントとか他社の）を集めて分析したり、
それを元にレポート作ったり、そのための提案書を作るためのデータを抽出したりということを
一貫して行いたく。それで、業務効率化のためのpythonを今いくつか作っていますが数が多くなってくるとどのスクリプトがどの業務に使うかややこしくなってきて結局形骸化しそうだったので扱いやすくダッシュボードみたいにできたらという意図でした
今あるのはこんな感じです
DiscordのAIアシスタントボット（Dify）を呼び出す
LINEトーク画面をつくる（これはHTML)
POWERPOINTをmarkdownからつくる
Tsvデータをcsvにする
Googleスプレッドシートをmarkdownテーブルにする、
パワーポイントをマークダウンにする
あるURLのサブページをスクレイピング
サーバーアップした画像からURL生成（今作った）
LINEのグループチャットを月別に切り分ける（今後、中身を分析してレポートを作る）
あるURLのクラスかID選択したらデータを取得してくる（他社や自社のLINE友達アカウント収集に使える）あるURLのHTMLとCSSでーたしゅとくしてくる（LINE内のページのデザイン効率化に役立つかも）
ワードクラウドをつくる
    
