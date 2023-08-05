from kotocore.exceptions import NotCached


class ServiceCache(object):
    """
    A centralized registry of classes that have already been built.

    Present to both prevent too much factory churn as well as to give the
    resource layer something to refer to in relations.

    Usage::

        >>> sc = ServiceCache()
        >>> len(sc)
        0
        >>> sc.set_connection('s3', S3Connection)
        >>> sc.set_resource('s3', 'Bucket', Bucket)
        >>> sc.set_collection('s3', 'BucketCollection', BucketCollection)
        # We only count services.
        >>> len(sc)
        1
        >>> 's3' in sc
        True
        # Later...
        >>> conn_class = sc.get_connection('s3')
        >>> res_class = sc.get_resource('s3', 'Bucket')
        >>> sc.del_resource('s3', 'Bucket')

    """
    # TODO: We may want to add LRU/expiration behavior in the future, to
    #       prevent the cache from taking up too much space.
    #       Unlikely, but potential.
    def __init__(self):
        self.services = {}

    def __str__(self):
        return 'ServiceCache: {0}'.format(
            ', '.join(sorted(self.services.keys()))
        )

    def __len__(self):
        return len(self.services)

    def __contains__(self, service_name):
        return service_name in self.services

    def get_connection(self, service_name):
        """
        Retrieves a connection class from the cache, if available.

        :param service_name: The service a given ``Connection`` talks to. Ex.
            ``sqs``, ``sns``, ``dynamodb``, etc.
        :type service_name: string

        :returns: A <kotocore.connection.Connection> subclass
        """
        service = self.services.get(service_name, {})
        connection_class = service.get('connection', None)

        if not connection_class:
            msg = "Connection for '{0}' is not present in the cache."
            raise NotCached(msg.format(
                service_name
            ))

        return connection_class

    def set_connection(self, service_name, to_cache):
        """
        Sets a connection class within the cache.

        :param service_name: The service a given ``Connection`` talks to. Ex.
            ``sqs``, ``sns``, ``dynamodb``, etc.
        :type service_name: string

        :param to_cache: The class to be cached for the service.
        :type to_cache: class
        """
        self.services.setdefault(service_name, {})
        self.services[service_name]['connection'] = to_cache

    def del_connection(self, service_name):
        """
        Deletes a connection for a given service.

        Fails silently if no connection is found in the cache.

        :param service_name: The service a given ``Connection`` talks to. Ex.
            ``sqs``, ``sns``, ``dynamodb``, etc.
        :type service_name: string
        """
        # Unlike ``get_connection``, this should be fire & forget.
        # We don't really care, as long as it's not in the cache any longer.
        try:
            del self.services[service_name]['connection']
        except KeyError:
            pass

    def build_classpath(self, klass=None):
        if not klass:
            classpath = 'default'
        else:
            classpath = "{0}.{1}".format(
                klass.__module__,
                klass.__name__
            )

        return classpath

    def get_resource(self, service_name, resource_name, base_class=None):
        """
        Retrieves a resource class from the cache, if available.

        :param service_name: The service a given ``Resource`` talks to. Ex.
            ``sqs``, ``sns``, ``dynamodb``, etc.
        :type service_name: string

        :param resource_name: The name of the ``Resource``. Ex.
            ``Queue``, ``Notification``, ``Table``, etc.
        :type resource_name: string

        :param base_class: (Optional) The base class of the object. Prevents
            "magically" loading the wrong class (one with a different base).
            Default is ``default``.
        :type base_class: class

        :returns: A <kotocore.resources.Resource> subclass
        """
        classpath = self.build_classpath(base_class)
        service = self.services.get(service_name, {})
        resources = service.get('resources', {})
        resource_options = resources.get(resource_name, {})
        resource_class = resource_options.get(classpath, None)

        if not resource_class:
            msg = "Resource '{0}' for {1} is not present in the cache."
            raise NotCached(msg.format(
                resource_name,
                service_name
            ))

        return resource_class

    def set_resource(self, service_name, resource_name, to_cache):
        """
        Sets the resource class within the cache.

        :param service_name: The service a given ``Resource`` talks to. Ex.
            ``sqs``, ``sns``, ``dynamodb``, etc.
        :type service_name: string

        :param resource_name: The name of the ``Resource``. Ex.
            ``Queue``, ``Notification``, ``Table``, etc.
        :type resource_name: string

        :param to_cache: The class to be cached for the service.
        :type to_cache: class
        """
        self.services.setdefault(service_name, {})
        self.services[service_name].setdefault('resources', {})
        self.services[service_name]['resources'].setdefault(resource_name, {})
        options = self.services[service_name]['resources'][resource_name]
        classpath = self.build_classpath(to_cache.__bases__[0])

        if classpath == 'kotocore.resources.Resource':
            classpath = 'default'

        options[classpath] = to_cache

    def del_resource(self, service_name, resource_name, base_class=None):
        """
        Deletes a resource class for a given service.

        Fails silently if no connection is found in the cache.

        :param service_name: The service a given ``Resource`` talks to. Ex.
            ``sqs``, ``sns``, ``dynamodb``, etc.
        :type service_name: string

        :param base_class: (Optional) The base class of the object. Prevents
            "magically" loading the wrong class (one with a different base).
            Default is ``default``.
        :type base_class: class
        """
         # Unlike ``get_resource``, this should be fire & forget.
        # We don't really care, as long as it's not in the cache any longer.
        try:
            classpath = self.build_classpath(base_class)
            opts = self.services[service_name]['resources'][resource_name]
            del opts[classpath]
        except KeyError:
            pass

    def get_collection(self, service_name, collection_name, base_class=None):
        """
        Retrieves a collection class from the cache, if available.

        :param service_name: The service a given ``Collection`` talks to. Ex.
            ``sqs``, ``sns``, ``dynamodb``, etc.
        :type service_name: string

        :param collection_name: The name of the ``Collection``. Ex.
            ``QueueCollection``, ``NotificationCollection``,
            ``TableCollection``, etc.
        :type collection_name: string

        :param base_class: (Optional) The base class of the object. Prevents
            "magically" loading the wrong class (one with a different base).
            Default is ``default``.
        :type base_class: class

        :returns: A <kotocore.collections.Collection> subclass
        """
        classpath = self.build_classpath(base_class)
        service = self.services.get(service_name, {})
        collections = service.get('collections', {})
        collection_options = collections.get(collection_name, {})
        collection_class = collection_options.get(classpath, None)

        if not collection_class:
            msg = "Collection '{0}' for {1} is not present in the cache."
            raise NotCached(msg.format(
                collection_name,
                service_name
            ))

        return collection_class

    def set_collection(self, service_name, collection_name, to_cache):
        """
        Sets a collection class within the cache.

        :param service_name: The service a given ``Collection`` talks to. Ex.
            ``sqs``, ``sns``, ``dynamodb``, etc.
        :type service_name: string

        :param collection_name: The name of the ``Collection``. Ex.
            ``QueueCollection``, ``NotificationCollection``,
            ``TableCollection``, etc.
        :type collection_name: string

        :param to_cache: The class to be cached for the service.
        :type to_cache: class
        """
        self.services.setdefault(service_name, {})
        self.services[service_name].setdefault('collections', {})
        self.services[service_name]['collections'].setdefault(collection_name, {})
        options = self.services[service_name]['collections'][collection_name]
        classpath = self.build_classpath(to_cache.__bases__[0])

        if classpath == 'kotocore.collections.Collection':
            classpath = 'default'

        options[classpath] = to_cache

    def del_collection(self, service_name, collection_name, base_class=None):
        """
        Deletes a collection for a given service.

        Fails silently if no collection is found in the cache.

        :param service_name: The service a given ``Collection`` talks to. Ex.
            ``sqs``, ``sns``, ``dynamodb``, etc.
        :type service_name: string

        :param collection_name: The name of the ``Collection``. Ex.
            ``QueueCollection``, ``NotificationCollection``,
            ``TableCollection``, etc.
        :type collection_name: string

        :param base_class: (Optional) The base class of the object. Prevents
            "magically" loading the wrong class (one with a different base).
            Default is ``default``.
        :type base_class: class
        """
         # Unlike ``get_collection``, this should be fire & forget.
        # We don't really care, as long as it's not in the cache any longer.
        try:
            classpath = self.build_classpath(base_class)
            opts = self.services[service_name]['collections'][collection_name]
            del opts[classpath]
        except KeyError:
            pass
