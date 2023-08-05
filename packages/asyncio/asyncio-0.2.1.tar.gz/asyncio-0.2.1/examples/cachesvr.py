"""A simple memcache-like server.

The basic data structure maintained is a single in-memory dictionary
mapping string keys to string values, with operations get, set and
delete.

This is a TCP server listening on port 54321.  There is no
authentication.

Requests provide an operation and return a response.  A connection may
be used for multiple requests.  The connection is also disconnected
when a client sends a bad request.

If a client is idle for over 5 seconds (i.e., it does not send another
request, or fails to read the whole response, within this time), it is
disconnected.  [Currently not implemented]

Framing of requests and responses within a connection uses a
line-based protocol.  The first line of a request is the frame header
and contains three whitespace-delimited tokens:

- the keyword 'request'
- a decimal request ID; the first request is '1', the second '2', etc.
- a decimal byte count giving the size of the rest of the request

Response frames look the same except the keyword is 'response'.  The
response ID matches the request ID.

Within the frame, individual requests and responses are JSON encoded.

If the frame header or the JSON request body cannot be parsed, an
unframed error message (always starting with 'error') is written back
and the connection is closed.

JSON-encoded requests can be:

- {"type": "get", "key": <string>}
- {"type": "set", "key": <string>, "value": <string>}
- {"type": "delete", "key": <string>}

Responses are also JSON-encoded:

- {"status": "ok", "value": <string>}  # Successful get request
- {"status": "ok"}  # Successful set or delete request
- {"status": "notfound"}  # Key not found for get or delete request

If the request cannot be handled (e.g., the type or key field is
absent or invalid), an error response of the following form is
returned, but the connection is not closed:

- {"error": <string>}
"""

import json

import asyncio


class Cache:

    def __init__(self, loop):
        self.loop = loop
        self.table = {}

    def handle_client(self, reader, writer):
        print('got a connection from',
              writer.get_extra_info('socket').getpeername())
        coro = self.frame_wrapper(reader, writer)
        # Must make it a Task so it runs asynchronously.
        asyncio.Task(coro, loop=self.loop)

    @asyncio.coroutine
    def frame_wrapper(self, reader, writer):
        # Wrapper to log errors and close writer (i.e., transport).
        try:
            yield from self.frame_parser(reader, writer)
        except BaseException as exc:
            print('error', repr(exc))
        else:
            print('end')
        finally:
            writer.close()

    @asyncio.coroutine
    def frame_parser(self, reader, writer):
        # This takes care of the framing.
        last_request_id = 0
        while True:
            # XXX The readline() and readexactly() calls will hang if
            # the client doesn't send enough data but doesn't hang up
            # either.  We should add a timeout (to each, probably).
            framing_b = yield from reader.readline(timeout=5)
            if not framing_b:
                break  # Clean close.
            try:
                frame_keyword, request_id_b, byte_count_b = framing_b.split()
            except ValueError:
                writer.write(b'error unparseable frame\r\n')
                break
            if frame_keyword != b'request':
                writer.write(b'error frame does not start with request\r\n')
                break
            try:
                request_id, byte_count = int(request_id_b), int(byte_count_b)
            except ValueError:
                writer.write(b'error unparsable frame parameters\r\n')
                break
            if request_id != last_request_id + 1 or byte_count < 2:
                writer.write(b'error invalid frame parameters\r\n')
                break
            last_request_id = request_id
            request_b = yield from reader.readexactly(byte_count, timeout=5)
            try:
                request = json.loads(request_b.decode('utf8'))
            except ValueError:
                writer.write(b'error unparsable json\r\n')
                break
            response = self.handle_request(request)  # Not a coroutine.
            if response is None:
                writer.write(b'error unhandlable request\r\n')
                break
            response_b = json.dumps(response).encode('utf8') + b'\r\n'
            byte_count = len(response_b)
            framing_s = 'response {} {}\r\n'.format(request_id, byte_count)
            writer.write(framing_s.encode('ascii'))
            writer.write(response_b)

    def handle_request(self, request):
        # This parses one request and farms it out to a specific handler.
        # Return None for all errors.
        if not isinstance(request, dict):
            return {'error': 'request is not a dict'}
        request_type = request.get('type')
        if request_type is None:
            return {'error': 'no type in request'}
        if request_type not in {'get', 'set', 'delete'}:
            return {'error': 'unknown request type'}
        key = request.get('key')
        if not isinstance(key, str):
            return {'error': 'key is not a string'}
        if request_type == 'get':
            return self.handle_get(key)
        if request_type == 'set':
            value = request.get('value')
            if not isinstance(value, str):
                return {'error': 'value is not a string'}
            return self.handle_set(key, value)
        if request_type == 'delete':
            return self.handle_delete(key)
        assert False, 'bad request type'  # Should have been caught above.

    def handle_get(self, key):
        value = self.table.get(key)
        if value is None:
            return {'status': 'notfound'}
        else:
            return {'status': 'ok', 'value': value}

    def handle_set(self, key, value):
        self.table[key] = value
        return {'status': 'ok'}

    def handle_delete(self, key):
        if key not in self.table:
            return {'status': 'notfound'}
        else:
            del self.table[key]
            return {'status': 'ok'}


def main():
    asyncio.set_event_loop(None)
    loop = asyncio.new_event_loop()
    cache = Cache(loop)
    task = asyncio.streams.start_serving(cache.handle_client,
                                         'localhost', 54321,
                                loop=loop)
    socks = loop.run_until_complete(task)
    for sock in socks:
        print(sock.getsockname())
    loop.run_forever()


if __name__ == '__main__':
    main()
