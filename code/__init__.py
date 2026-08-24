"""RViT+ FiLM — canonical single-stream Recurrent ViT with stable FiLM memory
feedback, a conv (end-to-end) front-end, and the standard NHP task battery
(validity4, vda4, setsize{2,4,9}, luo_maunsell_*, krauzlis). Reuses the
PER + PAC + QR-DQN harness. See README.md."""
from .model import RViTPaperModel  # noqa: F401
__all__ = ["RViTPaperModel"]
