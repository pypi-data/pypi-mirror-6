# Created by G. Peter Lepage (Cornell University) in 12/2013.
# Copyright (c) 2013 G. Peter Lepage. 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version (see <http://www.gnu.org/licenses/>).
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

ctypedef long INT_TYPE
ctypedef double (*cython_integrand)(double[::1]) 
ctypedef double (*cython_integrand_exc)(double[::1]) except? 1e111

cdef class VecCythonIntegrand:
    cdef cython_integrand fcn
    cdef readonly object fcntype

cdef object python_wrapper(cython_integrand fcn)

cdef class VecCythonIntegrandExc:
    cdef cython_integrand_exc fcn
    cdef readonly object fcntype

cdef object python_wrapper_exc(cython_integrand_exc fcn)

cdef class VecPythonIntegrand:
    cdef object fcn
    cdef readonly object fcntype

cdef class VecIntegrand:
    cdef readonly object fcntype

cdef class AdaptiveMap:
    # first index is direction, second is increment
    cdef readonly double[:, ::1] grid
    cdef readonly double[:, ::1] inc
    cdef double[:, ::1] sum_f
    cdef double[:, ::1] n_f

    cpdef map(self, double[:, ::1] y, double[:, ::1] x, double[::1] J, INT_TYPE ny=*)
    cpdef add_training_data(self, double[:, ::1] y, double[::1] f, INT_TYPE ny=*)

cdef class Integrator:
    # inputs
    cdef readonly object fcntype
    cdef readonly INT_TYPE neval
    cdef readonly INT_TYPE[::1] neval_hcube_range
    cdef readonly INT_TYPE nhcube_vec
    cdef readonly INT_TYPE maxinc_axis
    cdef readonly INT_TYPE max_nhcube
    cdef readonly INT_TYPE max_neval_hcube
    cdef readonly INT_TYPE nitn
    cdef readonly double alpha
    cdef readonly double rtol
    cdef readonly double atol
    cdef readonly bint adapt_to_errors
    cdef readonly double beta 
    cdef readonly object analyzer
    # generated
    cdef readonly AdaptiveMap map 
    cdef double[::1] sigf
    cdef double sum_sigf
    cdef bint minimize_sigf_mem
    cdef readonly INT_TYPE nstrat 
    cdef readonly INT_TYPE min_neval_hcube 
    cdef readonly INT_TYPE dim 
    cdef readonly INT_TYPE actual_neval
    # work areas
    cdef double[:, ::1] y
    cdef double[:, ::1] x
    cdef double[::1] jac 
    cdef double[::1] fdv 
    cdef double[::1] fdv2
    cdef INT_TYPE[::1] neval_hcube
    cdef void _init_workareas(self)
    cdef void _resize_workareas(self, INT_TYPE neval_vec)
    cdef object _calculate_neval_hcube(
        self, 
        INT_TYPE hcube_base,
        INT_TYPE nhcube_vec,
        fcn,
        )
    cdef void _generate_random_y_x_jac(
        self, 
        INT_TYPE neval_vec,
        INT_TYPE hcube_base, 
        INT_TYPE nhcube_vec,
        )
    cdef object _integrate_vec(
        Integrator self, 
        fcn,
        INT_TYPE neval_vec,
        INT_TYPE hcube_base, 
        INT_TYPE nhcube_vec,
        )

