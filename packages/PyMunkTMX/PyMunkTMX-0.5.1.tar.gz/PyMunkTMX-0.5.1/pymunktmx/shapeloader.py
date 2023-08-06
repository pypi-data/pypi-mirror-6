# -*- coding: utf-8; -*-

"""
PyMunkTMX provides an easy to use method for designing and importing pymunk
shapes from a Tiled Mapeditor Map file (tmx). It is designed to provide this
functionality as an extension to the excellent PyTMX library which is a
dependency of PyMunkTMX.

The only function a developer would most likely need from this module is
load_shapes. The other functions are documented in the case that some special
functionality is required.


.. py:data:: PYMUNK_TYPES

   This dict represents both the list of supported
   pymunk shapes as well as a mapping of the shape type to the function
   that can load it.

.. moduleauthor:: William Kevin Manire <williamkmanire@gmail.com>
"""

from uuid import uuid4
import logging
import re

logger = logging.getLogger("pymunktmx.shapeloader")

import pymunk


def set_attrs(attrs, obj, skip_keys=[]):
    """
    Given a set of attributes as a dict, set those attributes on an object.

    :param dict attrs: A dict of attribute names and values.
    :param object obj: An object to set the attributes on
    :param list skip_keys: A list, set or tuple of keys to skip.
    :rtype: None
    :return: None
    :raises AttributeError: If the attribute cannot be set.
    """
    for key, value in attrs.items():
        if key in skip_keys:
            continue
        try:
            setattr(obj, key, value)
        except AttributeError as ex:
            logger.error("Could not set %s to %s on object %s"
                         % (str(key), str(value), str(obj)))
            raise ex


def get_attrs(attrs_type, tmxobject):
    """
    Parse properties from a TiledObject and return them as a dict.

    :param str attrs_type: A prefix used to filter which object properties \
    to return. It must be one of 'shape', 'body', 'circle' or 'segment'.
    :param TiledObject tmxobject: The pytmx TiledObject instance that \
    contains the properties to be parsed.

    :rtype: dict
    :return: A dict of property keys and values.
    :raises ValueError: If the attrs_type param is not one of the \
    supported prefixes.
    """
    attr_types = set([u"shape", u"body", u"circle", u"segment"])
    if attrs_type not in attr_types:
        raise ValueError(u"attrs_type must be one of %s" % unicode(attr_types))

    attrs = dict()
    for key, value in tmxobject.__dict__.items():
        parts = key.split(u".")
        if len(parts) != 2:
            continue
        cat, prop = parts
        if cat == attrs_type:
            attrs[prop] = value
    return attrs


def uint(n):
    """
    This is an internal utility function that is intended to correct negative
    bitmask values for pymunk.

    :param int n: An integral number.
    :return: A positive integer.
    :rtype: int
    """
    return abs(int(n))

# flexible regexp for matching coordinate pairs
COORDS_RE = re.compile(
    r"^\(?\s*([-+]?[0-9]*\.?[0-9]+)\s*,\s*([-+]?[0-9]*\.?[0-9]+)\s*\)?$")


def parse_coordinates(coord_string):
    """
    Parses a coordinate tuple of floats from a string. It can handle any
    combination of the following formats:

    - (x, y)
    - x, y
    - x,y
    - x.0, y.0
    - (x.0, y.0)

    :param str coord_string: A string containing a coordinate expression.

    :rtype: tuple
    :return: A tuple of floats representing the x and y axis. (1.0, 2.0)
    :raises ValueError: If a coordinate tuple cannot be parsed from the string.
    """
    if coord_string is None:
        return None

    match = COORDS_RE.match(coord_string)
    if not match:
        raise ValueError("Invalid coordinate string")

    return (float(match.group(1)), float(match.group(2)))


