"""Reproduce Fig 2 (model schematic) for our variant — a cartoon of the architecture:
image sequence → 4 patches → conv SE-ResNet front-end → Recurrent-ViT self-attention (with memory
feedback) → spatial xLSTM working memory → readout H → actor-critic (RL) + JEPA head.
The self-attention box is variant-specific. Usage: repro_fig2.py <feedback> <label>"""
import os, sys
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
FB=sys.argv[1] if len(sys.argv)>1 else "crossattn1"; LAB=sys.argv[2] if len(sys.argv)>2 else FB
FIGS=os.path.join(os.path.dirname(os.path.abspath(__file__)),"figs"); os.makedirs(FIGS,exist_ok=True)
SA_LABEL={"crossattn1":r"Recurrent ViT self-attention""\n"r"$Q=W_qX,\;K,V=[W\,X\,\Vert\,W\,H^{(t-1)}]$""\n(cross-attention: image + memory keys)",
          "affine_ew":r"Recurrent ViT self-attention""\n"r"$X'=\gamma(H^{(t-1)})\odot X+\beta(H^{(t-1)})$""\n(element-wise affine memory modulation)"}
fig,ax=plt.subplots(figsize=(12,5)); ax.set_xlim(0,12); ax.set_ylim(0,6); ax.axis("off")
def box(x,y,w,h,txt,fc,fs=8):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.05",fc=fc,ec="black",lw=1.2))
    ax.text(x+w/2,y+h/2,txt,ha="center",va="center",fontsize=fs)
def arrow(x1,y1,x2,y2,txt="",ls="-",col="black"):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=14,lw=1.4,ls=ls,color=col))
    if txt: ax.text((x1+x2)/2,(y1+y2)/2+0.15,txt,ha="center",fontsize=6.5,color=col)
# environment image sequence
for i in range(3): ax.add_patch(Rectangle((0.3+0.12*i,3.5-0.12*i),1.0,1.0,fc="0.15",ec="black"))
ax.text(0.9,2.9,"image\nsequence $O^{(t)}$",ha="center",fontsize=7.5)
box(2.0,3.0,1.3,1.6,"4 patches\n$\\{o_i\\}$","0.85",7.5)
box(3.7,3.0,1.7,1.6,"Conv SE-ResNet\nfront-end $f_\\theta$\n$\\to\\hat o_i\\,(128)$","#cfe8cf",7.5)
box(5.8,2.9,2.6,1.9,SA_LABEL.get(FB,FB),"#dfe8fb",7)
box(9.0,3.0,2.6,1.6,"Spatial xLSTM\nworking memory\n$C^{(t)},H^{(t)}$","#f7e0c0",7.5)
box(9.2,0.6,2.2,1.1,"Actor–Critic (RL)\npolicy / value","#f6cccc",7.5)
box(6.2,0.6,2.4,1.1,"JEPA head (aux)\n$4\\times256$ softmax","#e8dff2",7)
# flow arrows
arrow(1.6,4.0,2.0,3.8); arrow(3.3,3.8,3.7,3.8); arrow(5.4,3.8,5.8,3.8,"$x_i=[\\hat o_i\\Vert\\rho\\Vert\\tau]$")
arrow(8.4,3.85,9.0,3.85,"$Z=X+AV$")
arrow(10.3,3.0,10.3,1.7,"readout $H^{(t)}$")
arrow(9.0,3.4,8.6,1.7,"$H^{(t)}$")   # to JEPA
# recurrent memory feedback H -> SA
ax.add_patch(FancyArrowPatch((9.0,4.6),(7.1,4.8),connectionstyle="arc3,rad=-0.4",arrowstyle="-|>",mutation_scale=14,lw=1.6,color="purple"))
ax.text(8.0,5.4,"memory feedback $H^{(t-1)}$",ha="center",fontsize=7,color="purple")
arrow(10.3,0.6,10.3,0.2,"reward $r$",ls="--",col="0.4")
ax.text(6,5.75,f"Figure 2 — Recurrent ViT schematic ({LAB} variant)",ha="center",fontsize=11,weight="bold")
fig.savefig(os.path.join(FIGS,f"fig2_schematic_{LAB}.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
print(f"saved fig2_schematic_{LAB}.png")
