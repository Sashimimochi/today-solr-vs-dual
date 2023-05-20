# 今日から始める Solr ベクトル検索

この度は、[今日から始める Solr ベクトル検索](https://techbookfest.org/product/wSCmsmFye1bL6xDWRT6vVK)をお手に取っていただきありがとうございます。

本リポジトリは同書に記載の

- 2.8.5 ジョイン検索
- 4.7.4 ジョイン検索でベクトル検索をする

におけるサンプルコードを公開しているリポジトリです。
書籍と内容と照らし合わせながらご活用ください。

もし、サンプルコードの実装エラーなどを見つけた際は、issue からご連絡ください。

## 環境概要

環境は Docker で構築する想定になっています。

| Service   | Version |
| :-------- | :------ |
| SolrCloud | 9.1.1   |
| Zookeeper | 3.7     |
| Python    | 3.7     |

## Quick Start

各ディレクトリトップから以下のコマンドを実行します。
2 つのネットワーク的に離れたサーバー構成を想定しているので、それぞれ起動が必要になります。
実行すると、コンテナの起動、Solr のコレクション作成が行われます。

```bash
$ cd solr1 # あるいは solr2
$ sh ./launch.sh
```

# Solr

Solr の管理画面には、それぞれ以下でアクセスできます。

- http://localhost:8983/solr/
- http://localhost:8984/solr/

## Maintenance

あまり触る機会はないと思いますが、Solr の実態は `opt/solr/bin/solr` にあります。
コンテナのホームディレクトリは `opt/solr` なので、`bin/solr`でたどり着けます。

例えば、以下のコマンドで Solr のステータス確認ができます。

```bash
$ docker-compose exec solr_node1 /opt/solr/bin/solr status
```

# Frontend(Streamlit)

ベクトル検索用画面にはそれぞれ以下でアクセスできます。

- http://localhost:8501
- http://localhost:8502

# MySQL

UI を持たないので省略します。
