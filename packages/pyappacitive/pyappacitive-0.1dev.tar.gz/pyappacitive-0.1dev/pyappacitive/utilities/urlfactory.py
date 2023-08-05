from pyappacitive import appcontext
import settings

__author__ = 'sathley'

base_url = settings.api_base_url


def get_headers(**headers_key):
    headers_key = {
        "Appacitive-Apikey": settings.api_key,
        "Appacitive-Environment": settings.environment,
        "Content-Type": "application/json"
    }
    user_token = appcontext.ApplicationContext.get_user_token()
    if user_token is not None:
        headers_key['Appacitive-User-Auth'] = user_token
    return headers_key


def get_user_headers(**headers_key):
    headers_key.update({
        "Appacitive-Apikey": settings.api_key,
        "Appacitive-Environment": settings.environment,
        "Appacitive-User-Auth": appcontext.ApplicationContext.get_user_token(),
        "Content-Type": "application/json"}
    )
    return headers_key


#region     OBJECT URLS


def __object_create_url(object_type):
    return '{0}/object/{1}'.format(base_url, object_type)


def __object_delete_url(object_type, object_id):
    return '{0}/object/{1}/{2}'.format(base_url, object_type, object_id)


def __object_multidelete_url(object_type):
    return '{0}/object/{1}/bulkdelete'.format(base_url, object_type)


def __object_delete_with_connections_url(object_type, object_id):
    return '{0}/object/{1}/{2}?deleteconnections=true'.format(base_url,
                                                              object_type,
                                                              object_id)


def __object_get_url(object_type, object_id, fields=None):
    url = '{0}/object/{1}/{2}'.format(base_url, object_type, object_id)
    if fields is not None:
        url += '?fields=' + ','.join(fields)
    return url


def __object_multiget_url(object_type, object_ids, fields=None):
    url = '{0}/object/{1}/multiget/{2}'.format(base_url, object_type,
                                                ','.join([str(object_id) for object_id in object_ids]))
    if fields is not None:
        url += '?fields=' + ','.join(fields)
    return url


def __object_update_url(object_type, object_id):
    return '{0}/object/{1}/{2}'.format(base_url, object_type, object_id)


def __object_find_all_url(object_type, query, fields=None):
    url = '{0}/object/{1}/find/all?{2}'.format(base_url, object_type,
                                                str(query))
    if fields is not None:
        url += '&fields=' + ','.join(fields)
    return url


def __object_find_between_two_objects_url(object_type, object_a_id, relation_a, label_a, object_b_id, relation_b, label_b, fields):
    url = '{0}/object/{1}/{2}/{3}/{4}/{5}/{6}/{7}'.format(base_url, object_type, object_a_id, relation_a, label_a, object_b_id, relation_b, label_b)
    if fields is not None:
        url += '?fields=' + ','.join(fields)
    return url

#endregion

#region     CONNECTION URLS


def __connection_create_url(relation_type):
    return '{0}/connection/{1}'.format(base_url, relation_type)


def __connection_get_url(relation_type, connection_id, fields=None):
    url = '{0}/connection/{1}/{2}'.format(base_url, relation_type,
                                           connection_id)
    if fields is not None:
        url += '?fields=' + ','.join(fields)
    return url



def __connection_multiget_url(relation_type, connection_ids, fields=None):
    url = '{0}/connection/{1}/multiget/{2}'.format(base_url, relation_type,
                                                    ','.join([str(connection_id) for connection_id in connection_ids]))
    if fields is not None:
        url += '?fields=' + ','.join(fields)
    return url


def __connection_delete_url(relation_type, connection_id):
    return '{0}/connection/{1}/{2}'.format(base_url, relation_type,
                                           connection_id)


def __connection_multidelete_url(relation_type):
    return '{0}/connection/{1}/bulkdelete'.format(base_url, relation_type)


def __connection_update_url(relation_type, connection_id):
    return '{0}/connection/{1}/{2}'.format(base_url, relation_type,
                                           connection_id)


def __connection_find_all_url(relation_type, query, fields=None):
    url = '{0}/connection/{1}/find/all?{2}'.format(base_url, relation_type,
                                                    str(query))
    if fields is not None:
        url += '&fields=' + ','.join(fields)
    return url


def __connection_find_for_objects_url(object_id1, object_id2, fields=None):
    url = '{0}/connection/find/{1}/{2}'.format(base_url, str(object_id1),
                                               str(object_id2))
    if fields is not None:
        url += '?fields=' + ','.join(fields)
    return url


def __connection_find_for_objects_and_relation_url(relation_type, object_id1,
                                                   object_id2, fields=None):
    url = '{0}/connection/{1}/find/{2}/{3}'.format(base_url, relation_type,
                                                    str(object_id1),
                                                    str(object_id2))
    if fields is not None:
        url += '?fields=' + ','.join(fields)
    return url


def __connection_find_interconnects_url(fields=None):
    url = '{0}/connection/interconnects'.format(base_url)
    if fields is not None:
        url += '?fields=' + ','.join(fields)
    return url


def __connection_find_connected_objects_url(relation, object_type, object_id, fields=None):
    url = '{0}/connection/{1}/{2}/{3}/find'.format(base_url, relation, object_type, object_id)
    if fields is not None:
        url += '?fields=' + ','.join(fields)
    return url


#endregion

#region DEVICE URLS


def __device_register_url():
    return '{0}/device/register'.format(base_url)


def __device_get_url(device_id):
    return '{0}/device/{1}'.format(base_url, device_id)


