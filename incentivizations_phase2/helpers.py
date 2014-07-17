#This file contains a few different helper functions that could be useful across the application

def get_config(filename):
    '''
    Gets all keys/values from config file
    @param filename: name of config file
    @type filename: String
    @return: dictionary of type {key:value} from config
    '''
    config = {}
    lines = [line.strip() for line in open(filename)]
    for line in lines:
        if len(line) == 0 or line[0] == "#":
            continue
        else:
            parts = line.split(":")
            config[parts[0]] = parts[1]
    return config

def get_userpasses(user_password_file_path):
  userpassfile = open(user_password_file_path, 'r')
  emailuserpass = userpassfile.readline().strip('\n').strip().split(':')
  apiuserpass = userpassfile.readline().strip('\n').strip().split(':')
  userpassfile.close()
