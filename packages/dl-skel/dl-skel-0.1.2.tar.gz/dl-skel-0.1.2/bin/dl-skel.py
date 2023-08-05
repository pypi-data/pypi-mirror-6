#!/usr/bin/env python
import os,sys

import optparse
import blessings

parser = optparse.OptionParser(usage='%prog [options]')
term = blessings.Terminal()

from dlskel.conf    import load_config, save_config, bootstrap_dlskel
from dlskel.skel    import skeleton_clone, skeleton_runsetup


# Some globals for now
SKEL_CONFIG = '~/.dl-skel/config.json'
SKEL_PATH   = '~/.dl-skel/'

# Do some bootstrap (Loading config first )
conf = None




# Skeleton config / update
parser.add_option('', '--skeleton-config',   dest='skelconfig',       action='store', default=SKEL_CONFIG, help=term.bold('dlskel Config file. Default is %s' % term.magenta(SKEL_CONFIG)))
parser.add_option('', '--skeleton-path',     dest='skelpath',         action='store', default=SKEL_PATH,   help=term.bold('Use another Skeleton Search Path. Default is %s' % term.magenta(SKEL_PATH)))

# Options
parser.add_option('-l', '--list',     dest='list_mode',         action='store_true',    help=term.bold('List skeletons'))



# Import group
import_arg_group = optparse.OptionGroup( parser, 'Import new Template')
import_arg_group.add_option('-i', '--import',  dest='import_template',   action='store', nargs=2, metavar='<GIT_REPO> <TEMPLATE_NAME>', help=term.bold("import a new template from the given GIT repository."))

# Create new project group
create_arg_group  = optparse.OptionGroup( parser, 'Create a new project')
create_arg_group.add_option('-c', '--create',   dest='create_project',      action='store', nargs=2, metavar='<TEMPLATE_NAME> <OUTPUT>',   help=term.bold("Create a new <project> skeleton"))





def parse_args():
    parser.add_option_group(import_arg_group)
    parser.add_option_group(create_arg_group)

    (opts,args) = parser.parse_args()
    global SKEL_CONFIG, SKEL_PATH, conf

    # Overwrite config paths
    if opts.skelconfig:
        SKEL_CONFIG = opts.skelconfig
    elif opts.skelpath:
        SKEL_PATH = opts.skelpath

    # Bootstrap (if necessary)
    try:
        conf = load_config( SKEL_CONFIG )
    except:
        print 'Bootstrapping config at %s' % term.magenta( SKEL_PATH )
        bootstrap_dlskel( SKEL_PATH )
        conf = load_config( SKEL_CONFIG )

    # launch actions
    if opts.list_mode:
        list_skeletons()

    # import a new
    elif opts.import_template:

        #
        (repo_url, template_name) = opts.import_template

        # Lets see if its local or remote
        if os.path.isdir(repo_url):
            repo_url = os.path.abspath( repo_url )

        new_skel = dict(name=template_name, url = repo_url )

        all_skeletons = conf.get("SKELETONS")
        all_skeletons.append( new_skel )

        conf.upsert('SKELETONS', all_skeletons)
        save_config( SKEL_CONFIG )
        print "Imported %s sucessfully"  % (term.bold(template_name))
        #print conf.export('json', indent=4)

    elif opts.create_project is not None:

        (projname,outdir) = opts.create_project
        outdir            = os.path.abspath(outdir)

        skel = get_skel_metadata( projname )
        if not skel:
            print "Skeleton template %s does not exist..." %  term.magenta(opts.project)
            sys.exit(-1)

        print "Cloning %s(%s) into %s" % (term.magenta(skel['name']), term.underline(skel['url']), term.bold(outdir))
        repo = skeleton_clone( skel['url'] , outdir )

        # Now we do the substitutions/other steps
        skel_vars = conf.get('CONFIG', dict())
        (success, tb) = skeleton_runsetup( outdir, skel_vars=skel_vars )

        if not success:
            print '%s\n%s' % (term.red('ERROR!!'), tb )
        else:
            print '%s\n' % (term.green('SUCCESS!!'))


    else:
        print parser.print_help()



def list_skeletons():
    """ List available skeletons """
    skeleton_list = conf.get('SKELETONS')
    for skel in skeleton_list:
        print '%s\t\t%s\t%s' % ( term.magenta(skel.get('name','')) , \
                                 term.underline(skel.get('url','')) , \
                                 term.bold( skel.get('description','') ) )




def get_skel_metadata(name):
    """
        Given a name, returns the skeleton metadata.
        Returns None if skeleton not found
    """

    skel = [skel for skel in conf.get('SKELETONS') if skel['name'] == name]
    return (skel and skel[0] or None)





if __name__ == '__main__':
    parse_args()
