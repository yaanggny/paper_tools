import os.path as opath
import sys, os, glob, shutil
import argparse

import subprocess
from multiprocessing import Pool as processPool

from bs4 import BeautifulSoup
cur_dir = opath.dirname(opath.abspath(__file__))


'''
https://openaccess.thecvf.com/menu
https://openaccess.thecvf.com/CVPR2023?day=all
'''

def runProgram(cmd):
    env = os.environ.copy()
    try:
        # print(cmd)
        ret = subprocess.call(cmd, env=env, shell=True)
    except Exception as e:
        print("Error:  failed to run: %s"%cmd)


def get_html_text(file):
    with open(file, 'r') as fd:
        data = fd.read()
    return data

html_f = r'CVPR 2022 Open Access Repository.html'
html = get_html_text(html_f)
# soup = BeautifulSoup(html, "html.parser")
soup = BeautifulSoup(html, "lxml")

paper_div = soup.find(id='content')
if paper_div is None:
    sys.exit(0)
r = paper_div.find_all(['dt', 'dd'])
if r is None:
    print(f'Found no dt, dd tags.')
    sys.exit(0)
# print(f'Found total dt/dd items: {len(r)}')
r.pop(0)
r.pop(-1)

n_papers = len(r)
assert(n_papers % 3 == 0)
n_papers = n_papers // 3
print(f'Found papers: {n_papers}')

tag = r[0]
assert(tag.has_attr('class'))

papers = []
for i in range(n_papers):
    pi = 3*i
    dt = r[pi]
    dd2 = r[pi+2]
    s = {}
    s['title'] = dt.a.get_text().strip()  
    # s['pdf'] = ''  
    # s['supp'] = ''  
    # s['arXiv'] = ''
    # s['bibtex'] = ''
    for c in dd2.children:
        if c.name == 'div' or c.name != 'a':  # bibtex
            continue
        # print(c)
        key = c.get_text().strip()
        url = c.get('href')
        s[key] = url
    # print(s)
    # sys.exit(0)
    papers.append(s)


def save_res_to_markdown(search_res, fo):
    f_dir = opath.dirname(opath.abspath(fo))
    os.makedirs(f_dir, exist_ok=True)

    with open(fo, 'wt') as fd:
        i, n = 0, len(search_res.keys())
        for k, v in search_res.items():
            fd.write(f'## {k}\n')
            seg_line = '' # if i == n-1 else '---\n'                
            fd.write(v + f'\n{seg_line}')
            i += 1
    print(f'Save: {fo}')



keywords = ['match', 'align', 'keypoint']
search_res = {}
for sk in keywords:
    ss = ''
    for s in papers:
        if sk in s['title'].lower():
            url = s['arXiv'] if 'arXiv' in s.keys() else s['pdf']
            ss += f"- [{s['title']}]({url}) | [thecvf]({s['pdf']})\n"
    search_res[sk] = ss
    # print(ss)

fo = 'search.md'
fo = opath.join(cur_dir, fo)
save_res_to_markdown(search_res, fo)