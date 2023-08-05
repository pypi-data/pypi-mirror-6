__author__ = 'sathley'

from pyappacitive import AppacitiveFile


def get_file_upload_url_test():
    response = AppacitiveFile.get_upload_url('image/jpeg', 'foto.jpeg')
    assert hasattr(response, 'url')
    assert response.url is not None
    assert hasattr(response, 'id')
    assert response.id is not None


def get_download_url_test():
    response = AppacitiveFile.get_download_url('random_file_id')
    assert hasattr(response, 'url')
    assert response.url is not None


def delete_file_test():
    AppacitiveFile.delete_file('random_file_id')
