from app.resource import DocumentationBase
from core.registrar import key as register, fns as representations
from app.resource.errors import NotFoundException
from core.hm import HypermediaFactory

## Import other representations
import app.representation

DocsBase = HypermediaFactory(
    base=DocumentationBase,
    class_name="DocumentationBase",
    resource_format="/docs/{key}",
    resource_route="/docs/<string:key>",
    doc_key='docs',
    doc_uri="/docs/docs",
    public_fields=[],
    private_fields=['key']
)

@register('docs')
class Docs(DocsBase):
    pass
