from logging import DEBUG, ERROR
from Products.PortalTransforms.utils import log
from Products.PortalTransforms.libtransforms.utils import MissingBinary

from redomino.appytransforms.config import TRANSFORM_IDS as modules

g = globals()
transforms = []
for m in modules:
    try:
        ns = __import__(m, g, g, None)
        transforms.append(ns.register())
    except ImportError, e:
        msg = "Problem importing module %s : %s" % (m, e)
        log(msg, severity=ERROR)
    except MissingBinary, e:
        log(str(e), severity=DEBUG)
    except Exception, e:
        import traceback
        traceback.print_exc()
        log("Raised error %s for %s" % (e, m), severity=ERROR)


def initialize(engine):
    for transform in transforms:
        engine.registerTransform(transform)
