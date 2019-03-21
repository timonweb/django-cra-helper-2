import logging
import os
import re
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def get_js_and_css(is_server_live: bool, cra_url: str, app_dir: str) -> dict:
    html = ''
    if is_server_live:
        resp = requests.get(cra_url, verify=False)
        html = resp.text
    else:
        build_dir = os.path.join(app_dir, 'build')
        # Add the CRA static directory to STATICFILES_DIRS so collectstatic can grab files in there
        static_dir = os.path.join(build_dir, 'static')
        settings.STATICFILES_DIRS += [static_dir]
        index_path = os.path.join(build_dir, 'index.html')
        try:
            with open(index_path, 'r') as f:
                logger.info('found index.html in React build files')
                html = f.read()
        except Exception as e:
            logger.error('can\'t load React index.html: {}'.format(e))

    return {
        'js': ['{}{}'.format(cra_url if is_server_live else '', match.group(1)) for match in
               re.finditer('<script src=\"(\S+)\"', html, re.MULTILINE | re.IGNORECASE)],
        'css': ['{}{}'.format(cra_url if is_server_live else '', match.group(1)) for match in
                re.finditer('<link href=\"(\S+)\"', html, re.MULTILINE | re.IGNORECASE)],
    }
