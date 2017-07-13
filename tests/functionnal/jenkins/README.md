## On Jenkins

Configure jenkins node to use it:
e.g: `ssh  -o StrictHostKeyChecking=no discovery@access.grid5000.fr "ssh luxembourg -o ConnectTimeout=600 jenkins/launch_slave_deploy.py <job_name>"`

## On g5k frontend

Install those scripts alongside the slave.jar file to use.

## Existing jobs

* `enos-packer`:
Build the vagrant/vbox and vagrant/libvirt base boxes using the static
provisioner and packer to orchestrate.

* `enos-functionnal`:
Wrapper to the following jobs. Triggered via a webhook on the push events on github.

* `enos-vagrant-vbox`:
Test the vagrant provisioner on a multinode vagrant/vbox setup.

* `enos-vagrant-topology`:
Test the network emulation on a multinode vagrant/vbox setup.

## Misc.

Each job is bound to a specific slave on G5K. If the slave is already created it
will be reused (until the walltime expires - default to 03:00:00).
