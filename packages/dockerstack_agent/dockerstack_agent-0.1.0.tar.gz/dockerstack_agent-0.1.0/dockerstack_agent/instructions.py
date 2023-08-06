# -*- coding: utf-8 -*-

from distutils.dir_util import copy_tree
import json
import os
import shutil
import subprocess
import urllib


def instruction_from(command):
    # inheritance is not implemented yet.
    return True


def instruction_maintainer(name):
    """
    The MAINTAINER instruction allows you to set the Author field of the
    generated images.
    """
    # who cares?
    return True


def instruction_run(command):
    """
    RUN <command>

    The RUN instruction will execute any commands on the current image and
    commit the results. The resulting committed image will be used for the
    next step in the Dockerfile.

    Layering RUN instructions and generating commits conforms to the core
    concepts of Docker where commits are cheap and containers can be created
    from any point in an image’s history, much like source control.
    """
    print "Command to be executed: %s" % command
    proc = subprocess.Popen(command, shell=True, stdin=None,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            executable="/bin/bash")
    proc.wait()
    print " ---> %s\n" % proc.stdout.read()
    return proc.returncode == 0


def instruction_cmd(command):
    """
    CMD has three forms:

    CMD ["executable","param1","param2"] (like an exec, preferred form)
    CMD ["param1","param2"] (as default parameters to ENTRYPOINT)
    CMD command param1 param2 (as a shell)
    """
    cmd = json.loads(command)
    retcode = subprocess.call(cmd)
    return retcode == 0


def instruction_expose(ports):
    """
    EXPOSE <port> [<port>...]

    The EXPOSE instruction exposes ports for use within links. This is
    functionally equivalent to running docker commit -run '{"PortSpecs":
        ["<port>", "<port2>"]}' outside the builder. Refer to Redirect Ports
        for detailed information.
    """
    # need to use an openstack call to add this to the security group that the
    # instance is being deployed to.
    return True


def instruction_env(command):
    """
    ENV <key> <value>

    The ENV instruction sets the environment variable <key> to the value
    <value>. This value will be passed to all future RUN instructions. This
    is functionally equivalent to prefixing the command with <key>=<value>
    """
    # should run an os.setenv() so that future runs get the environment
    # variable.
    parts = command.split(' ')
    os.putenv(parts[0], parts[1])
    return True


def instruction_add(command):
    """
    ADD <src> <dest>

    The ADD instruction will copy new files from <src> and add them to the
    container’s filesystem at path <dest>.

    <src> must be the path to a file or directory relative to the source
    directory being built (also called the context of the build) or a remote
    file URL.

    <dest> is the path at which the source will be copied in the destination
    container.

    All new files and directories are created with mode 0755, uid and gid 0.
    """
    parts = command.split(' ')
    src = parts[0]
    dest = parts[1]

    if src.startswith('http://') or src.startswith('https://'):
        urllib.urlretrieve(src, dest)
    elif os.path.isdir(src):

        if src.endswith('/'):
            copy_tree(src, dest)
        else:
            shutil.copytree(src, dest)
    else:
        shutil.copy(src, dest)

    return True


def instruction_entrypoint(command):
    """
    ENTRYPOINT has two forms:

    ENTRYPOINT ["executable", "param1", "param2"] (like exec, preferred form)
    ENTRYPOINT command param1 param2 (as a shell)

    There can only be one ENTRYPOINT in a Dockerfile. If you have more than
    one ENTRYPOINT, then only the last one in the Dockerfile will have an
    effect.

    An ENTRYPOINT helps you to configure a container that you can run as an
    executable. That is, when you specify an ENTRYPOINT, then the whole
    container runs as if it was just that executable.
    """

    return True


def instruction_volume(command):
    """
    VOLUME ["/data"]

    The VOLUME instruction will create a mount point with the specified name
    and mark it as holding externally mounted volumes from native host or
    other containers. For more information/examples and mounting
    instructions via docker client, refer to Share Directories via Volumes
    documentation.
    """
    # not sure how this applies, I haven't seen it used in any dockerfiles yet.
    return True


def instruction_user(user):
    """
    USER daemon

    The USER instruction sets the username or UID to use when running the
    image.
    """
    # in order to set the user for the next running commands, we'll need to use
    # a context manager or something which wraps commands in "su <user>".
    print "User switching is not supported"
    return True


def instruction_workdir(directory):
    """
    WORKDIR /path/to/workdir

    The WORKDIR instruction sets the working directory in which the command
    given by CMD is executed.
    """
    os.chdir(directory)
    return True
