'''
Created on: Mar 04, 2014

@author: qwang

This module provide api to use youpai cloud

API provided:
    1. get_access_url(url, size)
    2. put(url, data = None)
    3. delete(url)
    4. get_count()
    5. get_usage()
    6. get_info(url)
'''
import upyun

import configure

from tool import download, gen_key, encode
from exception import ParamException, ConfigParamInvalidException, \
        UpYunServiceException, UpYunClientException

class UpyunClient(object):
    '''
    Implement youpai service api
    '''
    def __init__(self, config):
        '''
        initialize UpyunApi object

        @Param: 
            1. config: upyun client configuration which is supposed to \
                    contain BUCKET, USERNAME, PASSWORD, TIMEOUT. \
        '''
        self._check(config)
        self._config = config
        self._upyun_client = upyun.UpYun(config['BUCKET'], config['USERNAME'], \
                config['PASSWORD'], timeout=config['TIMEOUT'], \
                endpoint=upyun.ED_AUTO)
        self._server = None
        if self._config.has_key('SERVER'):
            self._server = self._config['SERVER']

    def put(self, url, data = None):
        '''
        upload image to youpai cloud

        @Param: 
            1. url to be upload
            2. data of image. Default to be None, so API support downloading \
                    data by url, and uploading to cloud automatically. \
                    Also, you can provide url as well as data

        @output:
            1. when successed
                a dictionary like:
                    dict = {
                        'width': 50,
                        'height': 50,
                        'frames': 1,
                        'file-type': 'JPEG' 
                        }
                as well as "access_url" for original image
            2. when failed
                exception raised
                refers to: 
                    http://wiki.upyun.com/index.php?title=HTTP_REST_API%E6%8E%A5%E5%8F%A3#.E6.A0.87.E5.87.86API.E9.94.99.E8.AF.AF.E4.BB.A3.E7.A0.81.E8.A1.A8    

        @Notice:
            There is no way to determin if an image(url) to be upload \
                    has been uploaded before.
            So, try not to upload duplicated image !!!
        '''
        url = url.strip()
        if not data:
            data = download(url)
        key = gen_key(url)
        res = None
        try:
            res = self._upyun_client.put(key, data, checksum=True)
        except upyun.UpYunServiceException, error:
            raise UpYunServiceException(error)
        except upyun.UpYunClientException, error:
            raise UpYunServiceException(error)
        res['access_url'] = self.get_access_url(url)
        return res

    def delete(self, url):
        '''
        delete image
        '''
        key = gen_key(url)
        try:
            self._upyun_client.delete(key)
        except upyun.UpYunServiceException, error:
            raise UpYunServiceException(error)
        except upyun.UpYunClientException, error:
            raise UpYunServiceException(error)

    def get_access_url(self, url, size = None):
        '''
        get url, by which you can access image in youpai cloud

        @param:
            url: original image url
            size: supported sizes defined in configure.py. 
                Default None, means original image
        '''
        url_youpai = None

        if size and size not in configure.IMAGE_WIDTH:
            raise ParamException('unsupported size: %s' % size)

        key = encode(url)
        if not self._server:
            url_youpai = configure.SERVER % self._config['BUCKET'] + key
        else:
            url_youpai = 'http://' + self._server + '/' + key

        if size == 'original':
            size = None

        if size:
            url_youpai += ('!' + size)

        return url_youpai

    def get_count(self):
        '''
        get image count in youpai cloud
        '''
        try:
            infos = self._upyun_client.getlist()
        except upyun.UpYunServiceException, error:
            raise UpYunServiceException(error)
        except upyun.UpYunClientException, error:
            raise UpYunClientException(error)

        return len(infos)

    def get_info(self, url):
        '''
        get image info in youpai cloud
        '''
        key = gen_key(url)
        try:
            info = self._upyun_client.getinfo(key)
        except upyun.UpYunServiceException, error:
            raise UpYunServiceException(error)
        except upyun.UpYunClientException, error:
            raise UpYunClientException(error)
        return info

    def get_usage(self):
        '''
        get the space used, unit: B
        '''
        try:
            usage = self._upyun_client.usage()
        except upyun.UpYunServiceException, error:
            raise UpYunServiceException(error)
        except upyun.UpYunClientException, error:
            raise UpYunClientException(error)
        return usage

    def _check(self, config):
        '''
        check config
        '''

        if not config or not isinstance(config, dict):
            raise ConfigParamInvalidException('CONFIG_INVALID, dictionay needed')
        for item in configure.youpai_config:
            if item not in config:
                raise ConfigParamInvalidException('CONFIG_INVALID %s needed' % item)
        if 'TIMEOUT' not in config:
            config['TIMEOUT'] = configure.TIMEOUT
