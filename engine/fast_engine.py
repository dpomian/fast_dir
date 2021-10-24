import os
import json


def is_valid_name(name):
    if name and name.isalnum():
        return True
    return False


def is_valid_dir(dir_name):
    return os.path.exists(dir_name)


def add(f_dict, source, dest, update=False):
    if update:
        if dest:
            f_dict[source] = dest
            print("added {} -> {}".format(source, dest))
    else:
        if source not in f_dict:
            if dest:
                f_dict[source] = dest
                print("updated {} -> {}".format(source, dest))
            else:
                print("dest cannot be empty")
        else:
            print("fast dir {} already exists. Hint: use add --up to update".format(source))

    return f_dict


def add_new(f_dict, source, dest, tags):
    if not is_valid_name(source):
        raise ValueError("invalid source")

    if source not in f_dict:
        if dest:
            f_dict[source] = {}
            f_dict[source]["link"] = dest
        else:
            raise ValueError("dest cannot be empty")

        if tags:
            f_dict[source]["tags"] = tags.split(',')
    else:
        raise ValueError("source {} already exists. Hint: use add --up to update".format(source))

    return f_dict


def update(f_dict, source, dest, tags):
    if dest:
        f_dict[source]["link"] = dest
    if tags:
        f_dict[source]["tags"] = tags.split(',')

    return f_dict


def save(fd_dict, ofilename):
    with open(ofilename, 'w') as json_file:
        json.dump(fd_dict, json_file)


def read(ifilename):
    if not os.path.isfile(ifilename):
        with open(ifilename, 'w') as json_file:
            json.dump({}, json_file)

    with open(ifilename, "r") as myfile:
        try:
            fd_dict = json.load(myfile)
            return fd_dict
        except Exception as e:
            print(error("malformed_fd"))

    return {}


def list_all(storage):
    storage_dict = read(storage)
    for key in sorted(storage_dict.keys()):
        print('{} -> {}'.format(key, storage_dict[key]))


def view(f_dict, source):
    result = {}
    for key in sorted(f_dict.keys()):
        if source in key:
            result.update({key: f_dict[key]})
    return result
