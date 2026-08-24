#!/bin/zsh
# Build the v11 frame-repeat deep-dive PDF from markdown via pandoc + xelatex.
cd "$(dirname "$0")"
pandoc meta.yaml paper.md \
  --pdf-engine=xelatex \
  -V colorlinks=true \
  -V mainfont="Arial Unicode MS" \
  -V monofont="Menlo" \
  --toc --toc-depth=2 \
  -o RViT_plus_v11_framerepeat_deepdive.pdf
echo "built RViT_plus_v11_framerepeat_deepdive.pdf"; ls -lah RViT_plus_v11_framerepeat_deepdive.pdf
