"""
CR-045 — verification part 2: lock down the CLOSED-FORM smooth-branch curvature
decomposition  λ = λ_HR + λ_noFA  and the kink first-order (cusp) law.

(A) SMOOTH BRANCH (ā<1/N strictly): compare the analytic per-exchange second
    derivative R''_exch(0) at FIXED symmetric criteria to a finite difference at
    the SAME fixed criteria. They must agree. Then show the criterion-
    re-optimised λ adds a PSD (Schur-complement) shift, and report the h-form
    dependence (accelerating h=a^2 is the only smooth-branch concentration risk).

(B) KINK (ā=1/N): show R(t) along the exchange has a CUSP with one-sided slope
    ∝ (β−γ)=sign(r−1); the "second derivative" is an ε-artifact (∝1/ε), the
    SIGN is sign(r−1). Demonstrate the 1/ε scaling.

CR-045, run-013.
"""
from __future__ import annotations
import math
import numpy as np

_SQRT2 = math.sqrt(2.0); _SQRT_2PI = math.sqrt(2.0 * math.pi)
def Phi(x): return 0.5 * (1.0 + math.erf(x / _SQRT2))
def phi(x): return math.exp(-0.5 * x * x) / _SQRT_2PI
H = {"linear": (lambda a: a, lambda a: 1.0, lambda a: 0.0),
     "sqrt":   (lambda a: math.sqrt(a), lambda a: 0.5*a**-0.5, lambda a: -0.25*a**-1.5),
     "p0_3":   (lambda a: a**0.3, lambda a: 0.3*a**-0.7, lambda a: -0.21*a**-1.7),
     "p2":     (lambda a: a*a, lambda a: 2*a, lambda a: 2.0)}
def beta_gamma(r): return 2.0*r/(r+1.0), 2.0/(r+1.0)

N, dmax, f0 = 4, 2.0, 0.5
_CGRID = np.arange(-2.5, 2.5+1e-9, 0.05)

def f_tr(a, h):  return f0 + (1-f0)*h(a)

def dprime(a, r, h):
    a = min(max(a,0.0),1.0)
    b,g = beta_gamma(r); dbase = dmax*f_tr(1.0/N, h)
    dep = dmax*f_tr(a,h)-dbase
    s = b if a>=1.0/N else g
    return max(dbase+s*dep,0.0)

def opt_c_uncued(d_unc, w_u, CR, d_c, c_c_fixed=None, n_unc=3):
    """Symmetric uncued criterion: 1-D grid argmax of the uncued-dependent part
       with cued held (its c optimised jointly via a small 2-D for honesty)."""
    # joint 2-D over (c_c, c_u) on the grid (cued is one group, uncued another)
    HRc = np.array([Phi(d_c/2-c) for c in _CGRID]); OMFc = np.array([Phi(d_c/2+c) for c in _CGRID])
    HRu = np.array([Phi(d_unc/2-c) for c in _CGRID]); OMFu = np.array([Phi(d_unc/2+c) for c in _CGRID])
    val = (0.5*Vv*HRc)[:,None] + (0.5*n_unc*w_u*HRu)[None,:] \
          + 0.5*CR*(OMFc[:,None])*(OMFu[None,:]**n_unc)
    i,j = np.unravel_index(int(np.argmax(val)), val.shape)
    return float(_CGRID[i]), float(_CGRID[j])

def ER_fixed_c(alloc, r, h, c_list):
    """E[R] at EXPLICIT criteria c_list (len N), cued loc 0."""
    ds = [dprime(alloc[i], r, h) for i in range(N)]
    R = 0.0
    for i in range(N):
        wu = Vv if i==0 else w_u
        R += 0.5*wu*Phi(ds[i]/2 - c_list[i])
    prod = 1.0
    for i in range(N):
        prod *= Phi(ds[i]/2 + c_list[i])
    R += 0.5*CR*prod
    return R

