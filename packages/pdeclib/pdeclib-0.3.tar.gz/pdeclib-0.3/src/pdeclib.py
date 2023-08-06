#*****************************************************************/
# pdeclib.py v0.3    library for use with C accelerated decimal
#*****************************************************************/
#
#  The new C accelerated decimal module for python3.3 implements
#  the IEEE standard 854-1987, and therefore does not implement
#  many of the transcendental, or scientific functions.
#
#  The pdeclib module implements many of the common transcendental
#  or scientific functions with arbitrary precsision using the
#  accelerated decimal module written by Stefan Krah.
#
#            (default dscale(n) precision is preset n = 42)
#
#  With pdeclib.py in the PYTHONPATH the library is loaded in the
#     usual way with:  from pdeclib import *
#
#  To use the PI library (including pdeclib) load with the usual
#     syntax:  from pilib import *
#
#*****************************************************************/
#  author:     Mark H. Harris         harrismh777@gmail.com
# license:     GPLv3
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
#   CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
#   INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#   MECHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENCIAL DAMAGES (INCLUDING, BUT
#   NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#   LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERUPTION)
#   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE
#   EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#*****************************************************************/
#  CHANGE LOG
#       2-25-2014                   new library pdeclib.py v0.1
#                   Decimal
#                   d(float)    (for interactive use only)
#                   dscale(n)   (for interactive use only)
#                                  default n=42
#                               globals set by dscale(n):
#                                   __gpi__    reset D(0)
#               *   d2r(d)-->degree to radian
#               *   r2d(r)-->radian to degree
#               *   fact(x) 
#               *   pow(x, y)   built-in
#               *   root(x, y)
#               *   sqrt(x)     built-in
#               *   sqrt_n(x, n)
#               *   ln(x)       built-in
#               *   log10(x)    built-in
#               *   exp(x)      built-in
#               *   epx(x)      native e^(x)
#               *   sin(x)
#                       __sin__(q)
#               *   cos(x)
#                       __cos__(q)
#               *   tan(x)
#                       __tan__(q)
#               *   sinh(x)
#               *   cosh(x)
#               *   tanh(x)     (uses sinh/cosh)
#               *   asin(x)
#                       __asin__(q)
#               *   acos(x)     (uses __asin__)
#               *   atan(x)
#                       __atan__(q)         q**2 < 1
#                       __atan__Lt_1__(q)   q < -1
#                       __atan__Gt_1__(q)   q > 1
#               *   sinh_1(x)   (uses ln sqrt)
#               *   cosh_1(x)   (uses ln sqrt)  x > 1
#               *   tanh_1(x)   (uses sinh sqrt)
#               *   get_PI()
#                       __piagm__()
#                  
#  --------------------------------------------------------------
#
#       02-27-2014                          released date v0.1
#       02-28-2014  epx(x) was incorrectly coded for e(1) v0.2
#  --------------------------------------------------------------
#       03-02-2014  placed extraneous PI routines in pilib.py
#                       Uses pdeclib.py; rounded correctly with
#                       localcontext;  context manager.
#       03-02-2014  added get_PI() function to retreive __piagm__()
#                       from cache, or calculate if not.
#                       Use  +get_PI() for context rounding
#       03-02-2014  modified dscale(n) for interactive use only
#       03-02-2014  removed Decimal(numform) function /not necessary
#       03-02-2014  renamed deg():  d2r()
#       03-02-2014  renamed rad():  r2d()
#       03-02-2014  added d(float) for interactive use only. This
#                       function is NOT used internally, and only
#                       makes it easier for an interactive user
#                       to build a Decimal from a float literal.
#       03-02-2014  epx(x) modified to use less memory for
#                       intermediate results, reducing overflow
#                       for large values while improving performance.
#                       Might be useful elsewhere (note)
#                       Credit: Wolfgang Maier, thanks.
#       03-03-2014  using context manager to handle local precision
#                       and correct rounding; decimal handles it...
#                    [ with localcontext(ctx=None) as cmngr: ]
#                       Functions exempt (-)
#                       Functions with (*) above are have been
#                       implemented with a context manager.
#       03-03-2014                            released date v0.3
#*****************************************************************/
from decimal import *

