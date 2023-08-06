from gcloud.storage import exceptions
from gcloud.storage.acl import BucketACL
from gcloud.storage.acl import DefaultObjectACL
from gcloud.storage.iterator import KeyIterator
from gcloud.storage.key import Key


class Bucket(object):
  """A class representing a Bucket on Cloud Storage.

  :type connection: :class:`gcloud.storage.connection.Connection`
  :param connection: The connection to use when sending requests.

  :type name: string
  :param name: The name of the bucket.
  """

  def __init__(self, connection=None, name=None, metadata=None):
    self.connection = connection
    self.name = name
    self.metadata = metadata

    # ACL rules are lazily retrieved.
    self.acl = None
    self.default_object_acl = None

  @classmethod
  def from_dict(cls, bucket_dict, connection=None):
    """Construct a new bucket from a dictionary of data from Cloud Storage.

    :type bucket_dict: dict
    :param bucket_dict: The dictionary of data to construct a bucket from.

    :rtype: :class:`Bucket`
    :returns: A bucket constructed from the data provided.
    """

    return cls(connection=connection, name=bucket_dict['name'],
               metadata=bucket_dict)

  def __repr__(self):
    return '<Bucket: %s>' % self.name

  def __iter__(self):
    return iter(KeyIterator(bucket=self))

  def __contains__(self, key):
    return self.get_key(key) is not None

  @property
  def path(self):
    """The URL path to this bucket."""

    if not self.name:
      raise ValueError('Cannot determine path without bucket name.')

    return '/b/' + self.name

  def get_key(self, key):
    """Get a key object by name.

    This will return None if the key doesn't exist::

      >>> from gcloud import storage
      >>> connection = storage.get_connection(project_name, email, key_path)
      >>> bucket = connection.get_bucket('my-bucket')
      >>> print bucket.get_key('/path/to/key.txt')
      <Key: my-bucket, /path/to/key.txt>
      >>> print bucket.get_key('/does-not-exist.txt')
      None

    :type key: string or :class:`gcloud.storage.key.Key`
    :param key: The name of the key to retrieve.

    :rtype: :class:`gcloud.storage.key.Key` or None
    :returns: The key object if it exists, otherwise None.
    """

    # Coerce this to a key object (either from a Key or a string).
    key = self.new_key(key)

    try:
      response = self.connection.api_request(method='GET', path=key.path)
      return Key.from_dict(response, bucket=self)
    except exceptions.NotFoundError:
      return None

  def get_all_keys(self):
    """List all the keys in this bucket.

    This will **not** retrieve all the data for all the keys,
    it will only retrieve metadata about the keys.

    This is equivalent to::

      keys = [key for key in bucket]

    :rtype: list of :class:`gcloud.storage.key.Key`
    :returns: A list of all the Key objects in this bucket.
    """

    return list(self)

  def new_key(self, key):
    """Given a path name (or a Key), return a :class:`gcloud.storage.key.Key` object.

    This is really useful when you're not sure
    if you have a Key object or a string path name.
    Given either of those types,
    this returns the corresponding Key object.

    :type key: string or :class:`gcloud.storage.key.Key`
    :param key: A path name or actual key object.

    :rtype: :class:`gcloud.storage.key.Key`
    :returns: A Key object with the path provided.
    """

    if isinstance(key, Key):
      return key

    # Support Python 2 and 3.
    try:
      string_type = basestring
    except NameError:
      string_type = str

    if isinstance(key, string_type):
      return Key(bucket=self, name=key)

    raise TypeError('Invalid key: %s' % key)

  def delete(self):
    """Delete this bucket.

    The bucket **must** be empty in order to delete it.
    If the bucket doesn't exist,
    this will raise a :class:`gcloud.storage.exceptions.NotFoundError`.
    If the bucket is not empty,
    this will raise an Exception.

    :raises: :class:`gcloud.storage.exceptions.NotFoundError`
    """

    # TODO: Make sure the proper exceptions are raised.

    return self.connection.delete_bucket(self.name)

  def delete_key(self, key):
    # TODO: Should we accept a 'silent' param here to not raise an exception?
    """Deletes a key from the current bucket.

    If the key isn't found,
    this will throw a :class:`gcloud.storage.exceptions.NotFoundError`.

    For example::

      >>> from gcloud import storage
      >>> from gcloud.storage import exceptions
      >>> connection = storage.get_connection(project_name, email, key_path)
      >>> bucket = connection.get_bucket('my-bucket')
      >>> print bucket.get_all_keys()
      [<Key: my-bucket, my-file.txt>]
      >>> bucket.delete_key('my-file.txt')
      >>> try:
      ...   bucket.delete_key('doesnt-exist')
      ... except exceptions.NotFoundError:
      ...   pass


    :type key: string or :class:`gcloud.storage.key.Key`
    :param key: A key name or Key object to delete.

    :rtype: :class:`gcloud.storage.key.Key`
    :returns: The key that was just deleted.
    :raises: :class:`gcloud.storage.exceptions.NotFoundError`
    """

    key = self.new_key(key)
    self.connection.api_request(method='DELETE', path=key.path)
    return key

  def delete_keys(self, keys):
    # TODO: What should be the return value here?
    # NOTE: boto returns a MultiDeleteResult instance.
    for key in keys:
      self.delete_key(key)

  def copy_key(self):
    raise NotImplementedError

  def upload_file(self, filename, key=None):
    # TODO: What do we do about overwriting data?
    """Shortcut method to upload a file into this bucket.

    Use this method to quickly put a local file in Cloud Storage.

    For example::

      >>> from gcloud import storage
      >>> connection = storage.get_connection(project_name, email, key_path)
      >>> bucket = connection.get_bucket('my-bucket')
      >>> bucket.upload_file('~/my-file.txt', 'remote-text-file.txt')
      >>> print bucket.get_all_keys()
      [<Key: my-bucket, remote-text-file.txt>]

    If you don't provide a key value,
    we will try to upload the file using the local filename
    as the key
    (**not** the complete path)::

      >>> from gcloud import storage
      >>> connection = storage.get_connection(project_name, email, key_path)
      >>> bucket = connection.get_bucket('my-bucket')
      >>> bucket.upload_file('~/my-file.txt')
      >>> print bucket.get_all_keys()
      [<Key: my-bucket, my-file.txt>]

    :type filename: string
    :param filename: Local path to the file you want to upload.

    :type key: string or :class:`gcloud.storage.key.Key`
    :param key: The key (either an object or a remote path)
                of where to put the file.

                If this is blank,
                we will try to upload the file
                to the root of the bucket
                with the same name as on your local file system.
    """
    key = self.new_key(key)
    return key.set_contents_from_filename(filename)

  def has_metadata(self, field=None):
    """Check if metadata is available locally.

    :type field: string
    :param field: (optional) the particular field to check for.

    :rtype: bool
    :returns: Whether metadata is available locally.
    """

    if not self.metadata:
      return False
    elif field and field not in self.metadata:
      return False
    else:
      return True

  def reload_metadata(self, full=False):
    """Reload metadata from Cloud Storage.

    :type full: bool
    :param full: If True, loads all data (include ACL data).

    :rtype: :class:`Bucket`
    :returns: The bucket you just reloaded data for.
    """

    projection = 'full' if full else 'noAcl'
    query_params = {'projection': projection}
    self.metadata = self.connection.api_request(
        method='GET', path=self.path, query_params=query_params)
    return self

  def get_metadata(self, field=None, default=None):
    """Get all metadata or a specific field.

    If you request a field that isn't available,
    and that field can be retrieved by refreshing data
    from Cloud Storage,
    this method will reload the data using
    :func:`Bucket.reload_metadata`.

    :type field: string
    :param field: (optional) A particular field to retrieve from metadata.

    :type default: anything
    :param default: The value to return if the field provided wasn't found.

    :rtype: dict or anything
    :returns: All metadata or the value of the specific field.
    """

    if not self.has_metadata(field=field):
      full = (field and field in ('acl', 'defaultObjectAcl'))
      self.reload_metadata(full=full)

    if field:
      return self.metadata.get(field, default)
    else:
      return self.metadata

  def patch_metadata(self, metadata):
    """Update particular fields of this bucket's metadata.

    This method will only update the fields provided
    and will not touch the other fields.

    It will also reload the metadata locally
    based on the servers response.

    :type metadata: dict
    :param metadata: The dictionary of values to update.

    :rtype: :class:`Bucket`
    :returns: The current bucket.
    """

    self.metadata = self.connection.api_request(
        method='PATCH', path=self.path, data=metadata,
        query_params={'projection': 'full'})
    return self

  def configure_website(self, main_page_suffix=None, not_found_page=None):
    """Configure website-related metadata.

    .. note::
      This (apparently) only works
      if your bucket name is a domain name
      (and to do that, you need to get approved somehow...).

      Check out the official documentation here:
      https://developers.google.com/storage/docs/website-configuration

    If you want this bucket to host a website,
    just provide the name of an index page
    and a page to use when a key isn't found::

      >>> from gcloud import storage
      >>> connection = storage.get_connection(project_name, email, private_key_path)
      >>> bucket = connection.get_bucket(bucket_name)
      >>> bucket.configure_website('index.html', '404.html')

    You probably should also make the whole bucket public::

      >>> bucket.make_public(recursive=True, future=True)

    This says:
    "Make the bucket public,
    and all the stuff already in the bucket,
    and anything else I add to the bucket.
    Just make it all public."

    :type main_page_suffix: string
    :param main_page_suffix: The page to use as the main page of a directory.
                             Typically something like index.html.

    :type not_found_page: string
    :param not_found_page: The file to use when a page isn't found.
    """

    data = {
        'website': {
          'mainPageSuffix': main_page_suffix,
          'notFoundPage': not_found_page,
          }
        }
    return self.patch_metadata(data)

  def disable_website(self):
    """Disable the website configuration for this bucket.

    This is really just a shortcut for
    setting the website-related attributes to ``None``.
    """

    return self.configure_website(None, None)

  def reload_acl(self):
    """Reload the ACL data from Cloud Storage.

    :rtype: :class:`Bucket`
    :returns: The current bucket.
    """

    self.acl = BucketACL(bucket=self)

    for entry in self.get_metadata('acl', []):
      entity = self.acl.entity_from_dict(entry)
      self.acl.add_entity(entity)

    return self

  def get_acl(self):
    # TODO: This might be a VERY long list. Use the specific API endpoint.
    """Get ACL metadata as a :class:`gcloud.storage.acl.BucketACL` object.

    :rtype: :class:`gcloud.storage.acl.BucketACL`
    :returns: An ACL object for the current bucket.
    """

    if not self.acl:
      self.reload_acl()
    return self.acl

  def save_acl(self, acl=None):
    """Save the ACL data for this bucket.

    If called without arguments,
    this will save the ACL currently stored on the Bucket object.
    For example,
    this will save
    the ACL stored in ``some_other_acl``::

       >>> bucket.acl = some_other_acl
       >>> bucket.save_acl()

    You can also provide a specific ACL to save
    instead of the one currently set
    on the Bucket object::

       >>> bucket.save_acl(acl=my_other_acl)

    You can use this to set access controls
    to be consistent from one bucket to another::

      >>> bucket1 = connection.get_bucket(bucket1_name)
      >>> bucket2 = connection.get_bucket(bucket2_name)
      >>> bucket2.save_acl(bucket1.get_acl())

    If you want to **clear** the ACL for the bucket,
    you must save an empty list (``[]``)
    rather than using ``None``
    (which is interpreted as wanting to save the current ACL)::

      >>> bucket.save_acl(None)  # Saves the current ACL (self.acl).
      >>> bucket.save_acl([])  # Clears the current ACL.

    :type acl: :class:`gcloud.storage.acl.ACL`
    :param acl: The ACL object to save.
                If left blank, this will save the ACL
                set locally on the bucket.
    """

    # We do things in this weird way because [] and None
    # both evaluate to False, but mean very different things.
    if acl is None:
      acl = self.acl

    if acl is None:
      return self

    return self.patch_metadata({'acl': list(acl)})

  def clear_acl(self):
    """Remove all ACL rules from the bucket.

    Note that this won't actually remove *ALL* the rules,
    but it will remove all the non-default rules.
    In short,
    you'll still have access
    to a bucket that you created
    even after you clear ACL rules
    with this method.

    For example,
    imagine that you granted access to this bucket
    to a bunch of coworkers::

      >>> from gcloud import storage
      >>> connection = storage.get_connection(project_name, email, private_key_path)
      >>> bucket = connection.get_bucket(bucket_name)
      >>> acl = bucket.get_acl()
      >>> acl.user('coworker1@example.org').grant_read()
      >>> acl.user('coworker2@example.org').grant_read()
      >>> acl.save()

    Now they work in another part of the company
    and you want to 'start fresh' on who has access::

      >>> acl.clear_acl()

    At this point all the custom rules you created have been removed.
    """

    return self.save_acl(acl=[])

  def reload_default_object_acl(self):
    """Reload the Default Object ACL rules for this bucket.

    :rtype: :class:`Bucket`
    :returns: The current bucket.
    """

    self.default_object_acl = DefaultObjectACL(bucket=self)

    for entry in self.get_metadata('defaultObjectAcl', []):
      entity = self.default_object_acl.entity_from_dict(entry)
      self.default_object_acl.add_entity(entity)

    return self

  def get_default_object_acl(self):
    """Get the current Default Object ACL rules.

    If the appropriate metadata isn't available locally,
    this method will reload it from Cloud Storage.

    :rtype: :class:`gcloud.storage.acl.DefaultObjectACL`
    :returns: A DefaultObjectACL object for this bucket.
    """

    if not self.default_object_acl:
      self.reload_default_object_acl()
    return self.default_object_acl

  def save_default_object_acl(self, acl=None):
    """Save the Default Object ACL rules for this bucket.

    :type acl: :class:`gcloud.storage.acl.DefaultObjectACL`
    :param acl: The DefaultObjectACL object to save.
                If not provided, this will look at
                the ``default_object_acl`` property
                and save that.
    """

    acl = acl or self.default_object_acl

    if acl is None:
      return self

    return self.patch_metadata({'defaultObjectAcl': list(acl)})

  def clear_default_object_acl(self):
    """Remove the Default Object ACL from this bucket."""

    return self.save_default_object_acl(acl=[])

  def make_public(self, recursive=False, future=False):
    """Make a bucket public.

    :type recursive: bool
    :param recursive: If True, this will make all keys inside the bucket
                      public as well.

    :type future: bool
    :param future: If True, this will make all objects created in the future
                   public as well.
    """

    self.get_acl().all().grant_read()
    self.save_acl()

    if future:
      self.get_default_object_acl().all().grant_read()
      self.save_default_object_acl()

    if recursive:
      for key in self:
        key.get_acl().all().grant_read()
        key.save_acl()
