# SPDX-License-Identifier: copyleft-next-0.3.1

# Automatically archive of CI results

ifeq (,$(wildcard $(CURDIR)/.config))
else

DYNAMIC_RUNTIME_VARS :=

ifneq (,$(DEMO))
DYNAMIC_RUNTIME_VARS += \
	"kdevops_archive_demo": True
endif

ci-archive:
	$(Q)ansible-playbook $(ANSIBLE_VERBOSE) --connection=local \
		--inventory localhost, \
		playbooks/kdevops_archive.yml \
		-e 'ansible_python_interpreter=/usr/bin/python3' \
		--extra-vars '{ $(DYNAMIC_RUNTIME_VARS) }' \
		--extra-vars=@./extra_vars.yaml
endif
