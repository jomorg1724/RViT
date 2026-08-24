#!/bin/zsh
cd "$(dirname "$0")"; ln -sfn ../figs figs
pandoc meta.yaml paper.md --pdf-engine=pdflatex --toc --toc-depth=2 \
  -V colorlinks=true -V linkcolor=blue \
  -o RViT_plus_affine_cascade_deepdive.pdf
echo "built RViT_plus_affine_cascade_deepdive.pdf"
