import math

# Hard code min/max pH for now..
_PH_MIN = 3.4
_PH_MAX = 10.0

def bare_bones(cocktail1, cocktail2, compute=True):
    """
    Implementation of the "bare bones" metric from C6 (Newman et al. 2010). 

    This function implements a modified Canberra metric to compute the
    distance between two cocktails based on the concentration of their
    compounds. 

    .. math:: D(a,b) = \\frac{1}{T}\\sum\\limits_{t=1}^T \\frac{|[a_t]-[b_t]|}{max[t]} 

    Where :math:`T` is the number of distinct compounds in cocktails
    :math:`a` and :math:`b`, :math:`[a_t]` is the concentration of compound
    :math:`t` in cocktail :math:`a`, and :math:`max[t]` is the maximum
    concentration for compound :math:`t` across all known screens

    :param cocktail cocktail1: First cocktail to compare
    :param cocktail cocktail2: Second cocktail to compare

    :returns: The distance score between 0 and 1
        
    """

    a = cocktail1.map_by_name()
    b = cocktail2.map_by_name()

    distinct_compounds = list(set(a.keys() + b.keys()))

    distance = 0
    for name in distinct_compounds:
        if name not in a:
            distance += 1
        elif name not in b:
            distance += 1
        else:
            conc_diff = math.fabs(a[name].conc - b[name].conc)
            distance += float(conc_diff) / a[name].conc_max
            
    if not compute:
        return [distance, len(distinct_compounds)]

    return distance/len(distinct_compounds)


def distance(cocktail1, cocktail2):
    """
    Implementation of the "extended" metric from C6 (Newman et al. 2010).
    Incorporates pH, ion, and PEG factors.

    .. math::  
        \\begin{eqnarray}
           D_{ij} & = & \\frac{1}{T+3}\\Biggl(\\biggl(\\Bigl(\\sum_{t=1}^{T}\\frac{\\left|\\left[s_{ti}\\right]-\\left[s_{tj}\\right]\\right|}{\\max\\left[s_{t}\\right]}\\Bigr)+\\Bigl(\\frac{\\left|E(pH_{i})-E(pH_{j})\\right|}{gul(pH)-gll(pH)}\\Bigr)\\biggr) \\\\
            & +  & \\min\\left(1,\\left[\\left(\\frac{\\left|\\left[ion_{i}\\right]-\\left[ion_{j}\\right]\\right|}{\\frac{\\left(\\max\\left[ion_{i}\\right]+\\max\\left[ion_{j}\\right]\\right)}{2}}\\right)+0.3\\right]\\right) \\\\
            & +  & \\min\\left(1,\\left[\\left(\\frac{\\left|\\left[PEG_{i}\\right]-\\left[PEG_{j}\\right]\\right|}{\\frac{\\left(\\max\\left[PEG_{i}\\right]+\\max\\left[PEG_{j}\\right]\\right)}{2}}\\right)+0.2\\right]\\right)\\Biggr)
        \\end{eqnarray}


    Where :math:`T` is the number of distinct chemical species in conditions
    :math:`i` and :math:`j`, :math:`[s_{ti}]` is the concentration of chemical
    :math:`t` in condition :math:`i`, :math:`max[s_t]` is the maximum
    concentration found for chemical :math:`t`, :math:`E(pH_i)` is an estimate
    of the pH for condition :math:`i`, :math:`gul(pH)` is the overall
    maximum of pH, :math:`gll(pH)` is the overall minimum pH, :math:`[ion_i]`
    is the concentration of the salt :math:`i`, and :math:`[PEG_i]` is the concentration
    of PEG :math:`i`.


    :param cocktail cocktail1: First cocktail to compare
    :param cocktail cocktail2: Second cocktail to compare

    :returns: The distance score between 0 and 1
        
    """

    (distance, T) = bare_bones(cocktail1, cocktail2, False)
    ph = _ph_distance(cocktail1, cocktail2)
    ion = _ion_distance(cocktail1, cocktail2)
    peg = _peg_distance(cocktail1, cocktail2)

    if ph is not None: distance += ph
    if ion is not None: distance += ion
    if peg is not None: distance += peg

    return distance/(T+3.0)

