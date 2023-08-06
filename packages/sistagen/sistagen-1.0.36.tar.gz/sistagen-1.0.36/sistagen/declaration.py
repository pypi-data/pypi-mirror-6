# -*- coding: utf-8 -*-

import logging


class Declaration:
    '''
    Describes one graph or template declaration.
  

    Declarations:
        Template TEMPLATE_NAME 
        Graph GRAPH_NAME    
    '''
    
    
    UNKNOWN, TEMPLATE, GRAPH = -1, 0, 1
    
    
    def __init__(self):
        self.inputs = {}
        self.output = {
            'dir': '',
            'prefix': '',
            'mask': '_%(width)ix%(height)i',
            'suffix': '',
            'format': 'png'
            }
        self.sizes = []
        self.options = {}
        self.decls = []
        self.name = ''
        
        self.decl_class = Declaration.UNKNOWN


    def set_template(self):
        '''
        makes this declaration a template
        '''
        self.decl_class = Declaration.TEMPLATE


    def set_graph(self):
        '''
        makes this declaration a graph
        '''
        self.decl_class = Declaration.GRAPH


    def is_graph(self):
        return self.decl_class == Declaration.GRAPH


    def use(self, decl):
        '''
        Load all values from other declaration.
        '''
        import copy
        
        self.inputs.update( copy.deepcopy(decl.inputs) )
        self.output.update( copy.deepcopy(decl.output) )
        self.sizes += copy.deepcopy(decl.sizes)
        self.options.update( copy.deepcopy(decl.options) )
        self.decls += copy.deepcopy(decl.decls)
        
        
    def merge(self, decl, thisname, hisname):
        '''
        Merge all values from other declaration.
        The difference between merge and use is that 'use' will
        override all values in this declaration, while 'merge' 
        cause that they both will be preserved. It's usefull 
        when combining two or more graphs. Additionally, use
        will copy all declaration attributes, and merge: only
        inputs and decls attributes.
        Note that merge will change the 'other' input names.
        thisname and hisname are used to rename inputs
        '''
        import copy
        
        #inps = {}
        #for k in self.inputs.keys():
            #inps[thisname + k] = self.inputs[k]
        #self.inputs = inps
        
        inps = {}
        ninps = copy.deepcopy(decl.inputs)
        
        for k in ninps.keys():
            inps[hisname + k] = ninps[k]
        self.inputs.update(inps)
        
        #for d in self.decls:
            #d[1]['name'] = thisname + d[1]['name']
            
        ndecls = copy.deepcopy(decl.decls)
        for d in ndecls:
            d[1]['name'] = hisname + d[1]['name']
            
        self.decls += ndecls

        
    
    def input_file(self, file_, name=None):
        '''
        Set file for input named 'name'.
        If input doesn't exists - it would be created.
        If input exists already - it's file (and maybe dir) values will
        be overwritten. 
        file_ may be filename or file path (in that case the 'dir' value
        will be also set.
        '''
        from os import path
        
        if not name:
            for v in self.inputs.values():
                v['file'] = file_
            return 
        
        d, f = path.split(file_)
        if name not in self.inputs:
            self.inputs[name] = {}
        
        self.inputs[name]['file'] = f
        if d:
            self.inputs[name]['dir'] = d

            
            
    def input_dir(self, dir_, name=None):
        '''
        Set dir value for input named 'name'.
        If specified input doesn't exists it would be created.
        
        if dir is not specified, then:
         - name is treated as dir
         - dir is set for each known input
        '''

        if not name:
            for v in self.inputs.values():
                v['dir'] = dir_
        else:
            if name not in self.inputs:
                self.inputs[name] = {}    
            self.inputs[name]['dir'] = dir_



    def input_ds(self, ds, name=None):
        '''
        Set ds value for input named 'name'.
        If specified input doesn't exists it would be created.
        '''
        
        if not name:
            for v in self.inputs.values():
                v['ds'] = ds
        else:
            if name not in self.inputs:
                self.inputs[name] = {}
            self.inputs[name]['ds'] = ds


    def input_cf(self, cf, name=None):
        '''
        Set cf value for input named 'name'.
        If specified input doesn't exists it would be created.
        '''
        
        if not name:
            for v in self.inputs.values():
                v['cf'] = cf
        else:
            if name not in self.inputs:
                self.inputs[name] = {}
                
            self.inputs[name]['cf'] = cf


    def output_dir(self, path):
        '''
        Sets an output destination directory
        '''
        self.output['dir'] = path


    def output_file(self, file_):
        '''
        Sets an output dir, mask and format based on 
        filename. 
        '''
        
        from os import path
        
        d, f = path.split(file_)
        if d:
            self.output['dir'] = d
            
        f, e = path.splitext(f)
        self.output['mask'] = f
        self.output['prefix'] = ''
        self.output['suffix'] = ''

        #self.output['suffix'] = '' we may want to uncomment that
        self.output['format'] = e[1:]
        
        
        
    def output_mask(self, mask):
        '''
        Set output file mask.
        Mask may contains certain keywords, that would be replaced giving
        real destination filename.
        width - destination image width
        height - 
        name - graph declaration name
        '''
        
        self.output['mask'] = mask
        
        
        
    def output_prefix(self, prefix):
        '''
        Sets filename prefix to be used.
        Output filepath will be created as:
            OUTPUT-DIR + OUTPUT-PREFIX + SIZE + OUTPUT-SUFFIX + OUTPUT-FORMAT
        '''
        
        self.output['prefix'] = prefix


    def output_suffix(self, suffix):
        '''
        Sets filename suffix to be used.
        Output filepath will be created as:
            OUTPUT-DIR + OUTPUT-PREFIX + SIZE + OUTPUT-SUFFIX + OUTPUT-FORMAT
        '''
        
        self.output['suffix'] = suffix
        
        
    def output_format(self, format_):
         '''
         set output file format
         '''
         self.output['format'] = format_
         
         
    def add_size(self, size):
        '''
        adds graph dimensions, in which we want graph to be generated
        size should be one of:
         - str in form: 'WxH' - w-width, h-height, x-x :)
         - tuple with two int, example: (160, 120)
        '''
        
        if type(size) in (tuple, list):
            self.sizes.append(tuple(size))
        elif type(size) == str:
            w, h = size.split('x')
            w, h = int(w), int(h)
            self.sizes.append((w,h))
        else:
            raise ValueError('Size format (%s) is not supported' % str(type(size)))


    def remove_dec(self, decl_name):
        '''
        remove declaration from graph
        '''
        n = []
        for k, v in self.decls:
            if v['name'] != decl_name:
                n.append((k, v))
        self.decls = n
        

    def add_dec(self, decl_name, expr=None, name=None, aggr=None, color=None, text=None, stack=None):
        '''
        adds complex declaration, for lines, areas and so forth
        TODO: update this method so it won't add unneeded or unset data
        '''
        if expr and name:
            raise ValueError('There should be only expr or value defined, not both!')

        decl = (decl_name, {
                'expr': expr,
                'name': name,
                'aggr': aggr,
                'color': color,
                'text': text,
                'stack': stack,
            })
        self.decls.append(decl)


    def add_line1(self, expr=None, name=None, color=None, text=None, stack=None):
        self.add_dec('line1', expr=expr, name=name, color=color, text=text, stack=stack)

    def add_line2(self, expr=None, name=None, color=None, text=None, stack=None):
        self.add_dec('line2', expr=expr, name=name, color=color, text=text, stack=stack)

    def add_line3(self, expr=None, name=None, color=None, text=None, stack=None):
        self.add_dec('line3', expr=expr, name=name, color=color, text=text, stack=stack)

    def add_area(self, expr=None, name=None, color=None, text=None, stack=None):
        self.add_dec('area', expr=expr, name=name, color=color, text=text, stack=stack)

    def add_gprint(self, expr=None, name=None, aggr=None, text=None):
        self.add_dec('gprint', expr=expr, name=name, aggr=aggr, text=text)

    def add_comment(self, text=None):
        self.add_dec('comment', text=text)

    
    def add_option(self, option_name, value):
        
        # we need to hack rrd graph a bit, because we need to know
        # the datatype of the param
        from rrd.graph import Graph
        opname = option_name.replace('-', '_')
        datatype = Graph.SIMPLE_KEYWORDS[opname][0]
        
        self.options[opname] = datatype(value)
    
    
    def _random_name(self):
        import random
        s = ''
        c = 'abcdefghijklmnopqrstuvwxyz0123456789'
        for _ in range(10):
            s += c[random.randrange(len(c))]
        return s
        
    
    def _call_by_type(self, g, t, vname, decl):
        if t in ('line1', 'line2', 'line3', 'area'):
            getattr(g, t)(vname, decl['color'], decl['text'], decl['stack'])
        elif t in ('gprint',):
            getattr(g, t)(vname, decl['text'])
            

    def _get_output(self, size):
        '''
        returns output filename
        for given size
        '''
        import os
        return os.path.join(
                self.output['dir'],
                self.output['prefix'] 
                + self.output['mask'] % {
                    'width': size[0],
                    'height': size[1],
                    'name': self.name,
                    }
                + self.output['suffix'] 
                + '.' + self.output['format']
            )


    def get_graph(self):
        '''
        Prepares an Graph instance(s) based on passed data.
        This method will return as many graphs as many size declaration
        was passed.
        '''
        
        if self.decl_class != Declaration.GRAPH:
            raise AttributeError('Only graph declaration may be graphed')
        
        from rrd.graph import Graph
        import os        
    
        ret = []
        for s in self.sizes:
            g = Graph()
            g.width(s[0])
            g.height(s[1])
            
            for optname, optval in self.options.items():
                getattr(g, optname)(optval)
            
            g.filename(self._get_output(s))
            
            for vname, inp in self.inputs.items():
                try:
                    g.def_(vname, os.path.join(inp['dir'], inp['file']), inp['ds'], inp['cf'])
                except KeyError:
                    logging.warn('Could not declare graph data named "%s"' % vname)
                    self.remove_dec(vname)
            
            for t, decl in self.decls:
                if t in ('comment'):
                    g.comment(decl['text'])
                    continue
                    
                if decl['aggr']:
                    rndname = self._random_name()
                    if decl['name']:
                        w = decl['name']
                    elif decl['expr']:
                        w = self._random_name()
                        g.cdef(w, decl['expr'])
                    g.vdef(rndname, w, decl['aggr'])
                    self._call_by_type(g, t, rndname, decl)
                    #getattr(g, t)(rndname, decl['color'], decl['text'], decl['stack'])
                else:
                    if decl['name']:
                        self._call_by_type(g, t, decl['name'], decl)
                        #getattr(g, t)(decl['name'], decl['color'], decl['text'], decl['stack'])
                    elif decl['expr']:
                        rndname = self._random_name()
                        g.cdef(rndname, decl['expr'])
                        self._call_by_type(g, t, rndname, decl)
                        #getattr(g, t)(rndname, decl['color'], decl['text'], decl['stack'])


            
            ret.append(g)
            
        return tuple(ret)
