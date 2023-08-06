# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# See the COPYING file for license information.
#
# Copyright (c) 2006 Guillaume Chazarain <guichaz@gmail.com>

import asyncore
import errno
import os
import readline # Just to say we want to use it with raw_input
import signal
import socket
import subprocess
import sys
import tempfile
import termios
from threading import Thread, Event, Lock

from polysh import dispatchers, remote_dispatcher
from polysh.console import console_output, set_last_status_length
from polysh import completion

class input_buffer(object):
    """The shared input buffer between the main thread and the stdin thread"""
    def __init__(self):
        self.lock = Lock()
        self.buf = ''

    def add(self, data):
        """Add data to the buffer"""
        self.lock.acquire()
        try:
            self.buf += data
        finally:
            self.lock.release()

    def get(self):
        """Get the content of the buffer"""
        self.lock.acquire()
        try:
            data = self.buf
            if data:
                self.buf = ''
                return data
        finally:
            self.lock.release()

def process_input_buffer():
    """Send the content of the input buffer to all remote processes, this must
    be called in the main thread"""
    from polysh.control_commands_helpers import handle_control_command
    data = the_stdin_thread.input_buffer.get()
    remote_dispatcher.log('> ' + data)

    if data.startswith(':'):
        handle_control_command(data[1:-1])
        return

    if data.startswith('!'):
        try:
            retcode = subprocess.call(data[1:], shell=True)
        except OSError, e:
            if e.errno == errno.EINTR:
                console_output('Child was interrupted\n')
                retcode = 0
            else:
                raise
        if retcode > 128 and retcode <= 192:
            retcode = 128 - retcode
        if retcode > 0:
            console_output('Child returned %d\n' % retcode)
        elif retcode < 0:
            console_output('Child was terminated by signal %d\n' % -retcode)
        return

    for r in dispatchers.all_instances():
        try:
            r.dispatch_command(data)
        except asyncore.ExitNow, e:
            raise e
        except Exception, msg:
            console_output('%s for %s, disconnecting\n' % (msg, r.display_name))
            r.disconnect()
        else:
            if r.enabled and r.state is remote_dispatcher.STATE_IDLE:
                r.change_state(remote_dispatcher.STATE_RUNNING)

# The stdin thread uses a synchronous (with ACK) socket to communicate with the
# main thread, which is most of the time waiting in the poll() loop.
# Socket character protocol:
# d: there is new data to send
# A: ACK, same reply for every message, communications are synchronous, so the
# stdin thread sends a character to the socket, the main thread processes it,
# sends the ACK, and the stdin thread can go on.

class socket_notification_reader(asyncore.dispatcher):
    """The socket reader in the main thread"""
    def __init__(self):
        asyncore.dispatcher.__init__(self, the_stdin_thread.socket_read)

    def _do(self, c):
        if c == 'd':
            process_input_buffer()
        else:
            raise Exception, 'Unknown code: %s' % (c)

    def handle_read(self):
        """Handle all the available character commands in the socket"""
        while True:
            try:
                c = self.recv(1)
            except socket.error, why:
                if why[0] == errno.EWOULDBLOCK:
                    return
                else:
                    raise
            else:
                self._do(c)
                self.socket.setblocking(True)
                self.send('A')
                self.socket.setblocking(False)

    def writable(self):
        """Our writes are blocking"""
        return False

def write_main_socket(c):
    """Synchronous write to the main socket, wait for ACK"""
    the_stdin_thread.socket_write.send(c)
    while True:
        try:
            the_stdin_thread.socket_write.recv(1)
        except socket.error, e:
            if e[0] != errno.EINTR:
                raise
        else:
            break

#
# This file descriptor is used to interrupt readline in raw_input().
# /dev/null is not enough as it does not get out of a 'Ctrl-R' reverse-i-search.
# A Ctrl-C seems to make raw_input() return in all cases, and avoids printing
# a newline
tempfile_fd, tempfile_name = tempfile.mkstemp()
os.remove(tempfile_name)
os.write(tempfile_fd, chr(3))

