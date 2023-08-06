import os
import re
import sys
import time
import traceback
import types

################ util

def ddd(*args):
    raise RuntimeError(*args)

def coalesce(ll):
    """ xxx verify 
    join adjacent strings in a list.
    """
    reduced=[]
    cur=None
    while(len(ll)):
        item=ll.pop(0)
        if type(item)==str:
            if cur is None:
                cur=item
            else:
                cur=cur+item
        else:
            reduced.append(cur)
            reduced.append(item)
            cur=None
    reduced.append(cur)
    return filter(notnone, reduced) # xx

def notnone(x):
    if x is None:
        return False
    return True

def list_flatten(ll):
    if type(ll) != type([]): 
        return [ll]
    if ll == []: 
        return ll
    return list_flatten(ll[0]) + list_flatten(ll[1:])

def with_duration(f):
    then=time.time()
    ret=f()
    sys.stderr.write("took: %s" % (time.time()-then))
    return ret

def xeval(code, envdict):
    """ eval() with error message """
    try:
        return eval(code, envdict)
    except Exception, e:
        raise RuntimeError("failed to eval: '%s'" % code, e)

def progn(*args):
    """ as in scheme """
    val=None
    for code in args:
        val=code()
    return val

################ html

html_syntax={
    'tr'	: {
            'opt'	: True,
            'table'	: True
        },
    'input'	: {
            'empty'	: True,
            'img'	: True,
            'inline'	: True
        },
    'strike'	: {
            'inline'	: True
        },
    'keygen'	: {
            'empty'	: True,
            'inline'	: True
        },
    'table'	: {
            'block'	: True
        },
    'form'	: {
            'block'	: True
        },
    'h5'	: {
            'block'	: True,
            'heading'	: True
        },
    'meta'	: {
            'empty'	: True,
            'head'	: True
        },
    'map'	: {
            'inline'	: True
        },
    'isindex'	: {
            'block'	: True,
            'empty'	: True
        },
    'tfoot'	: {
            'opt'	: True,
            'table'	: True,
            'rowgrp'	: True
        },
    'caption'	: {
            'table'	: True
        },
    'nosave'	: {
            'block'	: True
        },
    'code'	: {
            'inline'	: True
        },
    'base'	: {
            'empty'	: True,
            'head'	: True
        },
    'ilayer'	: {
            'inline'	: True
        },
    'acronym'	: {
            'inline'	: True
        },
    'br'	: {
            'empty'	: True,
            'inline'	: True
        },
    'align'	: {
            'block'	: True
        },
    'strong'	: {
            'inline'	: True
        },
    'h4'	: {
            'block'	: True,
            'heading'	: True
        },
    'marquee'	: {
            'opt'	: True,
            'inline'	: True
        },
    'em'	: {
            'inline'	: True
        },
    'layer'	: {
            'block'	: True
        },
    'b'	: {
            'inline'	: True
        },
    'q'	: {
            'inline'	: True
        },
    'span'	: {
            'inline'	: True
        },
    'applet'	: {
            'img'	: True,
            'param'	: True,
            'inline'	: True,
            'object'	: True
        },
    'title'	: {
            'head'	: True
        },
    'spacer'	: {
            'empty'	: True,
            'inline'	: True
        },
    'multicol'	: {
            'block'	: True
        },
    'small'	: {
            'inline'	: True
        },
    'xmp'	: {
            'obsolete'	: True,
            'block'	: True
        },
    'area'	: {
            'block'	: True,
            'empty'	: True
        },
    'frame'	: {
            'frames'	: True,
            'empty'	: True
        },
    'dir'	: {
            'obsolete'	: True,
            'block'	: True
        },
    'body'	: {
            'opt'	: True,
            'omitst'	: True,
            'html'	: True
        },
    'nobr'	: {
            'inline'	: True
        },
    'ol'	: {
            'block'	: True
        },
    'html'	: {
            'opt'	: True,
            'omitst'	: True,
            'html'	: True
        },
    'var'	: {
            'inline'	: True
        },
    'ul'	: {
            'block'	: True
        },
    'del'	: {
            'mixed'	: True,
            'block'	: True,
            'inline'	: True
        },
    'blockquote'	: {
            'block'	: True
        },
    'nolayer'	: {
            'mixed'	: True,
            'block'	: True,
            'inline'	: True
        },
    'style'	: {
            'head'	: True
        },
    'dfn'	: {
            'inline'	: True
        },
    'iframe'	: {
            'inline'	: True
        },
    'h3'	: {
            'block'	: True,
            'heading'	: True
        },
    'textarea'	: {
            'field'	: True,
            'inline'	: True
        },
    'embed'	: {
            'empty'	: True,
            'img'	: True,
            'inline'	: True
        },
    'a'	: {
            'inline'	: True
        },
    'img'	: {
            'empty'	: True,
            'img'	: True,
            'inline'	: True
        },
    'font'	: {
            'inline'	: True
        },
    'tt'	: {
            'inline'	: True
        },
    'noframes'	: {
            'frames'	: True,
            'block'	: True
        },
    'blink'	: {
            'inline'	: True
        },
    'noembed'	: {
            'inline'	: True
        },
    'thead'	: {
            'opt'	: True,
            'table'	: True,
            'rowgrp'	: True
        },
    'abbr'	: {
            'inline'	: True
        },
    'u'	: {
            'inline'	: True
        },
    'plaintext'	: {
            'obsolete'	: True,
            'block'	: True
        },
    'bgsound'	: {
            'empty'	: True,
            'head'	: True
        },
    'sup'	: {
            'inline'	: True
        },
    'h6'	: {
            'block'	: True,
            'heading'	: True
        },
    'server'	: {
            'block'	: True,
            'mixed'	: True,
            'head'	: True,
            'inline'	: True
        },
    'address'	: {
            'block'	: True
        },
    'basefont'	: {
            'empty'	: True,
            'inline'	: True
        },
    'param'	: {
            'empty'	: True,
            'inline'	: True
        },
    'th'	: {
            'no_indent'	: True,
            'opt'	: True,
            'row'	: True
        },
    'htrue'	: {
            'block'	: True,
            'heading'	: True
        },
    'head'	: {
            'opt'	: True,
            'omitst'	: True,
            'html'	: True
        },
    'tbody'	: {
            'opt'	: True,
            'table'	: True,
            'rowgrp'	: True
        },
    'legend'	: {
            'inline'	: True
        },
    'dd'	: {
            'no_indent'	: True,
            'opt'	: True,
            'deflist'	: True
        },
    's'	: {
            'inline'	: True
        },
    'hr'	: {
            'block'	: True,
            'empty'	: True
        },
    'li'	: {
            'no_indent'	: True,
            'opt'	: True,
            'list'	: True
        },
    'label'	: {
            'inline'	: True
        },
    'td'	: {
            'no_indent'	: True,
            'opt'	: True,
            'row'	: True
        },
    'kbd'	: {
            'inline'	: True
        },
    'dl'	: {
            'block'	: True
        },
    'div'	: {
            'block'	: True
        },
    'object'	: {
            'img'	: True,
            'head'	: True,
            'param'	: True,
            'inline'	: True,
            'object'	: True
        },
    'listing'	: {
            'obsolete'	: True,
            'block'	: True
        },
    'servlet'	: {
            'img'	: True,
            'param'	: True,
            'inline'	: True,
            'object'	: True
        },
    'dt'	: {
            'no_indent'	: True,
            'opt'	: True,
            'deflist'	: True
        },
    'pre'	: {
            'block'	: True
        },
    'center'	: {
            'block'	: True
        },
    'samp'	: {
            'inline'	: True
        },
    'col'	: {
            'empty'	: True,
            'table'	: True
        },
    'option'	: {
            'opt'	: True,
            'field'	: True
        },
    'cite'	: {
            'inline'	: True
        },
    'select'	: {
            'field'	: True,
            'inline'	: True
        },
    'i'	: {
            'inline'	: True
        },
    'link'	: {
            'empty'	: True,
            'head'	: True
        },
    'script'	: {
            'block'	: True,
            'mixed'	: True,
            'head'	: True,
            'inline'	: True,
            'entag_required':True,
        },
    'bdo'	: {
            'inline'	: True
        },
    'menu'	: {
            'obsolete'	: True,
            'block'	: True
        },
    'colgroup'	: {
            'opt'	: True,
            'table'	: True
        },
    'wbr'	: {
            'empty'	: True,
            'inline'	: True
        },
    'h2'	: {
            'block'	: True,
            'heading'	: True
        },
    'ins'	: {
            'mixed'	: True,
            'block'	: True,
            'inline'	: True
        },
    'p'	: {
            'opt'	: True,
            'block'	: True
        },
    'comment'	: {
            'inline'	: True
        },
    'sub'	: {
            'inline'	: True
        },
    'big'	: {
            'inline'	: True
        },
    'fieldset'	: {
            'block'	: True
        },
    'frameset'	: {
            'frames'	: True,
            'html'	: True
        },
    'button'	: {
            'inline'	: True
        },
    'noscript'	: {
            'mixed'	: True,
            'block'	: True,
            'inline'	: True
        },
    'optgroup'	: {
            'opt'	: True,
            'field'	: True
        }
    }



