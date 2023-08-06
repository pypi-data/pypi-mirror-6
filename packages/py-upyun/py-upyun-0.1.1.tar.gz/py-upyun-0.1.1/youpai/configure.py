'''
Created on Mar 11, 2014

Author: zxzhang

'''

# client conf
SERVER = 'http://%s.b0.upaiyun.com/'

# supported image types
valid_image_types = ['image/jpg', 'image/png', 'image/gif',\
        'image/bmp', 'image/tif', 'image/jpeg']

# supported sizes
IMAGE_WIDTH = {
    'big': 500,
    'mid': 240,
    'small': 120,
    'original': None
}

# time out
TIMEOUT = 60

youpai_config = ['BUCKET', 'USERNAME', 'PASSWORD']
