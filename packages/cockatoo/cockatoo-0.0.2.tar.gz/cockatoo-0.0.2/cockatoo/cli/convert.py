import sys,logging,getopt
import cockatoo
from cockatoo.cli.exceptions import Usage

logger = logging.getLogger(__name__)

def run(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "vs:n:c:x:i:o:", ["verbose", "screen=", "name=", "summary=", "ions=","output="])
    except getopt.error, msg:
        raise Usage(msg)

    screen_file = None
    name = None
    summary_file = None
    ions_file = None
    out_file = None
    verbose = False
    for o, a in opts:
        if o in ("-s", "--screen"):
            screen_file = a
        elif o in ("-n", "--name"):
            name = a
        elif o in ("-c", "--summary"):
            summary_file = a
        elif o in ("-i", "--ions"):
            ions_file = a
        elif o in ("-o", "--output"):
            out_file = a
        elif o in ("-v", "--verbose"):
            verbose = True

    if screen_file is None:
        raise Usage("Please provide a path to the screen")
    if summary_file is None:
        raise Usage("Please provide a path to the compound summary file")
    if out_file is None:
        raise Usage("Please provide a path to the output file")

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    screen = cockatoo.screen.parse_csv(name, screen_file)
    screen._set_summary_stats(summary_file)

    if ions_file is not None:
        screen._set_ions(ions_file)

    with open(out_file, 'w') as output:
        output.write(screen.json())

    if verbose:
        logger.info("Screen stats:")
        screen.print_stats()
        logger.info("Done converting screen. Output written to: %s" % out_file)

    return 0

def synopsis():
    return "convert CSV screen to JSON format"

def options():
    return """
    -v, --verbose            print debugging output
    -s, --screen             screen
    -o, --output             outputfile
    -n, --name               name of screen (used in output)
    -c, --summary            path to compound summary file
    -i, --ions               path to ions table file
    """