def rule(tag, attr, default):
    """ a shorthand for syntax table lookup """
    return html_syntax.get(tag.lower(),{}).get(attr, default)

# Node renderers
# each class represents different types of nodes such 
# as the !-directives, text node and regular elements.
# each tests the text to see if it wants to handle it.
# A node can optionally emit opening or closing texts. 
# messing method indicates that no text should be emitted.
# 
# xxx these should be made for each instance of elm 
#     so that openinig and closing renders can share states.
class Root(object):
    def test(self, elm):
        return elm=='_root'
class Null(object):
    def test(self, elm):
        return elm.split(' ')[0]=='_null'
    def open(self, elm, children):
        return None
    def close(self, elm, children):
        return None
class Directive(object):
    def test(self, elm):
        return elm[0]=='!'
    def open(self, elm, children):
        return "<%s>" % elm
class Text(object):
    def test(self, elm):
        return elm[0]=='^'
    def open(self, elm, children):
        return elm[1:]
class Element(object):
    def test(self, *args):
        return True             # catchall

    def open(self, elm, children):
        """ 
        need to control closing / and tailing newline.
        """
        # xx because this object is not specific to the elm, 
        # closing tag needs to be recomputed later..
        close_tag=self.close(elm, children)
        if close_tag is None:
            slash=' /'
        else:
            slash=''
        return "<%s%s>" % (elm, slash)

    def close(self, elm, children):
        """
        decide if this element requires a separate closing tag.
        this depends on presence of children and the syntax table.
        """

        tag=re.sub(r'\s.*$', '', elm)

        if len(children)==0 and not rule(tag, 'entag_required', False):
            return None

        return "</%s>" % tag

