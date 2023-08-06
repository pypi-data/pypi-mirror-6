# -*- coding: utf-8 -*-
import sys,os
import urllib
import json
import requests

"""
* multi-mode
  --mode=data,run effectively turns on tracing
"""

class Deco(object):
    """function decorator that adds a reserved switch --mode controls execution mode"""

    def __call__(self, f):
        return self.decorate(f)

    def dispatch(self, mode):
        """mode-->handler"""

        if not mode:
            mode='raw'

        table=dict(raw=lambda x: x,
                   data=self.data,
                   cmd=self.cmd,
                   run=self.run)

        return table[mode]


    def decorate(self, f):

        def wrap(*args, **opt):

            # intercept opts for this execution mode
            modes=opt.pop('mode', '').split(',') # reserved.

            output=f(*args, **opt)

            # modes->handlers
            try:
                handlers=[self.dispatch(mode) for mode in modes]
            except KeyError:
                print >>sys.stderr, 'unknown mode:', mode
                sys.exit(1)

            # print all but last as side-effects. last one is returned as value.
            last=handlers.pop()
            for h in handlers:
                print h(output)
            return last(output)

        wrap.func_name=f.func_name
        wrap.func_defaults=f.func_defaults
        wrap.func_doc=f.func_doc
        wrap.__name__=f.__name__
        wrap.__doc__=f.__doc__

        return wrap

    def data(self, req): 
        """return json data representing the operation"""
        return json.dumps(req)
    # subclass hooks
    def cmd(self, req): 
        """suggest a command that would do the job"""
        override_me
    def run(self, req): 
        """peform the operation"""
        override_me

class HttpRequestDeco(Deco):

    def cmd(self, req):
        """compose curl invocation 
        curl -X{method} -H"Content-Type: application/json" [-H...] {url}
        """

        opts=['curl']

        # xx use the long opt..

        # -X POST
        if 'method' in req:
            opts.append('-X'+req['method'])

        # --data
        data=req.get('data')
        querystring=None
        if not data:
            pass
        elif req.get('method').upper()=='GET':
            # append querystring to the url
            assert not isinstance(data, basestring)
            querystring=urllib.urlencode(data)
        elif isinstance(data, basestring):
            opts.append('--data'+data) # ??
        elif isinstance(data, tuple):
            dtype,dval=data
            assert dtype=='file'
            opts.append('--data@'+dval)
        else:
            opts.append('--data'+json.dumps(data))

        # -H .. -H ..
        for hdr in req.get('headers',{}).items():
            opts.append('-H"{}: {}"'.format(*hdr))

        url=req['url']
        if querystring:
            url+='?'+querystring
        opts.append("'%s'" % url)

        return ' '.join(opts)

    def run(self, request):

        req=request.copy()

        url=req.pop('url')

        method=req.pop('method', 'get').lower()
        method_f=getattr(requests, method)

        data=req.get('data')
        if not data:
            pass
        elif isinstance(data, basestring):
            pass
        elif isinstance(data, tuple) and data[0]=='file': # ('file', './x.data.json')
            data=file(data[1])
        else:
            assert False, ('unknown data type', type(data))

        response=method_f(url, headers=req.get('headers'), data=data)

        # xxx how to pass back status and content..  make handlers generators?
        print >>sys.stderr, response.status_code
        sys.stderr.flush()

        return response.content
        

        
http_request=HttpRequestDeco()
