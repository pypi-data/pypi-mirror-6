from yams.buildobjs import EntityType, RelationType, SubjectRelation, String

try:
    from yams.buildobjs import RichString
except ImportError:
    from cubicweb.schema import RichString

class Zone(EntityType):
    """a geographical zone"""

    name = String(required=True, indexed=True, fulltextindexed=True, maxsize=64)
    type = String(fulltextindexed=True,  maxsize=32)
    code = String(indexed=True,  maxsize=32)
    description = RichString()

    situated_in = SubjectRelation('Zone', cardinality='?*')


class situated_in(RelationType):
    """"""

