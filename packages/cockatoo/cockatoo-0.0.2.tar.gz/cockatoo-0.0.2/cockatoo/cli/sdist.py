import sys,logging,getopt
import cockatoo
from cockatoo.cli.exceptions import Usage

logger = logging.getLogger(__name__)

def run(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "1:2:a:w:", ["screen1=", "screen2=", "algorithm=", "weights="])
    except getopt.error, msg:
        raise Usage(msg)

    screen1 = None
    screen2 = None
    algorithm = None
    weights = [1,1]
    for o, a in opts:
        if o in ("-1", "--screen1"):
            screen1 = a
        elif o in ("-2", "--screen2"):
            screen2 = a
        elif o in ("-a", "--algorithm"):
            algorithm = a
        elif o in ("-w", "--weights"):
            weights = []
            for w in re.split(r',', a):
                try:
                    weights.append(float(w))
                except:
                    raise Usage("Invalid weights")

    if screen1 is None or screen2 is None:
        raise Usage("Please provide 2 screens")
    if len(weights) != 2:
        raise Usage("Please provide a valid weights string: 1,1")

    metric_func = cockatoo.c6.distance
    if algorithm != "c6":
        metric_func = cockatoo.metric.distance
        algorithm = "CD_coeff"

    s1 = cockatoo.screen.parse_json(screen1)
    s2 = cockatoo.screen.parse_json(screen2)

    print "Using %s algorithm" % (algorithm)
    print "Computing distance between %s and %s..." % (s1.name, s2.name)

    score = cockatoo.c6.screen_distance(s1, s2, metric_func)
    print "Distance: %s" % str(score)

    return 0

def synopsis():
    return "compute the distance between 2 screens"

def options():
    return """
    -1, --screen1         path to screen1
    -2, --screen2         path to screen2
    -a, --algorithm       c6 | CD_coeff (default)
    -w, --weights         weights=1,1
    """
