import os
import re
import sys
import getpass
import argparse
import scm
from .repositories import download_file
from .repositories import create_repository
from .repositories import update_repository
from .repositories import delete_repository
from .repositories import get_user_repos
from .repositories import set_privilege
from .config import USERNAME, PASSWORD, SCM, PROTOCOL
from requests.exceptions import HTTPError
from requests.status_codes import _codes as status_codes


def password(func):
    # very basic password input
    def decorator(args):
        if not args.username:
            args.username = raw_input('username: ')
        if not args.password:
            args.password = getpass.getpass('password: ')
        func(args)
    return decorator


def display_repo_info(repo_info):
    repo_info['private'] = '-' if repo_info['is_private'] else '+'
    print '[{private}{scm: >4}] {owner}/{slug}'.format(**repo_info)


@password
def create_command(args):
    result = create_repository(args.reponame,
                               args.username,
                               args.password,
                               args.scm,
                               args.private,
                               args.owner)
    print ''
    print 'Repository successfully created.'
    display_repo_info(result)


@password
def update_command(args):
    result = update_repository(args.username,
                      args.reponame,
                      args.password,
                      is_private=args.private)
    print ''
    print 'Repository successfully updated.'
    display_repo_info(result)


@password
def delete_command(args):
    delete_repository(args.username,
                               args.reponame,
                               args.password)
    print '{0}/{1} was deleted.'.format(args.username, args.reponame)


@password
def clone_command(args):
    scm.clone(args.protocol,
              args.ownername,
              args.reponame,
              args.username,
              args.password)


def pull_command(args):
    scm.pull(args.protocol,
             args.ownername,
             args.reponame)


@password
def create_from_local(args):
    scm_type = scm.detect_scm()
    if scm_type:
        reponame = os.path.basename(os.getcwd()).lower()
        create_repository(reponame, args.username, args.password,
                          scm_type, args.private, args.owner)
        scm.add_remote(args.protocol, args.username, reponame)
        scm.push_upstream()
    else:
        print ('Could not detect a git or hg repo in your current directory.')

def add_remote(args):
    scm.add_remote(args.protocol, args.username, args.reponame,
                    args.remotename)

def download_command(args):
    download_file(args.ownername, args.reponame, args.filename,
                  args.username, args.password)
    print "Successfully downloaded " + args.filename


@password
def list_command(args):
    response = get_user_repos(args.username, args.password)
    repo_count = 0
    filters = []
    # filter for public and/or private repo
    filters.append(lambda repo: (args.list_public and not repo.get('is_private', False)) or
                                (args.list_private and repo.get('is_private', False)) or
                                (args.list_public == args.list_private))
    # filter for type of repository
    filters.append(lambda repo: args.scm == 'all' or repo['scm'] == args.scm)
    # filter name on regular expression
    exp = re.compile(args.expression, re.IGNORECASE)
    filters.append(lambda repo: exp.search(repo['name']))

    for repo in response:
        if all([filter(repo) for filter in filters]):
            repo_count += 1
            display_repo_info(repo)

    print '{0} repositories listed'.format(repo_count)


@password
def privilege_command(args):
    set_privilege(args.ownername, args.reponame, args.privilege,
                  args.privilege_account, args.username, args.password)


