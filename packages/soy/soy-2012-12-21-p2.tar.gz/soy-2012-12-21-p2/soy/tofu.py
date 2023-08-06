from soy.utils import TemplateRegistry


class SoyTofu(object):

    class Renderer(object):

        def __init__(self, function):
            self.function = function
            self.data = None
            self.ijData = None
            self.activeDelegatePackageNames = None

        def setData(self, **data):
            self.data = data
            return self

        def setIjData(self, **ijData):
            self.ijData = ijData
            return self

        def setActiveDelegatePackageNames(self, activeDelegatePackageNames):
            self.activeDelegatePackageNames = activeDelegatePackageNames
            return self

        def render(self):
            kwargs = {'data': self.data}
            if self.ijData is not None:
                kwargs['ijData'] = self.ijData
            if self.activeDelegatePackageNames is not None:
                kwargs['delPackages'] = self.activeDelegatePackageNames
            return self.function(**kwargs)

    def __init__(self, registry, namespace=None):
        self.registry = registry
        self.namespace = namespace

    def newRenderer(self, template):
        if self.namespace is not None and template.startswith('.'):
            template = self.namespace + template
        return SoyTofu.Renderer(self.registry.lookup(template))

    def forNamespace(self, namespace):
        return SoyTofu(self.registry, namespace)

    @classmethod
    def fromFile(cls, file):
        registry = TemplateRegistry()
        execfile(file.name, {'registry': registry})
        return cls(registry)

