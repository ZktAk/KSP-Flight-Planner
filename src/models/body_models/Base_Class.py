from utils.body_registry import register_body, get_body

class CelestialBody:
    def __init__(self):
      cls = self.__class__
      self.name = cls.name
      self.parent = cls._parent()
      self.children = cls._children()

    @classmethod
    def _parent(cls):
      return get_body(cls.parent_name)
    
    @classmethod
    def _children(cls):
      return [get_body(name) for name in cls.children_names]
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Automatically register every subclass when it's defined
        register_body(cls.name, cls)