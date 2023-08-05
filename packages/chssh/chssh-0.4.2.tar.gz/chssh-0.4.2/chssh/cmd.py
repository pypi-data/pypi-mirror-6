import sys
import os
from chef import autoconfigure, Node
import re
from urllib2 import HTTPError

class ChefCommand:
    def fqdn_for_node(self,node):
        self.node = node
        api = autoconfigure()
        n = Node(node)
        if n:
            try:
                self.fqdn = n.attributes['ec2']['public_hostname']
            except KeyError:
                try:
                    self.fqdn = n.attributes['ec2']['local_ipv4']
                except KeyError:
                    if 'fqdn' in n:
                        self.fqdn = n['fqdn']
                    else:
                        return None
        else:
            return None

        return self.fqdn

    def find_arg_idx(self):
        hostname_arg_idx = -1
        for i in range(len(sys.argv)):
            if self.is_node_arg(sys.argv[i]):
                hostname_arg_idx = i
        return hostname_arg_idx

    def run(self):
        idx = self.find_arg_idx()
        if idx >= 0:
            updated_arg = self.substitute_fdqn(sys.argv[idx])
        args = self.exec_args()
        for i in range(1,len(sys.argv)):
            if i != idx:
                args.append(sys.argv[i])
            else:
                args.append(updated_arg)

        if len(sys.argv) > 1:
            args.extend(self.extra_args())

        if getattr(self,'fqdn',None):
            print "Connecting to %s" % (self.fqdn)
        os.system(" ".join("'" + a + "'" for a in args))

    def is_node_arg(self,arg):
        return False

    def exec_args(self):
        """ Template method to return the first arg(s) to pass to execvp """
        return None

    def extra_args(self):
        """ Template method to allow subclasses to append additional arguments """
        return []

    def substitute_fdqn(self,arg):
        """ Template method for subclasses to override """
        return arg



class SshChefCommand(ChefCommand):
    # Borrowed with homage from ec2-ssh
    SSH_CMD='echo ". .bashrc && PS1=\\"%s:\\\\w$ \\"" > ~/.chsshrc ; /bin/bash --rcfile ~/.chsshrc -i'

    def find_arg_idx(self):
        return len(sys.argv) - 1

    def extra_args(self):
        return [self.SSH_CMD % self.node]

    def exec_args(self):
        return ['ssh','-t']

    def substitute_fdqn(self,arg):
        try:
            m = re.match("(.*)@(.*)",arg)
            if m:
                username = m.group(1)
                node = m.group(2)
                return "%s@%s" % (username,self.fqdn_for_node(node))
            return self.fqdn_for_node(arg)
        except KeyError:
            return arg
        except HTTPError:
            return arg


class ScpChefCommand(ChefCommand):
    def is_node_arg(self,arg):
        return arg.find(":") > 0

    def exec_args(self):
        return ["scp"]

    def substitute_fdqn(self,arg):
        try:
            (user_at_host,path) = arg.split(":")
            m = re.match("(.*)@(.*)",user_at_host)
            if m:
                username = m.group(1)
                node = m.group(2)
                return "%s@%s:%s" % (username,self.fqdn_for_node(node),path)
            return "%s:%s" % (self.fqdn_for_node(user_at_host),path)            
        except KeyError:
            return arg

class RsyncChefCommand(ScpChefCommand):
    def exec_args(self):
        return ["rsync"]


def scp():
    scp_command = ScpChefCommand()
    scp_command.run()

def ssh():
    ssh_command = SshChefCommand()
    ssh_command.run()

def rsync():
    rsync_command = RsyncChefCommand()
    rsync_command.run()


if __name__ == "__main__":
    ssh()