# precedence list of renderers. 
# first-come first-serve. order is important.
renderers=[Root(),Directive(),Null(),Text(),Element()]

def html_renderer(elm):
    """ choose the handler for this node """
    for r in renderers:
        if r.test(elm):
            return r
    return None

#### interface to tdl
def render_pre(elm, children, d):
    tag=filter(lambda s: len(s)>0, elm.split(' '))[0]
    r=html_renderer(elm)
    if r is None: 
        raise RuntimeError("unhandled ", tag)

    opener=getattr(r,'open', lambda *args: None)
    out=opener(elm, children)
    if out is None:
        return None

    things=[out]
    if not type(r)==Text:
        things.insert(0,"\n"+' '*(d)) # prefix
    return ''.join(things)
    
def render_post(elm, children, d):
    """ post order renderig of element """
    # tag=re.sub(r'\s.*$', '', elm)
    tag=filter(lambda s: len(s)>0, elm.split(' '))[0]

    # xx get the matching renderer object from the open render..
    r=html_renderer(elm)
    if r is None: 
        raise RuntimeError("unhandled ", elm)

    closer=getattr(r,'close', lambda *args: None)
    out=closer(tag, children)
    if out is not None:
        things=[out]
        if not rule(tag, 'inline', False) and not rule(tag, 'heading', False):
            things.insert(0,"\n"+' '*(d))
        return''.join(things)
    return None


################ tdl

#### util

class UnsetVariableError(Exception):
    pass

def stdout_stream(line):
    sys.stdout.write(line)

def module_by_filename(filename):
    for mod in sys.modules.values():
        try:
            # .pyc --> .py
            py_path=re.sub(r'\.pyc$', '.py', mod.__file__)
            if os.path.normpath(py_path)==os.path.normpath(filename):
                return mod
        except:
            pass
    return None

def truef(*arg):
    return True