#*****************************************************************/
# template(x)
#*****************************************************************/
def template(x):
    """ template(x)    function template for consistency

            (x can be string, int, or decimals)
            (returns decimal rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        # code goes here
        # code goes here
        ret=Decimal(x)
    return +ret

def dscale(n):
    """ dscale(n)     sets the context precision {n} digits

           (interactive use only)
           (returns previous context precision)
    """
    prec=getcontext().prec
    setcontext(Context(prec=n, rounding='ROUND_HALF_EVEN'))
    global __gpi__
    __gpi__ = Decimal(0)
    return prec

def d2r(d):
    """ d2r(d)--> degree to radian
                return radians: d converted to radians
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        global __gpi__
        if (__gpi__==Decimal(0)):
            __gpi__ = Decimal(__piagm__())
        r=Decimal(d)*__gpi__/180
    return +r

def r2d(r):
    """ r2d(r)--> radian to degree
                return degrees: r converted to degrees
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        global __gpi__
        if (__gpi__==Decimal(0)):
            __gpi__ = Decimal(__piagm__())
        d=Decimal(r)*180/__gpi__
    return +d

def d(float):
    """ d(float)   for interactive console use only

              This function is not used internally, and is
              provided to make construction of a Deciaml
              easier by forcing a call to the Decimal string
              constructor from a float literal, avoiding the
              binary to decimal error in conversion.
    """
    return Decimal(str(float))

def get_PI():
    """ Display __gpi__, or calculate and display if non exist


    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        global __gpi__
        if (__gpi__==Decimal(0)):
            __gpi__ = Decimal(__piagm__())
        else:
            print("retrieved __gpi__ from cache")
    return __gpi__

#*****************************************************************/
# fact(x)     factorial    {x}  int x > 0
#*****************************************************************/
def fact(x):
    """ fact(x)    factorial    {x} int x > 0        

            (x can be int)
    """
    for n in range(1,x,1):
        x*=n
    return x

