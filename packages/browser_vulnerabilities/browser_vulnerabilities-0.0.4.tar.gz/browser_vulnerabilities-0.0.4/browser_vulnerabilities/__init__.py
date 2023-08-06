import httpagentparser
from pkg_resources import parse_version
from data import OS, BROWSER

__all__ = ["BrowserVulnerability"]

class BrowserVulnerability:

    def __init__(self, ua):
        self.ua = ua
        self.parsed_ua = httpagentparser.detect(self.ua)

    @classmethod
    def get_readable_format(cls, data):
        readable_name = ""
        readable_version = ""
        if "readable_name" in data:
            readable_name = data["readable_name"]
        else:
            for a in ("name", "platform", "flavor"):
                if a in data:
                    readable_name = data[a]
                    break
        if "version" in data:
            readable_version = data["version"]
        elif "version__smaller" in data:
            readable_version = "older than %s" % data["version__smaller"]
        data["readable_version"] = "%s %s" % (readable_name, readable_version)
        return data

    def vulnerabilities(self):
        data = self.check_os()
        if data:
            return self.get_readable_format(data)
        data = self.check_browser()
        if data:
            return self.get_readable_format(data)
        return False

    @classmethod
    def check_version(cls, criteria, version):
        parsed = parse_version(version)
        if "version__smaller" in criteria:
            vp = parse_version(criteria.get("version__smaller"))
            if parsed >= vp:
                return False
        if "version__larger" in criteria:
            vp = parse_version(criteria.get("version__larger"))
            if parsed < vp:
                return False
        if "version__extra" in criteria:
            vp = criteria.get("version__extra")
            if vp.match(version) is None:
                return False
        return True

    def check_os(self):
        if "flavor" not in self.parsed_ua and "platform" not in self.parsed_ua:
            return False
        for os in OS:
            d = None
            for a in ("flavor", "platform"):
                if a in os:
                    d = self.parsed_ua.get(a)
                    break
            if not d:
                continue

            cname = d.get("name")
            cv = d.get("version")
            if cv is None:
                return

            tname = os.get("name")
            if os[a] == cname:
                version_check = self.check_version(os, cv)
                if version_check:
                    return os


    def check_browser(self):
        if "browser" not in self.parsed_ua:
            return False
        browser = self.parsed_ua["browser"]
        parsed_version = parse_version(browser.get("version", ""))
        for tbrowser in BROWSER:
            if tbrowser.get("name") != browser.get("name"):
                continue
            version_check = self.check_version(tbrowser, browser.get("version", ""))
            if version_check:
                return tbrowser

def main():
    uas = [
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.146 Safari/537.36',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.146 Safari/537.36',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.146 Safari/537.36',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.74.9 (KHTML, like Gecko) Version/7.0.2 Safari/537.74.9',
           'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0',
           'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0',
           'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:27.0) Gecko/20100101 Firefox/27.0',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:27.0) Gecko/20100101 Firefox/27.0',
          ]
    for ua in uas:
        b = BrowserVulnerability(ua)
        print 
        print ua
        print b.vulnerabilities()

if __name__ == '__main__':
    main()