def get_body_attrs(tmxobject):
    """
    Parses all body properties (body.xxx) from the TiledObject.

    :param TiledObject tmxobject: The TiledObject instance to parse body \
    properties from.

    :rtype: dict
    :return: A dict of parsed body properties with sane defaults applied.
    """
    attrs = get_attrs(u"body", tmxobject)
    body_attrs = {
        u"angle": float(attrs.get(u"angle", 0.0)),
        u"angular_velocity_limit": float(
            attrs.get(u"angular_velocity_limit", 0.0)),
        u"mass": float(attrs.get(u"mass", 1.0)),
        u"position": parse_coordinates(attrs.get("position")),
        u"offset": parse_coordinates(attrs.get("offset", "(0, 0)")),
        u"velocity_limit": float(attrs.get(u"velocity_limit", 0.0)),
        u"sensor": attrs.get(u"sensor", u"false").lower() == u"true",
        u"static": attrs.get(u"static", u"true").lower() == u"true",
    }

    return body_attrs


def get_shape_attrs(tmxobject):
    """
    Parses all shape properties (shape.xxx) from the TiledObject.

    :param TiledObject tmxobject: The TiledObject instance to parse shape \
    properties from.

    :rtype: dict
    :return: A dict of parsed shape properties with sane defaults applied.
    """
    attrs = get_attrs(u"shape", tmxobject)
    shape_attrs = {
        u"collision_type": uint(attrs.get(u"collision_type", 0)),
        u"elasticity": float(attrs.get(u"elasticity", 0.0)),
        u"friction": float(attrs.get(u"friction", 0.0)),
        u"layers": int(attrs.get(u"layers", -1)),
        u"sensor": attrs.get(u"sensor", u"false").lower() == u"true",
        u"radius": int(attrs.get(u"radius", 0.0))
    }
    return shape_attrs


def get_circle_attrs(tmxobject):
    """
    Parses all circle properties (circle.xxx) from the TiledObject.

    :param TiledObject tmxobject: The TiledObject instance to parse circle \
    properties from.

    :rtype: dict
    :return: A dict of parsed circle properties with sane defaults applied.
    """
    attrs = get_attrs(u"circle", tmxobject)
    shape_attrs = {
        u"inner_radius": float(attrs.get(u"inner_radius", 0.0))
    }
    return shape_attrs


def get_segment_attrs(tmxobject):
    """
    Parses all segment properties (segment.xxx) from the TiledObject.

    :param TiledObject tmxobject: The TiledObject instance to parse segment \
    properties from.

    :rtype: dict
    :return: A dict of parsed segment properties with sane defaults applied.
    """
    attrs = get_attrs(u"segment", tmxobject)
    segment_attrs = {
        u"radius": float(attrs.get(u"radius", 1.0))
    }
    return segment_attrs


def get_shape_name(tmxobject, suffix_fn=uuid4):
    """
    Returns the name of a TiledObject if it has one, otherwise it generates a
    name using the type and the return value of the suffix_fn. By default the
    suffix function is uuid.uuid4() but any function which returns a unique
    string can be used in its place.

    Example Auto Generated Name:
        "pymunk_circle_39869097-98fd-473d-b513-f0ad0cf2f368"

    :param TiledObject tmxobject: The TiledObject instance to get the name \
    from.
    :param function suffix_fn: A function that returns a unique string.
    :rtype: string
    :return: The original, or new name of the TiledObject.
    """
    if tmxobject.name is None:
        return tmxobject.type + u"_" + unicode(suffix_fn())
    return tmxobject.name


