# -*- coding: utf-8 -*-
"""loweb - local web tools

Static websites are still useful and quick to setup with free
hosting services. Though one does not want to write static html.
Separating data into readable form, eg. markdown or yaml files and
then combining those to html with some mustache templates.
Thats where loweb comes in and makes it easy for you to write
the logical steps of working with your data before generating
the static html from the templates.

It also has built in support for checking whether you have to
regenerate parts of the output or not.
"""
import os
import shutil
import re
import codecs

import pystache
import yaml


def load_template(fpath):
    with codecs.open(fpath, 'r', 'utf-8') as fh:
        template = fh.read()
        return template

def load_data(ypath):
    with codecs.open(ypath, 'r', 'utf-8') as fh:
        return yaml.load(fh)

def render(template, tofile, model):
    with codecs.open(tofile, 'w', 'utf-8') as fh:
        r = pystache.Renderer()
        blob = r.render(template, model)
        fh.write(blob)
        fh.close()
        print "Render ", tofile

def needs_update(*args):
    """First argument is the destination file and the others are
    dependencies whose modification time will be compared."""
    if not args:
        return True
    dest = args[0]
    if not os.path.exists(dest):
        return True
    destmtime = os.path.getmtime(dest)
    for x in args[1:]:
        if os.path.getmtime(x) > destmtime:
            return True
    return False

def mkdir(path):
    """Makes the directory of the given path. Parent directory must
    exist. Fails quietly."""
    tmp = ""
    last = None
    for c in path:
        if c == "/" and tmp != "":
            if not os.path.exists(tmp):
                try:
                    last = tmp
                    os.mkdir(tmp)
                except Exception as e:
                    print e
                    return tmp, e
        tmp = tmp + c
    return last, None

def rcopy(src, dst, pattern=".*"):
    """Recursive copy of src into dst."""
    for childroot, dirnames, filenames in os.walk(src):
        todir = os.path.join(dst, childroot, "")
        mkdir(todir)
        for filename in filenames:
            if re.match(pattern, filename):
                fromfile = os.path.join(childroot, filename)
                tofile = os.path.join(dst, childroot, filename)
                if os.path.isfile(tofile):
                    mt_a = os.path.getmtime(fromfile)
                    mt_b = os.path.getmtime(tofile)
                    if mt_a > mt_b:
                        shutil.copy(fromfile, tofile)
                        print "Copyto ", "%-40s" % tofile, " <- ", fromfile
                else:
                    shutil.copy(fromfile, tofile)
                    print "Copyto ", "%-40s" % tofile, " <- ", fromfile
