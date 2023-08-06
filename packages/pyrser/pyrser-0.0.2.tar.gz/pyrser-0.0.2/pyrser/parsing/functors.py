import types
from pyrser import meta, error
from pyrser.parsing.base import BasicParser
from pyrser.parsing.node import Node
from pyrser.parsing.stream import Tag


class Functor:
    """Dummy Base class for all parse tree classes.

    common property:
        pt if contain a Functor
        ptlist if contain a list of Functor
    """
    pass


class Seq(Functor):
    """A B C bnf primitive as a functor."""

    def __init__(self, *ptlist: Functor):
        Functor.__init__(self)
        if len(ptlist) == 0:
            raise TypeError("Expected Functor")
        self.ptlist = ptlist

    def __call__(self, parser: BasicParser) -> bool:
        parser._stream.save_context()
        for pt in self.ptlist:
            parser.skip_ignore()
            if not pt(parser):
                return parser._stream.restore_context()
        return parser._stream.validate_context()


class Scope(Functor):
    """functor to wrap SCOPE/rule directive or just []."""

    def __init__(self, begin: Seq, end: Seq, pt: Seq):
        Functor.__init__(self)
        self.begin = begin
        self.end = end
        self.pt = pt

    def __call__(self, parser: BasicParser) -> Node:
        if not self.begin(parser):
            return False
        res = self.pt(parser)
        if not self.end(parser):
            return False
        return res


class LookAhead(Functor):
    """!!A bnf primitive as a functor."""
    def __init__(self, pt: Functor):
        Functor.__init__(self)
        self.pt = pt

    def __call__(self, parser: BasicParser) -> bool:
        parser._stream.save_context()
        res = self.pt(parser)
        parser._stream.restore_context()
        return res


class Neg(Functor):
    """!A bnf primitive as a functor."""

    def __init__(self, pt: Functor):
        Functor.__init__(self)
        self.pt = pt

    def __call__(self, parser: BasicParser):
        parser._stream.save_context()
        if self.pt(parser):
            res = parser._stream.restore_context()
            return res
        return parser._stream.validate_context()


class Complement(Functor):
    """~A bnf primitive as a functor."""

    def __init__(self, pt: Functor):
        Functor.__init__(self)
        self.pt = pt

    def __call__(self, parser: BasicParser) -> bool:
        if parser.read_eof():
            return False
        ## skip/undo?
        parser.skip_ignore()
        parser._stream.save_context()
        res = self.pt(parser)
        if not res:
            parser._stream.incpos()
            return parser._stream.validate_context()
        parser._stream.restore_context()
        parser.undo_ignore()
        return False


class Until(Functor):
    """->A bnf primitive as a functor."""

    def __init__(self, pt: Functor):
        Functor.__init__(self)
        self.pt = pt

    def __call__(self, parser: BasicParser) -> bool:
        ## skip/undo?
        parser.skip_ignore()
        parser._stream.save_context()
        while not parser.read_eof():
            res = self.pt(parser)
            if res:
                return parser._stream.validate_context()
            parser._stream.incpos()
        parser._stream.restore_context()
        parser.undo_ignore()
        return False


class Call(Functor):
    """Functor wrapping a BasicParser method call in a BNF clause."""

    def __init__(self, callObject, *params):
        Functor.__init__(self)
        self.callObject = callObject
        self.params = params

    def __call__(self, parser: BasicParser) -> Node:
        return self.callObject(parser, *self.params)


class CallTrue(Call):
    """Functor to wrap arbitrary callable object in BNF clause."""

    def __call__(self, parser: BasicParser) -> Node:
        self.callObject(*self.params)
        return True


