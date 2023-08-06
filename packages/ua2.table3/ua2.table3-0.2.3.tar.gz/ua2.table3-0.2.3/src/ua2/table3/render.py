class LazyRender(object):
    def __init__(self):
        self.renders = {}

    def __get__(self, table, obj_type=None):
        return RenderProxy(table, obj_type, self.renders)

    def register(self, output, render_function):
        self.renders[output] = render_function


class RenderProxy(object):
    def __init__(self, obj, obj_type, registered_renders):
        self.obj = obj
        self.obj_type = obj_type
        self.registered_renders = registered_renders

    def __getattr__(self, key):
        if key not in self.registered_renders:
            return "Render %s not registered" % key
        return self.registered_renders[key](self.obj, self.obj_type)
