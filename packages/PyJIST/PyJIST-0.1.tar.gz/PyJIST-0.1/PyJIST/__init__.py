import os
import glob

names = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]
for name in names:
    exec "from %s import %s" % (name, name)
