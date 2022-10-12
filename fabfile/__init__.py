import sys

if 'fab' in sys.argv[0]:
    from edc_fabric import fabfile as common
    from edc_fabric.fabfile import cut_releases, generate_requirements
    from edc_fabric.fabfile import clone_repos