#### parser
class Node(object):
    def __init__(self,parent=None,elm=None,depth=None,code=None,source=None):
        self.parent=parent
        self.elm=elm
        self.depth=depth        # XXX invalid when grafted. use traversal depth.
        self.code=code
        self.comment=''
        self.children=[]
        self.source=source
    def __unicode__(self):
        return "<Node %d %s :::: %s>" % (self.depth, self.elm, self.code)
    def __repr__(self):
        return "<Node %d %s :::: %s>" % (self.depth, self.elm, self.code)
    def push_child(self, ch):
        ch.parent=self
        self.children.append(ch)
    def push_sibling(self, bro):
        if self.parent is None:
            raise RuntimeError("cannot add sibling to root")
        # xx in general should push right next to me. append for now.
        self.parent.push_child(bro)
    def ancestor(self, nth):
        n=0
        a=self
        for i in range(nth):
            a=a.parent
            if a is None:
                break
            n=n+1
            if n>=nth:
                break
        return a
    def dump(self, d=0):
        if self.code is not None:
            code="\t\t:::: "+self.code
        else:
            code=''
        print "%s%s%s" % (' '*d, self.elm, code)
        map(lambda c: c.dump(d+1), self.children)

    def tag(self):
        """ 'div class=...' --> 'div' """
        # xxx parse this and save..
        return re.match(r'^(\S*)', self.elm).group(1)

    def traverse(node, visitor, collector=list.extend):
        res=[visitor(node)]
        for c in node.children:
            collector(res, c.traverse(visitor, collector=collector))
        return res

    def classes(self):
        m=re.match(r'.*\sclass\s*=\s*"(.*?)"', self.elm.lower())
        if m is None:
            return m
        return set(re.split(r'\s+', m.group(1)))

    def id(self):
        m=re.match(r'.*\sid\s*=\s*[\'"](.*?)[\'"]', self.elm.lower())
        if m is None:
            return None
        return m.group(1)

    def find(node, 
             tag=	truef, 
             classx=	truef, 
             id=	truef,
             meta=	truef
             ):
        #
        # tag
        # xxx don't reuse the arg-vars..
        if isinstance(tag, basestring):
            tt=tag
            tag=lambda t: t==tt
        elif callable(tag):
            pass
        else:
            raise RuntimeError("bogus tag")

        #
        # classx
        #
        if isinstance(classx, basestring):
            tmp=classx.lower()
            classx=lambda cs: tmp in cs if cs else False
        elif callable(classx):
            pass
        else:
            raise RuntimeError("bogus classx")

        #
        # id xxx todo
        #
        if id==truef:
            pass
        elif isinstance(id,basestring):
            id2=id              
            tmp=lambda n: n.id()==id2
            id=tmp
        else:
            raise RuntimeError("unexpcted id '%s'" % id)

        #
        # meta
        # 
        if meta==truef:
            pass
        elif isinstance(meta, basestring):
            # predicate for the root node.
            meta=lambda n: n.depth==0
        else:
            raise RuntimeError("unexpcted meta '%s'" % meta)

        # need higher-order and: pred=and(tag,class,id)
        def pred(n):
            classes=n.classes()
            return tag(n.tag()) and classx(classes) and meta(n) and id(n)

        return filter(lambda x: x is not None, 
                      node.traverse(lambda n: n if pred(n) else None))

    def get(self, **kw):
        """ return selected node """
        found=self.find(**kw)
        if not len(found)==1:
            # self.dump()
            raise RuntimeError("found %d instead of one for %s" % (len(found), kw))
        return found[0]

    def source_path(self):
        sources=[]
        n=self
        while n.parent:
            if n.source:
                sources.append(n.source)
            n=n.parent
        if n.source:
            sources.append(n.source)
        return sources

def parse(lines):
    cur_d=None
    root=Node(elm='_root', depth=0, parent=None)
    cur_node=None
    
    for l in lines:
        if l[-1]=='\n':             # xx need chomp..
            line=l[:-1]
        else:
            line=l

        if re.match(r'^\s*#', line):  # comment
            continue
        elif re.match(r'^\s*$', line): # blank lines
            continue
        # the rest must be valid element or text node specs
        match=re.match(r'^( *)(\S.*?)\s*(:::: *(.*))?$', line)
        if match is None:
            raise RuntimeError("failed to parse '%s'" % line)
        new_depth=len(match.group(1))+1 # one for the root
        elm=match.group(2)
        code=match.group(4)
        # print (new_depth, elm, code)

        # setup new node
        new_node=Node(elm=elm, depth=new_depth, code=code)

        try:
            cur_depth=cur_node.depth
        except:
            cur_depth=None

        # analysis on depth difference from previous
        if cur_depth is None:          # first time
            root.push_child(new_node)
        elif cur_depth+1==new_depth:
            cur_node.push_child(new_node)
        elif cur_depth >= new_depth:
            cur_node.ancestor(cur_depth-new_depth).push_sibling(new_node)
        else:
            raise RuntimeError("bogus depth at: ", lines)

        cur_node=new_node

    return root

