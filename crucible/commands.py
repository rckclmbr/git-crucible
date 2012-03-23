import argparse


def get_config_values(opts):
    def _prompt(description, default):
        res = raw_input(description)
        if not res:
            return default
    def _get_config_value(opts, key, description, default=None, allowEmpty=False, echo=True):
        if not opts[key]:
            if not opts["INFILE"].name == "<stdin>":
                while not opts[key]:
                    opts[key] = _prompt(description, default)
                    if opts[key] or allowEmpty:
                        break
            elif allowEmpty:
                return default
            else:
                raise Exception("'%s' is required" % key)
                
        return opts[key]
    opts['host'] = _get_config_value(opts, 'host', 'Crucible base url:')
    if not opts['host'].endswith('/'):
        opts['host'] += '/'
    opts['username'] = _get_config_value(opts, 'username', 'username: ')
    opts['password'] = _get_config_value(opts, 'password', 'password: ', allowEmpty=True, echo=False)
    opts['reviewers'] = _get_config_value(opts, 'reviewers', 'reviewers (comma separated, e.g. "fred,joe,matt"): ', allowEmpty=True)
    opts['project'] = _get_config_value(opts, 'project', 'project (default is "CR"): ', default='CR')
    opts['repository'] = _get_config_value(opts, 'repository', 'Git Repository: ', allowEmpty=True)
    opts['title'] = _get_config_value(opts, 'title', 'Title (default is ""): ')
    opts['jira_issue'] = _get_config_value(opts, 'jira_issue', 'JIRA Issue: ', allowEmpty=True)
    opts['description'] = _get_config_value(opts, 'description', 'Description (default is ""): ', allowEmpty=True, default="")
    return opts

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
    def config_parser(parser):
        parser.add_argument('INFILE', type=argparse.FileType('r'),
            help="A patch-file to add.  Note when using stdin, you must specify all parameters"\
                 " on the command-line")
        parser.add_argument("--title", help="Title of the post")
        parser.add_argument("--project", help="Crucible project")
        parser.add_argument("--repository", help="Crucible git repository the commit is in")
        parser.add_argument("--reviewers", help="Reviewers (comma-separated, e.g. \"fred,joe,matt\")")
        parser.add_argument("--jira_issue", help="The JIRA issue (e.g. JIRA-1234) (optional)")
        parser.add_argument("--moderator", help="Moderator of the review (optional)")
        parser.add_argument("--description", help="Description or statement of this review", default="")

    @staticmethod
    def run(api, args):
        args = get_config_values(args)
        args["patch_text"] = get_patch_text(args["INFILE"])

        permaid = api.create_review(*[args[i] for i in ("title", "description", "project", "jira_issue", "moderator")])
        print "Created", api.review_url(permaid)
        if args["patch_text"]:
            print "Adding patch to review"
            api.add_patch(permaid, args["patch_text"], args["repository"])
        if args["reviewers"]:
            print "Adding reviewers to review"
            api.add_reviewers(permaid, args["reviewers"])

class AddPatch(object):

    command = "add-patch"
    help = "Adds a patch to a review.  See add-patch -h for more info"
    epilog = """
    """

    @staticmethod
    def config_parser(parser):
        parser.add_argument("CODEREVIEW", help="Which code review to add the patch to (e.g. CR-123)")
        parser.add_argument('INFILE', type=argparse.FileType('r'),
            help="A patch-file to add.  Note when using stdin, you must specify all parameters"\
                 " on the command-line")
        parser.add_argument("--repository", help="Crucible git repository the commit is in")

    @staticmethod
    def run(api, args):
        args = get_config_values(args)
        patch_text = get_patch_text(args["INFILE"])
        api.add_patch(args["permaid"], patch_text, args["repository"])
        print "Added patch to %s" % args["permaid"]
