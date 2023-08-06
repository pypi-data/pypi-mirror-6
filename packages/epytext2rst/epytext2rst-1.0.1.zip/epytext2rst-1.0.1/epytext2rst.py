import re
import os
from optparse import OptionParser
from glob import glob

#Set up option parser       
parser = OptionParser()
(options, args) = parser.parse_args()    

#define regex
re_field = re.compile('@(param|type|rtype|return|ivar)')     

def substitute(text):
    for i, line in enumerate(lines):
        old = line
        new = re_field.sub(r':\1', line)
        yield old, new

for arg in args:    
    for filename in glob(arg):
        substitute_all = False
        print "File %s" % filename
        #Check if file exists
        if not os.path.exists(filename):
            print "Error: File %s not found." % filename
            continue
        
        #Open file and read
        with open(filename) as f:
            lines = f.readlines()
           
        with open(filename, "w") as f:
            for i, (old, new) in enumerate(substitute(lines)):
                s = old
                if old != new:
                    line_nr = "Line %i:" % i
                    print line_nr + "\n" + "-" * len(line_nr) + "\n"
                    print old.rstrip() + "\n" + new.rstrip() + "\n"
                    if substitute_all:
                        s = new
                    else:
                        ans = raw_input("Substitute? ([y]/n/a):")                    
                        if ans in ["", "y", "a"]:
                            print "test"
                            s = new                    
                        if ans == "a":
                            print "all"
                            substitute_all = True                   
                f.writelines([s])