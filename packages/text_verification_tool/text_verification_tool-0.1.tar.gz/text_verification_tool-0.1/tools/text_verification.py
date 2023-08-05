#!/usr/bin/env python

from text_verification_challenge import text_verification

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) < 3:
        sys.exit(1)
    else:
        file1 = os.path.abspath(sys.argv[1])
        file2 = os.path.abspath(sys.argv[2])
        try:
            config_file = os.path.abspath(sys.argv[3])
        except:
            config_file = None
            #print 'no config file found'
        print sys.argv
        #print config_file
        text_verification.perform_comparision(file1, file2, config_file=config_file )
