import argparse
import asyncio
import logging


from . import EncodedFiles, Tmux, no_echo, noop


async def run(args):
    logging.debug('main()')
    async with Tmux(args.pane_id, args.tmux_exe, args.tmux_socket) as t:
        logging.debug('with_Tmux()')
        with no_echo(t) if args.quiet else noop():
            encoded_file = EncodedFiles(args.src)
            decode_cmd = encoded_file.uu_command()
            t.send_keys(decode_cmd)
            await asyncio.sleep(0.1)
            for i, part in enumerate(encoded_file.uu_encoded()):
                logging.info('Sending part %d', i)
                logging.debug('Part: %s', part)
                t.send_keys([part, '\n'], literal=True)
                await asyncio.sleep(0.0001)


def main():
    parser = argparse.ArgumentParser(description='send file/directory to remote session')
    parser.add_argument('src', help='source directory to send contents of')
    parser.add_argument('--pane-id', required=True, help='''
        The id of the pane to send the file to e.g. `#{pane_id}`.
        ''')
    parser.add_argument('--tmux-exe', default='tmux', help='''
        The name or path to the tmux executable to use e.g. `/proc/#{pid}/exe`.
        ''')
    parser.add_argument('--tmux-socket', help='''
        The path to the tmux socket file e.g. `#{socket_path}`.
        ''')
    parser.add_argument('--quiet', action='store_true', help='''
        Suppress file transfer output.
        ''')
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

    def print_exc(loop, context):
        logging.error('Error in event loop: %s', context['message'])

    asyncio.get_event_loop().set_exception_handler(print_exc)
    asyncio.get_event_loop().run_until_complete(run(args))


if __name__ == '__main__':
    main()
