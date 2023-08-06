## AUTHOR  : Zhenfei Yuan, Taizhong Hu
## EMAIL   : zf.yuan.y@gmail.com; thu@ustc.edu.cn
## DATE    : Jan, 3, 2013
## LICENCE : GPL (>= 2)

from numpy.distutils.core import Extension

DESCRIPTION = "Probability and sampling functions for six common seen bivariate copulas"

LONG_DESCRIPTION = """
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

ext_bv_norm = Extension(name = "bvcopula.bvnorm", sources = ['bvcopula/bvnorm.f90',
                                                             'bvcopula/bvnorm.pyf',
                                                             'bvcopula/src/prob.f90',
                                                             'bvcopula/src/lmin.f90',
                                                             'bvcopula/src/rseed.f90'])

ext_bv_t = Extension(name = "bvcopula.bvt", sources = ['bvcopula/bvt.f90',
                                                       'bvcopula/bvt.pyf',
                                                       'bvcopula/src/quadpack.f90',
                                                       'bvcopula/src/blas.f',
                                                       'bvcopula/src/lbfgsb.f',
                                                       'bvcopula/src/linpack.f',
                                                       'bvcopula/src/timer.f',
                                                       'bvcopula/src/prob.f90',
                                                       'bvcopula/src/lmin.f90',
                                                       'bvcopula/src/rseed.f90'])

ext_bv_clayton = Extension(name = "bvcopula.bvclayton", sources = ['bvcopula/bvclayton.f90',
                                                                   'bvcopula/bvclayton.pyf',
                                                                   'bvcopula/src/lmin.f90',
                                                                   'bvcopula/src/rseed.f90'])

ext_bv_gumbel = Extension(name = "bvcopula.bvgumbel", sources = ['bvcopula/bvgumbel.f90',
                                                                 'bvcopula/bvgumbel.pyf',
                                                                 'bvcopula/src/lmin.f90',
                                                                 'bvcopula/src/rseed.f90'])

ext_bv_frank = Extension(name = "bvcopula.bvfrank", sources = ['bvcopula/bvfrank.f90',
                                                               'bvcopula/bvfrank.pyf',
                                                               'bvcopula/src/lmin.f90',
                                                               'bvcopula/src/rseed.f90'])

ext_bv_joe = Extension(name = "bvcopula.bvjoe", sources = ['bvcopula/bvjoe.f90',
                                                           'bvcopula/bvjoe.pyf',
                                                           'bvcopula/src/lmin.f90',
                                                           'bvcopula/src/rseed.f90'])

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(name              = 'bvcopula',
          version           = '0.9.0',
          description       = DESCRIPTION,
          long_description  = LONG_DESCRIPTION,
          author            = "Zhenfei Yuan",
          author_email      = "zf.yuan.y@gmail.com",
          packages          = ['bvcopula'],
          requires          = ['numpy'],
          license           = ['GPL (>= 2)'],
          platforms         = ['Windows', 'Linux', 'Mac OS'],
          url               = "taizhonglab.ustc.edu.cn/software/bvcopula.html",
          ext_modules = [ext_bv_norm, ext_bv_t, ext_bv_clayton, ext_bv_gumbel, ext_bv_frank, ext_bv_joe]
          )