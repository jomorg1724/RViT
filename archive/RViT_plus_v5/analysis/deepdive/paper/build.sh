#!/bin/zsh
# Build the deep-dive paper PDF from markdown via pandoc + pdflatex.
cd "$(dirname "$0")"
# Figures live one level up in ../figs; the markdown references them as figs/<name>.
# Symlink so pandoc's relative image paths resolve from this dir.
ln -sfn ../figs figs
pandoc meta.yaml paper.md \
  --pdf-engine=xelatex \
  -V colorlinks=true \
  -V mainfont="Arial Unicode MS" \
  -V monofont="Menlo" \
  --toc --toc-depth=2 \
  -o RViT_plus_v5_deepdive.pdf
echo "built RViT_plus_v5_deepdive.pdf"
ls -lah RViT_plus_v5_deepdive.pdf