def internal_similarity(s, metric_func):
    """
    Compute the internal diversity within a screen (from Newman et al. 2010).

    :param screen s: The screen

    :returns: The diversity score between 0 and 1
        
    """
    sum_avg = 0
    for c1 in s.cocktails:
        isum = 0
        n = 0
        for c2 in s.cocktails:
            isum += metric_func(c1, c2)
            n += 1

        sum_avg += isum / n

    return sum_avg / len(s)
            

def screen_distance(screen1, screen2, metric_func):
    """
    Compute the distance between two screens (from Newman et al. 2010).

    :param screen screen1: First screen
    :param screen screen2: Second screen

    :returns: The distance score between 0 and 1
        
    """
    sum1 = 0.0
    for c1 in screen1.cocktails:
        mini = 100000000
        for c2 in screen2.cocktails:
            distance = metric_func(c1, c2)
            if mini > distance:
                mini = distance
        sum1 += mini

    sum2 = 0.0
    for c1 in screen2.cocktails:
        mini = 100000000
        for c2 in screen1.cocktails:
            distance = metric_func(c1, c2)
            if mini > distance:
                mini = distance
        sum2 += mini

    score = ( (sum1/float(len(screen1))) + (sum2/float(len(screen2))) )/2.0
    return score


def _ion_distance(cocktail1, cocktail2):
    """
    Compute ion distance. Assumes each cocktail contains a single salt.

    :param cocktail cocktail1: First cocktail to compare
    :param cocktail cocktail2: Second cocktail to compare

    :returns: The distance score between 0 and 1 or None if no matching ions are found.
        
    """

    salt1 = next((c for c in cocktail1.components if c.ions_by_name), None)
    salt2 = next((c for c in cocktail2.components if c.ions_by_name), None)

    if salt1 is None or salt2 is None:
        return None

    for i in salt1.ions_by_name:
        if i in salt2.ions_by_name:
            conc_diff = math.fabs(salt1.conc - salt2.conc);
            conc_max = (salt1.conc_max + salt2.conc_max) / 2.0
            return min(1, (conc_diff/conc_max) + 0.3)
    
    return None


def _peg_distance(cocktail1, cocktail2):
    """
    Compute PEG distance. Assumes each cocktail contains a single PEG. Only
    considers PEGs that have molecular weights within a factor of 2.

    :param cocktail cocktail1: First cocktail to compare
    :param cocktail cocktail2: Second cocktail to compare

    :returns: The distance score between 0 and 1 or None if no matching PEGs are found.
        
    """

    peg1 = next((c for c in cocktail1.components if c.is_peg), None)
    peg2 = next((c for c in cocktail2.components if c.is_peg), None)

    if peg1 is None or peg2 is None:
        return None

    pnum1 = peg1.molecular_weight;
    pnum2 = peg2.molecular_weight;
    factor = min(pnum1, pnum2) / max(pnum1, pnum2)
    if factor > 0.5 and factor < 2:
        conc_diff = math.fabs(peg1.conc - peg2.conc);
        conc_max = (peg1.conc_max + peg2.conc_max) / 2.0
        return min(1, (conc_diff/conc_max) + 0.2)

    return None


def _ph_distance(cocktail1, cocktail2):
    """
    Compute pH distance. Assumes estimates of overall pH min/max is known.

    :param cocktail cocktail1: First cocktail to compare
    :param cocktail cocktail2: Second cocktail to compare

    :returns: The distance score between 0 and 1 or None if cocktails are missing pH
        
    """
    ph1 = cocktail1.ph
    ph2 = cocktail2.ph

    if ph1 is None and ph2 is None:
        return None

    if ph1 is None or ph2 is None:
        return 1

    minmax = _PH_MAX - _PH_MIN

    return math.fabs(ph1 - ph2)/minmax
