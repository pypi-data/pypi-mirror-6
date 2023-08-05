#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import array

# Special points in FCC lattice
G1=[0,0,0]
G2=[1,1,1]
L=[1/2.0,1/2.0,1/2.0]
W=[1,1./2,3./2]
X=[0,0,1]
XP=[1,1,0]
qpath=array([G1,X,G2,L])

def get_EOS(d, comment=""):
    # Fitting functions
    def BMEOS(v,v0,b0,b0p):
        return (b0/b0p)*(pow(v0/v,b0p) - 1)
    fitfunc = lambda p, x: [BMEOS(xv,p[0],p[1],p[2]) for xv in x]
    errfunc = lambda p, x, y: fitfunc(p, x) - y
    
    pv=array([d[:,0]**3,d[:,1]]).T
    
    # Estimate the initial guess assuming b0p=1
    # Limiting volumes
    v1=min(pv[:,0])
    v2=max(pv[:,0])
    # The pressure is falling with the growing volume
    p2=min(pv[:,1])
    p1=max(pv[:,1])
    b0=(p1*v1-p2*v2)/(v2-v1)
    v0=v1*(p1+b0)/b0
    # Initial guess
    p0=[v0,b0,1]
    #Fitting
    #print p0
    fit, succ = optimize.leastsq(errfunc, p0[:], args=(pv[:,0],pv[:,1]))
    
    # Ranges - the ordering in pv is not guarateed at all!
    # In fact it may be purely random.
    x=numpy.array([min(pv[:,0]),max(pv[:,0])])
    y=numpy.array([min(pv[:,1]),max(pv[:,1])])
    
    # Plot the P(V) curves and points for the crystal
    # Plot the points
    plot(pv[:,0]**1/3,pv[:,1],'.',label='Calc. '+comment)
    
    # Mark the center P=0 V=V0
    axvline(fit[0]**1/3,ls='--')
    axhline(0,ls='--')
    
    # Plot the fitted B-M EOS through the points
    xa=numpy.linspace(x[0],x[-1],20)
    plot(xa**1/3,fitfunc(fit,xa),'-', label="B-M fit:\n$V_0$=%f ($A_0$=%f),\n$B_0$=%f kBar,\n$B'_0$=%f  " 
         % (fit[0], fit[0]**(1.0/3), fit[1], fit[2]) )
    legend()
    ylabel('Pressure (kBar)')
    xlabel('Lattice constant ($\mathrm{\AA}$)')
    draw();
    return fit, pv


def analize_dir(idx, ex=True, bdir='/home/jochym/Desktop/Fizyka/', 
                qp=array([G1,X,G2,L]), lbl=None, ax=None, castep=False):
    s=0
    t=[]
    for x in [0]+map(norm,qp[1:]-qp[:-1]):
        s+=x
        t.append(s)
    
    par=calcData[idx]
    
    try:
        frq=loadtxt(bdir + idx +'/'+par['prefix']+'.freq.gp')
    except IOError :
        print "Cannot open frequency file in", wd
        return
    if ax :
        ax1=ax[0]
    else :
        ax1=subplot2grid([1,4],[0,3],colspan=1)
    
    phdos=loadtxt(bdir+idx+'/'+params['prefix']+'.dos')
    clr=ax1.plot(phdos[:,1],cminv2meV*phdos[:,0])[0].get_color()
    ax1.yaxis.set_label_position("right")
    ax1.yaxis.tick_right()
    ax1.xaxis.tick_top()
    
    if ax :
        ax2=ax[1]
    else :
        ax2=subplot2grid([1,4],[0,0],colspan=3,sharey=ax1)

    
    clr=None
    
    if lbl :
        lbltxt=", ".join(["%s" % (l,) for l in lbl if not (l in par.keys())])
        lbltxt+=", ".join(["%s" % (par[l],) for l in lbl if l in par.keys()])
    else :
        lbltxt=idx    
    
    for i in range(frq.shape[1]-1):
        if clr :
            ax2.plot(frq[1:,0], cminv2meV*frq[1:,i+1],'.',color=clr)
        else :
            clr=ax2.plot(frq[1:,0], cminv2meV*frq[1:,i+1],'.',label=lbltxt)[0].get_color()
        
        
    if ex :
        frqexp1=loadtxt('thO2-phon.png.dat')
        clr=ax2.plot(frqexp1[:,0],frqexp1[:,1],'o')[0].get_color();
        frqexp2=loadtxt('thO2-phon-2.dat')
        ax2.plot(t[2]-frqexp2[:,0],frqexp2[:,1],'o',color=clr)[0];
        frqexp3=loadtxt('thO2-phon-3.dat')
        ax2.plot(t[2]+frqexp3[:,0],frqexp3[:,1],'o',color=clr,label='Experiment')[0];
    if castep :
        frqexp4=loadtxt('castep-take2.csv')
        ax2.plot((t[3]-t[0])*frqexp4[:,0], frqexp4[:,1],'o', label='CASTEP')

        
    title("M-P grid (e.s.): %(kx)dx%(ky)dx%(kz)d (phon): %(nq)d^3" % par)
    xlim(0,max(frq[1:,0]))
    ylim(0,ylim()[1])
    #xticks(t,[u'Γ','X',u'Γ','L'])
    vlines(xticks()[0][1:-1],ylim()[0],ylim()[1],linestyles='--')
    ylabel('Energy (meV)')
    subplots_adjust(wspace=0)
    return [ax1,ax2]