def load_box(tmxobject, map_height, static_body):
    """
    Creates a pymunk.Poly in the shape of a box from a TiledObject instance and
    orients it relative to the height of a TiledMap.

    :param TiledObject tmxobject: A TiledObject instance that represents a box.
    :param int map_height: The height of the TiledMap that the TiledObject \
    was loaded from in pixels.

    :rtype: pymunk.Poly
    :return: A pymunk.Poly shape instance.
    """
    shape_attrs = get_shape_attrs(tmxobject)
    body_attrs = get_body_attrs(tmxobject)
    offset = body_attrs[u"offset"]
    radius = shape_attrs[u"radius"]

    shape = None
    if body_attrs[u"static"]:
        tl = tmxobject.x, float(map_height) - tmxobject.y
        tr = tmxobject.x + tmxobject.width, tl[1]
        bl = tl[0], float(map_height) - (tmxobject.y + tmxobject.height)
        br = tr[0], bl[1]
        verts = [tl, bl, br, tr]
        shape = pymunk.Poly(static_body, verts, offset, radius)
    else:
        x = float(tmxobject.x)
        y = float(float(map_height) - tmxobject.y)
        mass = body_attrs[u"mass"]
        tl = 0.0, 0.0
        tr = float(tmxobject.width), 0.0
        bl = 0, -float(tmxobject.height)
        br = tr[0], bl[1]
        verts = [tl, bl, br, tr]
        moment = pymunk.moment_for_box(
            mass, tmxobject.height, tmxobject.width)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)

        set_attrs(body_attrs, body,
                  skip_keys=[u"position", u"mass", u"static"])

        shape = pymunk.Poly(body, verts, offset, radius)

    set_attrs(shape_attrs, shape, skip_keys=[u"radius"])
    return shape


def load_circle(tmxobject, map_height):
    """
    Creates a pymunk.Circle parsed from a TiledObject instance.

    :param TiledObject tmxobject: A TiledObject instance that represents a \
    circle.
    :param int map_height: The height of the TiledMap that the TiledObject \
    was loaded from in pixels.

    :rtype: pymunk.Circle
    :return: A pymunk.Circle shape instance.
    """
    if tmxobject.width != tmxobject.height:
        raise ValueError(u"pymunk only supports perfectly round circles. "
                         "No ovals or other non-uniform ellipses.")

    shape_attrs = get_shape_attrs(tmxobject)
    shape_attrs = get_shape_attrs(tmxobject)
    body_attrs = get_body_attrs(tmxobject)
    circle_attrs = get_circle_attrs(tmxobject)
    outer_radius = float(tmxobject.width / 2.0)
    offset = body_attrs["offset"]
    x = float(tmxobject.x) + outer_radius
    y = float(float(map_height) - (tmxobject.y + outer_radius))

    shape = None
    if body_attrs[u"static"]:
        shape = pymunk.Circle(pymunk.Body(), outer_radius, offset)
    else:
        moment = pymunk.moment_for_circle(
            body_attrs[u"mass"],
            circle_attrs[u"inner_radius"],
            outer_radius,
            body_attrs[u"offset"])
        body = pymunk.Body(body_attrs[u"mass"], moment)
        set_attrs(body_attrs, body,
                  skip_keys=[u"position", u"mass", u"static"])

        shape = pymunk.Circle(body, outer_radius, offset)

    shape.body.position = (x, y)
    set_attrs(shape_attrs, shape, skip_keys=[u"radius"])
    return shape


def load_poly(tmxobject, map_height, static_body):
    """
    Creates a pymunk.Poly parsed from a TiledObject instance.

    :param TiledObject tmxobject: A TiledObject instance that represents a \
    convex polygon with multiple vertices.
    :param int map_height: The height of the TiledMap that the TiledObject \
    was loaded from in pixels.

    :rtype: pymunk.Poly
    :return: A pymunk.Poly shape instance.
    """
    shape_attrs = get_shape_attrs(tmxobject)
    body_attrs = get_body_attrs(tmxobject)
    offset = body_attrs[u"offset"]
    radius = shape_attrs[u"radius"]

    shape = None
    if body_attrs[u"static"]:
        verts = [(p[0], map_height - p[1]) for p in tmxobject.points]
        shape = pymunk.Poly(static_body, verts, offset, radius)
    else:
        x = float(tmxobject.x)
        y = float(float(map_height) - tmxobject.y)
        mass = body_attrs[u"mass"]
        verts = [(p[0] - x, -(p[1] - y))
                 for p in tmxobject.points]
        moment = pymunk.moment_for_poly(mass, verts, offset)
        body = pymunk.Body(mass, moment)

        set_attrs(body_attrs, body,
                  skip_keys=[u"position", u"mass", u"static"])

        body.position = (x, y)
        shape = pymunk.Poly(body, verts, offset, radius)

    set_attrs(shape_attrs, shape, skip_keys=[u"radius"])
    return shape


