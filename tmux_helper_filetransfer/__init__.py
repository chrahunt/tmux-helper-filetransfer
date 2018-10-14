import asyncio
from contextlib import contextmanager
import gzip
import io
import logging
from pathlib import Path
import tarfile
from typing import List
import uu


class DataProtocol(asyncio.SubprocessProtocol):
    def __init__(self, exit_future):
        self._exit_future = exit_future

    def pipe_data_received(self, fd, data):
        logging.debug('Data received (%d): %s', fd, data)

    def pipe_connection_lost(self, fd, exc):
        logging.warning('Connection lost (%d) %s', fd, exc)

    def process_exited(self):
        logging.debug('process_exited()')
        self._exit_future.set_result(True)


class Tmux:
    def __init__(
            self, pane_id, tmux_exe, tmux_socket,
            loop=asyncio.get_event_loop()):
        self._pane_id = pane_id
        self._loop = loop
        self._tmux_exe = tmux_exe
        self._tmux_socket = tmux_socket

    async def __aenter__(self):
        self._exit_future = asyncio.Future(loop=self._loop)
        args = []
        if self._tmux_exe:
            args.append(self._tmux_exe)
        else:
            args.append('tmux')
        if self._tmux_socket:
            args.extend(['-S', self._tmux_socket])
        args.extend(['-C', 'attach', '-t', self._pane_id])
        transport, protocol = await self._loop.subprocess_exec(
                lambda: DataProtocol(self._exit_future), *args)
        self._transport = transport
        self._write_transport = self._transport.get_pipe_transport(0)
        self._protocol = protocol
        return self

    async def __aexit__(self, exc_type, exc, tb):
        logging.debug('Tmux.__aexit__()')
        if exc:
            logging.error(f'Exception: {exc}')
            logging.error(tb)
        # Ensure any previous command has been finished.
        self._write_transport.write(b'\n')
        self._write_transport.write(b'detach\n')
        self._transport.close()
        await self._exit_future
        logging.debug('Post-future')

    def _tmux_encode(self, s):
        escaped = (s
            .replace('\\', '\\\\')
            .replace('\n', '\\n')
            .replace('\t', '\\t')
            .replace('"', '\\"')
            .replace('$', '\\$'))
        return escaped.encode('utf-8')

    def send_keys(self, args: List[str], literal=False):
        logging.debug('Tmux.send_keys()')
        self._write_transport.write(b'send-keys')
        if literal:
            self._write_transport.write(b' -l')
        self._write_transport.write(b' "')
        for d in args:
            encoded = self._tmux_encode(d)
            logging.debug('Writing %s', encoded.decode('utf-8'))
            self._write_transport.write(encoded)
        # submit command
        self._write_transport.write(b'"\n')


class EncodedFiles:
    def __init__(self, path):
        logging.debug('EncodedFiles.__init__()')
        self._path = Path(path)

    def _make_tgz(self):
        logging.debug('EncodedFiles._make_tgz()')
        buf = io.BytesIO()
        path = self._path.resolve()
        if path.is_dir():
            # Omits top-level directory from inclusion.
            name = ''
        else:
            name = path.basename()
        with tarfile.TarFile(fileobj=buf, mode='w') as tar:
            tar.add(path, arcname=name)
        buf.seek(0)
        return gzip.compress(buf.read())

    def uu_encoded(self):
        logging.debug('EncodedFiles.uu_encoded()')
        buf = io.BytesIO(self._make_tgz())
        outbuf = io.BytesIO()
        uu.encode(buf, outbuf)
        outbuf.seek(0)
        return outbuf.read().decode('ascii').splitlines()

    def uu_command(self):
        logging.debug('EncodedFiles.uu_command()')
        decode_pipeline = [
            'uudecode',
            'gunzip -c -',
            'tar xf -'
        ]
        return [' | '.join(decode_pipeline), '\n']


@contextmanager
def no_echo(tmux):
    try:
        tmux.send_keys(['stty -echo\n'])
        yield
    finally:
        tmux.send_keys(['stty echo\n'])


@contextmanager
def noop():
    yield
