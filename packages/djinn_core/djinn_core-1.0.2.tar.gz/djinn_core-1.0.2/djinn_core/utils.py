from django.contrib.contenttypes.models import ContentType


# URN schema for objects
#
URN_SCHEMA = "urn:pu.in:%(object_app)s:%(object_ctype)s:%(object_id)s"


def _class_implements(clazz, superclazz, check_self=True):

    well_does_it = False

    if check_self and clazz == superclazz:
        return True
    elif isinstance(superclazz, basestring) and \
                    superclazz in map(lambda x: "%s.%s" %(x.__module__.split('.')[0], x.__name__), clazz.__bases__):
        well_does_it = True
    elif superclazz in  clazz.__bases__:
        well_does_it = True
    else:
        for base in clazz.__bases__:
            well_does_it = _class_implements(base, superclazz)
            if well_does_it:
                break

    return well_does_it


def implements(instance, clazz):

    """ Is it a bird? A plane? A clazz? """

    return _class_implements(instance.__class__, clazz)


def extends(clazz, otherclazz):

    """ Does the class extend the other one? """

    return _class_implements(clazz, otherclazz, check_self=False)


def object_to_urn(object):

    """ Create A URN for the given object """

    app_label = getattr(object, "app_label", object._meta.app_label)
    ct_name = getattr(object, object.ct_name,
                      object.__class__.__name__.lower())

    return URN_SCHEMA % {'object_app': app_label,
                         'object_ctype': ct_name,
                         'object_id': object.id}


def urn_to_object(urn):

    """ Fetch the object for this URN. If not found, return None """

    parts = urn.split(":")

    ctype = ContentType.objects.get(app_label=parts[2], model=parts[3])

    return ctype.get_object_for_this_type(id=parts[4])


def get_object_by_ctype_id(ctype_id, _id, app_label=None):

    ctype = ContentType.objects.get(app_label=app_label, model=ctype_id)

    return ctype.get_object_for_this_type(id=_id)
