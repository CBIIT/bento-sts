import subprocess


def get_yaml_for(model):

    result = subprocess.run(["perl", "-X", "../Bento-STS-CLI/bin/yaml.pl", '-model', model], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')
