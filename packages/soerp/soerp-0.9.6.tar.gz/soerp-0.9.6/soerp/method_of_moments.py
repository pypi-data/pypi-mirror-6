import numpy as np
from copy import copy

assume_linear = False # if True, the sqc and scp parts are ignored

###############################################################################

def standard_lc(lc, stdevs):
    """
    Standardizes the first derivatives in preparation for moment calculation.
    
    Parameters
    ----------
    lc : array
        The first partial derivatives of a single output.
    stdevs : array
        The standard deviations for each input
    
    Returns
    -------
    slc : array
        The standardized first-order derivatives
    """
    return np.array([coef*stdev for coef, stdev in zip(lc, stdevs)])

###############################################################################

def standard_qc(qc, stdevs):
    """
    Standardizes the pure second derivatives in preparation for moment 
    calculation.
    
    Parameters
    ----------
    qc : array
        The pure second partial derivatives of a single output.
    stdevs : array
        The standard deviations for each input
    
    Returns
    -------
    sqc : array
        The standardized pure second-order derivatives
    """
    return np.array([coef*stdev**2 for coef, stdev in zip(qc, stdevs)])

###############################################################################

def standard_cp(cp, stdevs):
    """
    Standardizes the cross-product second derivatives in preparation for 
    moment calculation.
    
    Parameters
    ----------
    cp : 2d-array
        The cross-product second-order partial derivatives matrix of a single 
        output.
    stdevs : array
        The standard deviations for each input
    
    Returns
    -------
    scp : 2d-array
        The standardized cross-product second-order derivatives matrix
    """
    nvars = cp.shape[1]
    scp = np.empty_like(cp)
    if nvars >= 2:
        for i in range(nvars):
            for j in range(i+1, nvars):
                scp[i,j] = cp[i,j]*stdevs[i]*stdevs[j]
                scp[j,i] = scp[i,j]
    return scp

###############################################################################

def standardize(lc, qc, cp, stdevs):
    """
    A helper function to convert normal first and second-order partial 
    derivatives to "standardized" partial derivatives, in preparation for
    moment calculations.
    
    Parameters
    ----------
    lc : array
        The first partial derivatives of a single output.
    qc : array
        The pure second partial derivatives of a single output.
    cp : 2d-array
        The cross-product second-order partial derivatives matrix of a single 
        output.
    stdevs : array
        The standard deviations for each input
    
    Returns
    -------
    slc : array
        The standardized first-order derivatives
    sqc : array
        The standardized pure second-order derivatives
    scp : 2d-array
        The standardized cross-product second-order derivatives matrix
    """
    slc = standard_lc(lc, stdevs)
    sqc = standard_qc(qc, stdevs)
    scp = standard_cp(cp, stdevs)
    return slc, sqc, scp

###############################################################################

