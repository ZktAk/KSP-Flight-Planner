BODY_REGISTRY = {}

def register_body(name: str, body_cls: type):
  BODY_REGISTRY[name] = body_cls

def get_body(name: str) -> type:
  return BODY_REGISTRY[name]