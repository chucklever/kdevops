# SPDX-License-Identifier: copyleft-next-0.3.1

firstconfig:
	$(Q)ansible-playbook \
		--extra-vars '{ kdevops_cli_install: True }' \
		--tags vars_simple,firstconfig \
		$(KDEVOPS_PLAYBOOKS_DIR)/devconfig.yml

# Cloud build has no VMs to configure
ifneq (y,$(CONFIG_BOOTLINUX_CLOUD_BUILD))
KDEVOPS_BRING_UP_DEPS_EARLY += firstconfig
endif

firstconfig-help:
	@echo "firstconfig    - Setup firstconfig"

HELP_TARGETS += firstconfig-help