#### rendering

def render_branches(branches, runtime):
    """ execute the list of renderables
    """
    for branch in branches:
        if type(branch)==str:
            runtime.outstream(str_eval(branch, runtime))
        elif type(branch)==types.FunctionType:
            branch(runtime)
        else:
            ddd("unexpected type: ", branch)

class UndefinedVariableError(Exception):
    pass

def str_eval(s, runtime):
    """ eval expr enclosed in {{}} """

    def replace(m):
        mstr,=m.groups()
        envdict=runtime.env.copy()
        try:
            return str(eval(mstr, envdict))
        except Exception, e:
            if runtime.eval_error_handler:
                return runtime.eval_error_handler(mstr, e)
            raise UndefinedVariableError("failed to eval expression: '%s'", mstr,
                                         str(e))

    return re.sub("{{(.*?)}}", replace, s) # xx persist this

#### compiler
def _compile(copt, tree, d=0):
    """
    internal, recursive compilation function.
    take tree node. return a callable that renders the tree 
    with runtime data.
    """
    elm,code,children=tree.elm,tree.code,tree.children
    # print 'xx', tree.elm
    # 
    # static
    # 
    if code is None:
        #
        # renderables=[pre, compiled-children, post]
        # flatten and join adjacent strings together.
        # return a list of renderables that are alternating
        # strings and functions.
        # 
        things=[]
        things.append(render_pre(elm, children, d))
        # xx bubble up the Renderer instance up here so this can be 
        # handled in class Null.
        incr=0 if elm.split(' ')[0]=='_null' else 1
        branches=map(lambda c: _compile(copt, c,d+incr), children)
        things.extend(list_flatten(branches))
        things.append(render_post(elm, children, d))

        coalesced=coalesce(filter(notnone, things))
        # print '.'*d, coalesced
        return coalesced

    # 
    # dynamic
    # 
    # make a static node
    #static=[elm]+children
    static=Node(elm=elm)
    static.children=children
    branch=_compile(copt, static, d)  # renderables
    # print 'dyn:', branch

    # renderer
    def deferred_node_d(runtime):
        # setup the frame
        xbranch=lambda: render_branches(branch, runtime)
        envdict=runtime.env
        def bind(**kw):
            """ evaluate the node in an extended environment """
            envdict.update(kw)
            return xbranch()
        envdict.update({'BRANCH':xbranch,
                        'BIND':bind,
                        })
        # 
        # deal with special syntax
        # 
        # BIND(dict()) special form.

        # iteration: 'for <foo> in <bar>' 
        # xx support destructuring: for n,v in dict.items()
        # 
        m=re.match(r'^\s*for\s+(\w+)\s+in\s+(.+)\s*?$', code)
        if m is not None:
            var_name=m.group(1)
            iterable_expr=m.group(2)
            # map(BRANCH, iterable)
            # iterate BRANCH over eval(iterable)
            # with var_name bound to the value.
            lst=xeval(iterable_expr, envdict)
            for var in lst:
                envdict.update({var_name:var})
                xbranch()
            # xx need to early return due to lack of assign and test in python
            return

        # 
        # conditional: 'if <cond>'
        # 
        m=re.match(r'^\s*if\s+(.+)\s*?$', code)
        if m is not None:
            cond_expr=m.group(1)
            if xeval(cond_expr, envdict):
                xbranch()
            else:
                pass
            return
        # 
        # prototype: PROTO(foo, bar)
        # 
        m=re.match(r'^PROTO\((.*)\)$', code.strip())
        if m:
            params=map(str.strip,m.group(1).split(','))
            unset_vars=[]
            for param_name in params:
                # test for existance or None-ness?
                try: 
                    xeval(param_name, envdict)
                except:
                    unset_vars.append(param_name)
            if unset_vars:
                ex=UnsetVariableError('undefined params: ', 
                                      unset_vars,
                                      'in: ', 
                                      tree.source_path())
                eval_error_handler=copt.get('eval_error_handler')
                if eval_error_handler:
                    eval_error_handler(str(unset_vars), ex)
                else:
                    raise ex
            else:
                xbranch()
            return
        # 
        # general python expression (none-special form)
        # 
        xeval(code, envdict)

    def wrapper(*args,**kw):
        """ wrapper around deferred_node_d to add source path to any exception """
        try:
            deferred_node_d(*args,**kw)
        except Exception, e:
            if not 'in: ' in e.args: # avoid repetition.
                e.args+=('in: ', tree.source_path(),)
            raise

    return [wrapper]

