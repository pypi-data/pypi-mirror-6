import re


TWO_DOTS_RE = re.compile("^.*\..*\..*$")

__all__ = ["OS", "BROWSER"]

OS = [
 {"platform": "Mac OS", "version__smaller": "X 10.9.2", "vuln": "http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-1266", "priority": "mandatory", "version__extra": TWO_DOTS_RE},
 {"flavor": "MacOS", "version__smaller": "X 10.9.2", "vuln": "http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-1266", "priority": "mandatory", "version__extra": TWO_DOTS_RE},
 {"flavor": "MacOS", "version__smaller": "X 10.9", "vuln": "http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-1266", "priority": "mandatory"},
]

BROWSER = [
 {"name": "Safari", "version__smaller": "7.0.2", "vuln": "http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-1266", "priority": "mandatory"},
 {"name": "Chrome", "version__smaller": "33.0.1750.117", "vuln": "http://www.cvedetails.com/cve/CVE-2013-6658/", "priority": "recommended"},
 {"name": "Chrome", "version__smaller": "32", "vuln": "Multiple vulnerabilities", "priority": "mandatory"},
 {"name": "Firefox", "version__smaller": "26.0", "vuln": "Multiple vulnerabilities", "priority": "mandatory"},
 {"name": "Firefox", "version__smaller": "27.0", "vuln": "Multiple vulnerabilities", "priority": "recommended"},
]
