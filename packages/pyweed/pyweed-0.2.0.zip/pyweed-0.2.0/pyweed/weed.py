# -*- coding: utf-8 -*-
import json
import os
import random
from collections import namedtuple

from .utils import (
    _get_data,
    _post_data,
    _delete_data,
    _file_encode_multipart
)


class WeedFS(object):
    master_addr = "localhost"
    master_port = 9333

    def __init__(self, master_addr='localhost', master_port=9333):
        self.master_addr = master_addr
        self.master_port = master_port

    def get_file_url(self, fid):
        """
        Get url for the file

        :param integer fid: File ID
        :rtype: string
        """
        volume_id, rest = fid.strip().split(",")
        file_location = self.get_file_location(volume_id)
        url = "http://{public_url}/{fid}".format(public_url=file_location.public_url, fid=fid)
        return url

    def get_file_location(self, volume_id):
        """
        Get location for the file

        :param integer volume_id: volume_id
        :rtype: namedtuple
        """
        url = "http://{master_addr}:{master_port}/dir/lookup?volumeId={volume_id}".format(
            master_addr=self.master_addr,
            master_port=self.master_port,
            volume_id=volume_id)
        data = json.loads(_get_data(url))
        _file_location = random.choice(data['locations'])
        FileLocation = namedtuple('FileLocation', "public_url url")
        return FileLocation(_file_location['publicUrl'], _file_location['url'])

    def delete_file(self, fid):
        """
        Delete file from WeedFS

        :param string fid: File ID
        """
        url = self.get_file_url(fid)
        return _delete_data(url)

    def upload_file(self, file_path):
        '''
        Uploads file to WeedFS

        :param string file_path:
        :rtype: string or None
        '''
        url = "http://{master_addr}:{master_port}/dir/assign".format(
            master_addr=self.master_addr,
            master_port=self.master_port)
        data = json.loads(_get_data(url))
        if data.get("error") is not None:
            return None
        # file_stream = open(file_path, "rb")
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as file_stream:
            content_type, body = _file_encode_multipart(filename, file_stream)
        post_url = "http://{publicUrl}/{fid}".format(**data)
        res = _post_data(
            post_url, body, headers={"Content-Type": content_type,
                                     "Content-Length": str(len(body)),
                                     "Accept": "*/*"})
        response_data = json.loads(res)
        size = response_data.get('size')
        if size is not None:
            return data['fid']
        else:
            return None


if __name__ == "__main__":
    pass
