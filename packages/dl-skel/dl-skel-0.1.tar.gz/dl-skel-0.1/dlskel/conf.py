from kaptan import Kaptan
from blessings import Terminal

import os
from os.path import join, dirname, exists, expanduser

DEFAULT_CONFIG =  {
    'SKELETONS': [
        {
         'name':        'wordpress5',
         'description': 'Wordpress 5.0 Skeleton',
         'url':         'git@github.com:doubleleft/skeleton-wordpress.git'
        },
        {
         'name':        'htmlrichapp',
         'description': 'HTML Rich App (grunt/bower/stylus)',
         'url':         'git@github.com:doubleleft/skeleton-htmlrichapp.git'
        }
    ]
}

conf = Kaptan(handler='json')
t = Terminal()

# Load config
def load_config(conf_file):
    """
        Load the conf file, returns a DICT or None
    """
    fp = expanduser( conf_file )

    conf.import_config( fp )

    return conf

def save_config( conf_file ):
    """
        Save the config file
    """
    fp = expanduser( conf_file )
    f = file( fp , 'w' )
    json = conf.export('json', indent=4,)
    f.write( json )
    f.close()


def bootstrap_dlskel( skel_path , force=False):
    """
        Create the basic structure of dlskel folder
    """
    fp = expanduser( skel_path )
    folder_exists =  exists( fp )
    if not folder_exists:
        os.makedirs( fp )

    # Create the folder to store skeletons
    skel_exists = exists( join(fp, 'skeletons'))
    if not skel_exists:
        os.makedirs( join( fp , 'skeletons' ) )

    # Create basic config
    if not exists( join(fp, 'config.json') ):
        conf.import_config(DEFAULT_CONFIG)
        save_config( join(fp, 'config.json') )
