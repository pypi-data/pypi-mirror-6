import sys

command_names = ['isim', 'cdist', 'sdist', 'convert','hclust'] 

commands = {}

for c in command_names:
    try:
        __import__('cockatoo.cli.%s' % c)
        commands[c] = sys.modules['cockatoo.cli.%s' % c]
    except Exception:
        # XXX need better error handling here
        pass

