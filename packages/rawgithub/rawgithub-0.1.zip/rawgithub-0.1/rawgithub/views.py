""" Cornice services.
"""
import logging
import os
import pkg_resources
import requests

from cornice import Service
from pyramid.httpexceptions import HTTPFound

logger = logging.getLogger(__package__)

hello = Service(name='hello', path='/', description='Hello page')


@hello.get()
def get_hello(request):
    return {'hello': 'Go to /{owner}/{repo}/{file}',
            'params': {'access_token': 'OAuth token',
                       'ref': 'branch, tag or commit reference'},
            'source': 'https://github.com/diecutter/rawgithub',
            'version': pkg_resources.get_distribution(__package__).version}


rawfile = Service(name='rawgithub',
                  path='/{owner}/{repo}/{file:[a-zA-Z-_\/\.0-9#:=;,]+}',
                  description="Return a file from github")


@rawfile.get()
def get_info(request):
    """Returns the file content from github."""
    owner = request.matchdict['owner']
    repo = request.matchdict['repo']
    file_path = request.matchdict['file']

    url = 'https://api.github.com/repos/{owner}/{repo}/' \
          'contents/{file_path}?'.format(
              owner=owner,
              repo=repo,
              file_path=file_path)

    access_token = request.params.get('access_token')
    ref = request.params.get('ref')

    if ref:
        url += 'ref={ref}&'.format(ref=ref)

    logger.debug('URL: %s' % url)

    if access_token:
        url += 'access_token={access_token}'.format(access_token=access_token)

    r = requests.get(url,
                     headers={'Accept': 'application/vnd.github.V3.raw'})
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        logger.debug('URL: %s' % url)
        logger.debug(str(e))
        return HTTPFound(
            'https://github.com/{owner}/{repo}/raw/{ref}/{file_path}'.format(
                owner=owner, repo=repo,
                ref=ref or 'master', file_path=file_path))

    response = request.response
    headers = r.headers.copy()
    del headers['Content-Length']
    response.headers = headers

    response.content_type = 'text/plain'
    path = file_path.lower()

    EXTENSIONS = {'.html': 'text/html',
                  '.css': 'text/css',
                  '.js': 'application/javascript',
                  '.gif': 'image/gif',
                  '.png': 'image/png',
                  '.jpg': 'image/jpeg',
                  '.jpeg': 'image/jpeg'}

    _, ext = os.path.splitext(path)
    if ext and ext in EXTENSIONS:
        response.content_type = EXTENSIONS[ext]

    response.write(r.text)
    return response
