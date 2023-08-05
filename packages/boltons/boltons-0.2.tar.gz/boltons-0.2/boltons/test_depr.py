from deprutils import deprecate_module_member


hiya = 'hi'
hello = 'hello'


deprecate_module_member(__name__, 'hiya', 'use hello instead')
