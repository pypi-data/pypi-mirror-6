import importlib

from django.conf import settings

def import_function(function_path):
    module_name, function_name = function_path.rsplit('.',1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)

DEFAULTS = {
    'SERIALIZE_FUNCTION': 'kvmodel.serializers.json_serialize',
    'DESERIALIZE_FUNCTION': 'kvmodel.serializers.json_deserialize',
}

USER_SETTINGS = getattr(settings, 'KVMODEL', {})

DEFAULTS.update(USER_SETTINGS)

kv_settings = {k: import_function(DEFAULTS[k]) for k in DEFAULTS}