class Runtime(object):
    def __init__(self,page_data={},outstream=None, fdict={}, eval_error_handler=None):
        self.outstream=outstream
        self.env=page_data.copy()
        self.env.update(fdict)
        # xx receiver does not get the 'this' object..
        #    client might want to get at the env..
        self.eval_error_handler=eval_error_handler

class Renderer(object):

    def __init__(self, tree, **ckw):
        
        self.ckw=ckw
        # xx adjust depth for the _root element..
        d=-1 if tree.elm=='_root' else 0
        self.renderer=_compile(ckw, tree, d)

    def render(self, **kw):
        # if outstream is not spcified, the output is accumulated 
        # and returned.  if it outstream is provided by the caller, 
        # an empy string is returned.

        for k,v in self.ckw.items():
            kw.setdefault(k,v)

        out_lines=[]
        kw.setdefault('outstream', out_lines.append)

        rt=Runtime(**kw)
        render_branches(self.renderer, rt)

        return ''.join(out_lines)

#### public interface
# note this name clobbers builtin compile in this module..
def compile(tree, **ckw):
    """ 
    returns a renderer that should be called with 
    page_data dictionary and **kw for the runtime:
    fdict, outstream..

    fdict can be explicitely passed like:
    fdict=tdl.funcs_in_module(__name__)

    xx now that page_data and fdict are merged, 
    git rid of fdict? both variables and functions can be 
    rounded oup by the caller into the envdict.
    """

    return Renderer(tree, **ckw)

def funcs_in_module(module):
    """
    a helper to round up funcs in a module.
    """
    import types

    if type(module)==str:
        mdict=__import__(module).__dict__
    else:
        mdict=module.__dict__
        
    func_dict={}
    for name in mdict.keys():
        if not re.match(r'__\w+__', name):
            val=mdict[name]
            if type(val)==types.FunctionType:
                func_dict[name]=val
    return func_dict

################ graft

def kwdict(**kw): 
    return kw

class Grafter(object):
    """ 
    top-level grafting interface.
    synopsis:

      # main_tdl wants to graft a branch from another tree def
      div 	:::: GRAFT("foo/.bar")
      
      # compile with forest
      r=renderer(tree=tree, forest={'main':main_tdl, 'foo':foo_tdl})

      # inf api
      # construct with a catalog of named trees.
      grafter=graft.Grafter(main=main_td, foo=branch_def)
      # resolve graft directives
      grafter.do_graft(tree)

      # the logical tree name 'foo' above can be referenced in tdl.
      # 'bar' would be a class name defined in the tree 'foo'.
      div 	:::: GRAFT("foo/.bar")

      DWIM handling of tree source.
      manages a repository of trees to simplify grafting operations.
    """
    def __init__(self, **name_treedef):
        """ DWIM interface for concise definition of tree sources.
        input is resolved to dict of form:
           { main=TreeDef(string=main_td) }
        name_treedef maps logical tree names to tree source specifier, 
        which can be: tdl string, path to file containing tdl...
        """
        self.forest={}
        for name,td_specifier in name_treedef.items():
            if '\n' in td_specifier:
                td=TreeDef(string=td_specifier,name=name)
            else:
                td=TreeDef(path=td_specifier,name=name)
            self.forest[name]=td

    def do_graft(grafter, tree):
        """ resolve graft directives in the tree.
            xx only single-layer grafting is supported.
               need to make it recursive.
        """

        def graft_point_p(node):
            """ predicate for graft point node """
            if node.code is None:
                return None
            # allow a pass-thru expression to follow GRATFT() statement, 
            # which gets evaluated at render time.
            # example: GRAFT("...") BIND(foo='bar')
            # xxx formalize and generalize multi-statements.
            # perhaps with ; 
            # xxx make GRAFT a function rather than a special form
            # so it could be embedded in the expression..
            m=re.match(r'^GRAFT\((.*?)\)\s*(.+)?\s*$', node.code)
            if m:
                return node,m.group(1),m.group(2)
            return None

        graft_points=filter(lambda x: x is not None, tree.traverse(graft_point_p))
        for gp in graft_points:
            	# unpack graft point finder's result
            node,branch_spec_expr,passthru_expr=gp
            	# xx branch spec is interpreted as a python expression
            	# which evaluates to a branch spec string.
            branch_spec_str=eval(branch_spec_expr)
        	# get the branch
            bs=BranchSelector(grafter, branch_spec_str)
            node.source=bs.tree_def.source
            	# rewrite the directive
            assert passthru_expr!=''
            node.code=passthru_expr
            # xxx need to add comment to render_pre call for this to work
            # node.comment="\t\t<!-- graft '%s' -->" % branch_spec_str
            node.elm+=" graft=\"%s\"" % branch_spec_str
        	# finally graft
            node.push_child(bs.branch())

