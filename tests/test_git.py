import unittest
from mock import patch, MagicMock
from crucible import git

import urllib2
import os


class GitTest(unittest.TestCase):
    
    def test_diff(self):
        os.chdir(os.path.join(os.path.dirname(__file__), "data/repo"))
        res = git.diff("HEAD^..")
        self.assertEquals(res, """diff --git a/test2 b/test2
index 180cf83..84a746b 100644
--- a/test2
+++ b/test2
@@ -1 +1,2 @@
 test2
+test3
""")
    def test_diff_error(self):
        os.chdir(os.path.join(os.path.dirname(__file__), "data/repo"))
        try:
            res = git.diff("HEAD^^^..")
        except Exception, e:
            self.assertEquals(str(e), """fatal: ambiguous argument 'HEAD^^^..': unknown """
                """revision or path not in the working tree.\nUse '--' to separate paths from revisions\n""")
        else:
            assert False, "Didn't raise an exception"
