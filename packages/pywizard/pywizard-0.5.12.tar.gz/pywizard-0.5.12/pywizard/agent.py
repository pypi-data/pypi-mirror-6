import argparse
import json
import os
import subprocess
import logging
from time import sleep
import pywizard
from pywizard.utils.file_transfer import extract_transport_package
from pywizard.utils.process import require_sudo, run
from pywizard.utils.execute import check_requirements, check_zmq, check_tornado, __atach_agent_logging, json_cmd
import tornado
from tornado.process import Subprocess
from zmq.eventloop.ioloop import PeriodicCallback
from pywizard.resources.package_pip import pip_command


def pywizard_agent_cmd():
    check_requirements()

    parser = argparse.ArgumentParser()
    parser.add_argument('--install', action='store_true', default=False)
    parser.add_argument('--node-name', type=str, nargs='?')
    parser.add_argument('--server-ip', type=str, nargs='?')
    args = parser.parse_args()

    if args.install:
        require_sudo()

        path = os.path.dirname(__file__) + '/templates/upstart-agent.conf'

        iargs = []
        if args.node_name:
            iargs.append('--node-name %s' % args.node_name)
        if args.server_ip:
            iargs.append('--server-ip %s' % args.server_ip)

        with open(path) as f:
            content = f.read().replace('%ARGS%', ' '.join(iargs))

        with open('/etc/init/pywizard-agent.conf', 'w+') as f:
            f.write(content)

        run('chmod +x /etc/init/pywizard-agent.conf')
        run('start pywizard-agent')
        run('status pywizard-agent')

    else:

        check_zmq()
        check_tornado()

        import zmq
        from zmq.eventloop import zmqstream, ioloop

        ioloop.install()

        ctx = zmq.Context()

        pub = ctx.socket(zmq.PUB)
        if args.server_ip:

            ip = 'tcp://%s:7373' % args.server_ip
            pub.connect(ip)
        else:
            pub.bind('tcp://127.0.0.1:7373')

        __atach_agent_logging(pub, args.node_name)

        def sub_message(message):
            pub.send_multipart(message)

        def write_data(data):
            pub.send_multipart([args.node_name, json_cmd('continue', data)])

        processes = []

        def exec_cmd(command):
            process = Subprocess(
                command,
                shell=isinstance(command, basestring),
                stdout=tornado.process.Subprocess.STREAM,
                stderr=subprocess.STDOUT
            )
            logging.info('Process started: %s' % command)

            def on_process_end(data):
                if len(data):
                    pub.send_multipart([args.node_name, json_cmd('continue', data)])
                for p in processes:
                    if p['process'] == process:
                        processes.remove(p)

            process.stdout.read_until_close(on_process_end, write_data)
            processes.append({
                'process': process,
                'command': command
            })

        def terminate():
            logging.info('Terminating pywizard-agent...')
            sleep(1)  # make sure everything is done
            logging.getLogger().disabled = True
            ctx.destroy()
            exit(0)

        def __install_pkg(cmd, dir_):
            logging.info('Removing old package: %s' % dir_)
            if not os.path.exists(dir_):
                run('mkdir -p %s' % dir_)
            run('rm -rf %s/*' % dir_)
            logging.info('Extracting new package ...')
            extract_transport_package(cmd['data']['pkg'], dir_)

        def cmd_message(message):

            cmd = json.loads(message[-1])

            if cmd['cmd'] == 'shell':
                print message
                command = cmd['data']
                parts = command.split(' ')
                if command.split(' ')[0] == 'cd':
                    os.chdir(command.split(' ')[1])
                    logging.info(os.getcwd())
                elif command == '#':
                    if len(processes) > 0:
                        for nr, info in enumerate(processes):
                            write_data('%d) %s' % (nr + 1, info['command']))
                    else:
                        logging.info('no tasks running!')
                elif parts[0] == '#' and parts[1] == 'kill':
                    nr = int(parts[2])
                    if len(processes) < nr:
                        logging.info('No task with id %d has been found!' % nr)
                    else:
                        p = processes[nr - 1]
                        p['process'].proc.kill()
                        logging.info('task %d has been killed!' % nr)
                        processes.remove(p)
                else:
                    exec_cmd(command)

            elif cmd['cmd'] == 'provision':
                os.chdir(cmd['data']['path'])
                exec_cmd(
                    ['pywizard', cmd['data']['script'], '--path', cmd['data']['path'], '--apply', '--roles', ','.join(cmd['data']['roles']),
                     '--log-level', cmd['data']['log-level'], '--context', json.dumps(cmd['data']['context'])]
                )

            elif cmd['cmd'] == 'provision_pkg':

                dir_ = os.path.realpath(cmd['data']['path'])

                if not 'provision' in dir_:
                    logging.error('Wrong provision dir: %s Provision dir should contain word "provision"')
                    return

                __install_pkg(cmd, dir_)
                logging.info('Provision package successfully transferred. Length: %s' % len(cmd['data']['pkg']))

            elif cmd['cmd'] == 'pywizard_pkg':

                dir_ = os.path.dirname(pywizard.__file__)

                __install_pkg(cmd, dir_)
                logging.info('Pywizard package successfully transferred. Length: %s' % len(cmd['data']['pkg']))

            elif cmd['cmd'] == 'upgrade':
                print message
                exec_cmd(pip_command('install pywizard --upgrade'))

            elif cmd['cmd'] == 'restart':
                print message
                terminate()
            else:
                print message
                pub.send_multipart([args.node_name, json_cmd('log', 'Unknown command (%s): %s' %
                                                                    (args.node_name, cmd['cmd']))])

        sub = ctx.socket(zmq.SUB)
        sub.bind('tcp://127.0.0.1:7374')
        sub.setsockopt(zmq.SUBSCRIBE, "")
        sub_stream = zmqstream.ZMQStream(sub)
        sub_stream.on_recv(sub_message)

        cmd = ctx.socket(zmq.SUB)
        if args.server_ip:

            cmd.connect('tcp://%s:7375' % args.server_ip)
        else:
            cmd.bind('tcp://127.0.0.1:7375')
        if args.node_name:
            # cmd.setsockopt(zmq.SUBSCRIBE, "")
            # cmd.setsockopt(zmq.SUBSCRIBE, "all_nodes")
            cmd.setsockopt(zmq.SUBSCRIBE, args.node_name)
        else:
            cmd.setsockopt(zmq.SUBSCRIBE, "")
        cmd_stream = zmqstream.ZMQStream(cmd)
        cmd_stream.on_recv(cmd_message)

        def report_status():
            pub.send_multipart([args.node_name, json_cmd('up')])

        rs = PeriodicCallback(report_status, 3000)
        rs.start()

        ioloop.IOLoop.instance().start()

