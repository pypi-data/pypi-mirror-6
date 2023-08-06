import sys,logging,getopt
import cockatoo
from cockatoo.cli.exceptions import Usage

logger = logging.getLogger(__name__)

def run(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "s:a:w:", ["screen=", "algorithm=", "weights="])
    except getopt.error, msg:
        raise Usage(msg)

    screen = None
    algorithm = None
    weights = [1,1]
    for o, a in opts:
        if o in ("-s", "--screen"):
            screen = a
        elif o in ("-a", "--algorithm"):
            algorithm = a
        elif o in ("-w", "--weights"):
            weights = []
            for w in re.split(r',', a):
                try:
                    weights.append(float(w))
                except:
                    raise Usage("Invalid weights")

    if screen is None:
        raise Usage("Please provide a screen")
    if len(weights) != 2:
        raise Usage("Please provide a valid weights string: 1,1")

    metric_func = cockatoo.c6.distance
    if algorithm != "c6":
        metric_func = cockatoo.metric.distance
        algorithm = "CD_coeff"

    s = cockatoo.screen.parse_json(screen)

    print "Using %s algorithm" % (algorithm)
    print "Computing internal similarity for %s..." % (s.name)

    score = cockatoo.c6.internal_similarity(s, metric_func)
    print "Internal similarity score: %s" % str(score)

    return 0

def synopsis():
    return "compute the internal similarity score for a screen"

def options():
    return """
    -s, --screen         path to screen
    -a, --algorithm       c6 | CD_coeff (default)
    -w, --weights         weights=1,1
    """
