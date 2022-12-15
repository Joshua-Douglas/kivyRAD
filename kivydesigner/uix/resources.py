import os 
from pathlib import Path 
import math 

'''
resource.py validates that application data is properly registered, and returns 
the full filepath to the requested resource. 

Application data is stored within the project data folder. PNG files must be provided
in each of the sizes specified by SUPPORTED_PNG_SIZES_PX, to improve icon resolution
when the use of an svg is not possible or practical.
'''

PARENT_DIR = Path(os.path.dirname(__file__)).parent
DATA_FOLDER = os.path.join(PARENT_DIR, 'data') 

PNG_IMAGES = [ 
    'kivy-icon',
    'python-icon',
    'default-file',
    'info'
]
SUPPORTED_PNG_SIZES_PX = (16, 32, 48, 64)

SVG_IMAGES = [
    'default-file',
    'new-file',
    'open-folder',
    'refresh',
    'collapse'
]

def _png_resource_filename(resource_name, requested_size):
    if requested_size not in SUPPORTED_PNG_SIZES_PX:
        raise ValueError(f'Requested PNG resource size does not exist. The following pixel sizes are available {SUPPORTED_PNG_SIZES_PX}')
    return os.path.join(DATA_FOLDER, f'{resource_name}-{requested_size}.png')

def _svg_resource_filename(resource_name):
    return os.path.join(DATA_FOLDER, f'{resource_name}.svg')

for img in PNG_IMAGES:
    for size in (16, 32, 48, 64):
        expected_filename = _png_resource_filename(img, size)
        if not os.path.exists(expected_filename):
            raise FileNotFoundError(f'Resource file {expected_filename} not found. All png data files must have four standard sizes available.')

for img in SVG_IMAGES:
    expected_filename = _svg_resource_filename(img)
    if not os.path.exists(expected_filename):
        raise FileNotFoundError(f'Resource file {expected_filename} not found.')

def get_png_resource(resource_name, requested_size):
    '''
    Return the path to the requested png resource, with the 
    size that best matches the requested_size. If the requested_size
    is not available, then return the next biggest png (or the 
    largest available).
    '''
    if resource_name not in PNG_IMAGES:
        raise KeyError(f'{resource_name} is not a valid png resource name. Add this resource to the data folder.')
    if requested_size <= 0:
        raise ValueError(f'Requested resource size {requested_size} is invalid. Only positive sizes are supported.')

    best_size = min(16 * math.ceil(requested_size / 16), 64)
    return _png_resource_filename(resource_name, best_size)

def get_svg_resource(resource_name):
    '''Return the path to the requested svg resource.'''
    if resource_name not in SVG_IMAGES:
        raise KeyError(f'{resource_name} is not a valid svg resource name. Add this resource to the data folder.')
    return _svg_resource_filename(resource_name)