#*****************************************************************/
# pow(x, y)  return decimal equiv x**y
#*****************************************************************/
def pow(x, y):
    """ pow(x, y)     decimal equiv  x**y

            (x & y can be strings, int, or decimals)
            (returns decimal rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        p=Decimal(x).__pow__(Decimal(y))
    return +p

#*****************************************************************/
# root(x, y)   return decimal equiv  x**(1/y)
#*****************************************************************/
def root(x, y):
    """ root(x, y)        decimal equiv x**(1/y)

            (x & y can be strings, int, or decimals)
            (returns decimal rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        rt=Decimal(x).__pow__(Decimal(1)/Decimal(y))
    return +rt

#*****************************************************************/
# sqrt(x)    return decimal sqrt(x) rounded to context precision
#*****************************************************************/
def sqrt(x):
    """ sqrt(x)     square root function

             (x may be string, int, or decimal)
             (returns decimal rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        sqr=Decimal(x).sqrt()
    return +sqr

#*****************************************************************/
# sqrt_n(x, n)    return decimal sqrt(x) rounded to {n} digits 
#*****************************************************************/
def sqrt_n(x, n):
    """ sqrt_n(x, n)     square root to {n} digits

             (x may be string, int, or decimal)
             (returns decimal rounded to {n} digits)
    """
    nprec=(n+7)
    with localcontext(ctx=None) as cmngr:
        cmngr.prec=nprec
        sqr=Decimal(x).sqrt()
    return sqr

#*****************************************************************/
# ln(x)    return decimal natural loge(x)
#*****************************************************************/
def ln(x):
    """ ln(x)      {x}   real x > 0

            (x can be string, int, float, or decimals)
            (returns decimal natural loge(x) in context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        log=Decimal(x).ln()
    return +log

#*****************************************************************/
# log10(x)    return decimal base 10 LOG
#*****************************************************************/
def log10(x):
    """ log10(x)     {x}   real x > 0

            (x can be string, int, or decimals)
            (returns decimal LOG10 rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        log=Decimal(x).log10()
    return log

#*****************************************************************/
# exp(x)    return decimal equiv  e^(x)    uses built-in
#*****************************************************************/
def exp(x):
    """ exp(x)    {x}    all x real values

            (x can be string, int, or decimals)
            (returns decimal e(x) rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        ex=Decimal(x).exp()
    return +ex

#*****************************************************************/
# epx(x)    return decimal equiv e^(x)    native python
#*****************************************************************/
def epx(x):
    """ epx(x)    {x}   all real values

            epx(x) = 1 + x + (x^2)/2! + (x^3)/3! + (x^4)/4! +...
    
            Native python routine for speed comparison with
              built-in exp() performance.
                ~same ~same for large dscale(10000)

            (x can be string, int, or decimals)
            (returns decimal e^(x) rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        q=Decimal(x)
        c=1
        new_element=q
        ex=new_element+1
        prev_ex=Decimal(0)
        while (ex!=prev_ex):
            prev_ex=ex
            c+=1
            new_element*=q/c
            ex+=new_element
    return +ex

#*****************************************************************/
# sin(x)     {x}    all real x in radians
#*****************************************************************/
def sin(x):
    """ sin(x)

        {x}    all real x in radians

        sin(x) = x - (x^3/3!) + (x^5/5!) - (x^7/7!) . . .

        (x can be string, int, or decimals)
        (returns sin in decimal rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec*=2
        n = Decimal(x)
        xx = -(n**2)
        d = 1
        c = d
        s = n/d
        prev_s = Decimal(0)
        while (s!=prev_s):
            prev_s = s
            n *= xx
            c += 1
            d *= c
            c += 1
            d *= c
            s += n/d
    return +s

#*****************************************************************/
# __sin__(q)     {q}    all real q in radians
#*****************************************************************/
def __sin__(q):
    """ __sin__(q)

        {q}    all real q in radians
    """
    n = Decimal(q)
    qq = -(n**2)
    d = 1
    c = d
    s = n/d
    prev_s = Decimal(0)
    while (s!=prev_s):
        prev_s = s
        n *= qq
        c += 1
        d *= c
        c += 1
        d *= c
        s += n/d
    return s

#*****************************************************************/
# asin(x)     {x}   x**2 < 1   -(pi/2) < asin(x) < (pi/2)
#*****************************************************************/
def asin(x):
    """ asin(x)   {x}   x**2 < 1   -(pi/2) < asin(x) < (pi/2)

        sin-1(x)=x+(x^3)/(2*3)+(x^5*1*3)/(2*4*5)+(x^7*1*3*5)/(2*4*6*7)...

            (cf.  series CRC 29th  p.279 )
            (x can be string, int, or decimals)
            (returns decimal asin(x) rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec*=2
        angle_mod=False
        global __gpi__
        if (__gpi__==Decimal(0)):
            __gpi__ = Decimal(__piagm__())
        half_pi=__gpi__/2    
        s=Decimal(x)
        if (s>=Decimal(.8) or s<Decimal(-.8)):
            angle_mod=True
            s=((Decimal(1)-Decimal(x)**2).sqrt()).copy_sign(Decimal(x))
    #--------------------------------------------/
    # angle modification required because this
    #   routine converges very slowly for values
    #   near +/- 1. we convert the sin to a cos,
    #   find asin of that, then convert the radian
    #   by subtracting from half_pi.
    #--------------------------------------------/
        xx=s**2
        nx=s               # First Term setup
        nc=-1              # All series algorithms work
        noc=1              #   essentially the same way,
        d1c=0              #   but asin is a little more
        d2c=1              #   complicated.
        dec=1              #
        doc=1
        prev_s=Decimal(0)
        while (s!=prev_s): # series Loop until convergence
            prev_s=s
            nc+=2          # numerator counter
            nx*=xx         # numerator x component
            noc*=nc        # numerator odd component
            n=noc*nx    # new numerator
            d1c+=2         # denominator even counter
            d2c+=2         # denominator odd counter
            dec*=d1c       # denominator even component
            doc=d2c        # denominator odd component
            d=dec*doc   # new denominator
            s+=n/d      # series += new numerator / new denominator
    #--------------------------------------------/
    # angle modification happens here, from above
    #   when the sin is too close to -1 or 1
    #--------------------------------------------/
    if (angle_mod==True):
        if (s<0):
            half_pi*=(-1)
        s = half_pi - s
    return +s

#*****************************************************************/
# __asin__(q)     {q}   q**2 < 1   -(pi/2) < asin(q) < (pi/2)
#*****************************************************************/
def __asin__(q):
    """ __asin__(q)   {q}   q**2 < 1   -(pi/2) < asin(q) < (pi/2)

            (returns decimal asin(q) rounded to context precision)
    """
    angle_mod=False
    half_pi=__gpi__/2    
    s=Decimal(q)
    if (s>=Decimal(.8) or s<Decimal(-.8)):
        angle_mod=True
        s=((Decimal(1)-Decimal(q)**2).sqrt()).copy_sign(Decimal(q))
    qq=s**2
    nq=s               
    nc=-1              
    noc=1              
    d1c=0              
    d2c=1              
    dec=1              
    doc=1
    prev_s=Decimal(0)
    while (s!=prev_s): 
        prev_s=s
        nc+=2          
        nq*=qq         
        noc*=nc        
        n=noc*nq    
        d1c+=2         
        d2c+=2         
        dec*=d1c       
        doc=d2c        
        d=dec*doc   
        s+=n/d      
    if (angle_mod==True):
        if (s<0):
            half_pi*=(-1)
        s = half_pi - s
    return s

#*****************************************************************/
# cos(x)     {x}    all real x in radians
#*****************************************************************/
def cos(x):
    """ cos(x)

        {x}    all real x in radians

        cos(x) = 1 - (x^2/2!) + (x^4/4!) - (x^6/6!) . . .

        (x can be string, int, or decimals)
        (returns cos in decimal rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec*=2
        xx = -(Decimal(x)**2)
        n = Decimal(1)
        d = 1
        c = 0
        cs = n/d
        prev_cs = Decimal(0)
        while (cs!=prev_cs):
            prev_cs = cs
            n *= xx
            c += 1
            d *= c
            c += 1
            d *= c
            cs += n/d
    return +cs

#*****************************************************************/
# __cos__(q)     {q}    all real q in radians
#*****************************************************************/
def __cos__(q):
    """ __cos__(q)

        {q}    all real q in radians
    """
    qq = -(Decimal(q)**2)
    n = Decimal(1)
    d = 1
    c = 0
    cs = n/d
    prev_cs = Decimal(0)
    while (cs!=prev_cs):
        prev_cs = cs
        n *= qq
        c += 1
        d *= c
        c += 1
        d *= c
        cs += n/d
    return cs

#*****************************************************************/
# acos(x)      {x}       x**2 < 1   0 < acos(x) < pi
#*****************************************************************/
def acos(x):
    """ acos(x)    {x}       x**2 < 1   0 < acos(x) < pi

        cos-1(x)=(pi/2)-[x+(x^3)/(2*3)+(x^5*1*3)/(2*4*5)+(x^7*1*3*5)/(2*4*6*7)...]

            (cf.  series CRC 29th  p.279 )
            (based on  sin-1(x)  uses asin(x)  )
            (x can be string, int, or decimals)
            (returns decimal acos(x) rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec*=2
        global __gpi__
        if (__gpi__==Decimal(0)):
            __gpi__ = Decimal(__piagm__())
        ac = __asin__(x)
        half_pi=__gpi__/2
        ac = half_pi - ac
    return +ac

#*****************************************************************/
# tan(x)    {x}     all real values
#*****************************************************************/
def tan(x):
    """ tan(x)    {x}    all real values

        (x can be string, int, or decimals)
        (returns a decimal rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec*=2
        q=Decimal(x)
        global __gpi__
        if (__gpi__==Decimal(0)):
            __gpi__ = Decimal(__piagm__())
        if (q<((__gpi__)/2)) and (q>(-(__gpi__)/2)):
            t=__tan__(q)
        else:
            t=__sin__(q)/__cos__(q)
    return +t


#*****************************************************************/
# __tan__(q)    {q}    q: Deciaml    (pi/2) > q > -(pi/2)
#*****************************************************************/
def __tan__(q):
    """ tan(q)    {q}    q: Decimal    (pi/2) > q > -(pi/2)

        {q} q<=1 t=s/sqrt(1-s**2)   {q} q>1 t=sqrt(1-c**2)/c

        (x can be string, int, or decimals)
        (returns a decimal rounded to context precision)
    """
    if (q<=1):
        s=__sin__(q)
        t = s/(1-s**2).sqrt()
    else:
        c=__cos__(q)
        t = ((1-c**2).sqrt())/c
    return t

#*****************************************************************/
# atan(x)    {x}   all real values  
#*****************************************************************/
def atan(x):
    """ atan(x)           {x}   all real values  

            (x can be string, int, or decimals)
            (returns decimal atan(x) rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec*=2
        n=Decimal(x)
        global __gpi__
        if (__gpi__==Decimal(0)):
            __gpi__ = Decimal(__piagm__())
        if (n == Decimal(1)):
            a = __gpi__/4
        elif (n == Decimal(-1)):
            a = -(__gpi__/4)
        elif (n < Decimal(-1)):
            a = __atan__Lt_neg1__(n)
        elif (n > Decimal(1)):
            a = __atan__Gt_1__(n)
        else:
            a = __atan__(n)
    return +a

#*****************************************************************/
# __atan__Gt_1__(q)     {q}   q > 1
#*****************************************************************/
def __atan__Gt_1__(q):
    """ __atan__Gt_1__(q)    {q}    q > 1

            (q: Decimal(q)   )
            (returns decimal atan(q) rounded to context precision)
    """
    global __gpi__
    qq = -(q**2)
    p = __gpi__/2
    n = Decimal(1)
    dx = -q
    c = 1
    d = dx*c
    p += n/d
    prev_p=Decimal(0)
    while (p!=prev_p):
        prev_p=p
        c+=2
        dx*=qq
        d=dx*c
        p+=n/d    
    return p

#*****************************************************************/
# __atan__Lt-1(q)    {q}   q < -1  
#*****************************************************************/
def __atan__Lt_neg1__(q):
    """ __atan__Lt-1(q)   {q}    q < -1

            (q: Decimal(q)   )
            (returns decimal atan(q) rounded to context precision)
    """
    global __gpi__
    qq = -(q**2)
    p = -(__gpi__/2)
    n = Decimal(1)
    dx = -q
    c = 1
    d = dx*c
    p += n/d
    prev_p=Decimal(0)
    while (p!=prev_p):
        prev_p=p
        c+=2
        dx*=qq
        d=dx*c
        p+=n/d
    return p

#*****************************************************************/
# __atan__(q)     {q} (q**) < 1    gregory power series
#*****************************************************************/
def __atan__(q):
    """ __atan__(q)     {q}  (q**2) < 1    Gregory Power Series

            atan(x) = x/1 - (x^3)/3 + (x^5)/5 - (x^7)/7 + (x^9)/9...

            q: Decimal(q)   {q}  (q**2) < 1
    """
    xx = -(q**2)
    n = q
    d = 1
    t = n/d
    p = Decimal(0)
    while (p!=t):
        p = t
        n *= xx
        d += 2
        t += n/d
    return p

#*****************************************************************/
# sinh(x)     {x}   all real values     abs(x) < infinity
#*****************************************************************/
def sinh(x):
    """ sinh(x)    {x}   all real values     abs(x) < infinity

            sinh(x)= x + (x^3/3!) + (x^5/5!) + (x^7/7!) +...

            (x can be string, int, or decimals)
            (returns decimal sinh(x) rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec*=2
        s=Decimal(x)
        xx=s**2
        n=s
        d=1
        dc=1
        prev_s=Decimal(0)
        while (s!=prev_s):
            prev_s=s
            n*=xx
            dc+=1
            d*=dc
            dc+=1
            d*=dc
            s+=n/d
    return +s

#*****************************************************************/
# sinh_1(x)        {x}    all real values     
#*****************************************************************/
def sinh_1(x):
    """ sinh_1(x)          {x}    all real values 

            (x can be string, int, float, or decimals)
            (returns decimal sinh-1(x) rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        n=Decimal(x)
        s = ((n**2 + 1).sqrt() + n).ln()
    return +s

#*****************************************************************/
# cosh(x)      {x}    all real values      abs(x) < infinity
#*****************************************************************/
def cosh(x):
    """ cosh(x)

             {x}    all real values      abs(x) < infinity

         cosh(x) = 1 + (x^2/2!) + (x^4/4!) + (x^6/6!) +...

            (x can be string, int, or decimals)
            (returns cosh(x) in decimal rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec*=2
        xx = Decimal(x)**2
        n = Decimal(1)
        d = 1
        c = 0
        ch = n/d
        prev_ch = Decimal(0)
        while (ch!=prev_ch):
            prev_ch = ch
            n *= xx
            c += 1
            d *= c
            c += 1
            d *= c
            ch += n/d
    return +ch

#*****************************************************************/
# cosh_1(x)        {x}    real values     x > 1
#*****************************************************************/
def cosh_1(x):
    """ cosh_1(x)          {x}    real values   x > 1

             positive values primary
             
            (x can be string, int, float, or decimals)
            (returns decimal cosh_1(x) rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        n=Decimal(x)
        c = ((n**2 - 1).sqrt() + n).ln()
    return +c

#*****************************************************************/
# tanh(x)     {x}    all real values
#*****************************************************************/
def tanh(x):
    """ tanh(x)        {x}    all real values

            (x can be string, int, or decimals)
            (returns decimal tanh(x) rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=7
        t=sinh(x)/cosh(x)
    return +t

#*****************************************************************/
# tanh_1(x)        {x}   all real values
#*****************************************************************/
def tanh_1(x):
    """ tanh_1(x)      {x}   all real values

            (x can be string, int, float, or decimals)
            (returns decimal tanh_1(x) rounded to context precision)
    """
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=14
        n=Decimal(x)
        t = sinh_1(n/(1 - n**2).sqrt())
    return +t

#*****************************************************************/
# __piagm__()    Calculate PI using AGM Gauss-Legendre Algorithm
#*****************************************************************/
def __piagm__():
    """ __piagm__()

        Calculate PI   using Gauss-Legendre Algorithm
                                   Commonly used AGM PI routine
                      (rapid convergence, few iterations, very fast )
                      (returns PI with local context manager        )
                      (called by dscale(n)  default, interactive    )
    """
    a=Decimal(1)
    b=1/Decimal(2).sqrt()
    t=1/Decimal(4)
    x=Decimal(1)
    prev_b=Decimal(0)
    while (b!=prev_b):
        prev_b=b
        y=a
        a=(a+b)/2
        b=Decimal(b*y).sqrt()
        t-=x*(y-a)**2
        x*=2
    sp=((a+b)**2)/(4*t)
    return sp

default_prec=dscale(42)
