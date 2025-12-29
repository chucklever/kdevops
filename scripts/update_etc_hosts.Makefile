update_etc_hosts:
	$(Q)ansible-playbook \
		playbooks/update_etc_hosts.yml

# Cloud build has no VMs to add to /etc/hosts
ifneq (y,$(CONFIG_BOOTLINUX_CLOUD_BUILD))
KDEVOPS_BRING_UP_DEPS_EARLY += update_etc_hosts
endif

PHONY += update_etc_hosts
