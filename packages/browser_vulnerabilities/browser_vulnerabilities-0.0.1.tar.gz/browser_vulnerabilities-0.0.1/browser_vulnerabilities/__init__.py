import httpagentparser
from pkg_resources import parse_version
from data import OS, BROWSER

__all__ = ["BrowserVulnerability"]

class BrowserVulnerability:

    def __init__(self, ua):
        self.ua = ua
        self.parsed_ua = httpagentparser.detect(self.ua)

    def vulnerabilities(self):
        data = self.check_os()
        if data:
            return data
        data = self.check_browser()
        if data:
            return data
        return False

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
            tv = os.get("version__smaller")

            if os[a] == cname:
                cversion = parse_version(cv)
                tversion = parse_version(tv)
                if cversion is not None and cversion < tversion:
                    return os
    
    def check_browser(self):
        if "browser" not in self.parsed_ua:
            return False
        browser = self.parsed_ua["browser"]
        parsed_version = parse_version(browser.get("version", ""))
        for tbrowser in BROWSER:
            if tbrowser.get("name") != browser.get("name"):
                continue
            tversion = parse_version(tbrowser.get("version__smaller"))
            if browser.get("version") is not None and parsed_version < tversion:
                return tbrowser


def main():
    uas = [
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.146 Safari/537.36',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.74.9 (KHTML, like Gecko) Version/7.0.2 Safari/537.74.9',
           'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0',
           'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0',
           'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0',
          ]
    for ua in uas:
        b = BrowserVulnerability(ua)
        print b.vulnerabilities()

if __name__ == '__main__':
    main()