def __device_update_url(device_id):
    return '{0}/device/{1}'.format(base_url, device_id)


def __device_delete_url(device_id, delete_connections=False):
    return '{0}/device/{1}?deleteconnections={2}'.format(base_url, device_id, delete_connections)


def __device_find_all_url(query, fields=None):
    url = '{0}/object/device/find/all?{1}'.format(base_url, str(query))
    if fields is not None:
        url += '&fields=' + ','.join(fields)
    return url


#endregion

#region     USER URLS


def __user_create_url():
    return '{0}/user/create'.format(base_url)


def __user_delete_url(user_id, user_id_type='id', delete_connections=False):
    return '{0}/user/{1}?useridtype={2}&deleteconnections={3}'.format(base_url, user_id, user_id_type, delete_connections)


def __user_multidelete_url():
    return '{0}/user/bulkdelete'.format(base_url)


def __user_delete_with_connections_url(user_id):
    return '{0}/user/{1}?deleteconnections=true'.format(base_url, user_id)


def __user_get_url(user_id, user_id_type='id'):
    return '{0}/user/{1}?useridtype={2}'.format(base_url, user_id, user_id_type)


def __user_multiget_url(user_ids):
    return '{0}/object/user/multiget/{1}'.format(base_url, ','.join([str(user_id) for user_id in user_ids]))


def __user_update_url(user_id):
    return '{0}/user/{1}'.format(base_url, user_id)


def __user_find_all_url(query, fields=None):
    url = '{0}/object/user/find/all?{1}'.format(base_url, str(query))
    if fields is not None:
        url += '&fields=' + ','.join(fields)
    return url


def __user_authenticate_url():
    return '{0}/user/authenticate'.format(base_url)


def __user_send_reset_password_email_url():
    return '{0}/user/sendresetpassword'.format(base_url)


def __user_validate_session_url():
    return '{0}/user/validate'.format(base_url)


def __user_invalidate_session_url():
    return '{0}/user/invalidate'.format(base_url)


def __user_checkin_url(user_id, latitude, longitude):
    return '{0}/user/{1}/checkin?lat={2}&long={3}'.format(base_url, user_id, latitude, longitude)


def __update__password_url(user_id, identification_type='id'):
    return '%s/user/%s/changepassword?useridtype=%s' % (base_url, user_id,
                                                        identification_type)

#endregion

#region MISC URLS

def __graph_filter_url(filter_query_name):
    return '{0}/search/{1}/filter'.format(base_url, filter_query_name)


def __graph_project_url(project_query_name):
    return '{0}/search/{1}/project'.format(base_url, project_query_name)


def __email_send_url():
    return '{0}/email/send'.format(base_url)


def __get_file_upload_url(content_type):
    return '{0}/file/uploadurl?contenttype={1}'.format(base_url, content_type)


def __get_file_download_url(file_id):
    return '{0}/file/download/{1}'.format(base_url, file_id)


def __get_file_delete_url(file_id):
    return '{0}/file/delete/{1}'.format(base_url, file_id)


def __get_send_push_url():
    return '{0}/push'.format(base_url)


def __get_push_url(notification_id):
    return '{0}/push/notification/{1}'.format(base_url, notification_id)


def __get_all_push_url():
    return '{0}/push/getall'.format(base_url)

#endregion

#region URL DICTS

user_urls = {
    "create": __user_create_url,
    "delete": __user_delete_url,
    "delete_with_connections": __user_delete_with_connections_url,
    "multidelete": __user_multidelete_url,
    "get": __user_get_url,
    "multiget": __user_multiget_url,
    "update": __user_update_url,
    "find_all": __user_find_all_url,
    "update_password": __update__password_url,
    "authenticate": __user_authenticate_url,
    "send_reset_password_email": __user_send_reset_password_email_url,
    "validate_session": __user_validate_session_url,
    "invalidate_session": __user_invalidate_session_url,
    "checkin": __user_checkin_url
}

device_urls = {
    "register": __device_register_url,
    "get": __device_get_url,
    "update": __device_update_url,
    "delete": __device_delete_url,
    "find_all": __device_find_all_url,
}

object_urls = {
    "create": __object_create_url,
    "delete": __object_delete_url,
    "delete_with_connections": __object_delete_with_connections_url,
    "multidelete": __object_multidelete_url,
    "get": __object_get_url,
    "multiget": __object_multiget_url,
    "update": __object_update_url,
    "find_all": __object_find_all_url,
    "find_between_two_objects": __object_find_between_two_objects_url
}

connection_urls = {
    "create": __connection_create_url,
    "get": __connection_get_url,
    "multiget": __connection_multiget_url,
    "delete": __connection_delete_url,
    "multidelete": __connection_multidelete_url,
    "update": __connection_update_url,
    "find_all": __connection_find_all_url,
    "find_for_objects": __connection_find_for_objects_url,
    "find_for_objects_and_relation": __connection_find_for_objects_and_relation_url,
    "find_interconnects": __connection_find_interconnects_url,
    "find_connected_objects": __connection_find_connected_objects_url
}

email_urls = {
    "send": __email_send_url
}

graph_search_urls = {
    "filter": __graph_filter_url,
    "project": __graph_project_url
}

file_urls = {
    "get_upload_url": __get_file_upload_url,
    "get_download_url": __get_file_download_url,
    "file_delete": __get_file_delete_url
}

push_urls = {
    "send": __get_send_push_url,
    "get": __get_push_url,
    "get_all": __get_all_push_url
}

#endregion