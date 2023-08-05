__author__ = 'sathley'

from pyappacitive import AppacitivePushNotification, PropertyFilter


def send_push_notification_test():
    response = AppacitivePushNotification.broadcast(data={'alert': 'hi from py sdk'})
    assert hasattr(response, 'id')
    assert response.id is not None and response.id > 0


def get_all_notifications_test():
    response = AppacitivePushNotification.get_all_notification()
    assert hasattr(response, 'notifications')
    assert len(response.notifications) > 0


def get_notification_by_id_test():
    response = AppacitivePushNotification.broadcast(data={'alert': 'hi from py sdk'})
    id = response.id
    response = AppacitivePushNotification.get_notification_by_id(id)
    assert hasattr(response, 'notification')
    assert response.notification is not None
    assert response.notification.id == id


def send_push_notification_to_channels_test():
    response = AppacitivePushNotification.send_to_channels(['male', '18-25'], {'alert': 'Hi from pyAppacitive'}, platform_options={
		"ios": {
			"sound": "test"
		},
		"android": {
			"title": "test title"
		}
	})

    assert hasattr(response, 'id')
    assert response.id is not None and response.id > 0


def send_push_notofication_to_specefic_devices_test():
    response = AppacitivePushNotification.send_to_specific_devices(['123', '456', '789'], {'alert': 'Hi from pyAppacitive'}, platform_options={
		"ios": {
			"sound": "test"
		},
		"android": {
			"title": "test title"
		}
	})

    assert hasattr(response, 'id')
    assert response.id is not None and response.id > 0


def send_push_using_query_test():
    query = PropertyFilter('devicetype').is_equal_to('ios')
    response = AppacitivePushNotification.send_using_query(query, {'alert': 'Hi from pyAppacitive'}, platform_options={
		"ios": {
			"sound": "test"
		},
		"android": {
			"title": "test title"
		}
	})
    assert hasattr(response, 'id')
    assert response.id is not None and response.id > 0