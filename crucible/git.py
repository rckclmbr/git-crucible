import popen2

def diff(command):
    r, w, e = popen2.popen3("git diff '%s'" % command)
    error = "".join(e)
    if error:
        raise Exception(error)
    return "".join(r)
