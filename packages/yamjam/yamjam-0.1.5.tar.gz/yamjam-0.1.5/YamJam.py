#!/usr/bin/env python
''' yamjam is a unified generic config method.  It allows multiple internal
projects to share common configuration settings, keeping the information stored
in a more secure area readable only by the user.
'''
import yaml
import os

def mergeDicts(s, t):
    '''smartly merge dictionaries s and t, unlike dict.update()'''
    for k in t:
        if type(t[k]) is type({}):
            if k in s:  #if there is a similar element in s
                mergeDicts(s[k], t[k]) #merge them
            else:
                s[k] = t[k] #else no merge required, just add it in
        else:
            s[k] = t[k]
    return s

def yamjam(yjFnames='~/.yamjam/config.yaml;config.yaml', merge=True):
    '''The main yamjam config file is located ~/.yamjam/config.yaml
        on windows:  c:\documents and settings\[username]\.yamjam\config.yaml
        on unix:     ~\.yamjam\config.yam;
       Then yamjam looks for possible overrides/additions in the local
       config.yaml(if it exists)

    You can override the config file(s) when you call the function by specifying
    a different one explicitly. i.e.
        myConfig = yamjam('file/path/filename')

    By default YamJam looks for 2 config.yaml files, the main and then a project
    specific one.  You may specify one or more files. Each file path listed
    should be separated by semi-colons(;)

    merge=True - Use smart merge as compared to the dict.update() method

    The file is yaml formatted which is a superset of json.
    http://www.yaml.org/

    Every call to yamjam() re-reads the config file.  If you wish to cache the info
    then do it in the calling code. i.e.
        myConfig = yamjam()

    If you only want to cache part of the configuration
        myCfg = yamjam()['mykey']
    '''
    config = {}
    for _yjFname in [f.strip() for f in yjFnames.split(';')]:
        if os.path.exists(os.path.expanduser(_yjFname)):
            ycfg = yaml.load(open(os.path.expanduser(_yjFname),"rb").read())
            if merge:
                config = mergeDicts(config, ycfg)
            else:
                config.update(ycfg)
    return config
