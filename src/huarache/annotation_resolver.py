import ast
from annotationlib import Format, ForwardRef, get_annotations
from importlib import import_module
from inspect import getmodule, getsource, isclass
from logging import getLogger
from typing import TYPE_CHECKING, get_args, get_origin

from .exceptions import DoesNotGetModuleError

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import ModuleType
    from typing import Any

logger = getLogger(__name__)


def get_type_checking_imports(module: ModuleType) -> dict[str, Any]:
    globals_ = getattr(module, "__dict__", {})
    result = {}
    for node in ast.walk(ast.parse(getsource(module))):
        if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
            for sub_node in ast.iter_child_nodes(node):
                if isinstance(sub_node, ast.Import):
                    for alias in sub_node.names:
                        if alias.asname:
                            result[alias.asname] = import_module(alias.name)
                        else:
                            # result[alias.name] = import_module(alias.name)
                            # NOTE: 親モジュールが解決されていないと `ForwardRef.evaluate` で NameError になる
                            target_mod_name = alias.name
                            while target_mod_name and target_mod_name not in globals_:
                                result[target_mod_name] = import_module(target_mod_name)
                                target_mod_name = ".".join(target_mod_name.split(".")[:-1])
                elif isinstance(sub_node, ast.ImportFrom):
                    from_module = import_module("." * sub_node.level + (sub_node.module or ""), module.__package__)
                    for alias in sub_node.names:
                        result[alias.asname or alias.name] = (
                            getattr(from_module, alias.name)
                            if hasattr(from_module, alias.name)
                            else import_module(f"{from_module.__name__}.{alias.name}")
                        )
    return result


def resolve_forwardref_recursive(annotation: Any, module: ModuleType, globals_: dict[str, Any]) -> Any:
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation, module=module.__name__)
    if isinstance(annotation, ForwardRef):
        annotation = annotation.evaluate(globals=globals_)
    args = get_args(annotation)
    if args:
        origin = get_origin(annotation)
        annotation = origin[*(resolve_forwardref_recursive(child, module, globals_) for child in annotation.__args__)]
    return annotation


class AnnotationResolver:
    def __init__(self) -> None:
        self._module_cache: dict[str, dict[str, Any]] = {}
        self._object_cache: dict[Any, dict[str, Any]] = {}

    def __call__(self, obj: Any) -> Mapping[str, Any]:
        resolved = self._object_cache.get(obj, None)
        if resolved is None:
            module = getmodule(obj)
            if module is None:
                raise DoesNotGetModuleError(obj)  # pragma: no cover

            type_checking_imports = self._module_cache.get(module.__name__, None)
            if type_checking_imports is None:
                type_checking_imports = get_type_checking_imports(module)
                self._module_cache[module.__name__] = type_checking_imports

            globals_ = getattr(module, "__dict__", {}).copy()
            globals_.update(type_checking_imports)

            callable_ = obj.__init__ if isclass(obj) else obj
            annotations = get_annotations(callable_, format=Format.FORWARDREF)
            resolved = {}
            for k, v in annotations.items():
                resolved[k] = resolve_forwardref_recursive(v, module, globals_)
            self._object_cache[obj] = resolved
        return resolved


get_resolved_annotations = AnnotationResolver()
