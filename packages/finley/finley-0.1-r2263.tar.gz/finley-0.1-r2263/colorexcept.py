# system modules
import math
import sys
import traceback

def colorexcept(exc_type, exc_value, exc_traceback): #isdoc
    frames = traceback.extract_tb(exc_traceback)
    framewidth = int(math.ceil(math.log(len(frames))/math.log(10)))
    filewidth = 0
    linewidth = 0
    functionwidth = 0
    for frame in frames:
        filewidth = max(filewidth, len(frame[0]))
        linewidth = max(linewidth, frame[1])
        functionwidth = max(functionwidth, len(frame[2]))
    linewidth = int(math.ceil(math.log(linewidth)/math.log(10)))
    print '\n\nTraceback: \033[1;92m{0}\033[0m: \033[1;91m{1}\033[0m'.format(exc_type.__name__, exc_value)
    for i in xrange(len(frames)):
        print ('\033[1;97m{0:' + str(framewidth) + '} \033[1;91m{1:' + str(filewidth) + '}\033[0m:{2:' + str(linewidth) + '} \033[1;92m{3:' + str(functionwidth) + '}\033[0m {4}').format(i, frames[i][0], frames[i][1], frames[i][2], frames[i][3])
    print 

if __name__ == 'colorexcept':
    if sys.stdout.isatty():
        sys.excepthook = colorexcept
