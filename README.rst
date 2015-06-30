===========
aloisius
===========

About
=====

aloisius helps you to manage the life-cycle of AWS CloudFormation stacks. It
allows you to use outputs from one stack as input parameters to other stacks.
There are other tools which allow you to do so, like i.e. Cumulus or Ansible,
but I couldn't find one which doesn't require you to use YAML or Jinja2. It
is a pure Python library and it is intended to be used in inter-play with
troposphere, but you can also use it with any CloudFormation JSON templates.

License
=======

The BSD 2-Clause License: http://opensource.org/licenses/BSD-2-Clause

Installation
============

aloisius can be installed using the pip distribution system for Python by
issuing::

  $ pip install aloisius

Alternatively, you can run use setup.py to install by cloning this repository
and issuing::

  # python setup.py install

Examples
========

A simple example creating a VPC containing an RDS could look like this::

   #!/usr/bin/env python

   from aloisius import Stack

   # I keep my troposphere templates as modules in a package.
   from templates.vpc import template as template_vpc
   from templates.rds import template as template_rds


   # I normally put some constants and helper functions here.
   app_name = 'myapp'
   region_name = 'eu-central-1'
   stack_name = lambda x: '-'.join([app_name, region_name, x])

   vpc = Stack(
       StackName=stack_name('vpc'),
       TargetState='present',
       RegionName=region_name,
       TemplateBody=template_vpc.to_json(),
   )

   rds = Stack(
       StackName=stack_name('rds'),
       TargetState='present',
       RegionName=region_name,
       TemplateBody=template_rds.to_json(),
       Parameters={
           # You can use outputs of previously created stacks as parameters.
           'VpcId': vpc.outputs['VpcId'],
           'PrivateSubnets': vpc.outputs['PrivateSubnets'],
           # More parameters here.
       },
   )

Why you shouldn't use aloisius
==============================

- It's not tested. I simply use it myself. There are probably many bugs.
- There's not much documentation (but there are comments in the code).

Why you should use aloisius
===========================

- You could find some bugs and help to make it better.
- Parallel stack creation/deletion.
- Integrates nicely with troposphere: No JSON and no YAML.
