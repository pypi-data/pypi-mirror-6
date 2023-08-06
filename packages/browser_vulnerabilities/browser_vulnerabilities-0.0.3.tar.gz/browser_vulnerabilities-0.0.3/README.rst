Browser vulnerabilities database
================================

This small library detects vulnerable operating systems and browsers
based on browser user-agent string. No active checks are included.

::

  from browser_vulnerabilities import BrowserVulnerability

  bv = BrowserVulnerability('Mozilla/5.0 (Windows NT 6.3; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0')
  print bv.vulnerabilities() # {'priority': 'mandatory', 'vuln': 'Multiple vulnerabilities', 'name': 'Firefox', 'version__smaller': '26.0'}
  bv = BrowserVulnerability('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0')
  print bv.vulnerabilities() # False

Minimalistic database is available in ``browser_vulnerabilities/data.py`` file.

License
-------

Licensed under MIT license:

Copyright (c) 2014 Olli jarva olli@jarva.fi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
