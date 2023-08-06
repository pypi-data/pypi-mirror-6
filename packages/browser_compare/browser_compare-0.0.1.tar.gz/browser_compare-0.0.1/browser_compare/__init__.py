import httpagentparser
from pkg_resources import parse_version

__all__ = ["UAException", "UAChangedException", "UADowngradedException", "BrowserCompare"]

class UAException(Exception):
    """ General exception for invalid user agent changes """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class UAChangedException(UAException):
    """ OS / browser name changed (might be parsing error) """
    pass

class UADowngradedException(UAException):
    pass

class BrowserCompare:

    def __init__(self, old, new):
        self.old = old
        self.new = new
        self.old_parsed = httpagentparser.detect(old)
        self.new_parsed = httpagentparser.detect(new)

    def compare_param(self, param_name):
        old_g = self.old_parsed.get(param_name)
        new_g = self.new_parsed.get(param_name)
        if (old_g != new_g) and ((old_g or new_g) == (new_g or old_g)):
            # Parameter disappeared or appeared.
            raise UAChangedException("Property %s disappeared or appeared" % param_name)
        if old_g is None or new_g is None:
            # Parameter does not exist in either version
            return
        old_name = old_g.get("name")
        new_name = new_g.get("name")
        if old_name != new_name:
            # Name changed
            raise UAChangedException("Name of %s changed from '%s' to '%s'" % (param_name, old_name, new_name))
        old_version = old_g.get("version", "")
        new_version = new_g.get("version", "")

        if old_version is None:
            old_version = ""
        if new_version is None:
            new_version = ""

        old_v = parse_version(old_version)
        new_v = parse_version(new_version)
        if old_v == new_v:
            return
        if new_v >= old_v:
            return
        raise UADowngradedException("%s was downgraded from %s to %s" % (param_name, old_version, new_version))


    def compare(self):
        params = ("platform", "flavor", "browser", "os")
        for param in params:
            self.compare_param(param)
        return True



def test_browser(old_ua, new_ua):
    print 
    print 
    print old_ua
    print "-"*80
    print new_ua

    a = BrowserCompare(old_ua, new_ua)
    a.compare()


def main():
    file = open("user-agents.txt")
    for line in file:
        line = line.split("'")
        old_ua = line[1]
        new_ua = line[3]
        test_browser(old_ua, new_ua)

if __name__ == '__main__':
    main()
