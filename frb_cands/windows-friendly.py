import os 
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument("dir")
args = parser.parse_args()
for root, dirs, files in os.walk(args.dir):
	for fname in files: 
		if ":" in fname:
			newname = fname.replace(":",";")
			os.rename(os.path.join(root,fname),  os.path.join(root,newname))