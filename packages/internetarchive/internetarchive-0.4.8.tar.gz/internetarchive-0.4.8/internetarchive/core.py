import os

from internetarchive.sessions import Session
from internetarchive.models import Item, File



# get_item()
#_____________________________________________________________________________________
def get_item(identifier, timeout=None):
    url = '{url_base}/metadata/{id}'.format(url_base='http://archive.org', id=identifier)
    response = http_session.get(url, timeout=timeout)
    return Item(response.json())


# iter_files()
#_____________________________________________________________________________________
def iter_files(identifier, timeout=None):
    item = get_item(identifier)
    files = item.get('files', [])
    for f in files:
        f['identifier'] = identifier
        yield File(f)


# get_file()
#_____________________________________________________________________________________
def get_file(identifier, key, timeout=None):
    for f in iter_files(identifier):
        if f.name == key:
            return f


# upload_file()
#_____________________________________________________________________________________
def upload_file(identifier, body, key=None, metadata={}, headers={}, 
                access_key=None, secret_key=None, queue_derive=True, 
                ignore_preexisting_bucket=False, verbose=False, debug=False):
    """Upload a single file to an item. The item will be created """
    if not hasattr(body, 'read'):
        body = open(body, 'rb')
    try:
        body.seek(0, os.SEEK_END)
        size = body.tell()
        body.seek(0, os.SEEK_SET)
    except IOError:
        size = None

    key = body.name.split('/')[-1] if key is None else key
    url = '{0}://s3.us.archive.org/{1}/{2}'.format(session.protocol, identifier, key)
    headers = s3.build_headers(metadata=metadata,
                               headers=headers,
                               queue_derive=queue_derive,
                               auto_make_bucket=True,
                               size_hint=size,
                               ignore_preexisting_bucket=ignore_preexisting_bucket)

    request = requests.Request(
        method='PUT',
        url=url,
        headers=headers,
        data=body,
        auth=s3.BasicAuth(access_key, secret_key),
    )

    if debug:
        #body.close()
        return request
    else:
        prepared_request = request.prepare()
        return http_session.send(prepared_request, stream=True)


# download_file()
#_____________________________________________________________________________________
def download_file(identifier, key, file_path=None, ignore_existing=False):
    """:todo: document ``internetarchive.File.download()`` method"""
    file = get_file(identifier, key)
    file_path = file.name if not file_path else file_path
    if os.path.exists(file_path) and not ignore_existing:
        raise IOError('File already exists: {0}'.format(file_path))

    parent_dir = os.path.dirname(file_path)
    if parent_dir != '' and not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    http_session.cookies = config.get_cookies()

    try:
        response = http_session.get(file.url, stream=True)
        response.raise_for_status()
    except HTTPError as e:
        raise HTTPError('Error downloading {0}, {1}'.format(file.url, e))
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()


# delete_file()
#_____________________________________________________________________________________
def delete_file(identifier, key, debug=False, verbose=False, 
                cascade_delete=False):

    headers = s3.build_headers(cascade_delete=cascade_delete)
    url = '{0}://s3.us.archive.org/{1}/{2}'.format(session.protocol, identifier, key)

    request = Request(
        method='DELETE',
        url=url,
        headers=headers,
    )

    if debug:
        return request
    else:
        if verbose:
            stdout.write(' deleting file: {0}\n'.format(key))
        prepared_request = request.prepare()
        return http_session.send(prepared_request)    
