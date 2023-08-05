# -*- coding: utf-8 -*-
"""

    General helpers

"""

import os, imp, sys, codecs
import traceback

from hashlib import sha512
from os.path import join as pathjoin

import jinja2
import sh

def skel_clone( outpath='my-new-project', repo='https://github.com/ionelmc/projectskel', vars=None):
    """ Clone a fucking skeleton """
    cl      = sh.git( 'clone', '--depth', '1', repo, outpath )
    gitrepo = sh.git.bake( _cwd=outpath )
    return gitrepo


def skel_addremote(gitrepo, remote_url):
    """
        Add a new remote to skeleton
    """
    return gitrepo.remote('add','origin', remote_url)


def skel_commit(gitrepo, msg):
    """ Make a  commit """
    return gitrepo.commit('-m',msg)



def skel_cleangit( path_of_gitrepo ):
    """ Deletes .git files, making it a clean repo """
    git_folder = pathjoin( path_of_gitrepo , '.git' )
    if os.path.exists( git_folder ):
        sh.rm('-rf', git_folder )


def skel_cleansurplus( project_path ):
    """
        Clean surplus files after successfull setup.
    """
    files = [ pathjoin( project_path , '__init__.py') , pathjoin( project_path, '__init__.pyc' ) ]
    return [ sh.rm('-rf', f_path) for f_path in files if os.path.exists( f_path ) ]



def render_file( tmpl, to='', skelvars=None):
    """
        Perform a jinja2 render of <file_in>, saving as <file_out>.
        If <file_in> == <file_out>, the original file will be overwrited.
    """
    file_out        = os.path.abspath( to )

    # Render the template
    content = tmpl.render( **skelvars )

    # Write to file as UTF8
    fp_out = codecs.open( file_out, 'w', 'utf-8')
    fp_out.write( content )
    fp_out.close()

    return True


def has_installed( program ):
    """
        Check if %program is installed on the machine.
    """
    try:
        sh.Command(program)
        return True
    except:
        return False



def install( program , manager='apt-get'):
    """
        Try to install program using the given manager
    """
    managers = { 'apt-get': ('apt-get','install'),
                 'brew':    ('brew','install'),
                 'python':  ('pip', 'install'),
                 'node':    ('npm', 'install')}

    m = managers[ manager ]
    sh.Command(m[0], m[1], program )


def make_password( length=16 ):
    """ Create a random password """
    return sha512( os.urandom(16) ).hexdigest()[:length]


def askYN(default=False, prompt='Continue?'):
    """
        Ask (prompt) if user may want this option. Only supports Y/N as
        answer, bool.
    """
    valid = {"yes": "yes",  "y": "yes", "ye": "yes", "t": "yes",  "true": "yes",
             "no":  "no",   "n": "no",  "f": "no", "false": "no"}

    opts = (default and '[Y/n]' or '[y/N]')
    def ask_func():
        while 1:
            sys.stdout.write('%s %s' % (prompt , opts))
            choice = raw_input().strip().lower()
            if default is not None and choice == '':
                return default
            elif choice in valid.keys():
                v = (valid[choice] == "yes" and True or False)
                return v
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "\
                                 "(or 'y' or 'n').\n")

    return ask_func



def askSTR(default='', prompt='Heheh'):
    """
        Asks for some string...
    """
    def ask_func():
        sys.stdout.write('%s' % prompt)
        return raw_input().strip().lower()

    return ask_func
