#!/bin/zsh
cd "$(dirname "$0")"
ln -sfn ../figs figs
pandoc meta.yaml paper.md --pdf-engine=xelatex -V colorlinks=true \
  -V mainfont="Arial Unicode MS" -V monofont="Menlo" --toc --toc-depth=2 \
  -o RViT_plus_v11_part5_distractor_deepdive.pdf
echo "built RViT_plus_v11_part5_distractor_deepdive.pdf"; ls -lah RViT_plus_v11_part5_distractor_deepdive.pdf