def get_stdin_pid(cached_result=None):
    """Try to get the PID of the stdin thread, otherwise get the whole process
    ID"""
    if cached_result is None:
        try:
            tasks = os.listdir('/proc/self/task')
        except OSError, e:
            if e.errno != errno.ENOENT:
                raise
            cached_result = os.getpid()
        else:
            tasks.remove(str(os.getpid()))
            assert len(tasks) == 1
            cached_result = int(tasks[0])
    return cached_result

def interrupt_stdin_thread():
    """The stdin thread may be in raw_input(), get out of it"""
    dupped_stdin = os.dup(0) # Backup the stdin fd
    assert not the_stdin_thread.interrupt_asked # Sanity check
    the_stdin_thread.interrupt_asked = True # Not user triggered
    os.lseek(tempfile_fd, 0, 0) # Rewind in the temp file
    os.dup2(tempfile_fd, 0) # This will make raw_input() return
    pid = get_stdin_pid()
    os.kill(pid, signal.SIGWINCH) # Try harder to wake up raw_input()
    the_stdin_thread.out_of_raw_input.wait() # Wait for this return
    the_stdin_thread.interrupt_asked = False # Restore sanity
    os.dup2(dupped_stdin, 0) # Restore stdin
    os.close(dupped_stdin) # Cleanup

echo_enabled = True
def set_echo(echo):
    global echo_enabled
    if echo != echo_enabled:
        fd = sys.stdin.fileno()
        attr = termios.tcgetattr(fd)
        if echo:
            attr[3] |= termios.ECHO
        else:
            attr[3] &= ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, attr)
        echo_enabled = echo

class stdin_thread(Thread):
    """The stdin thread, used to call raw_input()"""
    def __init__(self):
        Thread.__init__(self, name='stdin thread')
        completion.install_completion_handler()

    @staticmethod
    def activate(interactive):
        """Activate the thread at initialization time"""
        the_stdin_thread.input_buffer = input_buffer()
        if interactive:
            the_stdin_thread.raw_input_wanted = Event()
            the_stdin_thread.in_raw_input = Event()
            the_stdin_thread.out_of_raw_input = Event()
            the_stdin_thread.out_of_raw_input.set()
            s1, s2 = socket.socketpair()
            the_stdin_thread.socket_read, the_stdin_thread.socket_write = s1, s2
            the_stdin_thread.interrupt_asked = False
            the_stdin_thread.setDaemon(True)
            the_stdin_thread.start()
            the_stdin_thread.socket_notification = socket_notification_reader()
            the_stdin_thread.prepend_text = None
            readline.set_pre_input_hook(the_stdin_thread.prepend_previous_text)

    def prepend_previous_text(self):
        if self.prepend_text:
            readline.insert_text(self.prepend_text)
            readline.redisplay()
            self.prepend_text = None

    def want_raw_input(self):
        nr, total = dispatchers.count_awaited_processes()
        if nr:
            prompt = 'waiting (%d/%d)> ' % (nr, total)
        else:
            prompt = 'ready (%d)> ' % total
        self.prompt = prompt
        set_last_status_length(len(prompt))
        self.raw_input_wanted.set()
        while not self.in_raw_input.isSet():
            self.socket_notification.handle_read()
            self.in_raw_input.wait(0.1)
        self.raw_input_wanted.clear()

    def no_raw_input(self):
        if not self.out_of_raw_input.isSet():
            interrupt_stdin_thread()

    # Beware of races
    def run(self):
        while True:
            self.raw_input_wanted.wait()
            self.out_of_raw_input.set()
            self.in_raw_input.set()
            self.out_of_raw_input.clear()
            cmd = None
            try:
                cmd = raw_input(self.prompt)
            except EOFError:
                if self.interrupt_asked:
                    cmd = readline.get_line_buffer()
                else:
                    cmd = chr(4) # Ctrl-D
            if self.interrupt_asked:
                self.prepend_text = cmd
                cmd = None
            self.in_raw_input.clear()
            self.out_of_raw_input.set()
            if cmd:
                if echo_enabled:
                    completion.add_to_history(cmd)
                else:
                    completion.remove_last_history_item()
            set_echo(True)
            if cmd is not None:
                self.input_buffer.add(cmd + '\n')
                write_main_socket('d')

the_stdin_thread = stdin_thread()
