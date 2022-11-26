import os 
from pathlib import Path 
import math 

PARENT_DIR = Path(os.path.dirname(__file__)).parent
DATA_FOLDER = os.path.join(PARENT_DIR, 'data') 

PNG_IMAGES = [ 
    'kivy-icon',
    'python-icon'
]
SUPPORTED_PNG_SIZES_PX = (16, 32, 48, 64)

def png_resource_filename(resource_name, requested_size):
    if requested_size not in SUPPORTED_PNG_SIZES_PX:
        raise ValueError(f'Requested PNG resource size does not exist. The following pixel sizes are available {SUPPORTED_PNG_SIZES_PX}')
    return os.path.join(DATA_FOLDER, f'{resource_name}-{requested_size}.png')

for img in PNG_IMAGES:
    for size in (16, 32, 48, 64):
        expected_filename = png_resource_filename(img, size)
        if not os.path.exists(expected_filename):
            raise FileNotFoundError(f'{expected_filename} not found. All png data files must have four standard sizes available.')

def get_png_resource(resource_name, requested_size):
    '''
    Return the path to the requested png resource, with the 
    size that best matches the requested_size. If the requested_size
    is not available, then return the next biggest png (or the 
    largest available).
    '''
    if not resource_name:
        return ''
    if resource_name not in PNG_IMAGES:
        raise KeyError(f'{resource_name} is not a valid kd resource name. Add this resource to the data folder.')
    if requested_size <= 0:
        raise ValueError(f'Requested resource size {requested_size} is invalid. Only positive sizes are supported.')

    best_size = min(16 * math.ceil(requested_size / 16), 64)
    return png_resource_filename(resource_name, best_size)