class TreeDef(object):
    """ abstract various formats of tree defition """
    def __init__(self, string=None, path=None, name=None):
        self.name=name
        if string is not None:
            self.string=string
            self.source='<<tree-from-string "%s" >>' % name
        elif path:
            try:
                self.string=file(path).read()
            except Exception, e:
                raise RuntimeError(e, path)
            self.source='branch "%s" from "%s"' % (name,path)
    def lines(self):
        return filter(len, self.string.split('\n'))
    def tree(self):
        # xxx memoize this
        return parse(self.lines())

def parse_selector(selector):
    """ a mini css parser 
        see BranchSelector
    """

    if selector.startswith('&'):
        return { 'meta' : selector[1:] }
    
    m=re.match(r'^(\w+)?([.#])(\w+)$', selector)
    sel=None                # indicates root
    if m:
        type_name,prefix,cls_or_id_name=m.groups()
        sel={}
        if type_name is not None:
            sel['tag']=type_name
        if prefix=='.':
            sel.update({'classx':cls_or_id_name})
        elif prefix=='#':
            sel.update({'id':cls_or_id_name})
        else:
            raise RuntimeError("bogus selector '%s'" % selector)
    m=re.match(r'^(\w+)$', selector)
    if m:
        sel={'tag':m.grup(1)}
    return sel

class BranchSelector(object):
    """ 
    resolve a simple tree and node descriptors into a branch object.
    tree def + node selector
    """
    @classmethod
    def parse(cls, spec):
        """ 
        standalone (static) parser of Branch Selector Spec
            syntax:  
            spec: 	tree-name/selector
            tree-name:	^\w+$
            selector:	^(\w+)?[.#]\w+$   or ^\w+$
             (basically a mini css selector supporting id and class selector only 
              with no grouping)

            Thus
            BranchSelector("some_page/div.foo")
            is a short for:
            BranchSelector(tree_def=TreeDef(string=some_page_def),
                           node_selector=kwdict(tag="div",classx="foo")))

        """

        tree_name,selector=spec.split('/')
        #
        # parse selector spec into selector dict.
        #
        sel=parse_selector(selector)
        #
        # resolve the tree_name into tree_def.
        # 
        return tree_name,sel

    def parse2(self, spec):
        """ resolve tree_name into TreeDef object """
        tree_name,sel=BranchSelector.parse(spec)
        try:
            return self.grafter.forest[tree_name],sel
        except KeyError:
            raise RuntimeError("you need to register '%s' in forest" % tree_name)

    def __init__(self, grafter, spec=None, tree_def=None, node_selector=None):
        """ either spec is specified 
            or tree_def and node_selector are both provieded
        """
        # my parent object tha provides the context.
        assert isinstance(grafter, Grafter)
        self.grafter=grafter
        if spec:
            self.tree_def,self.node_selector=self.parse2(spec)
        else:
            self.tree_def=tree_def
            self.node_selector=node_selector
    def tree(self):
        return self.tree_def.tree()
    def branch(self):
        return self.tree().get(**self.node_selector)

def graft(tree, graft_point_sel, branch_sel):
    """ standalone util to graft the branch on the tree"""
    tree.get(**graft_point_sel).push_child(branch_sel.branch())
    return tree

################ top

