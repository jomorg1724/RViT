#!/bin/zsh
# Build the deep-dive paper PDF from markdown via pandoc + xelatex.
cd "$(dirname "$0")"
ln -sfn ../figs figs   # figures live in ../figs; markdown references figs/<name>
pandoc meta.yaml paper.md \
  --pdf-engine=xelatex \
  -V colorlinks=true \
  -V mainfont="Arial Unicode MS" \
  -V monofont="Menlo" \
  --toc --toc-depth=2 \
  -o RViT_plus_v5_part2_deepdive.pdf
echo "built RViT_plus_v5_part2_deepdive.pdf"; ls -lah RViT_plus_v5_part2_deepdive.pdf
