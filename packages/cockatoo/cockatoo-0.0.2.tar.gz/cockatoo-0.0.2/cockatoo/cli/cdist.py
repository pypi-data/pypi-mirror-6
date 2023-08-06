import sys,logging,getopt
import cockatoo
from cockatoo.cli.exceptions import Usage

logger = logging.getLogger(__name__)

def run(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "1:2:a:w:", ["cocktail1=", "cocktail2=", "algorithm=", "weights="])
    except getopt.error, msg:
        raise Usage(msg)

    cocktail1 = None
    cocktail2 = None
    algorithm = None
    weights = [1,1]
    for o, a in opts:
        if o in ("-1", "--cocktail1"):
            cocktail1 = a
        elif o in ("-2", "--cocktail2"):
            cocktail2 = a
        elif o in ("-a", "--algorithm"):
            algorithm = a
        elif o in ("-w", "--weights"):
            weights = []
            for w in re.split(r',', a):
                try:
                    weights.append(float(w))
                except:
                    raise Usage("Invalid weights")

    if cocktail1 is None or cocktail2 is None:
        raise Usage("Please provide 2 cocktails")
    if len(weights) != 2:
        raise Usage("Please provide a valid weights string: 1,1")

    metric_func = cockatoo.c6.distance
    if algorithm != "c6":
        metric_func = cockatoo.metric.distance
        algorithm = "CD_coeff"

    ck1 = cockatoo.screen.parse_cocktail(cocktail1)
    ck2 = cockatoo.screen.parse_cocktail(cocktail2)
    
    if ck1 is None or ck2 is None:
        raise Usage("Error parsing cocktails")

    print "Using %s algorithm" % (algorithm)
    print "Computing distance between %s and %s..." % (ck1.name, ck2.name)

    score = metric_func(ck1, ck2)
    print "Distance: %s" % str(score)

    return 0

def synopsis():
    return "compute the distance between 2 cocktails"

def options():
    return """
    -1, --cocktail1         path to cocktail1
    -2, --cocktail2         path to cocktail2
    -a, --algorithm       c6 | CD_coeff (default)
    -w, --weights         weights=1,1
    """
