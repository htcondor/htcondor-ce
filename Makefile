# Makefile for osg-test


# ------------------------------------------------------------------------------
# Release information: Update for each release
# ------------------------------------------------------------------------------

PACKAGE := htcondor-ce
VERSION := 5.1.4


# ------------------------------------------------------------------------------
# Other configuration: May need to change for a release
# ------------------------------------------------------------------------------

PYTHON			:= /usr/bin/python3

INSTALL_BIN_DIR		:= usr/bin
INSTALL_LIB_DIR         := usr/lib
INSTALL_SHARE_DIR	:= usr/share
INSTALL_STATE_DIR	:= var
INSTALL_SYSCONF_DIR	:= etc
INSTALL_WSGI_DIR        := $(INSTALL_STATE_DIR)/www/wsgi-scripts
INSTALL_PYTHON_DIR	:= $(shell $(PYTHON) -c 'from sysconfig import get_paths; print(get_paths()["purelib"])')

# ------------------------------------------------------------------------------
# HTCondor-CE client files
# ------------------------------------------------------------------------------

CLIENT_BIN_FILES := \
	src/condor_ce_config_val \
	src/condor_ce_hold \
	src/condor_ce_info_status \
	src/condor_ce_job_router_info \
	src/condor_ce_off \
	src/condor_ce_on \
	src/condor_ce_ping \
	src/condor_ce_q \
	src/condor_ce_qedit \
	src/condor_ce_reconfig \
	src/condor_ce_release \
	src/condor_ce_reschedule \
	src/condor_ce_restart \
	src/condor_ce_rm \
	src/condor_ce_run \
	src/condor_ce_scitoken_exchange \
	src/condor_ce_status \
	src/condor_ce_submit \
	src/condor_ce_trace \
	src/condor_ce_version

CLIENT_PYTHON_FILES := \
	src/htcondorce/__init__.py \
	src/htcondorce/info_query.py \
	src/htcondorce/tools.py

CLIENT_SHARE_FILES := \
	config/ce-status.cpf \
	config/pilot-status.cpf \
	src/condor_ce_create_password \
	src/condor_ce_env_bootstrap \
	src/condor_ce_startup \
	src/condor_ce_startup_internal \
	src/verify_ce_config.py

CLIENT_CONFIG_FILES := \
	config/condor_config \
	config/condor_mapfile

CLIENT_DEFAULT_CONFIG_FILES := \
	config/01-common-auth-defaults.conf \
	config/01-common-collector-defaults.conf

CLIENT_DEFAULT_MAP_FILES := \
	config/mapfiles.d/50-common-default.conf

# ------------------------------------------------------------------------------
# Compute Entrypoint files
# ------------------------------------------------------------------------------

CE_PYTHON_FILES         := src/htcondorce/audit_payloads.py

CE_SYSCONFIG_FILES	:= config/condor-ce

CE_TMPFILE_FILES	:= config/condor-ce.conf

CE_BIN_FILES := \
	src/condor_ce_history \
	src/condor_ce_host_network_check \
	src/condor_ce_register \
	src/condor_ce_router_q

CE_SERVICE_FILES := \
	config/condor-ce.service \
	contrib/apelscripts/condor-ce-apel.service \
	contrib/apelscripts/condor-ce-apel.timer

CE_SHARE_FILES := \
	src/condor_ce_router_defaults \
	src/gratia_cleanup.py \
	src/local-wrapper \
	contrib/apelscripts/condor_batch_blah.sh \
	contrib/apelscripts/condor_ce_apel.sh \
	contrib/bdii/htcondor-ce-provider \
	contrib/bosco/bosco-cluster-remote-hosts.py \
	contrib/bosco/bosco-cluster-remote-hosts.sh

CE_USER_MAP_FILES := \
	config/uid_acct_group.map \
	config/x509_acct_group.map

CE_CONFIG_FILES := \
	config/01-ce-auth.conf \
	config/01-ce-router.conf \
	config/01-pilot-env.conf \
	config/02-ce-bosco.conf \
	config/02-ce-condor.conf \
	config/02-ce-lsf.conf \
	config/02-ce-pbs.conf \
	config/02-ce-sge.conf \
	config/02-ce-slurm.conf \
	config/03-managed-fork.conf \
	contrib/apelscripts/50-ce-apel.conf

CE_DEFAULT_CONFIG_FILES := \
	config/01-ce-audit-payloads-defaults.conf \
        config/01-ce-auth-defaults.conf \
        config/01-ce-router-defaults.conf \
        config/01-pilot-env-defaults.conf \
	config/02-ce-bosco-defaults.conf \
	config/02-ce-condor-defaults.conf \
	config/02-ce-lsf-defaults.conf \
	config/02-ce-pbs-defaults.conf \
	config/02-ce-sge-defaults.conf \
	config/02-ce-slurm-defaults.conf \
	config/03-managed-fork-defaults.conf \
        config/05-ce-health-defaults.conf \
	contrib/apelscripts/50-ce-apel-defaults.conf

