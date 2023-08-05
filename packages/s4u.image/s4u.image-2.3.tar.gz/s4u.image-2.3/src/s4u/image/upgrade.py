from sqlalchemy import schema
from sqlalchemy import types
from s4u.upgrade import upgrade_context
from s4u.upgrade import upgrade_step
from s4u.image import configure
from s4u.sqlalchemy import meta
from sqlalchemy.engine.reflection import Inspector
from . import _create_directories


@upgrade_context('image',
        [('--fs-images-original',
            {'type': str, 'required': True, 'dest': 'fs_images_original'}),
         ('--fs-images-scaled',
            {'type': str, 'required': True, 'dest': 'fs_images_scaled'})])
def setup_image_paths(options):
    configure(options.fs_images_original, options.fs_images_scaled)
    return {'fs.images.original': options.fs_images_original,
            'fs.images.scaled': options.fs_images_scaled}


@upgrade_step(require=['image'])
def create_directories(environment):
    _create_directories(environment['fs.images.original'])
    _create_directories(environment['fs.images.scaled'])


@upgrade_step(require=['sql'])
def add_missing_entities(environment):  # pragma: no cover
    engine = environment['sql-engine']
    meta.metadata.create_all(engine)


@upgrade_step(require=['sql'])
def add_url_column(environment):
    engine = environment['sql-engine']
    alembic = environment['alembic']
    inspector = Inspector.from_engine(engine)
    columns = set(c['name']
                  for c in inspector.get_columns('image'))
    if 'url' not in columns:
        alembic.add_column('image', schema.Column('url', types.Text()))
