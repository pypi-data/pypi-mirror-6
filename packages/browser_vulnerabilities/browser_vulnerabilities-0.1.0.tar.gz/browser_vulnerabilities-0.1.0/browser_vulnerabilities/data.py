import re


TWO_DOTS_RE = re.compile("^.*\..*\..*$")

__all__ = ["OS", "BROWSER"]

OS = [
 {"platform": "Mac OS", "readable_name": "OS X", "version": "older than 10.9.2", "version__larger": "X 10.9", "version__smaller": "X 10.9.2", "vuln": "http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-1266", "priority": "mandatory", "version__extra": TWO_DOTS_RE},
 {"flavor": "MacOS", "readable_name": "OS X", "version": "older than 10.9.2", "version__larger": "X 10.9", "version__smaller": "X 10.9.2", "vuln": "http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-1266", "priority": "mandatory", "version__extra": TWO_DOTS_RE},
 {"flavor": "MacOS", "readable_name": "OS X", "version": "older than 10.8.5", "version__larger": "X 10.8", "version__smaller": "X 10.8.5", "priority": "mandatory", "version__extra": TWO_DOTS_RE},
 {"flavor": "MacOS", "readable_name": "OS X", "version": "older than 10.7.5", "version__larger": "X 10.7", "version__smaller": "X 10.7.5", "priority": "mandatory", "version__extra": TWO_DOTS_RE},
 {"flavor": "MacOS", "readable_name": "OS X", "version": "older than 10.7.5", "version__smaller": "X 10.7", "priority": "mandatory"},
 {"platform": "iOS", "version": "older than 7.0.6", "version__smaller": "7.0.6", "version__larger": "7.0", "priority": "mandatory"},
]

BROWSER = [
 {"name": "Safari", "version__larger": "7.0", "version__smaller": "7.0.2", "vuln": "http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-1266", "priority": "mandatory", "platform__not": "iOS"},
 {"name": "Chrome", "version__smaller": "33.0.1750.117", "vuln": "http://www.cvedetails.com/cve/CVE-2013-6658/", "priority": "recommended"},
 {"name": "Chrome", "version__smaller": "32", "priority": "mandatory"},
 {"name": "Firefox", "version__smaller": "26.0", "priority": "mandatory"},
 {"name": "Firefox", "version__smaller": "27.0", "priority": "recommended"},
]
