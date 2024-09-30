ifeq (y,$(CONFIG_WORKFLOWS_DEDICATED_WORKFLOW))
export KDEVOPS_HOSTS_TEMPLATE := rdstcp.j2
endif # CONFIG_WORKFLOWS_DEDICATED_WORKFLOW

RDSTCP_REPO:=$(subst ",,$(CONFIG_RDSTCP_REPO))
RDSTCP_ARGS += rdstcp_repo=$(RDSTCP_REPO)

RDSTCP_REPO_COMMIT:=$(subst ",,$(CONFIG_RDSTCP_REPO_COMMIT))
RDSTCP_ARGS += rdstcp_repo_commit=$(RDSTCP_REPO_COMMIT)

ifeq (y,$(CONFIG_RDSTCP_TEST_GROUP_PING))
RDSTCP_ENABLED_TEST_GROUPS += ping
endif
ifeq (y,$(CONFIG_RDSTCP_TEST_GROUP_STRESS))
RDSTCP_ENABLED_TEST_GROUPS += stress
endif

WORKFLOW_ARGS += $(RDSTCP_ARGS)
WORKFLOW_ARGS_SEPARATED += rdstcp_enabled_test_groups='$(subst $(space),+,$(RDSTCP_ENABLED_TEST_GROUPS))'

RDSTCP_KERNEL_CI_LOOP := false
RDSTCP_KERNEL_CI_LOOP_KOTD := false

ifeq (y,$(CONFIG_KERNEL_CI))
RDSTCP_KERNEL_CI_LOOP      := scripts/workflows/rdstcp/run_kernel_ci.sh
RDSTCP_KERNEL_CI_LOOP_KOTD := scripts/workflows/rdstcp/run_kernel_ci_kotd.sh
endif # CONFIG_KERNEL_CI

rdstcp:
	$(Q)ansible-playbook $(ANSIBLE_VERBOSE) -l baseline,dev \
		-f 30 -i hosts playbooks/rdstcp.yml \
		--skip-tags run_tests,copy_results

rdstcp-baseline:
	$(Q)ansible-playbook $(ANSIBLE_VERBOSE) \
		-f 30 -i hosts -l baseline playbooks/rdstcp.yml \
		--tags vars,run_tests,copy_results \
		--extra-vars=@./extra_vars.yaml

rdstcp-baseline-loop:
	$(Q)$(RDSTCP_KERNEL_CI_LOOP) baseline

rdstcp-baseline-kernelci:
	$(Q)$(RDSTCP_KERNEL_CI_LOOP_KOTD) baseline

rdstcp-dev-baseline:
	$(Q)ansible-playbook $(ANSIBLE_VERBOSE) \
		-f 30 -i hosts -l dev playbooks/rdstcp.yml \
		--tags vars,run_tests,copy_results \
		--extra-vars=@./extra_vars.yaml

rdstcp-dev-loop:
	$(Q)$(RDSTCP_KERNEL_CI_LOOP) dev

rdstcp-dev-kernelci:
	$(Q)$(RDSTCP_KERNEL_CI_LOOP_KOTD) dev

rdstcp-dev-reset:
	$(Q)ansible-playbook $(ANSIBLE_VERBOSE) \
		-f 30 -i hosts -l dev playbooks/rdstcp.yml \
		--tags vars,reset \
		--extra-vars=@./extra_vars.yaml

rdstcp-help-menu:
	@echo "rdstcp options:"
	@echo "rdstcp                              - Git clone rds-tools and install it"
	@echo "rdstcp-{baseline,dev}               - Run selected rds-tools on baseline or dev hosts and collect results"
	@echo "rdstcp-{baseline,dev}-loop"         - Run rdstcp in a loop until error or steady state
	@echo "rdstcp-{baseline,dev}-kernelci      - Run rdstcp kernel-ci loop"
	@echo ""

HELP_TARGETS += rdstcp-help-menu
