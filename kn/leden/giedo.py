# vim: et:sta:bs=2:sw=4:
from kn import settings

from kn.utils.whim import WhimDaemon, WhimClient

__GIEDO = None

def get_giedo_connection():
    global __GIEDO
    if __GIEDO is None:
        __GIEDO = WhimClient(settings.GIEDO_SOCKET)
    return __GIEDO

class ChangePasswordError(Exception):
    pass

def change_password(user, old, new):
    giedo = get_giedo_connection()
    ret = giedo.send({'type': 'setpass',
              'user': user,
              'oldpass': old,
              'newpass': new})
    if 'error' in ret:
        raise ChangePasswordError(ret['error'])

def change_villanet_password(user, old, new):
    giedo = get_giedo_connection()
    ret = giedo.send({'type': 'set-villanet-password',
              'user': user,
              'oldpass': old,
              'newpass': new})
    if 'error' in ret:
        raise ChangePasswordError(ret['error'])

def sync():
    get_giedo_connection().send({'type': 'sync'})

def update_site_agenda():
    get_giedo_connection().send({'type': 'update-site-agenda'})

def fotoadmin_create_event(date, name, humanName):
    return get_giedo_connection().send({'type': 'fotoadmin-create-event',
        'date': date,
        'name': name,
        'humanname': humanName})

def fotoadmin_move_fotos(event, user, dir):
    return get_giedo_connection().send({'type': 'fotoadmin-move-fotos',
        'event': event,
        'user': user,
        'dir': dir})

def openvpn_create(user, want):
    """ Requests giedo to create an OpenVPN installer.
        @user   the user for whom to create the installer
        @want   either 'zip' or 'exe' """
    get_giedo_connection().send({'type': 'openvpn_create',
        'user': user,
        'want': want})
