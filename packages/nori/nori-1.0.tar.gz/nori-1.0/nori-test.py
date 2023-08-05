#!/usr/bin/env python

from pprint import pprint as pp

import sys
import os
import shlex
import subprocess
import time
import socket

sys.path.insert(0, os.path.dirname(__file__) + os.path.sep + '..')
import nori


#nori.pyversion_check(-1, -1)
#nori.pyversion_check(8, -1)
#nori.pyversion_check(-1, 4)
#nori.pyversion_check(8, 4)
#nori.pyversion_check(7, -1)
#nori.pyversion_check(6, -1)
#nori.pyversion_check(-1, 2)
#nori.pyversion_check(-1, 3)

#print(nori.script_name)
#print(nori.script_shortname)
#print(nori.running_as_email)
#print(nori.default_config_files)

#print(nori.char_name(' '))
#print(nori.char_name('\t'))
#print(nori.char_name('\n'))
#print(nori.char_name('\r'))
#print(nori.char_name('\f'))
#print(nori.char_name('\v'))
#print(nori.char_name('\b'))
#print(nori.char_name('\a'))
#print(nori.char_name('x'))

#print(nori.type_list_string(nori.STRING_TYPES))
#print(nori.type_list_string(nori.STRINGISH_TYPES))
#print(nori.type_list_string())
#print(nori.type_list_string(5))

#print(nori.scalar_to_tuple(5))
#print(nori.scalar_to_tuple('adsf'))
#print(nori.scalar_to_tuple(()))
#print(nori.scalar_to_tuple([]))
#print(nori.scalar_to_tuple([5]))
#print(nori.scalar_to_tuple((5,)))

#print(nori.scalar_to_list(5))
#print(nori.scalar_to_list('adsf'))
#print(nori.scalar_to_list(()))
#print(nori.scalar_to_list([]))
#print(nori.scalar_to_list([5]))
#print(nori.scalar_to_list((5,)))

#print(nori.re_repl_escape(''))import
#print(nori.re_repl_escape('adsf'))
#print(nori.re_repl_escape('a\na'))
#print(nori.re_repl_escape('a\\na'))
#print(nori.re_repl_escape('\\1'))

#print(nori.str_to_bool(''))
#print(nori.str_to_bool('true'))
#print(nori.str_to_bool('on'))
#print(nori.str_to_bool('yes'))
#print(nori.str_to_bool('True'))
#print(nori.str_to_bool('On'))
#print(nori.str_to_bool('Yes'))
#print(nori.str_to_bool('1'))
#print(nori.str_to_bool('false'))
#print(nori.str_to_bool('off'))
#print(nori.str_to_bool('no'))
#print(nori.str_to_bool('False'))
#print(nori.str_to_bool('Off'))
#print(nori.str_to_bool('No'))
#print(nori.str_to_bool('0'))
#print(nori.str_to_bool('asdfads'))

#print(nori.is_legal_identifier(''))
#print(nori.is_legal_identifier('a'))
#print(nori.is_legal_identifier('_'))
#print(nori.is_legal_identifier('#'))
#print(nori.is_legal_identifier('aA'))
#print(nori.is_legal_identifier('_A'))
#print(nori.is_legal_identifier('#A'))
#print(nori.is_legal_identifier('AA'))
#print(nori.is_legal_identifier('A$'))

#print(nori.file_access_const('f'))
#print(nori.file_access_const('r'))
#print(nori.file_access_const('w'))
#print(nori.file_access_const('x'))
#print(nori.file_access_const('F'))

#print(nori.file_type_info('-'))
#print(nori.file_type_info('f'))
#print(nori.file_type_info('d'))
#print(nori.file_type_info('l'))
#print(nori.file_type_info('s'))
#print(nori.file_type_info('p'))
#print(nori.file_type_info('b'))
#print(nori.file_type_info('c'))
#print(nori.file_type_info('w'))


