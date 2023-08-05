import tff
import inspect
import hashlib

md5 = hashlib.md5()
specs = []
for name, member in inspect.getmembers(tff):
    if inspect.isclass(member):
        if name[0] != "_":
            classname = name
            for name, member in inspect.getmembers(member):
                if inspect.ismethod(member):
                    if name.startswith("__") or name[0] != "_":
                        argspec = inspect.getargspec(member)
                        args, varargs, keywords, defaultvalue = argspec
                        specstr = "%s.%s.%s" % (classname, name, args)
                        # {'class': classname, 'name': name, 'args': argspec.args, 'varargs': argspec.varargs, 'keywords': argspec.keywords}
                        specs.append(specstr)
specs.sort()
md5.update("".join(specs))
print md5.hexdigest()