print("="*72)
print("(A) SMOOTH BRANCH  ā<1/N : analytic λ vs fixed-criterion finite diff")
print("="*72)
V, v, variant = 0.5, 1, "A"      # value-blind so uncued carry real attention
Vv = V*v; w_u = (1-V)/(N-1); CR = (V*v+(1-V)) if variant=="A" else 1.0
alpha = 0.70                      # ⇒ ā=(1-α)/(N-1)=0.10 < 1/N=0.25 (SMOOTH)
abar = (1-alpha)/(N-1)
print(f"  config: V={V} v={v} variant={variant}  α={alpha} ⇒ ā={abar:.4f} (<1/N) ; w_u={w_u:.4f} CR={CR}")
for hname in ["sqrt","linear","p0_3","p2"]:
    hf, hp, hpp = H[hname]
    g  = dprime(abar, r:=1.0, hf)  # placeholder; recompute per r below
    for r in [0.398, 0.5, 1.0, 2.0]:
        b,gam = beta_gamma(r)
        dbase = dmax*f_tr(1.0/N, hf)
        # smooth γ-branch sensitivity and its a-derivatives (ā<1/N ⇒ s=γ)
        d = dbase + gam*(dmax*f_tr(abar,hf)-dbase)
        gp  = gam*dmax*(1-f0)*hp(abar)          # g'(ā)
        gpp = gam*dmax*(1-f0)*hpp(abar)         # g''(ā)
        d_c = dprime(alpha, r, hf)
        c_c, c_u = opt_c_uncued(d, w_u, CR, d_c)
        # analytic per-EXCHANGE second derivative at fixed criteria
        xH = d/2 - c_u; xF = d/2 + c_u
        HR_d  = 0.5*phi(xH);  HR_dd = 0.25*(-xH)*phi(xH)
        G     = Phi(xF);      G_d   = 0.5*phi(xF);  G_dd = 0.25*(-xF)*phi(xF)
        # HR part:  0.5 w_u · 2[HR_dd g'^2 + HR_d g'']
        lamHR = 0.5*w_u*(HR_dd*gp*gp + HR_d*gpp)            # = (1/2)·(per-exch HR'' )
        # no-FA/CR part: Q·{2G[G_dd g'^2 + G_d g''] − 2 G_d^2 g'^2}, Q=0.5 CR (1-FAR_c) G^{(n_unc-2)}
        FAR_c = Phi(-d_c/2 - c_c)
        n_unc = N-1
        Q = 0.5*CR*(1-FAR_c)*(G**(n_unc-2))
        perexch_noFA = Q*(2*G*(G_dd*gp*gp + G_d*gpp) - 2*G_d*G_d*gp*gp)
        lamFA = 0.5*perexch_noFA
        lam_analytic = lamHR + lamFA           # λ = R''_exch/2
        # finite diff at FIXED criteria along [+1,-1,0] exchange
        eps=1e-4
        c_list=[c_c, c_u, c_u, c_u]
        a0=[alpha,abar,abar,abar]
        ap=[alpha,abar+eps,abar-eps,abar]; am=[alpha,abar-eps,abar+eps,abar]
        R0=ER_fixed_c(a0,r,hf,c_list); Rp=ER_fixed_c(ap,r,hf,c_list); Rm=ER_fixed_c(am,r,hf,c_list)
        lam_fd = ((Rp-2*R0+Rm)/(eps*eps))/2.0
        flag = "" if abs(lam_analytic-lam_fd)<1e-3 else "  <-- MISMATCH"
        print(f"  h={hname:7s} r={r:5.3f}: λ_analytic={lam_analytic:+.5f}  λ_fd(fixed-c)={lam_fd:+.5f}"
              f"  [HR={lamHR:+.4f} noFA={lamFA:+.4f}]{flag}")
    print()

print("="*72)
print("(B) KINK ā=1/N : cusp first-order law, sign = sign(r-1); 1/ε blow-up")
print("="*72)
hf,hp,hpp = H["sqrt"]
alpha = 1.0/N; abar = 1.0/N
def ER_reopt_exch(t, r):
    a=[alpha, abar+t, abar-t, abar]
    ds=[dprime(a[i],r,hf) for i in range(N)]
    # group + exact joint criterion (<=2 groups generally 3 here; use coordinate exact)
    # quick: optimise each distinct d independently is wrong (coupled product) -> do 3-grid coarse
    # Use a 1-restart exact coordinate ascent (sufficient for sign/slope here)
    cidx=[len(_CGRID)//2]*N
    HRg=[np.array([Phi(ds[i]/2-c) for c in _CGRID]) for i in range(N)]
    OMFg=[np.array([Phi(ds[i]/2+c) for c in _CGRID]) for i in range(N)]
    for _ in range(60):
        changed=False
        for i in range(N):
            Pother=1.0
            for j in range(N):
                if j!=i: Pother*=OMFg[j][cidx[j]]
            wu = Vv if i==0 else w_u
            col=0.5*wu*HRg[i]+0.5*CR*Pother*OMFg[i]
            k=int(np.argmax(col))
            if k!=cidx[i]: cidx[i]=k; changed=True
        if not changed: break
    R=0.0
    for i in range(N):
        wu=Vv if i==0 else w_u; R+=0.5*wu*HRg[i][cidx[i]]
    prod=1.0
    for i in range(N): prod*=OMFg[i][cidx[i]]
    return R+0.5*CR*prod

for r in [0.5, 1.0, 2.0]:
    b,gam=beta_gamma(r)
    R0=ER_reopt_exch(0.0,r)
    print(f"  r={r}: β-γ={b-gam:+.3f} (sign={'+' if b>gam else ('0' if abs(b-gam)<1e-9 else '-')})")
    for eps in [1e-2, 5e-3, 1e-3]:
        Rp=ER_reopt_exch(eps,r); Rm=ER_reopt_exch(-eps,r)
        slope_oneside=(Rp-R0)/eps          # one-sided ~ |t| slope (cusp)
        secdiff=(Rp-2*R0+Rm)/(eps*eps)
        print(f"      eps={eps:7.4f}: (R(ε)-R0)/ε={slope_oneside:+.4f}  "
              f"2nd-diff={secdiff:+10.2f}  (ε·2nd-diff={eps*secdiff:+.4f} ~ const ⇒ 1/ε blow-up)")
print("="*72)
