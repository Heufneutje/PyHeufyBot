import argparse, shelve


if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="API key tool for PyHeufyBot.")
    parser.add_argument("-s", "--storage", help="The storage file to use", type=str, default="../heufybot.db")
    parser.add_argument("-k", "--key", help="The API key type to modify", type=str, required=True)
    parser.add_argument("-v", "--value", help="The value of the API key", type=str, required=True)
    options = parser.parse_args()

    storage = shelve.open(options.storage)
    if "api-keys" not in storage:
        storage["api-keys"] = {}
    keys = storage["api-keys"]
    keys[options.key] = options.value
    storage["api-keys"] = keys
    storage.close()
    print "Key '{}' with value '{}' has been added to the API keys.".format(options.key, options.value)