def rawmoment(slc, sqc, scp, vm, k):
    """
    This is where the resultant distribution moments are calculated. MODIFY 
    THIS CODE AT YOUR OWN RISK. These equations have been verified with
    published equations and example problems by N.D. Cox.
    
    Each of the derivative components need to be standardized prior to input
    to this function. This means multiplying them by their respective
    standard deviations, depending on the order of the derivative. Helper
    functions have been defined for this purpose (standard_lc, standard_qc,
    and standard_cp). However, this is only necessary if manually calling this
    function rather than using soerp_numeric below.
    
    Parameters
    ----------
    slc : array
        The standardized first derivative terms.
    sqc : array
        The standardized pure second derivative terms
    scp : 2d-array
        The standardized cross-product second derivative terms
    vm : 2d-array
        The first 9 (starting at 0) standardized distribution moments (one 
        row for each input variable, corresponding to the derivative array 
        order). See the documentation for ``soerp_numeric`` for more details.
    k : int
        The kth distribution moment to calculate.
    
    Returns
    -------
    rm : scalar
        The kth raw distribution moment
    """
    lc = copy(slc)
    qc = copy(sqc)
    cp = copy(scp)
    n = len(lc)
    
    if assume_linear:
        qc[:] = 0.0
        cp[:,:] = 0.0
        
    ans = 0.0
        
    ############################
    # The 0th raw moment
    
    if k==0:
        ans = 1
        
    ############################
    # The 1st raw moment
    
    elif k==1:
        for i in range(n):
            ans += qc[i]*vm[i,2]
    
    ############################
    # The 2nd raw moment
    
    elif k==2:
        for i in range(n):
            ans += lc[i]**2*vm[i,2] + 2*lc[i]*qc[i]*vm[i,3] + qc[i]**2*vm[i,4]
        
        if n>=2:
            for i in range(n-1):
                for j in range(i+1, n):
                    ans += (2*qc[i]*qc[j] + cp[i,j]**2)*vm[i,2]*vm[j,2]
    
    ############################
    # The 3rd raw moment
    
    elif k==3:
        for i in range(n):
            ans += lc[i]**3*vm[i,3] + qc[i]**3*vm[i,6] + \
                   3*lc[i]**2*qc[i]*vm[i,4] + 3*lc[i]*qc[i]**2*vm[i,5]
        
        if n>=2:
            for i in range(n-1):
                for j in range(i+1, n):
                    ans += cp[i,j]**3*vm[i,3]*vm[j,3] + \
                           6*lc[i]*lc[j]*cp[i,j]*vm[i,2]*vm[j,2] + \
                           6*qc[i]*qc[j]*cp[i,j]*vm[i,3]*vm[j,3]
            for i in range(n):
                for j in range(n):
                    if j!=i:
                        ans += 3*qc[i]**2*vm[i,4]*qc[j]*vm[j,2] + \
                               6*lc[i]*qc[j]*cp[i,j]*vm[i,2]*vm[j,3] +\
                               3*qc[i]*lc[j]**2*vm[i,2]*vm[j,2] + \
                               6*lc[i]*qc[i]*qc[j]*vm[i,3]*vm[j,2] + \
                               3*lc[i]*cp[i,j]**2*vm[i,3]*vm[j,2] + \
                               3*qc[i]*cp[i,j]**2*vm[i,4]*vm[j,2]
        
        if n>=3:
            for i in range(n-2):
                for j in range(i+1, n-1):
                    for k in range(j+1, n):
                        ans += (6*qc[i]*qc[j]*qc[k] + \
                                6*cp[i,j]*cp[i,k]*cp[j,k] + 
                                3*(qc[i]*cp[j,k]**2 + \
                                qc[j]*cp[i,k]**2 + \
                                qc[k]*cp[i,j]**2))*vm[i,2]*vm[j,2]*vm[k,1]
    
    ############################
    # The 4th raw moment
    
    elif k==4:
        for i in range(n):
            ans += lc[i]**4*vm[i,4] + qc[i]**4*vm[i,8] + \
                   4*lc[i]**3*qc[i]*vm[i,5] + 4*lc[i]*qc[i]**3*vm[i,7] + \
                   6*lc[i]**2*qc[i]**2*vm[i,6]
        
        if n>=2:
            for i in range(n-1):
                for j in range(i+1, n):
                    ans += 6*lc[i]**2*lc[j]**2*vm[i,2]*vm[j,2] + \
                           6*qc[i]**2*qc[j]**2*vm[i,4]*vm[j,4] + \
                           cp[i,j]**4*vm[i,4]*vm[j,4] + \
                           12*cp[i,j]*(lc[i]**2*lc[j]*vm[i,3]*vm[j,2] + \
                                       lc[i]*lc[j]**2*vm[i,2]*vm[j,3]) + \
                           12*cp[i,j]*qc[i]*qc[j]*(qc[i]*vm[i,5]*vm[j,3] + \
                                                   qc[j]*vm[i,3]*vm[j,6]) + \
                           12*qc[i]*qc[j]*(lc[i]**2*vm[i,4]*vm[j,2] + \
                                           lc[j]**2*vm[i,2]*vm[j,4] + \
                                           2*lc[i]*lc[j]*vm[i,3]*vm[j,3]) + \
                           6*cp[i,j]**2*(lc[i]**2*vm[i,4]*vm[j,2] + \
                                         lc[j]**2*vm[i,2]*vm[j,4] + \
                                         2*lc[i]*lc[j]*vm[i,3]*vm[j,3]) + \
                           6*cp[i,j]**2*(qc[i]**2*vm[i,6]*vm[j,2] + \
                                         qc[j]**2*vm[i,2]*vm[j,6] + \
                                         2*qc[i]*qc[j]*vm[i,4]*vm[j,4]) + \
                           12*cp[i,j]*(lc[j]*qc[i]*(lc[j]*vm[i,3]*vm[j,3] + \
                                                    2*lc[i]*vm[i,4]*vm[j,2]) + \
                                       lc[i]*qc[j]*(lc[i]*vm[i,3]*vm[j,3] + \
                                                    2*lc[j]*vm[i,2]*vm[j,4])) +\
                           12*cp[i,j]*(lc[i]*qc[j]*(qc[j]*vm[i,2]*vm[j,5] + \
                                                    2*qc[i]*vm[i,4]*vm[j,3]) + \
                                       lc[j]*qc[i]*(qc[i]*vm[i,5]*vm[j,2] + \
                                                    2*qc[j]*vm[i,3]*vm[j,4])) +\
                           12*cp[i,j]**2*(qc[i]*(lc[i]*vm[i,5]*vm[i,2] + \
                                                 lc[j]*vm[i,4]*vm[j,3]) + \
                                          qc[j]*(lc[i]*vm[i,3]*vm[j,4] + \
                                                 lc[j]*vm[i,2]*vm[j,5]))
            for i in range(n):
                for j in range(n):
                    if i!=j:
                        ans += 4*qc[i]**3*qc[j]*vm[i,6]*vm[j,2] + \
                               4*qc[i]*lc[j]**3*vm[i,2]*vm[j,3] + \
                               12*lc[i]*qc[i]*lc[j]**2*vm[i,3]*vm[i,2] + \
                               12*lc[i]*qc[i]**2*qc[j]*vm[i,5]*vm[i,2] + \
                               12*lc[i]*qc[i]*qc[j]**2*vm[i,3]*vm[j,4] + \
                               4*lc[i]*cp[i,j]**3*vm[i,4]*vm[j,3] + \
                               4*qc[i]*cp[i,j]**3*vm[i,5]*vm[j,3] + \
                               6*qc[i]**2*lc[j]**2*vm[i,4]*vm[j,2]
            
        if n>=3:
            for i in range(n-2):
                for j in range(i+1, n-1):
                    for k in range(j+1, n):
                        ans += (12*qc[i]**2*qc[j]*qc[k] + \
                               6*cp[i,j]**2*cp[i,k]**2 + \
                               12*qc[i]*(qc[k]*cp[i,j]**2 + qc[j]*cp[i,k]**2) + \
                               6*qc[i]**2*cp[j,k])*vm[i,4]*vm[j,2]*vm[k,2]
                        ans += (12*qc[i]*qc[j]**2*qc[k] + \
                               6*cp[i,j]**2*cp[j,k]**2 + \
                               12*qc[j]*(qc[k]*cp[i,j]**2 + qc[i]*cp[j,k]**2) + \
                               6*qc[j]**2*cp[i,k]**2)*vm[i,2]*vm[j,4]*vm[k,2]
                        ans += (12*qc[i]*qc[j]*qc[k]**2 + \
                               6*cp[i,k]**2*cp[j,k]**2 + \
                               12*qc[k]*(qc[i]*cp[j,k]**2 + qc[j]*cp[i,k]**2) + \
                               6*qc[k]**2*cp[i,j]**2)*vm[i,2]*vm[j,2]*vm[k,4]
                        ans += (12*cp[i,j]**2*cp[i,k]*cp[j,k] + \
                               24*qc[i]*qc[j]*qc[k]*cp[i,j] + \
                               4*qc[k]*cp[i,j]**3 + \
                               24*qc[i]*qc[k]*cp[i,k]*cp[j,k])*vm[i,3]*vm[j,3]*vm[k,2]
                        ans += (12*cp[i,j]*cp[i,k]**2*cp[j,k] + \
                               24*qc[i]*qc[j]*qc[k]*cp[i,k] + \
                               4*qc[j]*cp[i,k]**3 + \
                               24*qc[i]*qc[k]*cp[i,j]*cp[j,k])*vm[i,3]*vm[j,2]*vm[k,3]
                        ans += (12*cp[i,j]*cp[i,k]*cp[j,k]**2 + \
                               24*qc[i]*qc[j]*qc[k]*cp[j,k] + \
                               4*qc[i]*cp[j,k]**3 + \
                               24*qc[j]*qc[j]*cp[i,j]*cp[i,k])*vm[i,2]*vm[j,3]*vm[k,3]
                        ans += (12*cp[i,j]*cp[i,k]*cp[j,k] + \
                               24*qc[i]*qc[j]*qc[k]*cp[j,k] + \
                               4*qc[i]*cp[j,k]**3 + \
                               24*qc[j]*qc[k]*cp[i,j]*cp[i,k])*vm[i,2]*vm[j,3]*vm[k,3]
                        ans += 24*(qc[i]*qc[j]*qc[k] + \
                               cp[i,j]*cp[i,k]*cp[j,k])*(lc[i]*vm[i,3]*vm[j,2]*vm[k,2] + \
                                                         lc[j]*vm[i,2]*vm[j,3]*vm[k,2] + \
                                                         lc[k]*vm[i,2]*vm[j,2]*vm[k,3])
                        ans += 12*(lc[i]*cp[j,k]**2*vm[i,2]*(cp[i,j]*vm[j,3]*vm[k,2] + \
                               cp[i,k]*vm[j,2]*vm[k,3]) + lc[j]*cp[i,k]**2*vm[j,2]*(cp[i,j]*vm[i,3]*vm[k,2] + \
                               cp[j,k]*vm[i,2]*vm[k,3]) + \
                               lc[k]*cp[i,j]**2*vm[k,2]*(cp[i,k]*vm[i,3]*vm[j,2] + \
                               cp[j,k]*vm[i,2]*vm[j,3]))
                        ans += 12*(qc[i]*cp[j,k]**2*vm[i,3]*(cp[i,j]*vm[j,3]*vm[k,2] + \
                               cp[i,k]*vm[j,2]*vm[k,3]) + qc[j]*cp[i,k]**2*vm[j,3]*(cp[i,j]*vm[i,3]*vm[k,2] + \
                               cp[j,k]*vm[i,2]*vm[k,3]) + \
                               qc[k]*cp[i,j]**2*vm[k,3]*(cp[i,k]*vm[i,3]*vm[j,2] + \
                               cp[j,k]*vm[i,2]*vm[j,3]))
                        ans += 24*cp[i,j]*cp[i,k]*cp[j,k]*(qc[i]*vm[i,4]*vm[j,2]*vm[k,2] + \
                               qc[j]*vm[i,2]*vm[j,4]*vm[k,2] + qc[k]*vm[i,2]*vm[j,2]*vm[k,4])
                        ans += vm[i,2]*vm[j,2]*vm[k,2]*(12*(qc[i]*qc[j]*lc[k]**2 + \
                               qc[i]*qc[k]*lc[j]**2 + qc[j]*qc[k]*lc[i]**2) + \
                               6*(lc[i]**2*cp[j,k]**2 + lc[j]**2*cp[i,k]**2 + \
                               lc[k]**2*cp[i,j]**2) + \
                               24*(cp[i,j]*cp[i,k]*lc[j]*lc[k] + \
                                   cp[i,j]*cp[j,k]*lc[i]*lc[k] + \
                                   cp[i,k]*cp[j,k]*lc[i]*lc[j]) + \
                               24*(lc[i]*lc[j]*qc[k]*cp[i,j] + \
                                   lc[i]*lc[k]*qc[j]*cp[i,k] + \
                                   lc[j]*lc[k]*qc[i]*cp[j,k]))
                        ans += vm[i,3]*vm[j,2]*vm[k,2]*(24*lc[j]*cp[i,j]*qc[i]*qc[k] + \
                               24*lc[k]*cp[i,k]*qc[i]*qc[j] + \
                               12*lc[i]*cp[j,k]**2*qc[i] + \
                               24*lc[j]*cp[i,k]*cp[j,k]*qc[i] + \
                               24*lc[k]*cp[i,j]*cp[j,k]*qc[i] + \
                               12*lc[i]*cp[i,k]**2*qc[j] + \
                               12*lc[i]*cp[i,j]**2*qc[k])
                        ans += vm[i,2]*vm[j,3]*vm[k,2]*(24*lc[i]*cp[i,j]*qc[j]*qc[k] + \
                               24*lc[k]*cp[j,k]*qc[i]*qc[j] + \
                               12*lc[j]*cp[i,k]**2*qc[j] + \
                               24*lc[i]*cp[i,k]*cp[j,k]*qc[j] + \
                               24*lc[k]*cp[i,j]*cp[i,k]*qc[j] + \
                               12*lc[j]*cp[j,k]**2*qc[i] + \
                               12*lc[j]*cp[i,j]**2*qc[k])
                        ans += vm[i,2]*vm[j,2]*vm[k,3]*(24*lc[i]*cp[i,k]*qc[j]*qc[k] + \
                               24*lc[j]*cp[j,k]*qc[i]*qc[k] + \
                               12*lc[k]*cp[i,j]**2*qc[k] + \
                               24*lc[i]*cp[i,j]*cp[j,k]*qc[k] + \
                               24*lc[j]*cp[i,j]*cp[i,k]*qc[k] + \
                               12*lc[k]*cp[j,k]**2*qc[i] + \
                               12*lc[k]*cp[i,k]**2*qc[j])
        
        if n>=4:
            for i in range(n-3):
                for j in range(i+1, n-2):
                    for k in range(j+1, n-1):
                        for m in range(k+1, n):
                            ans += vm[i,2]*vm[j,2]*vm[k,2]*vm[m,2]*(24*(qc[i]*qc[j]*qc[k]*qc[m] +\
                                   cp[i,j]*cp[i,k]*cp[j,m]*cp[k,m] + \
                                   cp[i,j]*cp[i,m]*cp[j,k]*cp[k,m] + \
                                   cp[i,k]*cp[i,m]*cp[j,k]*cp[j,m] + \
                                   qc[i]*cp[j,k]*cp[j,m]*cp[k,m] + \
                                   qc[j]*cp[i,k]*cp[i,m]*cp[i,m] + \
                                   qc[k]*cp[i,j]*cp[i,m]*cp[j,m] + \
                                   qc[m]*cp[i,j]*cp[i,k]*cp[j,k]) + \
                                   12*(qc[i]*qc[j]*cp[k,m]**2 + \
                                       qc[i]*qc[k]*cp[j,m]**2 + \
                                       qc[i]*qc[m]*cp[j,k]**2 + \
                                       qc[j]*qc[k]*cp[i,m]**2 + \
                                       qc[j]*qc[m]*cp[i,k]**2 + \
                                       qc[k]*qc[m]*cp[i,j]**2) + \
                                   6*(cp[i,j]**2*cp[k,m]**2 + \
                                      cp[i,k]**2*cp[j,m]**2 + \
                                      cp[i,m]**2*cp[j,k]**2))
    
    ############################
    
    else:
        print('Can only calculate raw moments k = 0 to 4. Sorry.')
        ans = None
    
    return ans
    