class Capture(Functor):
    """Functor to handle capture nodes."""

    def __init__(self, tagname: str, pt: Functor):
        Functor.__init__(self)
        if not isinstance(tagname, str) or len(tagname) == 0:
            raise TypeError("Illegal tagname for capture")
        self.tagname = tagname
        self.pt = pt

    def __call__(self, parser: BasicParser) -> Node:
        if parser.begin_tag(self.tagname):
            # subcontext
            parser.push_rule_nodes()
            res = self.pt(parser)
            parser.pop_rule_nodes()
            if res and parser.end_tag(self.tagname):
                tag = parser.get_tag(self.tagname)
                # no bindings, wrap it in a Node instance
                if type(res) is bool:
                    res = Node()
                # update node cache
                parser.tag_node(self.tagname, res)
                parser.rule_nodes[self.tagname] = res
                # forward nodes
                return res
        return False


class DeclNode(Functor):
    """Functor to handle node declaration with __scope__:N."""

    def __init__(self, tagname: str):
        Functor.__init__(self)
        if not isinstance(tagname, str) or len(tagname) == 0:
            raise TypeError("Illegal tagname for capture")
        self.tagname = tagname

    def __call__(self, parser: BasicParser) -> Node:
        parser.rule_nodes[self.tagname] = Node()
        return True


class Bind(Functor):
    """Functor to handle the binding of a resulting nodes
    to an existing name.
    """

    def __init__(self, tagname: str, pt: Functor):
        Functor.__init__(self)
        if not isinstance(tagname, str) or len(tagname) == 0:
            raise TypeError("Illegal tagname for capture")
        self.tagname = tagname
        self.pt = pt

    def __call__(self, parser: BasicParser) -> Node:
        res = self.pt(parser)
        if res:
            parser.bind(self.tagname, res)
            return res
        return False


class Alt(Functor):
    """A | B bnf primitive as a functor."""

    def __init__(self, *ptlist: Seq):
        Functor.__init__(self)
        self.ptlist = ptlist

    def __call__(self, parser: BasicParser) -> Node:
        # save result of current rule
        parser.push_rule_nodes()
        for pt in self.ptlist:
            parser._stream.save_context()
            parser.skip_ignore()
            parser.push_rule_nodes()
            res = pt(parser)
            if res:
                parser.pop_rule_nodes()
                parser.pop_rule_nodes()
                parser._stream.validate_context()
                return res
            parser.pop_rule_nodes()
            parser._stream.restore_context()
        parser.pop_rule_nodes()
        return False


class RepOptional(Functor):
    """[]? bnf primitive as a functor."""
    def __init__(self, pt: Seq):
        Functor.__init__(self)
        self.pt = pt

    def __call__(self, parser: BasicParser) -> bool:
        parser.skip_ignore()
        res = self.pt(parser)
        if res:
            return res
        return True


class Rep0N(Functor):
    """[]* bnf primitive as a functor."""

    def __init__(self, pt: Seq):
        Functor.__init__(self)
        self.pt = pt

    def __call__(self, parser: BasicParser) -> bool:
        parser.skip_ignore()
        parser.push_rule_nodes()
        while self.pt(parser):
            parser.skip_ignore()
        parser.pop_rule_nodes()
        return True


class Rep1N(Functor):
    """[]+ bnf primitive as a functor."""

    def __init__(self, pt: Seq):
        Functor.__init__(self)
        self.pt = pt

    def __call__(self, parser: BasicParser) -> bool:
        parser._stream.save_context()
        # skip/undo
        parser.skip_ignore()
        parser.push_rule_nodes()
        if self.pt(parser):
            parser.skip_ignore()
            while self.pt(parser):
                parser.skip_ignore()
            parser.pop_rule_nodes()
            return parser._stream.validate_context()
        parser.pop_rule_nodes()
        return parser._stream.restore_context()


class Error(Functor):
    """Raise an error."""

    def __init__(self, msg: str, **kwargs):
        self.msg = msg
        self.kw = kwargs

    def __call__(self, parser: BasicParser) -> bool:
        error.throw(self.msg, parser, **self.kw)


class Rule(Functor):
    """Call a rule by its name."""

    def __init__(self, name: str):
        Functor.__init__(self)
        self.name = name

    def __call__(self, parser: BasicParser) -> Node:
        parser.push_rule_nodes()
        res = parser.eval_rule(self.name)
        parser.pop_rule_nodes()
        return res


