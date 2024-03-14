import os, sys
# Current directory where this __init__.py file is located
currentdir = os.path.dirname(os.path.realpath(__file__))

# Add the current directory to sys.path
sys.path.append(currentdir)

# Subdirectory you want to add
subdir = "grindr_access"

# Full path to the subdirectory
subdir_path = os.path.join(currentdir, subdir)

# Add the subdirectory to sys.path
sys.path.append(subdir_path)