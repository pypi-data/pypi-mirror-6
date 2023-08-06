"""Convenience routines for common actions on VOEvent objects"""

from __future__ import absolute_import
import datetime
import lxml
from voeparse.misc import Param, Group, Reference, Inference, Position2D, Citation

def pull_astro_coords(voevent):
    """
    Extracts the `AstroCoords` of the `ObservationLocation`.

    Returns a :py:class:`.Position2D` namedtuple.
    """
    ac = voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords
    ac_sys = voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoordSystem
    sys = ac_sys.attrib['id']

    try:
        assert ac.Position2D.Name1 == 'RA' and ac.Position2D.Name2 == 'Dec'
        posn = Position2D(ra=float(ac.Position2D.Value2.C1),
                          dec=float(ac.Position2D.Value2.C2),
                          err=float(ac.Position2D.Error2Radius),
                          units=ac.Position2D.attrib['unit'],
                          system=sys)
    except AttributeError:
        raise ValueError("Unrecognised AstroCoords type")
    return posn

def pull_params(voevent):
    """
    Attempts to load the `What` section of a voevent as a nested dictionary.

    **Returns:** Nested dict, ``Group->Param->Attribs``. Access like so::

        foo_param_val = what_dict['GroupName']['ParamName']['value']

    .. note::

      Parameters without a group are indexed under the key 'None' - otherwise,
      we might get name-clashes between `params` and `groups` (unlikely but
      possible) so for ungrouped Params you'll need something like::

        what_dict[None]['ParamName']['value']

    """
    result = {}
    w = voevent.What
    if w.countchildren() == 0:
        return result
    toplevel_params = {}
    result[None] = toplevel_params
    if hasattr(voevent.What, 'Param'):
        for p in voevent.What.Param:
            toplevel_params[p.attrib['name']] = p.attrib
    if hasattr(voevent.What, 'Group'):
        for g in voevent.What.Group:
            g_params = {}
            result[g.attrib['name']] = g_params
            for p in g.Param:
                g_params[p.attrib['name']] = p.attrib
    return result


def pull_isotime(voevent):
    """Returns a datetime object, or None if not found.

    Specifically, we return a standard library datetime object,
    i.e. one that is *timezone-naive* (that is, agnostic about its timezone,
    see python docs) - this avoids an added dependency on pytz.

    The details of the reference system for time and space are provided
    in the AstroCoords object, but typically time reference is UTC.

    """
    try:
        ol = voevent.WhereWhen.ObsDataLocation.ObservationLocation
        isotime_str = str(ol.AstroCoords.Time.TimeInstant.ISOTime)
        return datetime.datetime.strptime(isotime_str, "%Y-%m-%dT%H:%M:%S.%f")
    except AttributeError:
        return None

def prettystr(subtree):
    """Print an element tree with nice indentation.

    Prettyprinting a whole VOEvent doesn't seem to work - possibly this is
    due to whitespacing issues in the skeleton string definition.
    This function is a quick workaround for easily desk-checking
    what you're putting together.
    """
    lxml.objectify.deannotate(subtree)
    lxml.etree.cleanup_namespaces(subtree)
    return lxml.etree.tostring(subtree, pretty_print=True)


