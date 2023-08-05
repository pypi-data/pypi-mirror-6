# -*- coding: utf-8 -*-

import sh
import traceback

import os,sys
import imp

from .helpers import skel_clone, skel_cleansurplus, skel_cleangit

from jinja2 import FileSystemLoader, Environment

from blessings import Terminal

term = Terminal()

def skeleton_create( skeleton,
                     project,
                     skel_vars=None ):
    """
        Create a project using the given <skeleton>,
        saving it as <project>, and using
        vars as the configuration.

        Returns a tuple containing (success, description)
    """
    project_abspath = os.path.abspath( project )
    skelvars        = skel_vars or dict()

    # If local git Repository
    if os.path.isdir( skeleton ):
        skeleton = os.path.abspath( skeleton )

    # Clone
    print "Cloning %s into %s" % (term.underline(skel['url']), term.bold(project_abspath))
    skeleton_clone( skeleton , project_abspath )

    # Make the setup
    (success,tb ) = skeleton_runsetup( project_abspath , skel_vars=skel_vars )

    if not success:
        print tb
        print "%s\n%s" % (term.red('ERROR!!'), tb )
    else:
        print "%s\n" % (term.green('SUCCESS!!'))

    return (success, tb)




def skeleton_clone( skeleton, project ):
    """
        Perform a clean clone of <skeleton>, saving it as <project>
    """
    # Make a clone
    np_repository = skel_clone( outpath=project, repo=skeleton )

    # Clean git repo
    skel_cleangit( project )

    return np_repository






def skeleton_runsetup( project_abspath, skel_vars=None):
    """

        Run the setup of the skeleton. Returns a tuple
        containing (Success, Description)

    """
    skel_vars = skel_vars or dict()

    (success,tb) = (True, '')
    try:
        py_package = ( os.path.join( project_abspath, '__init__.py') )
        if not os.path.exists( py_package ):
            sh.touch( py_package )

        # Get the module
        skel_setup_file = os.path.join( project_abspath, 'dlbuild.py')
        skel_setup_mod  = imp.load_source( 'skel_setup', skel_setup_file )

        # Get the SKELETON_SETTINGS, and merge with defaults
        skel_vars_default = {'SKEL_ROOT': project_abspath,
                             'PROJECT':   os.path.split( project_abspath)[-1] }
        skel_vars         = dict()
        try:
            skel_vars_module = skel_setup_mod.SKELETON_SETTINGS

            for k,v in skel_vars_module.iteritems():
                if callable(v):
                    skel_vars_module[k] = v()

            # Merge skel_vars_default with skel_vars
            skel_vars = dict( skel_vars_default.items() + skel_vars_module.items() )

        except AtrributeError:
            skel_vars = dict( skel_vars_default.items() )

        # Create a jinja2 Loader/Context
        jinja_loader = FileSystemLoader( project_abspath )
        jinja_env    = Environment( loader=jinja_loader )

        # CD To new proj dir
        pwd = os.getcwd()
        os.chdir( project_abspath )

        # Join skel_vars
        # Run function setup with <SKEL_VARS>
        skel_setup_mod.setup( skel_vars=skel_vars , jinja_env=jinja_env )

        # Clean files
        skel_cleansurplus( project_abspath )

        # back2back
        os.chdir( pwd )

    except IOError:
        success = True
        tb  = 'Skipped skeleton setup.py...'
    except:
        success = False
        tb = traceback.format_exc()
    else:
        success = True
        tb = 'Running skeleton setup... SUCCESS'
    finally:
        return (success, tb)
