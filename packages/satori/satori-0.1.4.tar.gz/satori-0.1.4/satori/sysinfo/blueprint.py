#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
"""Devstructure Blueprint Data Plane Discovery Module."""

from __future__ import print_function

import logging

from satori import errors
from satori import ssh

COMMANDS = {
    "install": {
        "debian": [
            ("echo \"deb http://packages.devstructure.com $(lsb_release -sc) "
             "main\" | sudo tee /etc/apt/sources.list.d/devstructure.list"),
            "sudo wget -O /etc/apt/trusted.gpg.d/devstructure.gpg "
            "http://packages.devstructure.com/keyring.gpg",
            "sudo apt-get update",
            "sudo apt-get -y install blueprint",
        ],
        "redhat": [
            ("rpm -Uvh http://dl.fedoraproject.org/pub/epel/5/i386/"
             "epel-release-5-4.noarch.rpm"),
            "yum install python26",
            "git clone git://github.com/devstructure/blueprint.git",
            "cd blueprint",
            "git submodule update --init",
            "make && sudo make install PYTHON=/usr/bin/python26",
        ]
    }
}
LOG = logging.getLogger(__name__)


def get_systeminfo(ipaddress, config, interactive=False):
    """Run data plane discovery ugsing this module against a host."""
    sshclient = ssh.connect(host=ipaddress, private_key=config.host_key,
                            interactive=False)
    try:
        result = system_info(sshclient)
    except errors.SystemInfoCommandMissing as exc:
        LOG.exception(exc)
        install(sshclient)
        return system_info(sshclient)
    except errors.SystemInfoCommandOld as exc:
        LOG.exception(exc)
        remove_app(sshclient)
        install(sshclient)
        return system_info(sshclient)
    except errors.SystemInfoCommandInstallFailed as exc:
        LOG.exception(exc)
        LOG.error("ohai-solo install failed")
        raise
    except errors.SystemInfoNotJson as exc:
        LOG.exception(exc)
        raise

    return result


def system_info(ssh_client):
    """."""
    output = ssh_client.remote_execute("sudo blueprint create satori && "
                                       "blueprint show satori")
    return output


def install(ssh_client):
    """Install devstructure blueprint on host."""
    command_list = ["cd /tmp"]
    print("DIST", ssh_client.platform_info['dist'])
    if ssh_client.platform_info['dist'] in ['ubuntu', 'debian']:
        command_list.extend(COMMANDS['debian']['install'])
    elif ssh_client.platform_info['dist'] in ['redhat', 'centos', 'el']:
        command_list.extend(COMMANDS['install']['redhat'])
    command = " && ".join(command_list)

    output = ssh_client.remote_execute(command, with_exit_code=True)
    context = {'Platform': ssh_client.platform_info,
               'stdout': str(output['stdout'][:5000] + "...TRUNCATED"),
               'stderr': str(output['stderr'][:5000] + "...TRUNCATED")}
    if output['exit_code'] != 0:
        raise errors.SystemInfoCommandInstallFailed(context)
    else:
        return output


def remove_app(ssh_client):
    """Remove ohai-solo from specifc remote system.

    Currently supports:
        - ubuntu [10.x, 12.x]
        - debian [6.x, 7.x]
        - redhat [5.x, 6.x]
        - centos [5.x, 6.x]
    """
    if ssh_client.platform_info['dist'] in ['ubuntu', 'debian']:
        remove = "sudo dpkg --purge blueprint"
    elif ssh_client.platform_info['dist'] in ['redhat', 'centos', 'el']:
        remove = "sudo yum -y erase blueprint"

    command = "cd /tmp && " + remove
    output = ssh_client.remote_execute(command)
    return output
