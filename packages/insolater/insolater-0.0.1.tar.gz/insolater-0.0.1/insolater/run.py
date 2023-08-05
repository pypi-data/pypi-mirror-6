import sys
import argparse
from insolater import Insolater


help_str = ("{cmd} init [<remote_changes>]              Starts a new session.\n" +
            "{cmd} list                                 Displays versions.\n" +
            "{cmd} save  <version>                      Save to version.\n" +
            "{cmd} rm   <version>                       Remove version.\n" +
            "{cmd} open <version>                       Switches to the requested version\n" +
            "{cmd} pull <remote_location> [<version>]   Pull remote version [to version]\n" +
            "{cmd} push <remote_location> [<version>]   Push [version] to remote location\n" +
            "{cmd} exit [<version>]                     Permanently delete all versions\n" +
            (' ' * len(Insolater._CMD)) +
            "                                           and restore original or specified version."
            ).format(cmd=Insolater._CMD)


def cli(inso, argv, force):
    try:
        if argv[0] == 'init':
            if len(argv) <= 2:
                print(inso.init(*argv[1:]))
            else:
                print("Usage: {cmd} init [remote_changes]".format(cmd=Insolater._CMD))
        elif argv[0] == 'list':
                cv = inso.current_version()
                av = inso.all_versions()
                for v in av:
                    if cv == v:
                        print('* ' + v)
                    else:
                        print('  ' + v)
        elif argv[0] == 'save':
            if len(argv) < 2:
                print("Usage: {cmd} save <version>".format(cmd=Insolater._CMD))
            else:
                print(inso.save_version(argv[1], force or None))
        elif argv[0] == 'rm':
            if len(argv) < 2:
                print("Usage: {cmd} rm <version>".format(cmd=Insolater._CMD))
            else:
                print(inso.delete_version(argv[1]))
        elif argv[0] == 'open':
            if len(argv) < 2:
                print("Usage: {cmd} open <version>".format(cmd=Insolater._CMD))
            else:
                print(inso.change_version(argv[1]))
        elif argv[0] == 'pull':
            if len(argv) < 2:
                print("Usage: {cmd} pull <remote_location [<version>]".format(cmd=Insolater._CMD))
            else:
                print(inso.pull_version(*argv[1:]))
        elif argv[0] == 'push':
            if len(argv) < 2:
                print("Usage: {cmd} push <remote_location [<version>]".format(cmd=Insolater._CMD))
            else:
                print(inso.push_version(*argv[1:]))
        elif argv[0] == 'exit':
            if len(argv) >= 2:
                print(inso.exit(argv[1], force or None))
            else:
                print(inso.exit(discard_changes=force or None))
        else:
            print("Not a {cmd} command.".format(cmd=Insolater._CMD))
            print(help_str)
    except Exception as error_msg:
        print(error_msg.message)


def main():
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] == '-h' or argv[0] == '--help':
        print(help_str)
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action='store_true',
                        help="Send 'y' to all prompts.")
    parser.add_argument("-t", "--timeout", type=int, default=5,
                        help="set timeout for file transfers")
    parser.add_argument("-r", "--repo", type=str, default='.insolater_repo',
                        help="set repository to store versions")
    parser.add_argument("-p", "--filepattern", type=str, default='. *.py *.txt *.xml',
                        help="set filepatterns to track")
    parser.add_argument('cmd', nargs='+', help='command')
    args = parser.parse_args()
    i = Insolater(repo=args.repo, timeout=args.timeout, filepattern=args.filepattern)
    cli(i, args.cmd, args.force)


if __name__ == '__main__':
    main()
