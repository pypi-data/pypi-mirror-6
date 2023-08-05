import datetime
from bson import ObjectId
import yaml
import os
import logging

_logger = logging.getLogger(__name__)

FIXTURES_HOME = 'test/fixtures/'

def oid_con(seed):
    value = int(seed)
    dt = datetime.datetime.fromtimestamp(value)
    return ObjectId.from_datetime(dt)


def setup_data(paths, db):
    def object_id_constructor(loader, seed):
        seed = loader.construct_scalar(seed)
        return oid_con(seed)

    yaml.add_constructor(u'!oid', object_id_constructor)

    for path in paths:
        fixtures = yaml.load(file(os.path.join(FIXTURES_HOME, path)))
        if "configuration" in fixtures:
            conf = fixtures.pop('configuration')
            collection = conf['collection']
            if conf.get('drop', False):
                db[collection].drop()
            for key in fixtures:
                db[collection].insert(fixtures[key])
