tg2ext.express
==============

A small extension for TurboGears2

For example
----------------

    from tg2ext.express import ExpressController

    class ExampleModel(DeclarativeBase):
        __tablename__ = 'examples'

        #{ Columns
        id = Column(Integer, primary_key=True)
        data = Column(Unicode(256), nullable=False)
        created = Column(DateTime, default=func.NOW())
        #}

    class RootController(BaseController):
        # ...
        examples = ExpressController(model=ExampleModel, dbsession=DBSession)

        # ...

Exposed HTTP Interface:

    /examples/
    /examples/1
    /examples/?id__in=1,2,3
    /examples/?__include_fields=id,created&__begin=3&__limit=10
    ...

HTTP API:
----------------

    Controle Params:
        __begin:
        __limit:
        __include_fields:
        __extend_fields:

    Query Lookups: ${field_name}__${lookup}=${value(s)}
        not
        contains
        startswith
        endswith
        in
        range
        lt
        lte
        gt
        gte
        year
        month
        day
        hour
        minute
        dow
