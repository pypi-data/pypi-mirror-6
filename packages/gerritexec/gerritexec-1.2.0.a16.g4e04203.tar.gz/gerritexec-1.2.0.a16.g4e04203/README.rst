gerritexec
==========

gerritexec is a command line tool `listening to gerrit <https://gerrit-documentation.storage.googleapis.com/Documentation/2.7/cmd-stream-events.html>`_ on a designated project. On each `new patchset <https://gerrit-documentation.storage.googleapis.com/Documentation/2.7/cmd-stream-events.html#_events>`_, (or when a comment contains *recheck no bug* or *run gerritexec*) it will:

* git clone the project
* git pull the patchset
* cd in the git tree and run a script
* positively review the patchset ( +1 ) if the program exit(0)
* negatively review the patchset ( -1 ) otherwise

Examples
========

Positively review all patchsets in the `stackforge/puppet-ceph <https://review.openstack.org/#/q/project:stackforge/puppet-ceph,n,z>`_ project:

.. code:: sh

    gerritexec --hostname review.openstack.org \
               --username puppetceph \
               --script 'true' \
               --project stackforge/puppet-ceph

Run the `integration tests <https://github.com/stackforge/puppet-ceph/tree/master/spec/system>`_ found in the git tree of the `stackforge/puppet-ceph <https://review.openstack.org/#/q/project:stackforge/puppet-ceph,n,z>`_ project:

.. code:: sh

    gerritexec --hostname review.openstack.org \
               --username puppetceph \
               --script 'bundle exec rake spec:system' \
               --project stackforge/puppet-ceph

