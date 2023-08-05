# -*- coding: utf-8 -*-

import cgi
import os.path
import sys
import types
import inspect

import fin.module


FIN_DIR = os.path.dirname(os.path.abspath(__file__))


def is_child_module(module):
    mod_path = getattr(module, "__file__", None)
    return mod_path is not None and os.path.dirname(os.path.abspath(mod_path)).startswith(FIN_DIR)


COMMON_TYPES = (list, tuple, dict, types.NoneType, basestring, set, frozenset)
TYPE_MAP = {
    "type": "class",
    "NotImplementedType": "abstract",
    "object": "singleton",
    "instancemethod": "method"
}
UNDEFINED = object()


def map_ids(obs):
    if "obj" in obs:
        yield id(obs["obj"]), obs["path"]
    if "children" in obs:
        for child in obs["children"].values():
            for ids in map_ids(child):
                yield ids


def convert_args(args):
    if args in (None, ()):
        return args
    defaults = () if args.defaults is None else args.defaults
    extra = []
    if args.varargs is not None:
        extra.append(("*%s" % args.varargs, UNDEFINED))
    if args.keywords is not None:
        extra.append(("**%s" % args.keywords, UNDEFINED))
    normal = zip(args.args, ((UNDEFINED, ) * (len(args.args) - len(defaults))) + defaults)
    return tuple(normal + extra)


def describe_obj(obj, path):
    obj_type = type(obj)
    type_name = obj_type.__name__
    type_name = TYPE_MAP.get(type_name, type_name)
    args = () if callable(obj) else None

    for candidate in [obj, getattr(obj, "__init__", None), getattr(obj, "__init__", None)]:
        try:
            args = inspect.getargspec(candidate)
        except TypeError:
            pass
        else:
            break

    if isinstance(obj, types.TypeType):
        if issubclass(obj, Exception):
            type_name = "exception"

    if isinstance(obj, types.MethodType):
        if isinstance(obj.__self__, types.TypeType):
            type_name = "classmethod"
        args = args._replace(args=args.args[1:])

    doc = None
    if is_child_module(inspect.getmodule(obj)):
        doc = getattr(obj, "__doc__", None)
    return {
        "name": path[-1] if len(path) > 0 else None,
        "args": convert_args(args),
        "type": type_name,
        "doc": doc,
        "path": tuple(path)
    }


def build_dict(dict_ob, path, obj):
    base = dict_ob
    for el in path:
        if "children" not in base:
            base["children"] = {}
        base = base["children"]
        if el not in base:
            sub = {}
            base[el] = sub
        base = base[el]
    if "ob" not in base:
        base["obj"] = obj
        base.update(describe_obj(obj, path))


class Renderer(object):

    def __init__(self):
        super(Renderer, self).__init__()
        self.id_map = {}

    def recurse_objects(self, obj, prefix=None, obs=None, iter_fn=lambda x, p: True):
        if prefix is None:
            prefix = (self.NAME, )
        obs = set(() if obs is None else obs)
        if not iter_fn(obj, prefix):
            raise StopIteration()
        if id(obj) in obs:
            raise StopIteration()
        yield [prefix, obj]
        obs.add(id(obj))
        child_names = set()
        if isinstance(obj, types.ModuleType):
            for name, mod in fin.module.import_child_modules(obj, ignore=None).iteritems():
                child_names.add(name)
                for child in self.recurse_objects(mod, prefix + (name, ), obs, iter_fn):
                    yield child

        def handle_children(keys):
            for key in keys:
                if key in child_names:
                    continue
                value = getattr(obj, key, UNDEFINED)
                if value is UNDEFINED:
                    continue
                child_names.add(key)
                for child in self.recurse_objects(value, prefix + (key, ), obs, iter_fn):
                    yield child

        if hasattr(obj, "__dict__"):
            for child in handle_children(obj.__dict__.keys()):
                yield child
        if hasattr(obj, "__slots__"):
            for child in handle_children(obj.__slots__):
                yield child


def trunc(val, num):
    val = str(val)
    if len(val) > num:
        return cgi.escape(val[:num-1]) + "…"
    return cgi.escape(val)


