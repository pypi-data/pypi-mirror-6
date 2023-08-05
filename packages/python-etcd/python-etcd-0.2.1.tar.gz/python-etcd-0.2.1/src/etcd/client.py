"""
.. module:: python-etcd
   :synopsis: A python etcd client.

.. moduleauthor:: Jose Plana <jplana@gmail.com>


"""
import urllib3
import json
import ssl

import etcd


class Client(object):
    """
    Client for etcd, the distributed log service using raft.
    """

    def __init__(
            self,
            host='127.0.0.1',
            port=4001,
            read_timeout=60,
            allow_redirect=True,
            protocol='http',
            cert=None,
            ca_cert=None,
            allow_reconnect=False,
    ):
        """
        Initialize the client.

        Args:
            host (mixed):
                           If a string, IP to connect to.
                           If a tuple ((host, port), (host, port), ...)

            port (int):  Port used to connect to etcd.

            read_timeout (int):  max seconds to wait for a read.

            allow_redirect (bool): allow the client to connect to other nodes.

            protocol (str):  Protocol used to connect to etcd.

            cert (mixed):   If a string, the whole ssl client certificate;
                            if a tuple, the cert and key file names.

            ca_cert (str): The ca certificate. If pressent it will enable
                           validation.

            allow_reconnect (bool): allow the client to reconnect to another
                                    etcd server in the cluster in the case the
                                    default one does not respond.

        """
        self._machines_cache = []

        self._protocol = protocol

        def uri(protocol, host, port):
            return '%s://%s:%d' % (protocol, host, port)

        if not isinstance(host, tuple):
            self._host = host
            self._port = port
        else:
            self._host, self._port = host[0]
            self._machines_cache.extend(
                [uri(self._protocol, *conn) for conn in host])

        self._base_uri = uri(self._protocol, self._host, self._port)

        self.version_prefix = '/v1'

        self._read_timeout = read_timeout
        self._allow_redirect = allow_redirect
        self._allow_reconnect = allow_reconnect

        self._MGET = 'GET'
        self._MPOST = 'POST'
        self._MDELETE = 'DELETE'

        # Dictionary of exceptions given an etcd return code.
        # 100: Key not found.
        # 101: The given PrevValue is not equal to the value of the key
        # 102: Not a file  if the /foo = Node(bar) exists,
        #      setting /foo/foo = Node(barbar)
        # 103: Reached the max number of machines in the cluster
        # 300: Raft Internal Error
        # 301: During Leader Election
        # 500: Watcher is cleared due to etcd recovery
        self.error_codes = {
            100: KeyError,
            101: ValueError,
            102: KeyError,
            103: Exception,
            300: Exception,
            301: Exception,
            500: etcd.EtcdException,
            999: etcd.EtcdException}

        # SSL Client certificate support

        kw = {}

        if protocol == 'https':
            # If we don't allow TLSv1, clients using older version of OpenSSL
            # (<1.0) won't be able to connect.
            kw['ssl_version'] = ssl.PROTOCOL_TLSv1

            if cert:
                if isinstance(cert, tuple):
                    # Key and cert are separate
                    kw['cert_file'] = cert[0]
                    kw['key_file'] = cert[1]
                else:
                    #combined certificate
                    kw['cert_file'] = cert

            if ca_cert:
                kw['ca_certs'] = ca_cert
                kw['cert_reqs'] = ssl.CERT_REQUIRED

        self.http = urllib3.PoolManager(num_pools=10, **kw)

        if self._allow_reconnect:
            # we need the set of servers in the cluster in order to try
            # reconnecting upon error.
            self._machines_cache = self.machines
            self._machines_cache.remove(self._base_uri)
        else:
            self._machines_cache = []

    @property
    def base_uri(self):
        """URI used by the client to connect to etcd."""
        return self._base_uri

    @property
    def host(self):
        """Node to connect  etcd."""
        return self._host

    @property
    def port(self):
        """Port to connect etcd."""
        return self._port

    @property
    def protocol(self):
        """Protocol used to connect etcd."""
        return self._protocol

    @property
    def read_timeout(self):
        """Max seconds to wait for a read."""
        return self._read_timeout

    @property
    def allow_redirect(self):
        """Allow the client to connect to other nodes."""
        return self._allow_redirect

    @property
    def machines(self):
        """
        Members of the cluster.

        Returns:
            list. str with all the nodes in the cluster.

        >>> print client.machines
        ['http://127.0.0.1:4001', 'http://127.0.0.1:4002']
        """
        return [
            node.strip() for node in self.api_execute(
                self.version_prefix + '/machines',
                self._MGET).split(',')
        ]

    @property
    def leader(self):
        """
        Returns:
            str. the leader of the cluster.

        >>> print client.leader
        'http://127.0.0.1:4001'
        """
        return self.api_execute(
            self.version_prefix + '/leader',
            self._MGET)

    @property
    def key_endpoint(self):
        """
        REST key endpoint.
        """
        return self.version_prefix + '/keys'

    @property
    def watch_endpoint(self):
        """
        REST watch endpoint.
        """

        return self.version_prefix + '/watch'

    def __contains__(self, key):
        """
        Check if a key is available in the cluster.

        >>> print 'key' in client
        True
        """
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def ethernal_watch(self, key, index=None):
        """
        Generator that will yield changes from a key.
        Note that this method will block forever until an event is generated.

        Args:
            key (str):  Key to subcribe to.
            index (int):  Index from where the changes will be received.

        Yields:
            client.EtcdResult

        >>> for event in client.ethernal_watch('/subcription_key'):
        ...     print event.value
        ...
        value1
        value2

        """
        local_index = index
        while True:
            response = self.watch(key, local_index)
            if local_index is not None:
                local_index += 1
            yield response

    def test_and_set(self, key, value, prev_value, ttl=None):
        """
        Atomic test & set operation.
        It will check if the value of 'key' is 'prev_value',
        if the the check is correct will change the value for 'key' to 'value'
        if the the check is false an exception will be raised.

        Args:
            key (str):  Key.
            value (object):  value to set
            prev_value (object):  previous value.
            ttl (int):  Time in seconds of expiration (optional).

        Returns:
            client.EtcdResult

        Raises:
            ValueError: When the 'prev_value' is not the current value.

        >>> print client.test_and_set('/key', 'new', 'old', ttl=60).value
        'new'

        """
        path = self.key_endpoint + key
        payload = {'value': value, 'prevValue': prev_value}
        if ttl:
            payload['ttl'] = ttl
        response = self.api_execute(path, self._MPOST, payload)
        return self._result_from_response(response)

    def set(self, key, value, ttl=None):
        """
        Set value for a key.

        Args:
            key (str):  Key.

            value (object):  value to set

            ttl (int):  Time in seconds of expiration (optional).

        Returns:
            client.EtcdResult

        >>> print client.set('/key', 'newValue', ttl=60).value
        'newValue'

        """

        path = self.key_endpoint + key
        payload = {'value': value}
        if ttl:
            payload['ttl'] = ttl
        response = self.api_execute(path, self._MPOST, payload)
        return self._result_from_response(response)

    def delete(self, key):
        """
        Removed a key from etcd.

        Args:
            key (str):  Key.

        Returns:
            client.EtcdResult

        Raises:
            KeyValue:  If the key doesn't exists.

        >>> print client.delete('/key').key
        '/key'

        """

        response = self.api_execute(self.key_endpoint + key, self._MDELETE)
        return self._result_from_response(response)

    def get(self, key):
        """
        Returns the value of the key 'key'.

        Args:
            key (str):  Key.

        Returns:
            client.EtcdResult (or an array of client.EtcdResult if a
            subtree is queried)

        Raises:
            KeyValue:  If the key doesn't exists.

        >>> print client.get('/key').value
        'value'

        """

        response = self.api_execute(self.key_endpoint + key, self._MGET)
        return self._result_from_response(response)

    def watch(self, key, index=None):
        """
        Blocks until a new event has been received, starting at index 'index'

        Args:
            key (str):  Key.

            index (int): Index to start from.

        Returns:
            client.EtcdResult

        Raises:
            KeyValue:  If the key doesn't exists.

        >>> print client.watch('/key').value
        'value'

        """

        params = None
        method = self._MGET
        if index:
            params = {'index': index}
            method = self._MPOST

        response = self.api_execute(
            self.watch_endpoint + key,
            method,
            params=params)
        return self._result_from_response(response)

    def _result_from_response(self, response):
        """ Creates an EtcdResult from json dictionary """
        try:
            res = json.loads(response)
            if isinstance(res, list):
                return [etcd.EtcdResult(**v) for v in res]
            return etcd.EtcdResult(**res)
        except:
            raise etcd.EtcdException('Unable to decode server response')

    def _next_server(self):
        """ Selects the next server in the list, refreshes the server list. """
        try:
            return self._machines_cache.pop()
        except IndexError:
            raise etcd.EtcdException('No more machines in the cluster')

    def api_execute(self, path, method, params=None):
        """ Executes the query. """

        some_request_failed = False
        response = False

        while not response:
            try:
                url = self._base_uri + path

                if (method == self._MGET) or (method == self._MDELETE):
                    response = self.http.request(
                        method,
                        url,
                        fields=params,
                        redirect=self.allow_redirect)

                elif method == self._MPOST:
                    response = self.http.request_encode_body(
                        method,
                        url,
                        fields=params,
                        encode_multipart=False,
                        redirect=self.allow_redirect)

            except urllib3.exceptions.MaxRetryError:
                self._base_uri = self._next_server()
                some_request_failed = True

        if some_request_failed:
            self._machines_cache = self.machines
            self._machines_cache.remove(self._base_uri)

        if response.status == 200:
            return response.data

        else:
            try:
                error = json.loads(response.data)
                message = "%s : %s" % (error['message'], error['cause'])
                error_code = error['errorCode']
                error_exception = self.error_codes[error_code]
            except:
                message = "Unable to decode server response"
                error_exception = etcd.EtcdException
            raise error_exception(message)
