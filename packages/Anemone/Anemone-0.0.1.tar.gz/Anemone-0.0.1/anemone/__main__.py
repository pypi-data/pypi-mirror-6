import sys

def print_usage():
    print 'Anemone'
    print '======='
    print ''
    print 'Start GUI and shoe ananlysis running at LOCATION:'
    print ' anemone wxgui LOCATION'
    print

if len(sys.argv) != 3:
    print_usage()
    print 'ERROR: wrong number of command line arguments'
    sys.exit(1)
elif sys.argv[1] == 'wxgui':
    from anemone.gui_wx import run_wxgui
    address = sys.argv[2]
    run_wxgui(address)
else:
    print_usage()
    print 'ERROR: unknown command "%s"' % sys.argv[1]
