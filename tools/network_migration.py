import argparse, shelve

def renameDictKeys(storageDict):
    for key in storageDict.iterkeys():
        if isinstance(storageDict[key], dict):
            renameDictKeys(storageDict[key])
        if key == options.oldnetwork:
            storageDict[options.newnetwork] = storageDict[options.oldnetwork]
            del storageDict[options.oldnetwork]

if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="A tool for PyHeufyBot to migrate all storage data from one network "
                                                 "to another.")
    parser.add_argument("-s", "--storage", help="The storage file to use", type=str, default="../heufybot.db")
    parser.add_argument("-o", "--oldnetwork", help="The name of the old network that the data should be migrated "
                                                   "from.", type=str, required=True)
    parser.add_argument("-n", "--newnetwork", help="The name of the new network that the data should be migrated to.",
                        type=str, required=True)
    options = parser.parse_args()

    storage = shelve.open(options.storage)
    d = dict(storage)
    renameDictKeys(d)
    storage.clear()
    storage.update(d)

    storage.close()
    print "Data has been migrated from '{}' to '{}'.".format(options.oldnetwork, options.newnetwork)
