
from htcondorce.registry import create_app

# Uncomment one-or-more options to customize the webapp
# Most of these options are useful for running the HTCondor-CE Registry webapp
# out of a custom HTCondor (or HTCondor-CE) install.
test_config={
  #'CONDOR_TOKEN_REQUEST_LIST': '/home/example/condor-build/release_dir/bin/condor_token_request_list',
  #'HTCONDORCE_TEMPLATES': '/home/cse496/example/htcondor-ce/templates',
  #'DEBUG': True
}
if not test_config:
    test_config = None

application = create_app(test_config=test_config)