def run():
    # root command parser
    p = argparse.ArgumentParser(description='Interact with BitBucket',
            usage='bitbucket <command> [<args>]',
            epilog='See `bitbucket <command> --help` for more information on a specific command.')

    def add_standard_args(parser, args_to_add):
        # each command has a slightly different use of these arguments,
        # therefore just add the ones specified in `args_to_add`.
        if 'username' in args_to_add:
            parser.add_argument('--username', '-u', default=USERNAME,
                            help='your bitbucket username')
        if 'password' in args_to_add:
            parser.add_argument('--password', '-p', default=PASSWORD,
                            help='your bitbucket password')
        if 'owner' in args_to_add:
            parser.add_argument('--owner', '-w', default='',
                            help='repository owner')
        if 'private' in args_to_add:
            parser.add_argument('--private', '-c', action='store_true',
                            dest='private',
                            default=True,
                            help='make this repo private')
        if 'public' in args_to_add:
            parser.add_argument('--public ', '-o', action='store_false',
                            dest='private',
                            default=True,
                            help='make this repo private')
        if 'scm' in args_to_add:
            parser.add_argument('--scm', '-s', default=SCM,
                            help='which scm to use (git|hg)')
        if 'protocol' in args_to_add:
            parser.add_argument('--protocol', '-P', default=PROTOCOL,
                            help=('which network protocol '
                                  'to use (https|ssh)'))
        if 'ownername' in args_to_add:
            parser.add_argument('ownername',
                            type=str,
                            help='bitbucket account name')
        if 'reponame' in args_to_add:
            parser.add_argument('reponame',
                            type=str,
                            help='the bitbucket repository name')
        parser.add_argument('--debug', action='store_true', default=False)

    command_names = ('create', 'update', 'delete', 'clone', 'create_from_local',
                     'pull', 'download', 'list', 'privilege')
    # SUBPARSER
    subp = p.add_subparsers(title='Commands', metavar='\n  '.join(command_names))

    # CREATE COMMAND PARSER
    create_cmd_parser = subp.add_parser('create',
                        usage=('bitbucket create [-h] [--username USERNAME]\n'
                               '                        [--password PASSWORD] [--private | --public]\n'
                               '                        [--scm SCM] [--protocol PROTOCOL]\n'
                               '                        [--owner OWNER]\n'
                               '                        reponame'),
                        description='create a new bitbucket repository')
    add_standard_args(create_cmd_parser,
                      ('username',
                       'password',
                       'protocol',
                       'private',
                       'public',
                       'scm',
                       'owner',
                       'reponame'))
    create_cmd_parser.set_defaults(func=create_command)

    #
    # UPDATE COMMAND PARSER
    #
    update_cmd_parser = subp.add_parser('update',
                            usage=('bitbucket update [-h] [--username USERNAME]\n'
                                   '                        [--password PASSWORD]\n'
                                   '                        [--private | --public]\n'
                                   '                        reponame'),
                            description='update an existing bitbucket repository')
    add_standard_args(update_cmd_parser,
                      ('username',
                       'password',
                       'private',
                       'public',
                       'reponame'))
    update_cmd_parser.set_defaults(func=update_command)

    #
    # DELETE COMMAND PARSER
    #
    delete_cmd_parser = subp.add_parser('delete',
                            usage=('bitbucket delete [-h] [--username USERNAME]\n'
                                   '                        [--password PASSWORD]\n'
                                   '                        reponame'),
                            description='delete an existing bitbucket repository')
    add_standard_args(delete_cmd_parser,
                      ('username',
                       'reponame',
                       'password'))
    delete_cmd_parser.set_defaults(func=delete_command)

    #
    # CLONE COMMAND PARSER
    #
    clone_cmd_parser = subp.add_parser('clone',
                            usage=('bitbucket clone [-h] [--username USERNAME]\n'
                                   '                        [--password PASSWORD]\n'
                                   '                        [--protocol PROTOCOL]\n'
                                   '                        ownername\n'
                                   '                        reponame'),
                            description='clone a bitbucket repository')
    add_standard_args(clone_cmd_parser,
                      ('username',
                       'password',
                       'protocol',
                       'ownername',
                       'reponame'))
    clone_cmd_parser.set_defaults(func=clone_command)

    #
    # PULL COMMAND PARSER
    #
    pull_cmd_parser = subp.add_parser('pull',
                            usage=('bitbucket pull [-h] [--protocol PROTOCOL]\n'
                                   '                        ownername\n'
                                   '                        reponame'),
                            description='pull....')
    add_standard_args(pull_cmd_parser,
                      ('protocol',
                       'ownername',
                       'reponame'))
    pull_cmd_parser.set_defaults(func=pull_command)

    #
    # CREATE-FROM-LOCAL COMMAND PARSER
    #
    create_from_local_cmd_parser = subp.add_parser('create_from_local',
                            usage=('bitbucket create_from_local [-h]\n'
                                   '                        [--username USERNAME]\n'
                                   '                        [--password PASSWORD] [--private | --public]\n'
                                   '                        [--scm SCM] [--protocol PROTOCOL]\n'
                                   '                        [--owner OWNER]\n'),
                            description='create a bitbucket repo from existing local repo')
    add_standard_args(create_from_local_cmd_parser,
                      ('username',
                       'password',
                       'protocol',
                       'private',
                       'scm',
                       'owner'))
    create_from_local_cmd_parser.set_defaults(func=create_from_local)

    #
    # DOWNLOAD COMMAND PARSER
    #
    download_cmd_parser = subp.add_parser('download',
                            usage=('bitbucket download [-h] [--username USERNAME]\n'
                                   '                        [--password PASSWORD]\n'
                                   '                        ownername\n'
                                   '                        reponame\n'
                                   '                        filename'),
                            description='download a file from a bitbucket repo')
    add_standard_args(download_cmd_parser,
                      ('username',
                       'password',
                       'ownername',
                       'reponame'))
    download_cmd_parser.add_argument('filename', type=str,
                                     help='the file you want to download')
    download_cmd_parser.set_defaults(func=download_command)

    #
    # LIST COMMAND PARSER
    #
    list_cmd_parser = subp.add_parser('list',
                            usage=('bitbucket list [-h] [--username USERNAME]\n'
                                   '                      [--password PASSWORD]\n'
                                   '                      [--public]\n'
                                   '                      [--private]\n'
                                   '                      [--scm SCM]\n'
                                   '                      [--expression EXPRESSION]'),
                            description='list all bitbucket repos')
    add_standard_args(list_cmd_parser,
                      ('username',
                       'password'))
    list_cmd_parser.set_defaults(func=list_command)
    list_cmd_parser.add_argument('--private', '-c', action='store_true',
              dest='list_private',
              default=False,
              help='list private repositories only.')
    list_cmd_parser.add_argument('--public ', '-o', action='store_true',
              dest='list_public',
              default=False,
              help='list public repositories only.')
    list_cmd_parser.add_argument('--scm', '-s', default='all',
              help='list only the given scm (git|hg)')
    list_cmd_parser.add_argument('--expression', '-e', default='.*',
              help='list only repository names matching expression')


    #
    # PRIVILEGE COMMAND PARSER
    #
    privilege_cmd_parser = subp.add_parser('privilege',
                            usage=('bitbucket privilege [-h]\n'
                                   '                    [--username USERNAME]\n'
                                   '                    [--password PASSWORD]\n'
                                   '                    ownername\n'
                                   '                    reponame\n'
                                   '                    privilege_account\n'
                                   '                    privilege'),
                            description='update account privilege on an existing repo')
    add_standard_args(privilege_cmd_parser,
                      ('username',
                       'password',
                       'ownername',
                       'reponame'))
    privilege_cmd_parser.add_argument('privilege_account', type=str,
                                      help='the account you want to change')
    privilege_cmd_parser.add_argument('privilege', choices=['read', 'write', 'admin', 'none'],
                                      help='the privilege to grant')
    privilege_cmd_parser.set_defaults(func=privilege_command)

    #
    # Add Remote Command
    #

    add_remote_cmd_parser = subp.add_parser('add_remote',
            usage = ('bitbucket add_remote [-h]\n'
                     '                     [--username USERNAME]\n'
                     '                     [--password PASSWORD]\n'
                     '                     ownername\n'
                     '                     reponame\n'
                     '                     [--protocol PROTOCOL]\n'
                     '                     [--remote REMOTE]\n'),
                     description='add remote url')
    add_standard_args(add_remote_cmd_parser,
                        ('username', 'password',
                         'ownername', 'reponame',
                         'protocol'))
    add_remote_cmd_parser.add_argument('--remote', '-r',
                    dest='remotename', default='origin',
                    help = 'the name of the remote')
    add_remote_cmd_parser.set_defaults(func=add_remote)

    def debug_print_error(args):
        if args and args.debug:
            import traceback
            print '-' * 60
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_tb(exc_tb)
            print '-' * 60

    def print_http_error(ex):
        import re
        http_err_code = ex.response.status_code
        http_err = status_codes.get(http_err_code, [''])[0]
        print '\nRequest Error {0}: {1}'.format(http_err_code, http_err.replace('_', ' '))
        # Errros are being sent back as html, so let's strip
        # out the markup to make it a bit more readable on the
        # commandline.
        msg = re.sub('\<[^\>]+\>', ' ', ex.response.content)
        msg = re.sub(' +', ' ', msg)
        msg = msg.strip()
        if msg:
            print msg

    args = None
    exit_code = 0

    try:
        args = p.parse_args()
        args.func(args)
    except KeyboardInterrupt:
        pass
    except HTTPError as ex:
        # If we get this, then we know it's something with requests
        print_http_error(ex)
        debug_print_error(args)
        exit_code = 1
    except Exception as ex:
        # and if we're here, then something is really wrong
        print 'Unhandled error: {0}'.format(ex)
        debug_print_error(args)
        exit_code = 2
    finally:
        sys.exit(exit_code)