def run_mode_hook():
    #try:
        #open('/nonexistent')
    #except (OSError, IOError) as e:
        #print(nori.render_io_exception(e))
        #print(nori.file_error_handler(
        #    e, 'foo', 'fiiile', '/nonexistent', must_exist=True,
        #    use_logger=False, warn_only=False
        #))
        #print(nori.file_error_handler(
        #    e, 'foo', 'fiiile', '/nonexistent', must_exist=False,
        #    use_logger=False, warn_only=False
        #))
        #print(nori.file_error_handler(
        #    e, 'foo', 'fiiile', '/nonexistent', must_exist=True,
        #    use_logger=False, warn_only=False
        #))
        #print(nori.file_error_handler(
        #    e, 'foo', 'fiiile', '/nonexistent', must_exist=True,
        #    use_logger=True, warn_only=False
        #))
        #print(nori.file_error_handler(
        #    e, 'foo', 'fiiile', '/nonexistent', must_exist=True,
        #    use_logger=False, warn_only=True
        #))
        #print(nori.file_error_handler(
        #    e, 'foo', 'fiiile', '/nonexistent', must_exist=True,
        #    use_logger=True, warn_only=True
        #))

    #print(nori.check_file_type(
    #    '/vmlinuz', 'kernel', type_char='l', follow_links=True,
    #    must_exist=True, use_logger=False, warn_only=False, exit_val=47
    #))
    #print(nori.check_file_type(
    #    '/vmlinuz', 'kernel', type_char='l', follow_links=False,
    #    must_exist=True, use_logger=False, warn_only=False, exit_val=47
    #))
    #print(nori.check_file_type(
    #    '/vvv', 'kernel', type_char='l', follow_links=False,
    #    must_exist=True, use_logger=False, warn_only=False, exit_val=47
    #))
    #print(nori.check_file_type(
    #    '/vvv', 'kernel', type_char='l', follow_links=False,
    #    must_exist=False, use_logger=False, warn_only=False, exit_val=47
    #))
    #print(nori.check_file_type(
    #    '/vmlinuz', 'kernel', type_char='g', follow_links=False,
    #    must_exist=True, use_logger=False, warn_only=False, exit_val=47
    #))
    #print(nori.check_file_type(
    #    '/vmlinuz', 'kernel', type_char='f', follow_links=True,
    #    must_exist=True, use_logger=False, warn_only=False, exit_val=47
    #))
    #print(nori.check_file_type(
    #    '/vmlinuz', 'kernel', type_char='s', follow_links=True,
    #    must_exist=True, use_logger=False, warn_only=False, exit_val=47
    #))
    #print(nori.check_file_type(
    #    '/vmlinuz', 'kernel', type_char='spf', follow_links=True,
    #    must_exist=True, use_logger=False, warn_only=False, exit_val=47
    #))
    #print(nori.check_file_type(
    #    '/vmlinuz', 'kernel', type_char='spd', follow_links=True,
    #    must_exist=True, use_logger=False, warn_only=False, exit_val=47
    #))
    #print(nori.check_file_type(
    #    '/vmlinuz', 'kernel', type_char='sd', follow_links=True,
    #    must_exist=True, use_logger=False, warn_only=False, exit_val=47
    #))

    #print(nori.check_file_access(
    #    '/vmlinuz', 'kernel', file_rwx='g', use_logger=False,
    #    warn_only=False, exit_val=47
    #))
    #print(nori.check_file_access(
    #    '/vmlinuz', 'kernel', file_rwx='f', use_logger=False,
    #    warn_only=True, exit_val=47
    #))
    #print(nori.check_file_access(
    #    '/vmlinuz', 'kernel', file_rwx='r', use_logger=False,
    #    warn_only=True, exit_val=47
    #))
    #print(nori.check_file_access(
    #    '/vmlinuz', 'kernel', file_rwx='w', use_logger=False,
    #    warn_only=True, exit_val=47
    #))
    #print(nori.check_file_access(
    #    '/vmlinuz', 'kernel', file_rwx='x', use_logger=False,
    #    warn_only=True, exit_val=47
    #))
    #print(nori.check_file_access(
    #    '/vvv', 'kernel', file_rwx='f', use_logger=False,
    #    warn_only=True, exit_val=47
    #))
    #print(nori.check_file_access(
    #    '/tmp', 'temp', file_rwx='r', use_logger=False,
    #    warn_only=True, exit_val=47
    #))
    #print(nori.check_file_access(
    #    '/tmp', 'temp', file_rwx='w', use_logger=False,
    #    warn_only=True, exit_val=47
    #))
    #print(nori.check_file_access(
    #    '/tmp', 'temp', file_rwx='x', use_logger=False,
    #    warn_only=True, exit_val=47
    #))
    #print(nori.check_file_access(
    #    '/root', 'root', file_rwx='x', use_logger=False,
    #    warn_only=True, exit_val=47
    #))
    #print(nori.check_file_access(
    #    '/root', 'root', file_rwx='', use_logger=False,
    #    warn_only=True, exit_val=47
    #))

    #print(nori.check_filedir_create(
    #    '/root', 'root', create_type='g', need_rotation=False,
    #    use_logger=False, warn_only=True, exit_val=47
    #))
    #print(nori.check_filedir_create(
    #    '/root', 'root', create_type='f', need_rotation=False,
    #    use_logger=False, warn_only=True, exit_val=47
    #))
    #print(nori.check_filedir_create(
    #    '/root', 'root', create_type='d', need_rotation=False,
    #    use_logger=False, warn_only=True, exit_val=47
    #))
    #print(nori.check_filedir_create(
    #    '/tmp', 'temp', create_type='d', need_rotation=False,
    #    use_logger=False, warn_only=True, exit_val=47
    #))
    #print(nori.check_filedir_create(
    #    '/asdf', 'asdf', create_type='d', need_rotation=False,
    #    use_logger=False, warn_only=True, exit_val=47
    #))
    #print(nori.check_filedir_create(
    #    '/tmp/asdf', 'tmpasdf', create_type='d', need_rotation=False,
    #    use_logger=False, warn_only=True, exit_val=47
    #))
    #print(nori.check_filedir_create(
    #    '/var/log/syslog/foo', 'vlsf', create_type='d', need_rotation=False,
    #    use_logger=False, warn_only=True, exit_val=47
    #))
    #print(nori.check_filedir_create(
    #    '/root/foo', 'rootfoo', create_type='d', need_rotation=False,
    #    use_logger=False, warn_only=True, exit_val=47
    #))
    #print(nori.check_filedir_create(
    #    '/root/foo', 'rootfoo', create_type='d', need_rotation=True,
    #    use_logger=False, warn_only=True, exit_val=47
    #))

    #print(nori.fix_path(''))
    #print(nori.fix_path('~'))
    #print(nori.fix_path('~root'))
    #print(nori.fix_path('~root/asdfg'))
    #print(nori.fix_path('/tmp/~'))
    #print(nori.fix_path('/tmp/~sgsgfs'))

    #print(nori.filemode(0o777))
    #print(nori.filemode(0o773))
    #print(nori.filemode(0o775))
    #print(nori.filemode(0o776))
    #print(nori.filemode(0o737))
    #print(nori.filemode(0o757))
    #print(nori.filemode(0o767))
    #print(nori.filemode(0o377))
    #print(nori.filemode(0o577))
    #print(nori.filemode(0o677))
    #print(nori.filemode(0o1777))
    #print(nori.filemode(0o2777))
    #print(nori.filemode(0o4777))
    #print(nori.filemode(0o2707))
    #print(nori.filemode(0o4077))

    #print(nori.get_file_metadata('/asdf'))
    #print(nori.get_file_metadata('/srv'))
    #print(nori.get_file_metadata('/tmp'))
    #print(nori.get_file_metadata('/vmlinuz'))
    #print(nori.get_file_metadata('/var/log/syslog'))
    #print(nori.get_file_metadata('/dev/null'))
    #print(nori.get_file_metadata('/dev/sda'))

    #print(nori.file_newer_than('/tmp', 1))
    #nori.touch_file('/tmp', 'temp')
    #print(nori.file_newer_than('/tmp', 1))

    #print(nori.parentdir('//'))                   # /
    #print(nori.parentdir('//foo'))                # /
    #print(nori.parentdir('//foo//'))              # /
    #print(nori.parentdir('//foo//bar'))           # //foo
    #print(nori.parentdir('//foo//bar//'))         # //foo
    #print(nori.parentdir('//foo//bar//baz'))      # //foo//bar
    #print(nori.parentdir('//foo//bar//baz//'))    # //foo//bar
    #print(nori.parentdir('.'))                    # ..
    #print(nori.parentdir('.//'))                  # ..
    #print(nori.parentdir('.//foo'))               # .
    #print(nori.parentdir('.//foo//'))             # .
    #print(nori.parentdir('.//foo//bar'))          # .//foo
    #print(nori.parentdir('.//foo//bar//'))        # .//foo
    #print(nori.parentdir('.//foo//bar//baz'))     # .//foo//bar
    #print(nori.parentdir('.//foo//bar//baz//'))   # .//foo//bar
    #print(nori.parentdir('..'))                   # ../..
    #print(nori.parentdir('..//'))                 # ../..
    #print(nori.parentdir('..//foo'))              # ..
    #print(nori.parentdir('..//foo//'))            # ..
    #print(nori.parentdir('..//foo//bar'))         # ..//foo
    #print(nori.parentdir('..//foo//bar//'))       # ..//foo
    #print(nori.parentdir('..//foo//bar//baz'))    # ..//foo//bar
    #print(nori.parentdir('..//foo//bar//baz//'))  # ..//foo//bar
    #print(nori.parentdir('foo'))                  # .
    #print(nori.parentdir('foo//'))                # .
    #print(nori.parentdir('foo//bar'))             # foo
    #print(nori.parentdir('foo//bar//'))           # foo
    #print(nori.parentdir('foo//bar//baz'))        # foo//bar
    #print(nori.parentdir('foo//bar//baz//'))      # foo//bar

    #print(nori.open_create_only('/tmp/foo'))
    #print(nori.open_create_only('/tmp/foo'))
    #print(nori.rm_rf('/tmp/foo', 'tmpfoo'))

    #print(nori.get_file_metadata('/tmp/foo'))
    #print(nori.touch_file('/tmp/foo', 'tmpfoo'))
    #print(nori.get_file_metadata('/tmp/foo'))
    #print(nori.touch_file('/tmp/foo', 'tmpfoo'))
    #print(nori.rm_rf('/tmp/foo', 'tmpfoo'))
    #print(nori.touch_file('/root/asdf', 'rootadsf'))
    #print(nori.get_file_metadata('/tmp'))
    #print(nori.touch_file('/tmp', 'tmp'))
    #print(nori.get_file_metadata('/tmp'))
    #print(nori.touch_file('/tmp', 'tmp'))

    #print(os.mkdir('/tmp/foo'))
    #print(nori.touch_file('/tmp/foo/bar', 'tmpfoobar'))
    #print(nori.get_file_metadata('/tmp/foo'))
    #print(nori.get_file_metadata('/tmp/foo/bar'))
    #print(nori.rm_rf('/tmp/foo', 'tmpfoo'))
    #print(nori.rm_rf('/tmp/foo', 'tmpfoo'))
    #print(nori.rm_rf('/tmp/foo', 'tmpfoo', must_exist=True))

    #nori.rotate_num_files('/root', 'asdf', '=', 'a')
    # test with .gz, in cwd, in other dir

    #nori.prune_num_files('/root', 'asdf', '=', 'a', 1, 1)
    # test with .gz, in cwd, in other dir

    #print(nori.pps('adsf'))

    #nori.err_exit('adsfasdafg\nwhgsfhg', 47)

    #nori.logging_stop_syslog()
    #nori.logging_stop_stdouterr()
    #nori.core.status_logger.info('asdf1')
    #nori.core.status_logger.debug('asdf2')
    #nori.logging_start_syslog()
    #nori.logging_start_stdouterr()
    #nori.core.alert_logger.error('asdf3')
    #nori.core.alert_logger.debug('asdf4')
    #nori.core.email_logger.error('asdf5a')
    #nori.logging_email_stop_logging()
    #nori.core.email_logger.error('asdf5b')
    #nori.logging_email_start_logging()
    #nori.core.output_logger.info('asdf6')
    #nori.core.output_log_fo.write('asdf7\n')
    #nori.core.output_log_fo.flush()

    #nori.end_logging_output()
    #nori.core.output_log_fo.write('asdf7\n')

    #nori.generic_error_handler(ValueError('foo\nbar'), 'broken')
    #nori.generic_error_handler(None, 'broken')
    #nori.generic_error_handler(ValueError('foo\nbar'), 'broken',
    #                           lambda x: x.message.capitalize())
    #nori.generic_error_handler(ValueError('foo\nbar'), 'broken',
    #                           lambda x: x.message.capitalize(),
    #                           warn_only=True)
    #nori.generic_error_handler(None, 'broken', exit_val=47)
    #print(nori.generic_error_handler(None, 'broken', warn_only=True))
    #nori.generic_error_handler(None, 'broken1', use_logger=None)
    #def foo(x, y):
    #    print('a {0} b {1}'.format(x, y))
    #nori.generic_error_handler(None, 'broken2', use_logger=foo)
    #nori.generic_error_handler(None, 'broken3', use_logger=True)
    #nori.generic_error_handler(None, 'broken4', use_logger=False)
    #nori.generic_error_handler(None, 'broken5', use_logger=True,
    #                           exit_val=None)
    #nori.generic_error_handler(None, 'broken6', use_logger=False,
    #                           exit_val=None)
    #nori.generic_error_handler(None, 'broken w1', use_logger=None,
    #                           warn_only=True)
    #nori.generic_error_handler(None, 'broken w2', use_logger=foo,
    #                           warn_only=True)
    #nori.generic_error_handler(None, 'broken w3', use_logger=True,
    #                           warn_only=True)
    #nori.generic_error_handler(None, 'broken w4', use_logger=False,
    #                           warn_only=True)
    #nori.generic_error_handler(None, 'broken w5', use_logger=True,
    #                           warn_only=True, exit_val=None)
    #nori.generic_error_handler(None, 'broken w6', use_logger=False,
    #                           warn_only=True, exit_val=None)

    #f1 = open('core.py')
    #f2 = open('ssh.py')
    #nori.multi_fan_out(
    #    [
    #        (f1, [sys.stdout, sys.stderr]),
    #        (f1, [sys.stdout, sys.stderr])
    #    ]
    #)
    #f1 = os.open('core.py', os.O_RDONLY)
    #f2 = os.open('ssh.py', os.O_RDONLY)
    #nori.multi_fan_out(
    #    [
    #        (f1, [sys.stdout, sys.stderr]),
    #        (f2, [sys.stdout, sys.stderr])
    #    ]
    #)
    #o1 = os.open('/dev/fd/1', os.O_WRONLY|os.O_APPEND)
    #o2 = os.open('/dev/fd/2', os.O_WRONLY)
    #nori.multi_fan_out(
    #    [
    #        (f1, [o1, o2]),
    #        (f1, [o1, o2])
    #    ]
    #)

    #try:
    #    nori.run_command(
    #        'asdf', shlex.split('adsf'), stdin=None, stdout='devnull',
    #        stderr=subprocess.STDOUT, bg=False, atexit_reg=True,
    #        env_add=None
    #    )
    #except (OSError, ValueError) as e:
    #    print(nori.render_command_exception(e))
    #nori.run_command(
    #    'asdf', shlex.split('adsf'), stdin=None, stdout='devnull',
    #    stderr=subprocess.STDOUT, bg=False, atexit_reg=True,
    #    env_add=None, use_logger=True, warn_only=False, exit_val=43
    #)
    #nori.run_command(
    #    'asdf', shlex.split('adsf'), stdin=None, stdout='devnull',
    #    stderr=subprocess.STDOUT, bg=False, atexit_reg=True,
    #    env_add=None, use_logger=False, warn_only=False, exit_val=43
    #)
    #nori.run_command(
    #    'asdf', shlex.split('adsf'), stdin=None, stdout='devnull',
    #    stderr=subprocess.STDOUT, bg=False, atexit_reg=True,
    #    env_add=None, use_logger=True, warn_only=True, exit_val=43
    #)
    #nori.run_command(
    #    'listing', shlex.split('ls -la /varadsf'), stdin=subprocess.PIPE,
    #    stdout='devnull', stderr=subprocess.STDOUT, bg=False,
    #    atexit_reg=True, env_add=None
    #)
    #nori.run_command(
    #    'listing', shlex.split('ls -la /varadsf'), stdin=None,
    #    stdout='devnull', stderr=subprocess.STDOUT, bg=False,
    #    atexit_reg=True, env_add=None
    #)
    #nori.run_command(
    #    'env', shlex.split('env'), stdin=None,
    #    stdout=[sys.stdout, sys.stderr], stderr=[sys.stdout, sys.stderr],
    #    bg=False, atexit_reg=True, env_add={'ZZZ':'4'}
    #)
    #print(nori.run_command(
    #    'listing', shlex.split('ls -la /varadsf'), stdin=None,
    #    stdout=[sys.stdout, sys.stderr], stderr=[sys.stdout, sys.stderr],
    #    bg=False, atexit_reg=True, env_add={'ZZZ':'4'}
    #))
    #print(nori.run_command(
    #   'env', shlex.split('env'), stdin=None,
    #    stdout=[sys.stdout, sys.stderr], stderr=[sys.stdout, sys.stderr],
    #    bg=False, atexit_reg=True, env_add={'ZZZ':'4'}, env={'Z':'5'}
    #))
    #p1 = nori.run_command(
    #    'listing', shlex.split('ls -la /varadsf'), stdin=None,
    #    stdout=[sys.stdout, sys.stderr], stderr=[sys.stdout, sys.stderr],
    #    bg=True, atexit_reg=False, env_add={'ZZZ':'4'}
    #)
    #p2 = nori.run_command(
    #    'env', shlex.split('env'), stdin=None,
    #    stdout=[sys.stdout, sys.stderr], stderr=[sys.stdout, sys.stderr],
    #    bg=True, atexit_reg=True, env_add={'ZZZ':'4'}, env={'Z':'5'}
    #)
    #p1.wait()
    #time.sleep(30)
    #p = nori.run_command(
    #    'sleep', shlex.split('/bin/sleep 60'), stdin=None,
    #    stdout=[sys.stdout, sys.stderr], stderr=[sys.stdout, sys.stderr],
    #    bg=True, atexit_reg=True, env_add={'ZZZ':'4'}, env={'Z':'5'}
    #)
    #p = nori.run_command(
    #    'listing', shlex.split('ls /var'), stdin=None,
    #    stdout=[sys.stdout, sys.stderr], stderr=[sys.stdout, sys.stderr],
    #    bg=True, atexit_reg=True, env_add={'ZZZ':'4'}, env={'Z':'5'}
    #)
    #p = nori.run_command(
    #    'listing', shlex.split('find /var'), stdin=None,
    #    stdout=[sys.stdout, sys.stderr], stderr=[sys.stdout, sys.stderr],
    #    bg=True, atexit_reg=True, daemon=False, env_add={'ZZZ':'4'}
    #)
    #time.sleep(3)
    #print(nori.kill_bg_command(p, 10))

    #nori.run_with_logging('listing', ['lsasdf', '/tmp'], True, True,
    #                      env_add={'PATH':'/bin/:/usr/bin/', 'A':'B'},
    #                      use_logger=True, warn_only=False, exit_val=42)
    #nori.run_with_logging('listing', ['lsasdf', '/tmp'], True, True,
    #                      env_add={'PATH':'/bin/:/usr/bin/', 'A':'B'},
    #                      use_logger=False, warn_only=False, exit_val=42)
    #nori.run_with_logging('listing', ['lsasdf', '/tmp'], True, True,
    #                      env_add={'PATH':'/bin/:/usr/bin/', 'A':'B'},
    #                      use_logger=True, warn_only=True, exit_val=42)
    #nori.run_with_logging('listing', ['ls', '/tmp'], True, True,
    #                      env_add={'PATH':'/bin/:/usr/bin/', 'A':'B'})
    #nori.run_with_logging('listing', ['ls', '/tmp', '/adsf'], True, True)
    #nori.run_with_logging('listing', ['ls', '/tmp', '/adsf'], True, False)
    #nori.run_with_logging('listing', ['ls', '/tmp', '/adsf'], False, True)
    #print(nori.run_with_logging('listing', ['ls', '/tmp', '/adsf'],
    #                            False, False))
    #print(nori.run_with_logging('listing', ['ls', '/tmp', '/adsf'],
    #                            False, False, True))
    #try:
    #    nori.run_with_logging('listing', ['find', '/'], True, True)
    #except IOError as e:
    #    print('adfasdhhhhjhhhhhhfasdfa')

    #print(nori.test_remote_port(
    #    'porrrrt', ('127.0.0.1', 22), ('127.0.0.1', 5555),
    #    timeout=5, use_logger=False, warn_only=False
    #))
    #print(nori.test_remote_port(
    #    'porrrrt', ('127.0.0.1', 82), ('127.0.0.1', 5556),
    #    timeout=5, use_logger=False, warn_only=True
    #))
    #print(nori.test_remote_port(
    #    'porrrrt', ('127.0.0.1', 22),
    #    timeout=5, use_logger=False, warn_only=False
    #))
    #print(nori.test_remote_port(
    #    'porrrrt', ('127.0.0.1', 82),
    #    timeout=5, use_logger=False, warn_only=True
    #))
    #print(nori.test_remote_port(
    #    'porrrrt', ('127.0.0.1', 82), ('127.0.0.1', 5556),
    #    timeout=5, use_logger=False, warn_only=False
    #))
    #print(nori.test_remote_port(
    #    'porrrrt', ('127.0.0.1', 82), ('127.0.0.1', 5556),
    #    timeout=5, use_logger=False, warn_only=False, exit_val=42
    #))

    #print(nori.config_settings['syslog_addr']['default'])
    #print(nori.config_settings['syslog_sock_type']['default'])

    #print(nori.setting_walk('alert_emails_host'))
    #print(nori.setting_walk(('alert_emails_host',)))
    #print(nori.setting_walk(('alert_emails_host',0)))
    #print(nori.setting_walk(('alert_emails_host',2)))

    #print(nori.setting_is_set('alert_emails_host'))
    #print(nori.setting_is_set(('alert_emails_host',)))
    #print(nori.setting_is_set(('alert_emails_host',0)))
    #print(nori.setting_is_set(('alert_emails_host',2)))

    #print(nori.setting_is_unset('alert_emails_host'))
    #print(nori.setting_is_unset(('alert_emails_host',)))
    #print(nori.setting_is_unset(('alert_emails_host',0)))
    #print(nori.setting_is_unset(('alert_emails_host',2)))

    #print(nori.setting_check_is_set('alert_emails_host'))
    #print(nori.setting_check_is_set(('alert_emails_host',)))
    #print(nori.setting_check_is_set(('alert_emails_host',0)))
    #print(nori.setting_check_is_set(('alert_emails_host',2)))

    #print(nori.setting_check_one_is_set(['alert_emails_host']))
    #print(nori.setting_check_one_is_set([('alert_emails_host', )]))
    #print(nori.setting_check_one_is_set([('alert_emails_host', 0)]))
    #print(nori.setting_check_one_is_set([('alert_emails_host', 2)]))
    #print(nori.setting_check_one_is_set(['alert_emails_host',
    #                                    ('alert_emails_host', 0)]))
    #print(nori.setting_check_one_is_set([('alert_emails_host', )]))
    #print(nori.setting_check_one_is_set([('alert_emails_host', 0)]))
    #print(nori.setting_check_one_is_set([('alert_emails_host', 2)]))
    #print(nori.setting_check_one_is_set([('alert_emails_host', 2),
    #      ('alert_emails_host', 0)]))

    #print(nori.setting_check_type(('alert_emails_host', 2),
    #                              nori.STRING_TYPES))
    #print(nori.setting_check_type(('alert_emails_host', 0),
    #                              nori.STRING_TYPES))
    #print(nori.setting_check_type(('alert_emails_host', 0),
    #                              nori.NUMBER_TYPES))
    #print(nori.setting_check_type(('alert_emails_host',0), int))
    #print(nori.setting_check_type(('alert_emails_host',0), 5))

    #print(nori.setting_check_not_empty(('alert_emails_host', 0)))
    #print(nori.setting_check_not_empty('alert_emails_hostasdf'))
    #print(nori.setting_check_not_empty('alert_emails_host'))

    #print(nori.setting_check_not_all_empty(['alert_emails_hostasdf']))
    #print(nori.setting_check_not_all_empty(['send_alert_emails']))
    #print(nori.setting_check_not_all_empty(['alert_emails_host',
    #                                        'alert_emails_to']))
    #print(nori.setting_check_not_all_empty(['alert_emails_host']))

    #print(nori.setting_check_len(['alert_emails_hostasdf'],
    #                                       1, 2))
    #print(nori.setting_check_len(['send_alert_emails'], 1, 2))
    #print(nori.setting_check_len('alert_emails_host', 1, 5))
    #print(nori.setting_check_len('alert_emails_host', None, 5))
    #print(nori.setting_check_len('alert_emails_host', 3, 3))
    #print(nori.setting_check_len('alert_emails_host', 1, 1))
    #print(nori.setting_check_len('alert_emails_host', None, None))
    #print(nori.setting_check_len('alert_emails_host', 1, 1))
    #print(nori.setting_check_len('alert_emails_host', 3, 2))
    #print(nori.setting_check_len('alert_emails_from', 1, 25))
    #print(nori.setting_check_len('alert_emails_from', None, 25))
    #print(nori.setting_check_len('alert_emails_from', 21, 25))
    #print(nori.setting_check_len('alert_emails_from', None, None))
    #print(nori.setting_check_len('alert_emails_from', 1, 1))

    #print(nori.setting_check_not_blank(('alert_emails_host', 0)))
    #print(nori.setting_check_not_blank('alert_emails_hostasdf'))
    #print(nori.setting_check_not_blank('send_alert_emails'))
    #print(nori.setting_check_not_blank('alert_emails_from'))
    #print(nori.setting_check_not_blank('alert_emails_from', True))

    #print(nori.setting_check_not_all_blank([('alert_emails_host', 0)]))
    #print(nori.setting_check_not_all_blank(['alert_emails_hostasdf']))
    #print(nori.setting_check_not_all_blank(['send_alert_emails']))
    #print(nori.setting_check_not_all_blank([('alert_emails_host', 0),
    #                                        'alert_emails_from']))
    #print(nori.setting_check_not_all_blank(['alert_emails_from']))
    #print(nori.setting_check_not_all_blank(['alert_emails_from'], True))

    #print(nori.setting_check_no_blanks(('alert_emails_host', 0)))
    #print(nori.setting_check_no_blanks('alert_emails_hostasdf'))
    #print(nori.setting_check_no_blanks('alert_emails_host'))
    #print(nori.setting_check_no_blanks('alert_emails_to'))
    #print(nori.setting_check_no_blanks('alert_emails_to', True))
    #print(nori.setting_check_no_blanks('alert_emails_to', False, False))
    #print(nori.setting_check_no_blanks('alert_emails_to', True, False))

    #print(nori.setting_check_kwargs('alert_emails_to'))
    #print(nori.setting_check_kwargs('alert_emails_to', True))

    #print(nori.setting_check_no_char('alert_emails_hostasdf', '#'))
    #print(nori.setting_check_no_char('alert_emails_host', '#'))
    #print(nori.setting_check_no_char('alert_emails_from', '@'))
    #print(nori.setting_check_no_char('alert_emails_from', '@', True))
    #print(nori.setting_check_no_char('alert_emails_from', '9'))

    #print(nori.setting_check_list('mysqlstuff_protocoladsf',
    #      ['tcp', 'socket']))
    #print(nori.setting_check_list('mysqlstuff_use_ssh_tunnel',
    #      ['tcp', 'socket']))
    #print(nori.setting_check_list('mysqlstuff_protocol',
    #                              ['tcp', 'socket']))

    #print(nori.setting_check_num('mysqlstuff_protocoladsf', 0, 5))
    #print(nori.setting_check_num('mysqlstuff_use_ssh_tunnel', 0, 5))
    #print(nori.setting_check_num('foo_ssh_port', 1, 5555))
    #print(nori.setting_check_num('foo_ssh_port', 22, 5555))
    #print(nori.setting_check_num('foo_ssh_port', 25, 5555))
    #print(nori.setting_check_num('foo_ssh_port', 1, 5555))
    #print(nori.setting_check_num('foo_ssh_port', 1, 22))
    #print(nori.setting_check_num('foo_ssh_port', 1, 20))

    #print(nori.setting_check_file_type('output_logasdf', 'f'))
    #print(nori.setting_check_file_type('output_log', 'f'))
    #print(nori.setting_check_file_type('output_log', 'd'))
    #print(nori.setting_check_file_type('foo_ssh_key_file', 'f', False))
    #print(nori.setting_check_file_type('foo_ssh_key_file', 'f'))

    #print(nori.setting_check_file_access('output_logasdf', 'r'))
    #print(nori.setting_check_file_access('output_log', 'r'))
    #print(nori.setting_check_file_access('output_log', 'x'))

    #print(nori.setting_check_file_read('output_logasdf'))
    #print(nori.setting_check_file_read('output_log'))
    #print(nori.setting_check_file_read('foo_ssh_key_file'))

    #print(nori.setting_check_file_rw('output_logasdf'))
    #print(nori.setting_check_file_rw('output_log'))
    #print(nori.setting_check_file_rw('foo_ssh_key_file'))

    #print(nori.setting_check_dir_search('output_logasdf'))
    #print(nori.setting_check_dir_search('output_log'))
    #print(nori.setting_check_dir_search('test'))

    #print(nori.setting_check_dir_full('output_logasdf'))
    #print(nori.setting_check_dir_full('output_log'))
    #print(nori.setting_check_dir_full('test'))

    #print(nori.setting_check_filedir_create('output_logasdf'))
    #print(nori.setting_check_filedir_create('output_log'))
    #print(nori.setting_check_filedir_create('test'))
    #print(nori.setting_check_filedir_create('test', 'd'))

    #time.sleep(60)
    #time.sleep(3)

    #pp(sys.modules)

    #pp(nori.config_modules)
    #pp(nori.cfg)
    #pp(nori.config_settings)

    #print(os.environ['PATH'])
    #current_umask = os.umask(0)
    #os.umask(current_umask)
    #print(oct(current_umask))

    #print(nori.core.start_time)
    #print(time.strftime(nori.FULL_DATE_FORMAT, time.localtime()))
    #time.sleep(5)
    #print(nori.core.start_time)
    #print(time.strftime(nori.FULL_DATE_FORMAT, time.localtime()))

    #print(s.get_cmd())

    #print(s.get_tunnel_cmd())

    #print(nori.SSH.atexit_close_tunnels_registered)
    #print(nori.SSH.open_tunnels)
    #s.open_tunnel('footunnel', atexit_reg=True, use_logger=True,
    #              warn_only=False, exit_val=43)
    #print(s.open_tunnel('footunnel', atexit_reg=True, use_logger=True,
    #                    warn_only=True, exit_val=43))
    #print(s2.open_tunnel('bartunnel', atexit_reg=True, use_logger=True,
    #                     warn_only=True, exit_val=43))
    #print(nori.SSH.atexit_close_tunnels_registered)
    #print(nori.SSH.open_tunnels)

    ######## MySQL ########

    #pp(m._conn_args)

    #print(m.err_use_logger,
    #      m.err_warn_only,
    #      m.err_no_exit,
    #      m.warn_use_logger,
    #      m.warn_warn_only,
    #      m.warn_no_exit)
    #m.save_err_warn()
    #m.err_use_logger = not m.err_use_logger
    #m.err_warn_only = not m.err_warn_only
    #m.err_no_exit = not m.err_no_exit
    #m.warn_use_logger = not m.warn_use_logger
    #m.warn_warn_only = not m.warn_warn_only
    #m.warn_no_exit = not m.warn_no_exit
    #print(m.err_use_logger,
    #      m.err_warn_only,
    #      m.err_no_exit,
    #      m.warn_use_logger,
    #      m.warn_warn_only,
    #      m.warn_no_exit)
    #m.restore_err_warn()
    #print(m.err_use_logger,
    #      m.err_warn_only,
    #      m.err_no_exit,
    #      m.warn_use_logger,
    #      m.warn_warn_only,
    #      m.warn_no_exit)

    #m.err_use_logger = not m.err_use_logger
    #m.err_warn_only = not m.err_warn_only
    #m.err_no_exit = not m.err_no_exit

    #print(m.connect())
    #m.connect()

    #print('#' * 76)

    #pp(m.cursor())
    #pp(m.cur)

    #m.cursor()
    #c = m.cursor(False)

    #print('#' * 76)

    #m._SUPPORTED.remove('autocommit')

    #print(m.autocommit(None))
    #print(m.autocommit(True))
    #print(m.autocommit(None))
    #print(m.autocommit(False))
    #print(m.autocommit(None))
    #return

    #print('FA:' + str(m._fake_autocommit))

    #print(m.execute(None, 'show dastabases', has_results=True))

    #print(m.execute(None, 'show databases', has_results=True))
    #for i in range(1, 10):
    #    print(m.fetchone(None))
    #for i in range(1, 10):
    #    print(m.fetchmany(None, 2))
    #print(m.fetchall(None))
    #f = lambda: m.fetchone_generator(None)
    #for row in f():
    #    print(row)

    #i = 0
    #d = {}
    #while True:
    #    d[i] = (m.fetchone(None))
    #    print(d)
    #    if d[i][1] is None:
    #        break
    #    i += 1
    #m.close()
    #print(d)

    #print(m.execute(None, 'select * from user where user=%s', ['root'],
    #                has_results=True))
    #print(m.fetchall(None))
    #print(m.execute(
    #    None,
    #    "update user set password='111111111' where user=%s",
    #    ['root']
    #))
    #print(m.executemany(
    #    None,
    #    "update user set password=%s where user=%s",
    #    [['4444444', 'root'], ['22222222222', 'test']]
    #))
    #print(m.execute(None, 'select * from user', has_results=True))
    #print(m.fetchall(None))
    #print(m.executemany(None, 'select * from user', [[]], has_results=True))
    #print(m.fetchall(None))

    #print(m.commit())
    #print(m.rollback())

    #print(m.executemany(None, 'select * from user where user=%s',
    #                    [['root'], ['test']],
    #                    has_results=True))
    #print(m.fetchall(None))

    #print(m.execute(c, 'show tables', has_results=True))
    #print(m.fetchall(c))

    #print(m.get_db_list(None))

    #print(m.change_db(None, 'mysql'))
    #print(m.execute(None, 'select * from user where user=%s', ['root'],
    #                has_results=True))
    #print(m.fetchall(None))

    #print(m.nextset(None))
    #print(m.setinputsizes(None, [4, 5]))
    #print(m.setoutputsize(None, 400))

    #print('#' * 76)

    #m.close_cursor(c)
    #m.close_cursor(c)
    #m.close_cursor()
    #m.close_cursor()

    #print(m.get_db_list(None))

    #print('#' * 76)

    #m.close()
    #m.close()

    ######## PostgreSQL ########

    #pp(p._conn_args)

    #print(p.err_use_logger,
    #      p.err_warn_only,
    #      p.err_no_exit,
    #      p.warn_use_logger,
    #      p.warn_warn_only,
    #      p.warn_no_exit)
    #p.save_err_warn()
    #p.err_use_logger = not p.err_use_logger
    #p.err_warn_only = not p.err_warn_only
    #p.err_no_exit = not p.err_no_exit
    #p.warn_use_logger = not p.warn_use_logger
    #p.warn_warn_only = not p.warn_warn_only
    #p.warn_no_exit = not p.warn_no_exit
    #print(p.err_use_logger,
    #      p.err_warn_only,
    #      p.err_no_exit,
    #      p.warn_use_logger,
    #      p.warn_warn_only,
    #      p.warn_no_exit)
    #p.restore_err_warn()
    #print(p.err_use_logger,
    #      p.err_warn_only,
    #      p.err_no_exit,
    #      p.warn_use_logger,
    #      p.warn_warn_only,
    #      p.warn_no_exit)

    #p.err_use_logger = not p.err_use_logger
    #p.err_warn_only = not p.err_warn_only
    #p.err_no_exit = not p.err_no_exit

    #print(p.connect())
    #p.connect()

    #print('#' * 76)

    #pp(p.cursor())
    #pp(p.cur)

    #p.cursor()
    #c = p.cursor(False)
    #pp(c)

    #print('#' * 76)

    #p._SUPPORTED.remove('autocommit')

    #print(p.autocommit(None))
    #print(p.autocommit(True))
    #print(p.autocommit(None))
    #print(p.autocommit(False))
    #print(p.autocommit(None))
    #return

    #print('FA:' + str(p._fake_autocommit))

    #print(p.execute(None, 'show dastabases', has_results=True))

    #print(p.execute(None, 'show databases', has_results=True))
    #for i in range(1, 10):
    #    print(p.fetchone(None))
    #for i in range(1, 10):
    #    print(p.fetchmany(None, 2))
    #print(p.fetchall(None))

    #print(p.execute(None, 'select * from user where user=%s', ['root'],
    #                has_results=True))
    #print(p.fetchall(None))
    #print(p.execute(
    #    None,
    #    "update user set password='111111111' where user=%s",
    #    ['root']
    #))
    #print(p.executemany(
    #    None,
    #    "update user set password=%s where user=%s",
    #    [['4444444', 'root'], ['22222222222', 'test']]
    #))
    #print(p.execute(None, 'select * from user', has_results=True))
    #print(p.fetchall(None))
    #print(p.executemany(None, 'select * from user', [[]], has_results=True))
    #print(p.fetchall(None))

    #print(p.commit())
    #print(p.rollback())

    #print(p.executemany(None, 'select * from user where user=%s',
    #                    [['root'], ['test']],
    #                    has_results=True))
    #print(p.fetchall(None))

    #print(p.execute(c, 'show tables', has_results=True))
    #print(p.fetchall(c))

    #print(p.get_db_list(None))

    #print(p.change_db(None, 'mysql'))
    #print(p.execute(None, 'select * from user where user=%s', ['root'],
    #                has_results=True))
    #print(p.fetchall(None))

    #print(p.nextset(None))
    #print(p.setinputsizes(None, [4, 5]))
    #print(p.setoutputsize(None, 400))

    #print('#' * 76)

    #p.close_cursor(c)
    #p.close_cursor(c)
    #p.close_cursor()
    #p.close_cursor()

    #print(p.get_db_list(None))

    #print('#' * 76)

    #p.close()
    #p.close()

    ########

    #status_logger.debug('status debug')
    #status_logger.info('status info')
    #alert_logger.debug('alert debug')
    #alert_logger.info('alert info')
    #email_logger.debug('email debug')
    #email_logger.info('email info')

    #print(render_config())

    pass

