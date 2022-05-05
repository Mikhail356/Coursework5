#!/usr/bin/env bash

cat intro.md tech.md math.md real.md end.md l_list_.md > _coursework_pandoc.md
# cat intro.md tech.md math.md real.md end.md l_list.md > _coursework_pandoc.md
#cat intro.md > _coursework_pandoc.md
#https://github.com/citation-style-language/schema/blob/master/schemas/input/csl-data.json
pandoc -f markdown_github+tex_math_dollars+citations -t latex -o _coursework_pandoc.tex --citeproc --bibliography=bibliography.yaml --csl=gost-r-7-0-5-2008-numeric-alphabetical.csl _coursework_pandoc.md

# 3 раза — для корректных ссылок
lualatex coursework.tex
lualatex coursework.tex
lualatex coursework.tex
