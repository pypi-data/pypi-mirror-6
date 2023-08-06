#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# flac2mp3 - example combined server and client flac to mp3 converter
# Copyright (C) 2010-2011  The pypastset project lead by Brian Vinter
#
# This file is part of pypastset.
#
# pypastset is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pypastset is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# -- END_HEADER ---
#

"""Convert flac file(s) to mp3"""

import getopt
import os
import subprocess
import sys
import time
import pastset

def usage():
    """Usage help"""
    print "%s [OPTIONS]" % sys.argv[0]

def parse_tags(output):
    """Translate raw TAG=Value lines to a dictionary of tag and Value"""
    tag_list = []
    for line in output:
        if not '=' in line:
            print "skipping non-tag line: %s" % line
            continue
        (name, value) = line.strip().split('=', 1)
        tag_list.append((name.lower(), value))
    return dict(tag_list)
        
def client(conf):
    """Run client side of conversion"""
    pset = pastset.PastSet()

    jobs = pset.enter(('convert-jobs', str))
    results = pset.enter(('convert-results', bool, str))

    while True:
        path = jobs.observe()[0]  # Job is a tuple (str,)
        convert = True
        src_path = os.path.join(conf['source'], path)
        if not os.path.isfile(src_path):
            msg = 'no such source: %s' % src_path
            results.move((False, msg))
            print msg
            continue
        
        src_dir = os.path.dirname(src_path)
        dst_path = os.path.join(conf['destination'], path.replace('flac',
                                                                  'mp3'))
        dst_dir = os.path.dirname(dst_path)
        try:
            os.makedirs(dst_dir)
        except Exception, exc:
            pass
        if not os.path.isdir(dst_dir):
            msg = 'could not create destination dir %s: %s' % (dst_dir, exc)
            results.move((False, msg))
            print msg
            continue
        if conf.get('sync-time-stamps', False):
            source_stamp = os.stat(src_dir)
            os.utime(dst_dir, (source_stamp.st_atime, source_stamp.st_mtime))
        helper = {'src_path': src_path, 'dst_path': dst_path}
        tags_cmd = [conf['tags_path']] + \
                   [i % helper for i in conf['tags_opts']]
        readtags = subprocess.Popen(tags_cmd, stdout=subprocess.PIPE)
        readtags.wait()
        tags = dict([(i, '') for i in conf['tag_map'].keys()])
        tags.update(parse_tags(readtags.stdout))
        helper.update(tags)
        decode_cmd = [conf['decode_path']] + \
                     [i % helper for i in conf['decode_opts']]
        encode_cmd = [conf['encode_path']] + \
                     [i % helper for i in conf['encode_opts']]
        if not os.path.isfile(dst_path) or conf['overwrite']:
            decode = subprocess.Popen(decode_cmd, stdout=subprocess.PIPE)
            encode = subprocess.Popen(encode_cmd, stdin=decode.stdout)
            decode.wait()
            encode.wait()
            convert += decode.returncode
            convert += encode.returncode
        if conf.get('sync-time-stamps', False):
            source_stamp = os.stat(src_path)
            os.utime(dst_path, (source_stamp.st_atime, source_stamp.st_mtime))
        results.move((convert, ''))
    return True

def server(conf):
    """Run server side of conversion"""
    total_time = -time.time()
    pset = pastset.PastSet()

    jobs = pset.enter(('convert-jobs', str))
    results = pset.enter(('convert-results', bool, str))
    tasks = 0

    if os.path.isfile(conf['source']):
        print 'enqueue single file %s' % conf['source']
        jobs.move((conf['source'], ))
        tasks += 1
    elif os.path.isdir(conf['source']) and conf['recursive']:
        print 'enqueue files recusively in %s' % conf['source']
        for (root, _, files) in os.walk(conf['source']):
            for filename in files:
                if not filename.endswith('.flac'):
                    continue
                real_path = os.path.join(root, filename)
                relative_path = real_path.replace(conf['source'] + os.sep, '')
                print 'enqueue nested file %s' % relative_path
                jobs.move((relative_path, ))
                tasks += 1
    else:
        print 'invalid source: %s' % conf["source"]
        print 'source must be an existing file or directory.'
        print 'if it is a directory recursive must be set.'
        
    print 'spawning %(workers)d workers' % conf
    for _ in xrange(conf['workers']):
        pset.spawn(sys.argv[0], sys.argv[1:]+['--client=True'])

    convert_val = True
    convert_err = []
    print 'waiting for %d results' % tasks
    for _ in xrange(tasks):
        res = results.observe()
        convert_val &= res[0]  # result is a tuple(bool,)
        if res[1]:
            convert_err.append(res[1])

    print 'Convert result is %s with %d worker(s), %d task(s)' \
        % (convert_val, conf['workers'], tasks)
    if convert_err:
        print "Convert errors:\n%s" % '\n'.join(convert_err)

    pset.halt()
    total_time += time.time()
    if tasks:
        avg_time = total_time / tasks
    else:
        avg_time = total_time
    print 'Convert finished in %.2fs (avg %.2fs)' % (total_time, avg_time)
    return True

if __name__ == '__main__':
    work_dir = os.getcwd()
    tag_map = {'title': 'tt', 'tracknumber': 'tn', 'date': 'ty',
               'artist': 'ta', 'album': 'tl', 'genre': 'tg', 'comment': 'tc'}
    settings = {'tags_path': '/usr/bin/metaflac',
                'decode_path': '/usr/bin/flac',
                'encode_path': '/usr/bin/lame',
                'tags_opts': ['--export-tags-to=-', '%(src_path)s'],
                'decode_opts': ['-sdc', '%(src_path)s'],
                'encode_opts': ['-S', '--add-id3v2', '-', '%(dst_path)s'],
                'source': work_dir, 'destination': work_dir,
                'workers': 1, 'sync-time-stamps': False, 'recursive': False,
                'overwrite': False, 'client': False, 'tag_map': tag_map}
    for (tag, opt) in tag_map.items():
        settings['encode_opts'] = ['--%s' % opt, '%%(%s)s' % tag] + \
                                  settings['encode_opts']
    options = {'client': bool, 'source': os.path.normpath,
               'destination': os.path.normpath, 'recursive': bool,
               'workers': int, 'sync-time-stamps': bool, 'overwrite': bool}
    flag_str = 'h'
    opts_str = ["%s=" % i for i in options.keys()] + ["help"]

    try:
        (opts, args) = getopt.getopt(sys.argv[1:], flag_str, opts_str)
    except getopt.GetoptError, exc:
        print 'Error: ', exc.msg
        usage()
        sys.exit(1)

    for (opt, val) in opts:
        opt_name = opt.lstrip('-')
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt_name in options.keys():
            settings[opt_name] = val
        else:
            print 'Error: %s not supported!' % opt
            usage()
            sys.exit(1)

    if args:
        print 'Error: raw arguments are not supported!' % opt
        usage()
        sys.exit(1)

    # Make sure settings are sane

    for (opt, caster) in options.items():
        try:
            settings[opt] = caster(settings[opt])
        except Exception, exc:
            print "Failed to sanitize %s setting: %s" % (opt, exc)
            usage()
            sys.exit(1)

    # Now split into producer and consumers
    
    if settings.get('client', False):
        client(settings)
    else:
        server(settings)
    sys.exit(0)