CE_MAP_FILES := \
	config/mapfiles.d/10-gsi.conf \
	config/mapfiles.d/10-scitokens.conf \
	config/mapfiles.d/50-gsi-callout.conf

CE_CONDOR_CONFIG_FILES := \
	config/50-condor-ce-defaults.conf \
	contrib/apelscripts/50-condor-apel.conf \
	contrib/bdii/50-ce-bdii-defaults.conf \
	contrib/bdii/99-ce-bdii.conf

CE_APEL_README_FILES := contrib/apelscripts/README.md

# ------------------------------------------------------------------------------
# Central Collector files
# ------------------------------------------------------------------------------

COLL_HTTP_FILES		:= config/htcondorce_registry.conf

COLL_SERVICE_FILES	:= config/condor-ce-collector.service

COLL_SHARE_FILES	:= src/condor_ce_create_password

COLL_SYSCONFIG_FILES	:= config/condor-ce-collector

COLL_TMPFILE_FILES	:= config/condor-ce-collector.conf

COLL_WSGI_FILES		:= src/htcondor-ce-registry.wsgi

COLL_CONFIG_FILES	:= config/01-ce-collector.conf

COLL_DEFAULT_CONFIG_FILES := \
	config/01-ce-auth-defaults.conf \
	config/01-ce-collector-defaults.conf \
	config/01-ce-collector-requirements.conf \
	config/05-ce-collector-auth.conf

COLL_DEFAULT_MAP_FILES := \
	config/mapfiles.d/50-central-collector.conf

# ------------------------------------------------------------------------------
# HTCondor-CE View files
# ------------------------------------------------------------------------------

VIEW_METRIC_DIR := config/metrics.d
VIEW_STATIC_DIR := src/htcondorce/static
VIEW_TEMPLATE_DIR := templates

VIEW_PYTHON_FILES :=  \
	src/htcondorce/registry.py \
	src/htcondorce/rrd.py \
	src/htcondorce/web.py \
	src/htcondorce/web_utils.py

VIEW_SHARE_FILES := \
	src/condor_ce_jobmetrics \
	src/condor_ce_metric \
	src/condor_ce_view

VIEW_PLUGIN_FILES := src/htcondorce/plugins/agis_json.py

VIEW_CONFIG_FILES := \
	config/05-ce-health.conf \
	config/05-ce-view.conf \
	config/05-ce-view-table.nonosg.conf \
	config/05-ce-view-table.osg.conf

VIEW_DEFAULT_CONFIG_FILES := \
	config/05-ce-view-defaults.conf \
	config/05-ce-view-table-defaults.nonosg.conf \
	config/05-ce-view-table-defaults.osg.conf \

# ------------------------------------------------------------------------------
# HTCondor-CE Python files
# ------------------------------------------------------------------------------

