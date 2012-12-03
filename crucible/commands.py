from __future__ import absolute_import
import argparse
import ConfigParser
import os
from crucible.client import API
from getpass import getpass


def prompt(opts, key, description, default=None, allowEmpty=False, echo=True):
    if not opts[key]:
        if opts["INFILE"].name != "<stdin>":
            while not opts[key]:
                if echo:
                    res = raw_input(description)
                else:
                    res = getpass(description)
                if not res and allowEmpty:
                    opts[key] = default
                    return default
                opts[key] = res
        elif allowEmpty:
            return default
        else:
            raise Exception("%s is required" % key)
    return opts[key]

def get_patch_text(infile):
    """ Validates patch exists and returns string """
    return "".join(infile.readlines())

class CreateReview(object):

    command = "create-review"
    help = "Creates a review.  See create-review -h for more info"
    epilog = """
Examples:
    git diff origin/deploy.. | git-crucible create-review \\
                  --jira_issue "FSD-1125" \\
                  --title "Automate XML Import -"

    git-crucible create-review --patch_file test.diff \\
                 --jira_issue "FSD-1125" \\
                 --title "Automate XML Import" \\
                 --description "Some long description here \\
                 test.diff 

    cat test.diff | git-crucible create-review \\
                  --jira_issue "FSD-1125" \\
                  --title "Automate XML Import -"
    """

    @staticmethod
    def prompt_for_config(args):
        prompt(args, 'title', 'Title (""): ', allowEmpty=True, default="")
        prompt(args, 'project', 'project ("CR"): ', default='CR')
        prompt(args, 'repository', 'Git Repository: ', allowEmpty=True)
        prompt(args, 'reviewers', 'reviewers (comma separated, e.g. "fred,joe,matt"): ', allowEmpty=True)
        prompt(args, 'jira_issue', 'JIRA Issue: (""): ', allowEmpty=True)
        prompt(args, "moderator", "Moderator of the review (optional): ", allowEmpty=True)
        prompt(args, 'description', 'Description (""): ', allowEmpty=True, default="")
        return args

    @staticmethod
    def config_parser(parser):
        parser.add_argument('INFILE', type=argparse.FileType('r'),
            help="A patch-file to add.  Note when using stdin, you must specify all parameters"\
                 " on the command-line")
        parser.add_argument("-t", "--title", help="Title of the post")
        parser.add_argument("-p", "--project", help="Crucible project")
        parser.add_argument("-r", "--repository", help="Crucible git repository the commit is in")
        parser.add_argument("-R", "--reviewers", help="Reviewers (comma-separated, e.g. \"fred,joe,matt\")")
        parser.add_argument("-j", "--jira_issue", help="The JIRA issue (e.g. JIRA-1234) (optional)")
        parser.add_argument("-m", "--moderator", help="Moderator of the review (optional)")
        parser.add_argument("-d", "--description", help="Description or statement of this review", default="")

    @staticmethod
    def run(api, args):
        args["patch_text"] = get_patch_text(args["INFILE"])

        permaid = api.create_review(*[args[i] for i in ("title", "description", "project", "jira_issue", "moderator")])
        print "Created", api.review_url(permaid)
        if args["patch_text"]:
            print "Adding patch to review"
            api.add_patch(permaid, args["patch_text"], args["repository"])
        if args["reviewers"]:
            print "Adding reviewers to review"
            api.add_reviewers(permaid, args["reviewers"])
        print "Opening review"
        api.open_review(permaid)

class AddPatch(object):

    command = "add-patch"
    help = "Adds a patch to a review.  See add-patch -h for more info"
    epilog = """
    """

    @staticmethod
    def prompt_for_config(args):
        prompt(args, 'repository', 'Git Repository: ', allowEmpty=True)
        return args

    @staticmethod
    def config_parser(parser):
        parser.add_argument("CODEREVIEW", help="Which code review to add the patch to (e.g. CR-123)")
        parser.add_argument('INFILE', type=argparse.FileType('r'),
            help="A patch-file to add.  Note when using stdin, you must specify all parameters"\
                 " on the command-line")
        parser.add_argument("-r", "--repository", help="Crucible git repository the commit is in")

    @staticmethod
    def run(api, args):
        patch_text = get_patch_text(args["INFILE"])
        api.add_patch(args["CODEREVIEW"], patch_text, args["repository"])
        print "Added patch to %s" % args["CODEREVIEW"]


class Main(object):
    """Contains the main program.  Uses all other commands"""

    epilog="""

Config file:
    All config options can also be specified in the file ~/.git_crucible.conf.
    For example:

    [crucible]
    host=http://crucible.yourcompany.com/crucible
    username=jbraegger
    password=test
    reviewers=nbrunson,aglemann
    repository=gitreponame
    project=CR

    If you have the above in your config, the rest is easy.  

Examples:
    See specific command help for examples (e.g. git-crucible create-review -h)
    """

    commands = [CreateReview, AddPatch]

    def run(self):
        args = self.get_config();
        args = self.prompt_for_config(args)
        api = API(args["host"], args["username"], args["password"], verbose=args["verbose"], debug=args["debug"])
        args.get("command").run(api, args)

    def prompt_for_config(self, args):
        prompt(args, 'host', 'Crucible base url:')
        prompt(args, 'username', 'username: ')
        prompt(args, 'password', 'password: ', allowEmpty=True, echo=False)
        args = args.get("command").prompt_for_config(args)
        return args

    def validate_required_args(self, args):
        for i in "host", "username", "password":
            if not args[i]:
                raise Exception("'%s' is required" % key)

    def get_config(self):
        parser = argparse.ArgumentParser(description="""Submit code reviews to Crucible.""", 
            formatter_class=argparse.RawTextHelpFormatter, epilog=self.epilog)

        parser.set_defaults(**self.get_config_file_settings())
        parser.add_argument("--host", help="base url of Crucible")
        parser.add_argument("--username", help="Crucible username")
        parser.add_argument("--password", help="Crucible password")
        parser.add_argument("--verbose", action="store_true", default=False, help="Print full server requests and responses")
        parser.add_argument("--debug", action="store_true", default=False, help="Don't actually send any requests")

        subparsers = parser.add_subparsers()
        for command in self.commands:
            subparser = subparsers.add_parser(command.command, help=command.help, epilog=command.epilog,
                                                formatter_class=argparse.RawTextHelpFormatter)
            command.config_parser(subparser)
            subparser.set_defaults(command=command)

        return vars(parser.parse_args())

    def get_config_file_settings(self):
        defaults = dict()
        config_file = os.path.expanduser("~/.git_crucible.conf")
        if os.path.isfile(config_file):
            config = ConfigParser.SafeConfigParser()
            config.read([config_file])
            defaults.update(config.items("crucible"))
        return defaults
