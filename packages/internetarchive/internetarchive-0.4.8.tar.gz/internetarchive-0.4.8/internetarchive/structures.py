# ItemDict class
#_________________________________________________________________________________________
class ItemDict(dict):
    """This class represents an archive.org item."""
    # init()
    #_____________________________________________________________________________________
    def __init__(self, data=None, secure=False, **kwargs):
        """
        :type identifier: str
        :param identifier: The globally unique Archive.org identifier
                           for a given item.

        :type secure: bool
        :param secure: (optional) If secure is True, use HTTPS protocol, 
                       otherwise use HTTP.

        """
        self._store = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

        self.exists = False if self == {} else True
        self.identifier = self.get('metadata', {}).get('identifier')
        self.server = self.get('server')
        self.primary = self.get('d1')
        self.secondary = self.get('d2')
        self.dir = self.get('dir')
        self.metadata = self.get('metadata')
        self.files = self.get('files')
        self.item_size = self.get('item_size')
        self.files_count = self.get('files_count')

        # URLs
        protocol = 'https' if secure else 'http'
        url_base = '{0}://archive.org'.format(protocol)
        self.metadata_url = '{0}/metadata/{1}'.format(url_base, self.identifier)
        self.history_url = '{0}/history/{1}'.format(url_base, self.identifier)
        self.details_url = '{0}/details/{1}'.format(url_base, self.identifier)
        self.download_url = '{0}/download/{1}'.format(url_base, self.identifier)
        self.s3_url = '{0}://s3.us.archive.org/{1}'.format(protocol, self.identifier)
   
    def __repr__(self): 
        return '%s(%r)' % (self.__class__.__name__, dict(self.items()))



# FileDict class
#_________________________________________________________________________________________
class FileDict(dict):
    """:todo: document ``internetarchive.File`` class."""
    # init()
    #_____________________________________________________________________________________
    def __init__(self, data=None, secure=False, **kwargs):
        self._store = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

        self.external_identifier = self.get('external-identifier')
        self.name = self.get('name')
        self.source = self.get('source')
        self.size = self.get('size')
        self.format = self.get('format')
        self.mtime = self.get('mtime')
        self.md5  = self.get('md5')
        self.crc32 = self.get('crc32')
        self.sha1 = self.get('sha1')
        self.fname = self.get('name', '').encode('utf-8')
        self.length = self.get('length')

        if self.get('identifier'):
            protocol = 'https' if secure else 'http'
            url_base = '{0}://archive.org'.format(protocol)
            self.identifier = self.get('identifier')
            self.url = '{0}/download/{1}/{2}'.format(url_base, self.get('identifier'), 
                                                     self.name)

    # __repr__()
    #_____________________________________________________________________________________
    def __repr__(self): 
        return '%s(%r)' % (self.__class__.__name__, dict(self.items()))