###############################################################################

def centralmoment(vi, k):
    """
    Converts raw distribution moments to central moments
    
    Parameters
    ----------
    vi : array
        The first four raw distribution moments
    k : int
        The central moment (0 to 4) to calculate (i.e., k=2 is the variance)
    
    Returns
    -------
    cm : scalar
        The central moment itself
        
    """
    if k==0:
        ans = 1
    elif k==1:
        ans = 0
    elif k==2:
        ans = vi[2] - vi[1]**2
    elif k==3:
        ans = vi[3] - 3*vi[2]*vi[1] + 2*vi[1]**3
    elif k==4:
        ans = vi[4] - 4*vi[3]*vi[1] + 6*vi[2]*vi[1]**2 - 3*vi[1]**4
    else:
        print('Can only calculate central moments k = 0 to 4. Sorry.')
        ans = None
    return ans

###############################################################################

def variance_components(slc, sqc, scp, var_moments, vz):
    """
    Calculate the 1st and 2nd-order output variance components for each input
    variable.
    
    Parameters
    ----------
    slc : array
        The standardized first derivative terms.
    sqc : array
        The standardized pure second derivative terms
    scp : 2d-array
        The standardized cross-product second derivative terms
    var_moments : 2d-array
        The first 9 (starting at 0) standardized distribution moments (one 
        row for each input variable, corresponding to the derivative array 
        order). See the documentation for ``soerp_numeric`` for more details.
    vz : array
        The 1st-4th central output distribution moments
    
    Returns
    -------
    var_comp_lc : array
        The actual variance components from the 1st-order terms
    var_comp_qc : array
        The actual variance components from the pure 2nd-order terms
    var_comp_cp : 2d-array
        The actual variance components from the cross-product 2nd-order terms
    """
    n = len(slc)
    var_comp_lc = np.empty(n)
    var_comp_qc = np.empty(n)
    var_comp_cp = np.empty((n, n))

    for i in range(n):
        slc_tmp = copy(slc)
        slc_tmp[i] = 0.0
        vy_tmp = [rawmoment(slc_tmp, sqc, scp, var_moments, k) for k in range(3)]
        var_comp_lc[i] = vz[2] - centralmoment(vy_tmp, 2)

    for i in range(n):
        sqc_tmp = copy(sqc)
        sqc_tmp[i] = 0.0
        vy_tmp = [rawmoment(slc, sqc_tmp, scp, var_moments, k) for k in range(3)]
        var_comp_qc[i] = vz[2] - centralmoment(vy_tmp, 2)

    for i in range(n-1):
        for j in range(i+1, n):
            scp_tmp = copy(scp)
            scp_tmp[i,j] = 0.0
            scp_tmp[j,i] = 0.0
            vy_tmp = [rawmoment(slc, sqc, scp_tmp, var_moments, k) for k in range(3)]
            var_comp_cp[i,j] = vz[2] - centralmoment(vy_tmp, 2)

    return var_comp_lc, var_comp_qc, var_comp_cp