def renderer(**kw):
    """
    compile one of the forms: file, string, parsed tree
    """

    tdl_file=kw.get('file', None)
    if tdl_file is not None:
        # may be check stffix..
        kw['source']=kw['file']
        del kw['file']
        try:
            tdl_file=file(tdl_file)
        except Exception, e:
            # xx force it to print the file..
            raise RuntimeError(str(e))
        return renderer(tree=parse(tdl_file.readlines()), **kw)

    string=kw.get('string', None)
    if string is not None:
        kw['source']='<<tree-from-string>>'
        del kw['string']
        return renderer(tree=parse(filter(len, string.split('\n'))), **kw)

    # tree is supplied
    assert kw['tree']
    kw.setdefault('source', '<<tree>>')

    # grab the functions in callers module
    # and make them available to the template.
    fdict=kw.get('fdict',None)
    if fdict is None:
        # ddd(__file__, map(lambda x:x[0], traceback.extract_stack()))
        #print filename, map(lambda t: t[0], traceback.extract_stack())
        filename=re.sub(r'pyc$', 'py', __file__)
        above_me=filter(lambda mo: mo[0]!=filename, traceback.extract_stack())
        # ddd(map(lambda x:x[0], above_me))
        frame=above_me[-1]
        client_filename=frame[0]
        # ddd(client_filename)
        mod=module_by_filename(client_filename)
        if mod is None:
            raise RuntimeError("could not find '%s' in %s" % (client_filename, sys.modules.keys()))
        fdict=funcs_in_module(mod)
        #ddd(fdict)
    kw['fdict']=fdict

    # optionally apply node selection for partial rendering.
    selector=kw.get('selector', None)
    if selector is not None:
        tree=kw['tree'].get(**selector)
    else:
        tree=kw['tree']

    tree.source=kw['source']

    #
    # splice. graft branches specified as compiler arg.
    # xx todo: allow BranchSelector syntax for the splice values.
    # need to extend BranchSelector to handle tree_def name or file (path).
    #      * split by left-most /, so that lhs could be a path
    #      * look up the rhs in forest. 
    #        failing that, if -f, then load as file: TreeDef(path=tree_def)
    #
    splice=kw.get('splice', {})
    for graft_point,branch_selector in splice.items():
        # graft_point is simply a node (css) selector string.
        assert isinstance(graft_point, basestring)
        # branch_selector: tree-def [ node-selector ]
        try:
            tree_def,selector=branch_selector
        except:
            tree_def,selector=branch_selector,'&root' # defaults to root

        # graft selected branch on the graft point of this tree
        gp_sel=graft.parse_selector(graft_point)
        br_sel=graft.parse_selector(selector)

        bs=graft.BranchSelector(graft.Grafter(), 
                                tree_def=graft.TreeDef(path=tree_def), 
                                node_selector=br_sel)
        graft.graft(tree, gp_sel, bs)

    #
    # resolve grafts embedded in tdl
    #
    forest=kw.get('forest', None)
    if forest is not None:
        grafter=graft.Grafter(**forest)
        grafter.do_graft(tree)
        # XXX make it two-phase resolution.
        # really, need to do this recursively..
        grafter.do_graft(tree)  

    # slice compile and runtime options.
    ckw=dict([(k,v) for k,v in kw.items() if k in set(['eval_error_handler', 'fdict'])])
    return compile(tree, **ckw)


################ cli
def main():

    import baker
    import json
    
    @baker.command
    def render(tempura_file, page_data_json_file):
        """render html based on the tempura definition and page data
        """
        
        print renderer(string=file(tempura_file).read()).render(page_data=json.load(file(page_data_json_file)))

    @baker.command
    def demo():
        """demonstrage the rendering api"""

        doc_tmpr="""
html
 body
  div
   table
    tr	class="{{'ODD' if ii%2 else 'EVEN'}}"	:::: for ii in range(3)  # iteration
     td
      ^hi
      span class="conditional"		::::  if ii%2                    # conditional
       ^{{ii}} odd
     td
      ^ho {{ii}}                                                         # string literal and interpolation
   div class="footer"
    span
     ^oh hai {{name}}
   span					:::: for tag in tags
    ^{{tag}}
   span
    ^any ptyhon expression can be embedded: 
    ^{{'&'.join(map('='.join, [('foo','bar'),('baz','arg')]))}}          # interpolation with expression
"""

        page_data={'tags':['foo', 'bar', 'baz'], 'name': 'tengu'}
        print renderer(string=doc_tmpr).render(page_data=page_data)

    baker.run()


if __name__=='__main__':

    main()
