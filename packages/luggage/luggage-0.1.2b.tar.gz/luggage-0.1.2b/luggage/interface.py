import exceptions


class ObjectInfo:
    """
    Provides information and operations on an object on a cloud storage.
    """

    def __init__(self, url, path, mtime, size, etag, extra, storage=None):
        self.url = url
        self.path = path
        self.mtime = mtime
        self.size = size
        self.etag = etag
        self.extra = extra
        self.storage = storage

    def __str__(self):
        return self.url
    __repr__ = __str__

    def delete(self):
        """
        Deletes this object from the storage.
        """
        try:
            self.storage.delete(self.path)
        except exceptions.ObjectDoesNotExistException:
            pass  # If the object didn't exist in the first place we don't need to do anything.

    def get(self, destination=''):
        """
        Downloads the object to the destination.

        :param destination: The destination on the local filesystem. If not set, the path of this object is used
        """
        self.storage.pull(self.path, destination)

    def __eq__(self, other):
        try:
            return self.url == other.url
        except AttributeError:
            return False


class CloudStorage:
    """
    The parent class for all storage implementations.

    A "storage" is a service on the web which allows remote storage in a file-like manner.
    These storages may be divided into multiple "containers" which can vary in accessibility and size.
    These containers then contain "objects" which are the file-like objects on the remote machine.

    Or in short: Storage (S3, CloudFiles, Dropbox) > Container (Bucket, Container, Box) > Object (or Key, i.e. test.txt)

    The methods in this class are the ones provided by all storage services. Those storage classes
    may offer additional methods, consult their documentation.
    """

    def __init__(self, url):
        self.url = url

    def _unimplemented(self, method):
        message = 'CloudStorage {0} has not implemented the "{1}" method'.format(self.__class__.__name__, method)
        return AttributeError(message)

    def list(self, path=''):
        """
        Lists object names under a given path.

        :param path: The path to search under, or an empty string if you want to search in the root of the storage
        :returns: A list of object names (i.e. a list of str)
        """
        raise self._unimplemented('list')

    def find(self, obj):
        """
        Retrieves the ObjectInfo for a single object.

        :param object: The path relative to the root of the storage
        :returns: ObjectInfo
        """
        raise self._unimplemented('find')

    def findall(self, path=''):
        """
        Finds all objects with complete meta-information.

        This will be a costly operation to do on most cloud storage services.

        :param path: The path to search under, or an empty string if you want to search in the root of the storage
        :returns: A list containing the ObjectInfo for each object
        """
        raise self._unimplemented('lsall')

    def delete(self, obj):
        """
        Deletes an object from the storage

        :param obj: The path which to delete
        :returns: True if this request deleted the file, false in all other cases
        """
        raise self._unimplemented('delete')

    def put_file(self, local_file, remote_path=None, verify=False):
        """
        Pushes the local file to a remote path.

        :param local_file: The local file to transfer
        :param remote_path: The path on the remote side. If not set, the basename of the local file is used.
        :param verify: Whether or not the successful transfer of the file should be verified after transmission (by md5)
        """
        raise self._unimplemented('push')

    def put_data(self, data, remote_path, verify=False):
        """
        Pushes in-memory data to a remote path.

        :param data: The data to push
        :type data: str or bytes
        :param remote_path: The path on the remote side.
        :param verify: Whether or not the successful transfer of the file should be verified after transmission (by md5)
        """
        raise self._unimplemented('push_data')

    def get(self, remote_path, local_file=None):
        """
        Pulls from the remote path to a local file.

        If the local file is not set, the full path of the remote file will be used, relative to the current
        working directory.
        """
        raise self._unimplemented('pull')

    def read(self, obj, binary=False):
        """
        Reads out the contents of the given object.

        :param obj: Object path
        :param binary: If set to true, a bytes-object will be returned instead of a string
        """
        raise self._unimplemented('read')

    def exists(self, obj):
        """
        Checks whether or not the given object exists.
        """
        raise self._unimplemented('exists')