def load_segment(tmxobject, map_height, static_body):
    """
    Creates a pymunk.Segment parsed from a TiledObject instance.

    :param TiledObject tmxobject: A TiledObject instance that represents a \
    line segment with two points, A to B.
    :param int map_height: The height of the TiledMap that the TiledObject \
    was loaded from in pixels.

    :rtype: pymunk.Segment
    :return: A pymunk.Segment shape instance.
    """
    shape_attrs = get_shape_attrs(tmxobject)
    body_attrs = get_body_attrs(tmxobject)
    radius = shape_attrs[u"radius"]

    shape = None
    if body_attrs[u"static"]:
        verts = [(p[0], map_height - p[1]) for p in tmxobject.points]
        shape = pymunk.Segment(static_body, verts[0], verts[1], radius)
    else:
        x = float(tmxobject.x)
        y = float(float(map_height) - tmxobject.y)
        mass = body_attrs[u"mass"]
        verts = [(p[0] - x, map_height - p[1] - y)
                 for p in tmxobject.points]
        moment = pymunk.moment_for_segment(mass, verts[0], verts[1])
        body = pymunk.Body(mass, moment)

        set_attrs(body_attrs, body,
                  skip_keys=[u"position", u"mass", u"static"])

        body.position = (x, y)
        shape = pymunk.Segment(body, verts[0], verts[1], radius)

    set_attrs(shape_attrs, shape, skip_keys=[u"radius"])

    return shape

PYMUNK_TYPES = {u"pymunktmx_box": load_box,
                u"pymunktmx_circle": load_circle,
                u"pymunktmx_poly": load_poly,
                u"pymunktmx_segment": load_segment}


def find_shapes(tmxdata):
    """
    This is a generator function that yields all recognized pymunk shapes from
    all object groups of the TiledMap instance.

    :param TiledMap tmxdata: The TiledMap instance to search for pymunk \
    shapes in.

    :rtype: generator
    :return: A generator that yields TiledObject instances.
    """
    for objectgroup in tmxdata.objectgroups:
        for tmxobject in objectgroup:
            if tmxobject.type in PYMUNK_TYPES:
                yield tmxobject, tmxobject.type


def load_shapes(tmxdata, space=None, default_layers=-1):
    """
    Returns a collection of pre-configured pymunk shapes parsed from a
    PyTMX TiledMap. Optionally, a Space instance may be provided and
    all of the shapes will be added to it. If no layers value is
    supplied in the TiledMap then default_layers will be applied.

    :param pymunk.Space space: A pymunk Space instance to load all of the \
    found shapes into. This param os optional.
    :param int default_layers: If the layers property of a shpae is not set \
    then this value will be used.
    :param TiledMap tmxdata: A TiledMap instance loaded from a tmx file with \
    pytmx.

    :rtype: dict
    :return: A dict of shape names and pymunk shapes.
    """
    shapes = dict()
    objects = ((o, o.type) for g in tmxdata.objectgroups
               for o in g if o.type in PYMUNK_TYPES)

    map_height = tmxdata.height * tmxdata.tileheight

    static_body = None
    if space is not None:
        static_body = space.static_body

    for o, t in objects:
        name = get_shape_name(o)
        o.name = name
        if t == "pymunktmx_box":
            shape = load_box(o, map_height, static_body)
        elif t == "pymunktmx_circle":
            shape = load_circle(o, map_height)
        elif t == "pymunktmx_poly":
            shape = load_poly(o, map_height, static_body)
        elif t == "pymunktmx_segment":
            shape = load_segment(o, map_height, static_body)

        shapes[name] = shape
        if space is not None:
            space.add(shape)
        logger.debug("Loaded shape %s" % name)

    return shapes
