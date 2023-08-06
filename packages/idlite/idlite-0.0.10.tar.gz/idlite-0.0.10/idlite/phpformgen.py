from __future__ import absolute_import, division, print_function, unicode_literals
from functools import partial

from mako.template import Template

from idlite.types import List, Class, Enum, Object


def generate(spec, out):
    out.write("<php\n")
    for t in spec:
        if isinstance(t, Class):
            out.write(_class_t.render(class_=t))
        elif isinstance(t, Enum):
            # TODO
            out.write(_enum_t.render(enum=t))


_class_t = Template(
"""
% if class_.doc:
/**
%  for L in class_.doc.splitlines():
 *${L}
%  endfor
 */
% endif
class ${class_.name} {
% for field in class_.fields:
%  if field.doc is not None:
%   for L in field.doc.splitlines():
    //${L}
%   endfor
%  endif
%   if field.enum:
    public int $${field.name};  // enum ${field.type}
%   elif isinstance(field.type, List):
    public array $${field.name};  // List<${field.type.T}>
%   else:
    public ${field.type} $${field.name};
%   endif
% endfor

    public function __construct(array $arg)
    {
% for field in class_.fields:
        if (! isset($arg['${field.name}'])) {
            throw new InvalidRequestQuestResultException("${class_.name}.${field.name} is not found.");
        }
%  if field.enum:
        $this->${field.name} = (int)$arg['${field.name}'];
%  elif isinstance(field.type, List):
%    if field.type.T in ("int", "float", "string"):
        $this->${field.name} = $arg['${field.name}'];
%    else:
        $this->${field.name} = array();
        foreach ($arg['${field.name}'] as $v) {
            $this->${field.name}[] = new ${field.type.T}($v);
        }
%    endif
%  elif field.type in ("int", "float", "string"):
        $this->${field.name} = (${field.type})$arg['${field.name}'];
%  else:
        $this->${field.name} = new ${field.type}($arg['${field.name}']);
%  endif
% endfor
    }
};
""", format_exceptions=True, imports=["from idlite.types import List"])


_enum_t = Template(
"""
""", format_exceptions=True)
