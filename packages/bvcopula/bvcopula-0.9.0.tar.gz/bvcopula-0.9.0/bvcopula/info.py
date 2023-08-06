## AUTHOR  : Zhenfei Yuan, Taizhong Hu
## EMAIL   : zf.yuan.y@gmail.com; thu@ustc.edu.cn
## URL     : taizhonglab.ustc.edu.cn/software/bvcopula.html
## DATE    : Jan, 3, 2012
## LICENCE : GPL (>= 2)

__doc__="""
BVCOPULA
========

This module mainly contains routines of probability distribution functions,
density functions, random sample generating functions, H-functions and Inverse
H-functions for six bivariate copulas families (will includes BB1, BB6, BB7, BB8
etc families in future). In this package, we label the ten families with an
integer as below.

        0 ~ Independent
        1 ~ Normal 
        2 ~ Student t 
        3 ~ Clayton
        4 ~ Gumbel
        5 ~ Frank
        6 ~ Joe
        7 ~ BB1 (coming soon)
        8 ~ BB6 (coming soon)
        9 ~ BB7 (coming soon)
       10 ~ BB8 (coming soon)

"""



__all__ = [
    'bv_cop_mle',
    'bv_cop_cdf',
    'bv_cop_pdf',
    'bv_cop_loglik',
    'bv_cop_sim',
    'bv_cop_hfunc',
    'bv_cop_inv_hfunc',
    'bv_cop_model_selection'
    ]

