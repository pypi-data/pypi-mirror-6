=================================================
chssh -- Interactive ssh and scp for chef server
=================================================

Inspired by ec2-ssh from instagram, this uses the pychef library to allow you to address your hosts by their chef node name instead of the dns name.

This differs from `knife ssh` because these tools operate with interactive shells, and are meant for working with 1 node at a time.

Prerequisities
--------------

You need to have an installed and configured chef client on your machine. The code uses the pychef autoconfigure() to discover and load the chef configuration

Usage
-----

        ``chssh node1``   # ssh to chef node node1

        ``chssh user@node1``  # ssh as user to chef node node1

        ``chscp file user@node1:path`` # scp file to chef node node1

        ``chscp user@node1:path`` . # scp file from chef node node1

Enjoy!