###############################################################################

def variance_contrib(var_comp_lc, var_comp_qc, var_comp_cp, vz):
    """
    Convert actual variance components to percent contributions (best if used
    in conjunction with ``variance_components`` function).
    
    Parameters
    ----------
    var_comp_lc : array
        The actual variance components from the 1st-order terms
    var_comp_qc : array
        The actual variance components from the pure 2nd-order terms
    var_comp_cp : 2d-array
        The actual variance components from the cross-product 2nd-order terms
    vz : array
        The 1st-4th central output distribution moments
    
    Returns
    -------
    var_contrib_lc : array
        The contribution percentage of the variance components from the 
        1st-order terms
    var_contrib_qc : array
        The contribution percentage of the variance components from the pure 
        2nd-order terms
    var_contrib_cp : 2d-array
        The contribution percentage of the variance components from the 
        cross-product 2nd-order terms
        
    """
    n = len(var_comp_lc)
    var_contrib_lc = np.empty_like(var_comp_lc)
    var_contrib_qc = np.empty_like(var_comp_qc)
    var_contrib_cp = np.empty_like(var_comp_cp)

    for i in range(n):
        if vz[2]:
            var_contrib_lc[i] = np.abs(var_comp_lc[i]/vz[2])
        else:
            var_contrib_lc[i] = 0.0

    for i in range(n):
        if vz[2]:
            var_contrib_qc[i] = np.abs(var_comp_qc[i]/vz[2])
        else:
            var_contrib_qc[i] = 0.0

    for i in range(n - 1):
        for j in range(i + 1, n):
            if vz[2]:
                var_contrib_cp[i, j] = np.abs(var_comp_cp[i, j]/vz[2])
            else:
                var_contrib_cp[i, j] = 0.0
        
    return var_contrib_lc, var_contrib_qc, var_contrib_cp
    
