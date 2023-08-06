#*****************************************************************/
# pilib.py    PI   library for python  decimal.Decimal module
#*****************************************************************/
#    PI library containing various historical algorithms for
#    generating PI using Python3.3 and the C accelerated decimal
#    module.
#
#    This module uses and loads dmath.py which provides the decimal
#    support plus the atan(x) routine.
#
#*****************************************************************/
#
#    Mark H. Harris
#      02-13-2014           (new file ported from my BC pilib
#      03-02-2014           (built seperate pilib.py
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
from pdeclib import *

#*****************************************************************/
#* Calculate PI using Arctan function atan(x)                    */
#*     rapid convergence                                         */
#*     see (A History of PI, 144)                                */
#*     Used by John Machin   1706                                */
#*****************************************************************/
def pia1():
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=7
        d1=Decimal(1)
        pi = 16*atan(d1/5) - 4*atan(d1/239)
    return +pi

#*****************************************************************/
#* Calculate PI using Arctan function atan(x)                    */
#*     rapid convergence                                         */
#*     Used by Leonard Euler    born 1707                        */
#*****************************************************************/
def pia2():
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=7
        d1=Decimal(1)
        pi = 8*atan(d1/3) + 4*atan(d1/7)
    return +pi

#*****************************************************************/
#* Calculate PI using Arctan function atan(x)                    */
#*     rapid convergence                                         */
#*     Used by Leonard Euler    born 1707                        */
#*****************************************************************/
def pia3():
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=7
        d1=Decimal(1)
        d3=Decimal(3)
        pi = 20*atan(d1/7) + 8*atan(d3/79)
    return +pi

#*****************************************************************/
#* Calculate PI using Arctan function atan(x)                    */
#*     rapid convergence                                         */
#*     Used by William Rutherford    1841                        */
#*****************************************************************/
def pia4():
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=7
        d1=Decimal(1)
        pi = 16*atan(d1/5) - 4*atan(d1/70) + 4*atan(d1/99)
    return +pi

#*****************************************************************/
#* Calculate PI using Arctan function atan(x)                    */
#*     rapid convergence                                         */
#*     Used by Tseng Chi-hung        1874                        */
#*****************************************************************/
def pia5():
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=7
        d1=Decimal(1)
        pi = 4*atan(d1/2) + 4*atan(d1/3)
    return +pi

#*****************************************************************/
#* Calculate PI using Arctan function atan(x)                    */
#*     rapid convergence                                         */
#*     Used by John Wrench & Daniel Shanks    1963               */
#*          equation found by Stormer in 1896                    */
#*****************************************************************/
def pia6():
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=7
        d1=Decimal(1)
        pi = 24*atan(d1/8) + 8*atan(d1/57) + 4*atan(d1/239)
    return +pi

#*****************************************************************/
#* Calculate PI using Arctan function atan(x)                    */
#*     rapid convergence                                         */
#*     Used by D.F.Ferguson      1947                            */
#*****************************************************************/
def pia7():
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=7
        d1=Decimal(1)
        pi = 12*atan(d1/4) + 4*atan(d1/20) + 4*atan(d1/1985)
    return +pi

#****************************************************************/
#* Calculate PI using AGM Gauss-Legendre Method                 */
#*     Crandall: Projects In Scientific Computation  pp.11-12   */
#*     rapid convergence   (few iterations, fast )              */
#****************************************************************/
def piagm2():
    with localcontext(ctx=None) as cmngr:
        cmngr.prec+=7
        x=Decimal(2).sqrt()
        p=2+x
        y=Decimal(x).sqrt()
        while True:
            s=Decimal(x).sqrt()
            x=(s+1/s)/2
            q=p*((x+1)/(y+1))
            if (q==p): break
            p=q
            s=Decimal(x).sqrt()
            y=((y*s)+(1/s))/(y+1)
    return +p
