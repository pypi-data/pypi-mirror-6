# conf.py
import os
import json
import yaml


def merge_conf(to_hash, other_hash, path=[]):
    "merges other_hash into to_hash"
    for key in other_hash:
        if (key in to_hash and isinstance(to_hash[key], dict)
                and isinstance(other_hash[key], dict)):
            merge_conf(to_hash[key], other_hash[key], path + [str(key)])
        else:
            to_hash[key] = other_hash[key]
    return to_hash


def parse_conf_file(conf_file_path):

    ext = os.path.splitext(conf_file_path)[1]
    if ext == ".json":
        return json.load(open(conf_file_path))
    elif ext == ".yaml" or ext == ".yml":
        return yaml.load(open(conf_file_path))
    else:
        raise Exception("Unsupported conf file kind", conf_file_path)
