import re
import os
import argparse

#Set up argument parser
parser = argparse.ArgumentParser(
    description="convert your epytext docstrings to reStruturedText")    
    
parser.add_argument("input",
    help="input file or directory to convert")

parser.add_argument("-v", "--verbose", action="store_true", default=False,
    help="show changes")

parser.add_argument("-o", "--output-dir", dest="output",
    help="directory for output of parsed files")
    
args = parser.parse_args()   

#define regex
re_field = re.compile('@(param|type|rtype|return|ivar)')
re_italics = re.compile('I\{(.*?)\}')
re_bold = re.compile('B\{(.*?)\}')
re_code = re.compile('C\{(.*?)\}')


def substitute(text):
    for i, line in enumerate(lines):
        old = line
        new = re_field.sub(r':\1', line)
        new = re_italics.sub(r'*\1*', new)
        new = re_bold.sub(r'**\1**', new)
        new = re_code.sub(r'``\1``', new)        
        yield old, new


def get_filelist(filename):
    if not os.path.exists(filename):
        return None

    if os.path.isdir(filename):
        filenames = os.listdir(filename)
        filenames = [os.path.join(filename, f) for f in filenames if f.endswith(('.py', '.pyw'))]
    else:
        filenames = [filename]
    return filenames


filenames = get_filelist(args.input)
print filenames

for filename in filenames:
    #Check if file exists
    if not os.path.exists(filename):
        print "Error: File %s not found." % filename
        continue

    #Open file and read
    with open(filename) as f:
        lines = f.readlines()

    if args.output:
        output = os.path.join(args.output, os.path.basename(filename))
        f = open(output, "w")

    count = 0
    messages = []
    for i, (old, new) in enumerate(substitute(lines)):
        if old != new:
            count += 1
            messages.append("%s, %i:" % (os.path.basename(filename), i) +
                            "\n" + old.strip() + "\n" + new.strip() + "\n")
        if args.output:
            f.writelines([new])

    #Print results to screen
    result = "%s: %i substitutions" % (filename, count)
    if args.verbose:
        print "-" * len(result)
    print result
    if args.verbose:
        print "-" * len(result)
        for msg in messages:
            print msg

    if args.output:
        f.close()