class Hook(Functor):
    """Call a hook by his name."""

    def __init__(self, name: str, param: [(object, type)]):
        Functor.__init__(self)
        self.name = name
        # compose the list of value param, check type
        for v, t in param:
            if type(t) is not type:
                raise TypeError("Must be pair of value and type (i.e: int, "
                                "str, Node)")
        self.param = param

    def __call__(self, parser: BasicParser) -> bool:
        valueparam = []
        for v, t in self.param:
            if t is Node:
                if v not in parser.rule_nodes:
                    error.throw("Unknown capture variable : %s" % v, parser)
                valueparam.append(parser.rule_nodes[v])
            elif type(v) is t:
                valueparam.append(v)
            else:
                raise TypeError("Type mismatch expected {} got {}".format(
                    t, type(v)))
        return parser.eval_hook(self.name, valueparam)


class MetaDirectiveWrapper(type):
    """metaclass of all DirectiveWrapper subclasses.
    ensure that begin and end exists in subclasses as method"""
    def __new__(metacls, name, bases, namespace):
        cls = type.__new__(metacls, name, bases, namespace)
        if 'begin' not in namespace:
            raise TypeError(
                "DirectiveWrapper %s must have a begin method" % name)
        if not(isinstance(namespace['begin'], types.FunctionType)):
            raise TypeError(
                "'begin' not a function class in DirectiveWrapper %s" % name)
        if 'end' not in namespace:
            raise TypeError(
                "DirectiveWrapper %s subclasse must have a end method" % name)
        if not(isinstance(namespace['end'], types.FunctionType)):
            raise TypeError(
                "'end' not a function class in DirectiveWrapper %s" % name)
        return cls


class DirectiveWrapper(metaclass=MetaDirectiveWrapper):
    """functor to wrap begin/end directive"""

    def __init__(self, ):
        Functor.__init__(self)

    def checkParam(self, params: list):
        if (not hasattr(self.__class__, 'begin') or
                not hasattr(self.__class__, 'end')):
            return False
        pbegin = self.__class__.begin.__code__.co_varnames
        tbegin = self.__class__.begin.__annotations__
        pend = self.__class__.end.__code__.co_varnames
        tend = self.__class__.end.__annotations__
        idx = 0
        for pname in pbegin:
            if pname in tbegin:
                if not isinstance(params[idx], tbegin[pname]):
                    raise TypeError(
                        "{}: Wrong parameter in begin method parameter {} "
                        "expected {} got {}".format(
                            self.__class__.__name__,
                            idx, type(params[idx]),
                            tbegin[pname]))
                idx += 1
        idx = 0
        for pname in pend:
            if pname in tend:
                if not isinstance(params[idx], tend[pname]):
                    raise TypeError(
                        "{}: Wrong parameter in end method parameter {} "
                        "expected {} got {}".format(
                            self.__class__.__name__,
                            idx,
                            type(params[idx]),
                            tend[pname]))
                idx += 1
        return True

    def begin(self):
        pass

    def end(self):
        pass


class Directive(Functor):
    """functor to wrap directive HOOKS"""

    def __init__(self, directive: DirectiveWrapper, param: [(object, type)],
                 pt: Functor):
        Functor.__init__(self)
        self.directive = directive
        self.pt = pt
        # compose the list of value param, check type
        for v, t in param:
            if type(t) is not type:
                raise TypeError(
                    "Must be pair of value and type (i.e: int, str, Node)")
        self.param = param

    def __call__(self, parser: BasicParser) -> Node:
        valueparam = []
        for v, t in self.param:
            if t is Node:
                valueparam.append(parser.rule_nodes[v])
            elif type(v) is t:
                valueparam.append(v)
            else:
                raise TypeError(
                    "Type mismatch expected {} got {}".format(t, type(v)))
        if not self.directive.checkParam(valueparam):
            return False
        if not self.directive.begin(parser, *valueparam):
            return False
        res = self.pt(parser)
        if not self.directive.end(parser, *valueparam):
            return False
        return res
