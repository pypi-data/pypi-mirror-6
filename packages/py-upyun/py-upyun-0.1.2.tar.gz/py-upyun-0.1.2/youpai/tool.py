'''
Created on Mar 11, 2014

@author: zxzhang

'''

import base64

import downloader

from exception import DownloadException

def gen_key(url):
    '''
    This function is to generate key, used for upload image into cloud

    input: url of image
    output: key of image

    '''
    key = encode(url)
    return key

def download(url):
    '''
    This function is to download image.

    Note1:
        1. suppose url inputed refers to a real image, not a html or other object
        2. check image when downloaded, check item:
            a. an image ?
            b. image type supported ?
            c. downloaded successfully ?
    Note2: 
        check image was deprecated
    '''
    resp = _download(url)
    if not resp:
        raise DownloadException(resp, 'Download failed, try again later!')
    if resp.status == 200:
        return resp.body
    else:
        raise DownloadException(resp)

def encode(s):
    '''
    base64 encode
    '''
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    url_encoded = base64.urlsafe_b64encode(s)
    return url_encoded

def _download(url):
    '''
    download image by url
    '''
    max_try_count = 3
    try_count = 0
    resp = None
    while True:
        if try_count >= max_try_count:
            break
        try:
            resp = downloader.download(url)
        except Exception:
            try_count += 1
            continue
        try_count += 1
    return resp
