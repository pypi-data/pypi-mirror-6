# -*- coding: utf-8 -*-

u"""BibTeX ファイルを日付でソートして, HTMLとして出力するプログラム

Created by Ryo Murakami and Masaki Adachi
Updated by Yusuke Miyazaki
"""

import sys

from bibtexparser.bparser import BibTexParser

from akatsuki.exporter import export_html
from akatsuki.parser import load_bibtex_file


def main(bibtex_file, html_file):
    u""""""
    entries = load_bibtex_file(bibtex_file)
    export_html(html_file, entries)

#entries = load_bibtex_file("/Users/yusuke/Downloads/hirasawa.bib")
#print(entries)
#sys.exit(0)

# PubMed のURL
PUBMED_URL = 'http://www.ncbi.nlm.nih.gov/pubmed/'
MONTH_DICT = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12
}
HTML_HEADER = [
    '<!DOCTYPE html>\n',
    '<html>\n',
    '<head>\n',
    '<meta charset="utf-8">\n',
    '<title>Bibliography</title>\n',
    '</head>\n',
    '<body>\n',
    '<h1>Bibliography</h1>\n'
]
HTML_FOOTER = [
    '</body>\n',
    '</html>',
]


def amain(bib, html):
    u"""BibTeX をソートし, HTML に変換して出力する処理

    :param bib: 入力する BibTeX ファイル名
    :param html: 出力する HTML ファイル名
    """
    # BibTeX ファイルを開いて読み込む
    with open(bib, 'rU') as bibfile:
        # BibTexPatser で BibTeX ファイルをパースする
        bp = BibTexParser(bibfile)
        # エントリのリストを取得
        entry_list = bp.get_entry_list()

    for entry in entry_list:
        # pmid に対応する URL を追加する
        # エントリの id から pmid を取得
        pmid = entry['id'].strip()
        # id の先頭が pmid でなければ, スキップ
        if pmid[0:4] != 'pmid':
            continue
        # エントリの URL に PubMed の URL をセット
        entry['URL'] = PUBMED_URL + pmid[4:]
        # 月名を数字に変換
        if entry['month'] in MONTH_DICT:
            entry['month_n'] = MONTH_DICT[entry['month']]
        else:
            entry['month_n'] = 0

    # エントリを降順にソート
    entry_list = sorted(entry_list,
                        key=lambda e: 100 * int(e['year']) + int(e['month_n']),
                        reverse=True)

    # HTMLを出力
    fw = open(html, 'w')
    # ヘッダを出力
    fw.writelines(HTML_HEADER)

    # 年の変わり目を検出するための変数
    year = 0

    for entry in entry_list:
        # 年の変わり目に区切り線と見出しを挿入
        if int(entry['year']) != year:
            fw.write('<hr>')
            fw.write('<h2>%s</h2>' % entry['year'])
            year = int(entry['year'])
        # エントリを出力
        fw.write('<p>\n')
        fw.write('%s . ' % entry['author'])
        fw.write('<b><a href="%s">%s</a></b> . ' % (entry['URL'],
                                                    entry['title']))
        fw.write('%s . <i>%s</i>, ' % (entry['year'], entry['journal']))
        if 'volume' in entry:
            fw.write('%s(%s):%s' % (entry['volume'], entry['number'],
                                    entry['pages']))
        fw.write('</p>\n')

    # フッタを出力
    fw.writelines(HTML_FOOTER)
