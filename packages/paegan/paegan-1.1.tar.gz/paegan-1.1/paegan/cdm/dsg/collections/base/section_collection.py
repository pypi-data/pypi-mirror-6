from paegan.cdm.dsg.collections.base.nested_point_collection import NestedPointCollection

class SectionCollection(NestedPointCollection):
    """
        A collection of Sections
    """

    def __init__(self, **kwargs):
        super(SectionCollection,self).__init__(**kwargs)