class SingleFile(object):

    HEAD = """<!DOCTYPE html>
    <head>
        <title>%(title)s</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        %(extra)s
    </head>
    <body>
    <nav class="navbar navbar-default" role="navigation">
      <div class="navbar-header">
        <a class="navbar-brand" href="#">%(title)s</a>
        </div>
    </nav>
    <div class="container">
    """
    TAIL = """</div>
    </body>"""
    STYLESHEETS = ("bootstrap.css", "doc.css", )
    SCRIPTS = ()
    OBJECT_PLACEHOLDER = '<span class="complex">object</span>'

    NAME = NotImplemented

    TYPE_STYLES = {
        "module": "info",
        "function": "success",
        "abstract": "warning"
    }

    def __init__(self):
        super(SingleFile, self).__init__()

    @property
    def title(self):
        return "%s Documentation" % (cgi.escape(self.NAME), )

    @property
    def head(self):
        extra = []
        for sheet in self.STYLESHEETS:
            extra.append('<link rel="stylesheet" type="text/css" href="%s">' % (sheet, ))
        return self.HEAD % {
            "title": self.title,
            "extra": "".join(extra)
        }

    @property
    def top(self):
        return ""

    @property
    def bottom(self):
        return ""

    def output_element(self, element):
        if "obj" not in element:
            return "".join(self.output_element(c) for c in element["children"].values())
        type_style = self.TYPE_STYLES.get(element["type"], "default")
        data = []
        data += '<div class="panel panel-%s">' % (type_style, )
        data += '<div class="panel-heading"><div class="panel-title">'
        data += '<a name="%s"></a>' % (".".join(element["path"]), )
        type_id = id(type(element["obj"]))
        if type_id in self.id_map:
            type_path = ".".join(self.id_map[type_id])
            data += '<span class="label label-default"><a href="#%s">%s</a></span> ' % (type_path, type_path)
        else:
            data += '<span class="label label-default">%s</span> ' % (element["type"], )
        if isinstance(element["obj"], types.ModuleType):
            data += ".".join(element["path"])
        else:
            data += element["name"]
        if element.get("args") is not None:
            param_data = self.parameters(element["args"])
            data += '(<span class="params">' + ", ".join(param_data) + "</span>)"
        value_data = self.value_data(element["obj"])
        if value_data != self.OBJECT_PLACEHOLDER:
            data += ' <span class="value">= ' + value_data + "</span>"
        data += "</div></div>"
        sub = []
        sub.extend(self.document_object(element))
        if "children" in element:
            for child in element["children"].viewvalues():
                sub.append(self.output_element(child))
        if len(sub):
            data += '<div class="panel-body">'
            data.extend(sub)
            data += "</div>"
        data += "</div>"
        return "".join(data)

    def parameters(self, args):
        out = []
        for arg, default in args:
            if default is UNDEFINED:
                if arg[0] == "*":
                    out.append("<em>%s</em>" % arg)
                else:
                    out.append(arg)
            else:
                out.append("%s=%s" % (arg, self.value_data(default, 1)))
        return out

    def value_data(self, obj, limit=2):
        if limit < 1:
            return "…"
        if obj in (None, True, False):
            return '<span class="const">%s</span>' % repr(obj)
        if isinstance(obj, (int, long, float, complex)):
            return "%s" % (obj, )
        if isinstance(obj, basestring):
            return '"%s"' % (trunc(obj, 40), )
        for ty, before, after in [
            (list, "[", "]"),
            (tuple, "(", ")"),
            (set, "{", "}")
        ]:
            if isinstance(obj, ty):
                val = ", ".join([self.value_data(o, limit-1) for o in obj])
                return '%s%s%s' % (before, trunc(val, 60), after)
        if limit != 2 and id(obj) in self.id_map:
            path = ".".join(self.id_map[id(obj)])
            return '<a href="#%s">%s</a>' % (path, trunc(path, 40))
        if isinstance(obj, dict):
            val = ", ".join("%s: %s" % (self.value_data(k, limit-1), self.value_data(v, limit-1)) for k, v in obj.viewitems())
            return "{%s}" % (trunc(val, 60))
        return self.OBJECT_PLACEHOLDER

    def render(self, doc, path):
        doc["name"] = self.NAME
        file = os.path.join(path, "index.html")
        with open(file, "wb") as fh:
            fh.write(self.head)
            fh.write(self.top)
            fh.write(self.output_element(doc))
            fh.write(self.TAIL)


class Rst(object):

    def document_object(self, element):
        parts = []
        if "doc" in element and element["doc"] is not None:
            parts.append('<div class="doc">')
            parts.append(element["doc"])
            parts.append("</div>")
        return parts


class FinDoc(Renderer, SingleFile, Rst):

    NAME = "fin"

    def filter_objects(self, obj, path):
        if isinstance(obj, (types.TypeType)):
            return True
        if len(path) > 0 and path[-1].startswith("_"):
            return False
        if isinstance(obj, types.ModuleType):
            if "_test" in os.path.basename(getattr(obj, "__file__", "_test")):
                return False
            return is_child_module(obj)
        return True


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    renderer = FinDoc()

    all_obs = {}
    for p, o in renderer.recurse_objects(fin, iter_fn=renderer.filter_objects):
        build_dict(all_obs, p, o)

    renderer.id_map.update(map_ids(all_obs))

    renderer.render(all_obs, "tmp/")


if __name__ == "__main__":
    sys.exit(main())