PYTHON_FILES := \
	contrib/bosco/bosco-cluster-remote-hosts.py \
        contrib/bdii/htcondor-ce-provider \
        src/verify_ce_config.py \
        src/condor_ce_view \
        src/condor_ce_trace \
        src/condor_ce_run \
        src/condor_ce_register \
        src/condor_ce_host_network_check \
        src/condor_ce_info_status \
        src/condor_ce_jobmetrics \
        src/condor_ce_router_defaults \
        src/condor_ce_scitoken_exchange \
        src/gratia_cleanup.py \
        src/condor_ce_metric \
        src/collector_to_agis \
	src/htcondorce/*.py

# ------------------------------------------------------------------------------

.PHONY: _default _mkdirs _view client entrypoint collector install check

_default:
	@echo "There is no default target; choose one of the following:"
	@echo "make client DESTDIR=path		-- install client files to path"
	@echo "make entrypoint DESTDIR=path     -- install compute entrypoint files to path"
	@echo "make collector DESTDIR=path	-- install central collector files to path"
	@echo "make install DESTDIR=path	-- install all files to path"
	@echo "make check			-- use pylint to check for errors"

# The EL7 version of 'install' doesn't create the dir specified by
# --target-directory when specifying -D so we have to do it ourselves
_mkdirs:
	@echo ""
	@echo "Installing HTCondor-CE directories"
	@echo "==================================="
	@echo ""

	mkdir -p $(DESTDIR)/$(INSTALL_BIN_DIR)
	mkdir -p $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/{apel,ceview-plugins,config.d,mapfiles.d,plugins,templates}
	mkdir -p $(DESTDIR)/$(INSTALL_PYTHON_DIR)/htcondorce/static
	mkdir -p $(DESTDIR)/$(INSTALL_WSGI_DIR)/htcondor-ce/

	mkdir -p $(DESTDIR)/$(INSTALL_LIB_DIR)/systemd/system
	mkdir -p $(DESTDIR)/$(INSTALL_LIB_DIR)/tmpfiles.d

	mkdir -p $(DESTDIR)/$(INSTALL_STATE_DIR)/lib/condor-ce/{execute,spool}
	mkdir -p $(DESTDIR)/$(INSTALL_STATE_DIR)/lib/condor-ce/spool/ceview/{metrics,vos}
	mkdir -p $(DESTDIR)/$(INSTALL_STATE_DIR)/lib/gratia/condorce_data  # TODO: Move this folder ownership to the osg-ce packaging
	mkdir -p $(DESTDIR)/$(INSTALL_STATE_DIR)/{lock,log}/condor-ce/user
	mkdir -p $(DESTDIR)/$(INSTALL_STATE_DIR)/run/condor-ce/

	mkdir -p $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/condor/config.d/
	mkdir -p $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/condor-ce/{config.d,mapfiles.d,metrics.d,passwords.d,tokens.d,webapp.tokens.d}
	mkdir -p $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/httpd/conf.d/
	mkdir -p $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/sysconfig

_view: _mkdirs
	@echo ""
	@echo "Installing HTCondor-CE View files"
	@echo "================================="
	@echo ""

	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/condor-ce/config.d/		$(VIEW_CONFIG_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/condor-ce/metrics.d/		$(VIEW_METRIC_DIR)/*

	install -p -m 0755 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/			$(VIEW_SHARE_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/ceview-plugins/	$(VIEW_PLUGIN_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/config.d/		$(VIEW_DEFAULT_CONFIG_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/templates/		$(VIEW_TEMPLATE_DIR)/*

	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_PYTHON_DIR)/htcondorce/			$(VIEW_PYTHON_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_PYTHON_DIR)/htcondorce/static		$(VIEW_STATIC_DIR)/*

client: _mkdirs
	@echo ""
	@echo "Installing HTCondor-CE client files"
	@echo "==================================="
	@echo ""
	install -p -m 0755 -D -t $(DESTDIR)/$(INSTALL_BIN_DIR)/					$(CLIENT_BIN_FILES)
	install -p -m 0755 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/			$(CLIENT_SHARE_FILES)

	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/condor-ce/			$(CLIENT_CONFIG_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/config.d/		$(CLIENT_DEFAULT_CONFIG_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/mapfiles.d/		$(CLIENT_DEFAULT_MAP_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_PYTHON_DIR)/htcondorce/		 	$(CLIENT_PYTHON_FILES)

entrypoint: client _view
	@echo ""
	@echo "Installing Compute Entrypoint files"
	@echo "==================================="
	@echo ""

	install -p -m 0755 -D -t $(DESTDIR)/$(INSTALL_BIN_DIR)/				$(CE_BIN_FILES)
	install -p -m 0755 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/ 		$(CE_SHARE_FILES)

	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/condor/config.d/	$(CE_CONDOR_CONFIG_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/condor-ce/ 		$(CE_USER_MAP_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/condor-ce/config.d/	$(CE_CONFIG_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/condor-ce/mapfiles.d/	$(CE_MAP_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/sysconfig/		$(CE_SYSCONFIG_FILES)

	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/apel		$(CE_APEL_README_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/config.d/	$(CE_DEFAULT_CONFIG_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_PYTHON_DIR)/htcondorce/		$(CE_PYTHON_FILES)

	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_LIB_DIR)/systemd/system/		$(CE_SERVICE_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_LIB_DIR)/tmpfiles.d/		$(CE_TMPFILE_FILES)

	sed -i -e 's/@HTCONDORCE_VERSION@/$(VERSION)/g' \
		$(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/config.d/01-ce-router-defaults.conf

collector: client _view
	@echo ""
	@echo "Installing Central Collector files"
	@echo "=================================="
	@echo ""

	install -p -m 0755 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/			$(COLL_SHARE_FILES)

	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/condor-ce/config.d/		$(COLL_CONFIG_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/httpd/conf.d/		$(COLL_HTTP_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SYSCONF_DIR)/sysconfig/			$(COLL_SYSCONFIG_FILES)

	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_LIB_DIR)/systemd/system/			$(COLL_SERVICE_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_LIB_DIR)/tmpfiles.d/			$(COLL_TMPFILE_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_WSGI_DIR)/htcondor-ce/			$(COLL_WSGI_FILES)

	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/config.d/		$(COLL_DEFAULT_CONFIG_FILES)
	install -p -m 0644 -D -t $(DESTDIR)/$(INSTALL_SHARE_DIR)/condor-ce/mapfiles.d/		$(COLL_DEFAULT_MAP_FILES)


install: client _view entrypoint collector

check:
	pylint -E $(PYTHON_FILES)