###############################################################################

def soerp_numeric(slc, sqc, scp, var_moments, func0, title=None, debug=False, 
    silent=False):
    """
    This performs the same moment calculations, but expects that all input
    derivatives and moments have been put in standardized form. It can also
    describe the variance contributions and print out any output distribution
    information, both raw and central moments.
    
    Parameters
    ----------
    slc : array
        1st-order standardized derivatives (i.e., multiplied by the standard 
        deviation of the related input)
    sqc : array
        2nd-order derivatives (i.e., multiplied by the standard 
        deviation squared, or variance, of the related input)
    scp : 2d-array
        2nd-order cross-derivatives (i.e., multiplied by the two standard 
        deviations of the related inputs)
    var_moments : 2-d array
        Standardized moments where row[i] contains the first 9 moments of 
        variable x[i]. FYI: the first 3 values should always be [1, 0, 1]
    func0 : scalar
        System mean (i.e. value of the system evaluated at the means of all
        the input variables)
        
    Optional
    --------
    title : str
        Identifier for results that get printed to the screen
    debug : bool, false by default
        If true, all intermediate calculation results get printed to the screen
    silent : bool, false by default
        If true, nothing gets printed to the screen (overrides debug).
    
    Returns
    -------
    moments : list
        The first four standard moments (mean, variance, skewness and kurtosis
        coefficients)
    
    Example
    -------
    Example taken from the original SOERP user guide by N. D. Cox:
        >>> norm_moments = [1, 0, 1, 0, 3, 0, 15, 0, 105]
        >>> lc = [-802.65, -430.5]
        >>> qc = [205.54, 78.66]
        >>> cp = np.array([[0, -216.5], [-216.5, 0]])
        >>> vm = np.array([norm_moments, norm_moments])
        >>> f0 = 4152
        >>> soerp_numeric(lc, qc, cp, vm, f0,
        ...     title='EXAMPLE FROM ORIGINAL SOERP USER GUIDE')
        ********************************************************************************
        **************** SOERP: EXAMPLE FROM ORIGINAL SOERP USER GUIDE *****************
        ********************************************************************************
        Variance Contribution of lc[x0]: 66.19083%
        Variance Contribution of lc[x1]: 19.04109%
        Variance Contribution of qc[x0]: 8.68097%
        Variance Contribution of qc[x1]: 1.27140%
        Variance Contribution of cp[x0, x1]: 4.81572%
        ********************************************************************************
        MEAN-INTERCEPT (EDEL1)....................  2.8420000E+02
        MEAN......................................  4.4362000E+03
        SECOND MOMENT (EDEL2).....................  1.0540873E+06
        VARIANCE (VARDL)..........................  9.7331770E+05
        STANDARD DEVIATION (RTVAR)................  9.8656865E+02
        THIRD MOMENT (EDEL3)......................  1.4392148E+09
        THIRD CENTRAL MOMENT (MU3DL)..............  5.8640938E+08
        COEFFICIENT OF SKEWNESS SQUARED (BETA1)...  3.7293913E-01
        COEFFICIENT OF SKEWNESS (RTBT1)...........  6.1068742E-01
        FOURTH MOMENT (EDEL4).....................  5.0404781E+12
        FOURTH CENTRAL MOMENT (MU4DL).............  3.8956371E+12
        COEFFICIENT OF KURTOSIS (BETA2)...........  4.1121529E+00
        ********************************************************************************
    """
    if not silent:
        print('\n', '*'*80)
        if title:
            print('{:*^80}'.format(' SOERP: ' + title + ' '))

    ############################

    vy = np.empty(5)
    if debug and not silent:
        print('*'*80)
    for k in range(5):
        vy[k] = rawmoment(slc, sqc, scp, var_moments, k)
        if debug and not silent:
            print('Raw Moment {}: {}'.format(k, vy[k]))

    ############################

    vz = np.empty(5)
    if debug and not silent:
        print('*'*80)
    for k in range(5):
        vz[k] = centralmoment(vy, k)
        if debug and not silent:
            print('Central Moment {}: {}'.format(k, vz[k]))
    sysmean = float(vy[1] + func0)

    ############################

    # Calculate variance contributions
    vc_lc, vc_qc, vc_cp = variance_components(slc, sqc, scp, var_moments, vz)
    vlc, vqc, vcp = variance_contrib(vc_lc, vc_qc, vc_cp, vz)
    n = len(slc)

    if not silent:
        print('*'*80)
        for i in range(n):
            print('Variance Contribution of lc[x{:d}]: {:7.5%}'.format(i, vlc[i]))

        for i in range(n):
            print('Variance Contribution of qc[x{:d}]: {:7.5%}'.format(i, vqc[i]))

        for i in range(n - 1):
            for j in range(i + 1, n):
                print('Variance Contribution of cp[x{:d}, x{:d}]: {:7.5%}'.format(i, j, vcp[i, j]))
        
        
    ############################

    stdev = vz[2]**(0.5)
    if stdev:
        rtbt1 = vz[3]/vz[2]**(1.5)
        beta2 = vz[4]/vz[2]**2
    else:
        rtbt1 = 0.0
        beta2 = 0.0
    beta1 = rtbt1**2
    if not silent:
        print('*'*80)
        print('MEAN-INTERCEPT (EDEL1)....................','{: 8.7E}'.format(vy[1]))
        print('MEAN......................................','{: 8.7E}'.format(sysmean))
        print('SECOND MOMENT (EDEL2).....................','{: 8.7E}'.format(vy[2]))
        print('VARIANCE (VARDL)..........................','{: 8.7E}'.format(vz[2]))
        print('STANDARD DEVIATION (RTVAR)................','{: 8.7E}'.format(stdev))
        print('THIRD MOMENT (EDEL3)......................','{: 8.7E}'.format(vy[3]))
        print('THIRD CENTRAL MOMENT (MU3DL)..............','{: 8.7E}'.format(vz[3]))
        print('COEFFICIENT OF SKEWNESS SQUARED (BETA1)...','{: 8.7E}'.format(beta1))
        print('COEFFICIENT OF SKEWNESS (RTBT1)...........','{: 8.7E}'.format(rtbt1))
        print('FOURTH MOMENT (EDEL4).....................','{: 8.7E}'.format(vy[4]))
        print('FOURTH CENTRAL MOMENT (MU4DL).............','{: 8.7E}'.format(vz[4]))
        print('COEFFICIENT OF KURTOSIS (BETA2)...........','{: 8.7E}'.format(beta2))
        print('*'*80)
    
    return [sysmean, vz[2], rtbt1, beta2]

if __name__=='__main__':
    # standardized moments of a normal distribution: 
    norm_moments = [1, 0, 1, 0, 3, 0, 15, 0, 105]
    
    lc = [-802.65, -430.5]
    qc = [205.54, 78.66]
    cp = np.array([[0, -216.5], [-216.5, 0]])
    
    vm = np.array([norm_moments, norm_moments])
    f0 = 4152
    
    m = soerp_numeric(lc, qc, cp, vm, f0,
        title='EXAMPLE FROM ORIGINAL SOERP USER GUIDE')
    
    print('Returned moments:')
    print('  Mean.................... {}'.format(m[0]))
    print('  Variance................ {}'.format(m[1]))
    print('  Standardized Skewness... {}'.format(m[2]))
    print('  Standardized Kurtosis... {}'.format(m[3]))
