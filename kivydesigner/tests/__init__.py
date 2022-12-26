import sys 
from pathlib import Path
sys.path.append(Path(__file__).parents[2].as_posix())

'''Must import common before any other test modules. 

The common module sets environmental variables that are (unfortunately)
needed to initialize global variables within kivy.tests.common.py.'''
import kivydesigner.tests.common