nori.core.task_article = 'a'
nori.core.task_name = 'test'
nori.core.tasks_name = 'tests'

#def bar(msg, full):
#    msg += '\nbar'
#    if full:
#        msg += '\n baz'
#    msg += '\n'
#    return msg
#nori.render_status_messages_hooks.append(bar)
#nori.render_status_metadata_hooks.append(bar)

#def foo():
#    print('foo')
#nori.apply_config_defaults_hooks.append(foo)
#nori.process_config_hooks.append(foo)

#nori.core.config_file_header='foo'
#nori.core.default_config_files=['foo', 'bar']

#def ap_foo(ap):
#    pp(ap)
#    return ap
#nori.create_arg_parser_hooks.append(ap_foo)

#nori.core.supported_features = []

nori.run_mode_hooks.append(run_mode_hook)

#nori.config_settings_no_print_output_log(False)
#nori.config_settings['exec_path']['no_print'] = False
#nori.config_settings['log_cmds']['no_print'] = False

#s = nori.SSH('foo')
#s = nori.SSH('foo', ':')
#print(s._prefix)
#print(s._delim)
#s.create_settings(heading='foo ssh', extra_text='asdfadf', tunnel=True,
#                  default_local_port=1111, default_remote_port=11111)
#s.create_settings(extra_text='asdfadf', tunnel=True,
#                  default_local_port=1111, default_remote_port=11111)
#s.create_settings(tunnel=False,
#                  default_local_port=1111, default_remote_port=11111)
#s.create_settings(heading='foo ssh', extra_text='asdfadf', tunnel=True,
#                  default_local_port=1111, default_remote_port=11111,
#                  ignore=lambda: True)

#s2 = nori.SSH('bar')
#s2.create_settings(heading='bar ssh', tunnel=True)

#m = nori.MySQL('mysqlstuff')
#m.create_settings()
#m.create_settings(heading='mysql stuff', extra_text='asdf')
#m.create_settings(heading='mysql stuff', extra_text='asdf',
#                  extra_requires=['rrr'])
#m.create_settings(heading='mysql stuff', tunnel=False)
#m.create_settings(heading='mysql stuff', ignore=lambda: True)
#m.create_settings(heading='mysql stuff')
#pp(nori.config_settings)


#p = nori.PostgreSQL('postgresstuff')
#p.create_settings()
#p.create_settings(heading='postgres stuff')
#p.create_settings(heading='postgres stuff', extra_text='ghtfhf')
#p.create_settings(heading='postgres stuff', extra_text='ghtfhf',
#                  ignore=lambda: True)
#p.create_settings(heading='postgres stuff', extra_text='ghtfhf',
#                  extra_requires=['rrr'])
#p.create_settings(tunnel=False)

#nori.config_settings['test']={'descr':'test'}

nori.process_command_line()
