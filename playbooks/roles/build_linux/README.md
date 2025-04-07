build_linux
===========

The build_linux role downloads and builds the Linux kernel.  It also
lets you apply custom patches, remove kernels, etc.; anything you
have to do with regards to generic kernel development.

By default, it tracks one of the latest stable kernels that are
still supported using the linux stable git tree.

Requirements
------------

A separate block device is required on which to create the file
system where the test kernel is built.

Role Variables
--------------

  * infer_uid_and_group: defaults to False, if set to True, then we will ignore
    the passed on data_user and data_group and instead try to infer this by
    inspecting the `whoami` and getent on the logged in target system we are
    provisioning. So if user sam is running able on a host, targetting a system
    called foofighter and logging into that system using username pincho,
    then the data_user will be set overwritten and set to pincho. We will then
    also lookup for pincho's default group id and use that for data_group.
    This is useful if you are targetting a slew of systems and don't really
    want to deal with the complexities of the username and group, and the
    default target username you use to ssh into a system suffices to use as
    a base. This is set to False to remain compatible with old users of
    this role.
  * data_path: where to place the git trees we clone under
  * data_user: the user to assign permissions to
  * data_group: the group to assign permissions to

  * data_device: the target device to use for the data partition
  * data_fstype: the filesystem to store the data parition under
  * data_label: the label to use
  * data_fs_opts: the filesystem options to use, you want to ensure to add the
    label

  * target_linux_admin_name: your developer name
  * target_linux_admin_email: your email
  * target_linux_git: the git tree to clone, by default this is the linux-stable
    tree
  * target_linux_tree: the name of the tree
  * target_linux_dir_path: where to place the tree on the target system

  * target_linux_ref : the actual tag as used on linux, so v4.19.62
  * target_linux_extra_patch: if defined an extra patch to apply with git
     am prior to compilation
  * target_linux_config: the configuration file to use

Dependencies
------------

None.

Example Playbook
----------------

Below is an example playbook, say a build_linux.yml file:

```
---
- hosts: all
  roles:
    - role: build_linux
```

License
-------

copyleft-next-0.3.1
