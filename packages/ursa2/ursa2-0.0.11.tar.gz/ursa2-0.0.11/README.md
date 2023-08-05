Ursa2
=====
Enhanced version of [ursa](https://github.com/sogou-ufo/ursa).

ursa2 supports [JSON Auto Combining](https://github.com/yanni4night/ursa2/wiki/JSON-Auto-Combining) , [Sub Tpl Preview](https://github.com/yanni4night/ursa2/wiki/Sub-Tpl-Preview) and more detail features,such as, supporting _url()_ in sub directory of css,which would bring bugs in previous,required data output in _http://origin/tpl.data_ url path,etc.


Feature
=====
 - Local HTTP/HTTPS server
 - Custom variables replace
 - Jinja2/Twig like template engine
 - Web data simulation
 - JSON data auto combining
 - JS/CSS merge&optimize
 - LESS auto translation
 - GET/POST(quirk) proxy
 - Intelligent timestamp

Install
=====
Checkout from [GitHub](https://github.com/yanni4night/ursa2) and run :
    
    $ python setup.py install

or use Python Package Index:

    $ pip install ursa2

Super permission may be required.

Usage
=====

###initialize project

    $ ursa2 init

###start server
     
     $ ursa2 start [port]

###view template list
    
open browser to http://[hostname]:[port]/

###view static resource list

open browser to http://[hostname]:[port]/s

###build project

    $ ursa2 build [target][--compress][--html]


Dependencies
=====
 - Unix/Linux/OS X
 - Java 1.5+ (for yuicompressor)
 - Python 2.6+ (3.x not supported)
 - [node](https://github.com/joyent/node) (for less)
 - [less](https://github.com/less/less.js)
 - [docopt](https://github.com/docopt/docopt) (for log)
 - [jinja2](https://github.com/mitsuhiko/jinja2)
 - [requests](https://github.com/kennethreitz/requests) (for proxy)


Documents
=====
 - [Manifest.json](https://github.com/yanni4night/ursa2/wiki/manifest.json)
 - [Ursa2 Specification](https://github.com/yanni4night/ursa2/wiki/Ursa2-Specification)
 - [JSON Auto Combining](https://github.com/yanni4night/ursa2/wiki/JSON-Auto-Combining)
 - [Sub Tpl Preview](https://github.com/yanni4night/ursa2/wiki/Sub-Tpl-Preview).

Quirk
=====
 - Server plugin not supported.
 - Mobile project initializing not supported.
 - POST data in proxy not supported.
 - Relative path of static resource not supported(which you should never do).

LICENCE
=====
The MIT License (MIT)

Copyright (c) 2013 YinYong

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
