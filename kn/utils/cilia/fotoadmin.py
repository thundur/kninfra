# vim: et:sta:bs=2:sw=4:
from kn import settings

import subprocess
import os.path
import re

def fotoadmin_remove_moved_fotos(cilia, user, directory):
    if not re.match('^[a-z0-9]{3,32}$', user):
        return {'error': 'Invalid user'}
    if not re.match('^[^/\\.][^/]*$', directory):
        return {'error': 'Invalid dir'}
    user_path = os.path.join(settings.USER_DIRS, user)
    if not os.path.isdir(user_path):
        return {'error': 'Invalid user'}
    fotos_path = os.path.join(user_path, 'fotos', directory)
    if not os.path.isdir(fotos_path):
        return {'error': 'Invalid fotodir'}
    if not os.path.realpath(fotos_path).startswith(user_path):
        return {'error': 'Security exception'}
    subprocess.call(['rm', '-rf', fotos_path])
    return {'success': True}