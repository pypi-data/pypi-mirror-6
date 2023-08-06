from sys import stdout

from . import item, search, catalog


# get_item()
#_________________________________________________________________________________________
def get_item(identifier, metadata_timeout=None, config=None):
    """Get an :class:`Item <Item>` object.

    Usage::

        >>> from internetarchive import get_item
        >>> item = get_item('nasa')
        >>> item.metadata['title']
        u'NASA Images'

    :type identifier: str
    :param identifier: The globally unique Archive.org identifier for a given item.

    :type metadata_timeout: int
    :param metadata_timeout: (optional) Set a timeout for retrieving an item's metadata.

    :type config: dict
    :param secure: (optional) Configuration options for session.

    """
    return item.Item(identifier, metadata_timeout, config)

# get_files()
#_________________________________________________________________________________________
def get_files(identifier, files=None, source=None, formats=None, glob_pattern=None,
              metadata_timeout=None, config=None):
    """Get :class:`File <File>` objects.

    Usage::

        >>> from internetarchive import get_files
        >>> files = get_files('nasa', formats=['JPEG', 'Metadata'])
        >>> [f.name for f in files]
        [u'globe_west_540.jpg', u'nasa_reviews.xml', u'nasa_meta.xml', u'nasa_files.xml']

    :type identifier: str
    :param identifier: The globally unique Archive.org identifier for a given item.

    :type files: str, set, list
    :param files: (optional) Return files matching the given filenames.

    :type source: str, list
    :param source: (optional) Return files matching the given formats.

    :type formats: str, list
    :param formats: (optional) Return files matching the given formats.

    :type glob_pattern: str
    :param glob_pattern: (optional) Return files matching the given pattern.

    :type metadata_timeout: int
    :param metadata_timeout: (optional) Set a timeout for retrieving an item's metadata.

    :type config: dict
    :param config: (optional) Configuration options for session.

    """
    item = get_item(identifier, metadata_timeout, config)
    return item.get_files(files, source, formats, glob_pattern)

# iter_files()
#_________________________________________________________________________________________
def iter_files(identifier, metadata_timeout=None, config=None):
    """Iterates over all of an :class:`Item <Item>` objects 
    :class:`File <File>` objects.

    Usage::
        
        >>> from internetarchive import iter_files
        >>> for f in iter_files('nasa'):
        ...     print(f.name, f.format, f.size)

    :type metadata_timeout: int
    :param metadata_timeout: (optional) Set a timeout for retrieving an item's metadata.

    :type config: dict
    :param config: (optional) Configuration options for session.

    """
    item = get_item(identifier, metadata_timeout, config)
    return item.iter_files()

# modify_metadata()
#_________________________________________________________________________________________
def modify_metadata(identifier, metadata, metadata_timeout=None, target='metadata', 
                    append=False, priority=0, access_key=None, secret_key=None, 
                    debug=False):
    """Modify the metadata of an existing item on Archive.org.

    Note: The Metadata Write API does not yet comply with the
    latest Json-Patch standard. It currently complies with `version 02
    <https://tools.ietf.org/html/draft-ietf-appsawg-json-patch-02>`_.

    Usage::

        >>> from internetarchive import modify_metadata
        >>> md = dict(new_key='new_value', foo=['bar', 'bar2'])
        >>> r = modify_metadata('mapi_test_item1', md)
        >>> r.status_code
        200

    :type identifier: str
    :param identifier: The globally unique Archive.org identifier for a given item.

    :type metadata: dict
    :param metadata: Metadata used to update the item.

    :type metadata_timeout: int
    :param metadata_timeout: (optional) Set a timeout for retrieving an item's metadata.

    :type target: str
    :param target: (optional) Set the metadata target to update.

    :type append: bool
    :param append: (optional) If True, append new value to current current value.

    :type priority: int
    :param priority: (optional) Set task priority.

    :type access_key: str
    :param access_key: Your `IA-S3 Access Key <https://archive.org/account/s3.php>`_.

    :type secret_key: str
    :param secret_key: Your `IA-S3 Secret Key <https://archive.org/account/s3.php>`_.

    :rtype: class:`requests.Response <Response>
    :returns: A class:`requests.Response <Response>` object.

    """
    item = get_item(identifier, metadata_timeout=metadata_timeout)
    return item.modify_metadata(metadata, target=target, append=append, 
                                priority=priority, access_key=access_key, 
                                secret_key=secret_key, debug=debug)

# upload()
#_____________________________________________________________________________________
def upload(identifier, files, **kwargs):
    """Upload files to an item. The item will be created if it
    does not exist.

    Usage::

        >>> from internetarchive import upload
        >>> md = dict(mediatype='image', creator='Jake Johnson')
        >>> upload('identifier', '/path/to/image.jpg', metadata=md)
        [<Response [200]>]

    :type files: list
    :param files: The filepaths or file-like objects to upload.

    :type access_key: str
    :param access_key: Your `IA-S3 Access Key <https://archive.org/account/s3.php>`_.

    :type secret_key: str
    :param secret_key: Your `IA-S3 Secret Key <https://archive.org/account/s3.php>`_.

    :rtype: list
    :returns: A list of :class:`requests.Response <Response>` objects.

    """
    item = get_item(identifier)
    return item.upload(files, **kwargs)

# download()
#_________________________________________________________________________________________
def download(identifier, filenames=None, **kwargs):
    """Download an item into the current working directory.

    Usage::

        >>> import internetarchive
        >>> internetarchive.download('stairs', source=['metadata', 'original'])

    :type filenames: str, list, set
    :param filenames: The filename(s) of the given file(s) to download.

    :type concurrent: bool
    :param concurrent: Download files concurrently if ``True``.

    :type source: str
    :param source: Only download files matching given source.

    :type formats: str
    :param formats: Only download files matching the given Formats.

    :type glob_pattern: str
    :param glob_pattern: Only download files matching the given glob pattern

    :type ignore_existing: bool
    :param ignore_existing: Overwrite local files if they already exist.

    :rtype: bool
    :returns: True if if files have been downloaded successfully.

    """
    item = get_item(identifier)
    if filenames:
        if not isinstance(filenames, (set, list)):
            filenames = [filenames]
        for fname in filenames:
            f = item.get_file(fname)
            f.download(**kwargs)
    else:
        item.download(**kwargs)

# delete()
#_________________________________________________________________________________________
def delete(identifier, filenames=None, **kwargs):
    item = get_item(identifier)
    if filenames:
        if not isinstance(filenames, (set, list)):
            filenames = [filenames]
        for f in item.iter_files():
            if not f.name in filenames:
                continue
            f.delete(**kwargs)

# get_tasks()
#_________________________________________________________________________________________
def get_tasks(**kwargs):
    _catalog = catalog.Catalog(identifier=kwargs.get('identifier'),
                               params=kwargs.get('params'),
                               task_ids=kwargs.get('task_ids'))
    task_type = kwargs.get('task_type')
    if task_type:
        return eval('_catalog.{0}_rows'.format(task_type.lower()))
    else:
        return _catalog.tasks

# search_items()
#_________________________________________________________________________________________
def search_items(query, **kwargs):
    return search.Search(query, **kwargs)

# mine()
#_________________________________________________________________________________________
def get_data_miner(identifiers, **kwargs):
    from . import mine
    return mine.Mine(identifiers, **kwargs)
