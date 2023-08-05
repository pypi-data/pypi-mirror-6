""" Supporting objects and functions to convert Matplotlib objects into Bokeh

"""

import warnings
import matplotlib as mpl

from . import glyphs, objects

def axes2plot(axes):
    """ In the matplotlib object model, Axes actually are containers for all
    renderers and basically everything else on a plot.

    This takes an MPL Axes object and returns a list of Bokeh objects
    corresponding to it.
    """

    plot = objects.Plot(title=axes.get_title())
    plot.x_range = objects.DataRange1d()
    plot.y_range = objects.DataRange1d()
    datasource = objects.ColumnDataSource()
    plot.data_sources = [datasource]

    bokehaxes = extract_axis(axes)
    for baxis in bokehaxes:
        baxis.plot = plot
    plot.renderers.extend(bokehaxes) # + extract_grid(axes))

    # Break up the lines and markers by filtering on linestyle and marker style
    lines = [line for line in axes.lines if line.get_linestyle() not in ("", " ", "None", "none", None)]
    markers = [m for m in axes.lines if m.get_marker() not in ("", " ", "None", "none", None)]
    renderers = [_make_line(datasource, plot.x_range, plot.y_range, line) for line in lines]
    renderers.extend(_make_marker(datasource, plot.x_range, plot.y_range, marker) for marker in markers)
    plot.renderers.extend(renderers)

    #plot.renderers.extend(map(MPLText.convert, axes.texts))
    #for collection in axes.collections:
    #    if isinstance(collection, mpl.collections.PolyCollection):
    #        plot.renderers.extend(map(MPLPatches.convert, collection))
    #    elif isinstance(collection, mpl.collections.LineCollection):
    #        plot.renderers.extend(map(MPLMultiLine.convert, collection))
    #    else:
    #        warnings.warn("Not yet implemented: %r" % collection)

    # Add tools
    pantool = objects.PanTool(dataranges = [plot.x_range, plot.y_range],
                      dimensions=["width", "height"])
    wheelzoom = objects.WheelZoomTool(dataranges = [plot.x_range, plot.y_range],
                              dimensions=["width", "height"])
    plot.tools = [pantool, wheelzoom]
    return plot

def _convert_color(mplcolor):
    charmap = dict(b="blue", g="green", r="red", c="cyan", m="magenta",
                   y="yellow", k="black", w="white")
    if mplcolor in charmap:
        return charmap[mplcolor]

    try:
        colorfloat = float(mplcolor)
        if 0 <= colorfloat <= 1.0:
            # This is a grayscale value
            return tuple([int(255*colorfloat)] * 3)
    except:
        pass

    if isinstance(mplcolor, tuple):
        # These will be floats in the range 0..1
        return int(255*mplcolor[0]), int(255*mplcolor[1]), int(255*mplcolor[2])

    return mplcolor

def _map_text_props(mplText, obj, prefix=""):
    """ Sets various TextProps on a bokeh object based on values from a
    matplotlib Text object.  An optional prefix is added to the TextProps
    field names, to mirror the common use of the TextProps property.
    """
    alignment_map = {"center": "middle", "top": "top", "bottom": "bottom"}  # TODO: support "baseline"
    fontstyle_map = {"oblique": "italic", "normal": "normal", "italic": "italic"}

    setattr(obj, prefix+"text_font_style", fontstyle_map[mplText.get_fontstyle()])
    # we don't really have the full range of font weights, but at least handle bold
    if mplText.get_weight() in ("bold", "heavy"):
        setattr(obj, prefix+"text_font_style", "bold")
    setattr(obj, prefix+"text_font_size", "%dpx" % mplText.get_fontsize())
    setattr(obj, prefix+"text_alpha", mplText.get_alpha())
    setattr(obj, prefix+"text_color", _convert_color(mplText.get_color()))
    setattr(obj, prefix+"text_baseline", alignment_map[mplText.get_verticalalignment()])

    # Using get_fontname() works, but it's oftentimes not available in the browser,
    # so it's better to just use the font family here.
    #setattr(obj, prefix+"text_font", mplText.get_fontname())
    setattr(obj, prefix+"text_font", mplText.get_fontfamily()[0])

def _make_axis(axis, dimension):
    """ Given an mpl.Axis instance, returns a bokeh LinearAxis """
    # TODO:
    #  * handle `axis_date`, which treats axis as dates
    #  * handle log scaling
    #  * map `labelpad` to `major_label_standoff`
    #  * deal with minor ticks once BokehJS supports them
    #  * handle custom tick locations once that is added to bokehJS

    newaxis = objects.LinearAxis(dimension=dimension, location="min",
                                 axis_label=axis.get_label_text())

    # First get the label properties by getting an mpl.Text object
    label = axis.get_label()
    _map_text_props(label, newaxis, prefix="axis_label_")

    # To get the tick label forat, we look at the first of the tick labels
    # and assume the rest are formatted similarly.
    ticktext = axis.get_ticklabels()[0]
    _map_text_props(ticktext, newaxis, prefix="major_label_")

    #newaxis.bounds = axis.get_data_interval()  # I think this is the right func...
    return newaxis


def extract_axis(mplaxes):
    """ Given a matplotlib Axes object, extracts the actual X and Y axes from
    it and returns a set of bokeh objects.
    """
    return _make_axis(mplaxes.xaxis, 0), _make_axis(mplaxes.yaxis, 1)


#def extract_grid(mplaxes):
#    if mplaxis.xaxis._gridOnMajor:
#        axis = mplaxes.get_xaxis()


def _make_marker(datasource, xdr, ydr, line2d):
    """ Given a matplotlib line2d instance that has non-null marker type,
    return an appropriate Bokeh Marker glyph.
    """
    marker_map = {
        "o": glyphs.Circle,
        "s": glyphs.Square,
        "+": glyphs.Cross,
        "^": glyphs.Triangle,
        "v": glyphs.InvertedTriangle,
        "x": glyphs.Xmarker,
        "D": glyphs.Diamond,
        "*": glyphs.Asterisk,
    }
    if line2d.get_marker() not in marker_map:
        warnings.warn("Unable to handle marker: %s" % line2d.get_marker())
    marker = marker_map[line2d.get_marker()]()
    marker.line_color = line2d.get_markeredgecolor()
    marker.fill_color = line2d.get_markerfacecolor()
    marker.line_width = line2d.get_markeredgewidth()
    marker.size = line2d.get_markersize()

    # Is this the right way to handle alpha? MPL doesn't seem to distinguish
    marker.fill_alpha = marker.line_alpha = line2d.get_alpha()

    xydata = line2d.get_xydata()
    marker.x = datasource.add(xydata[:, 0])
    marker.y = datasource.add(xydata[:, 1])
    xdr.sources.append(datasource.columns(marker.x))
    ydr.sources.append(datasource.columns(marker.y))

    glyph = objects.Glyph(
        data_source = datasource,
        xdata_range = xdr,
        ydata_range = ydr,
        glyph = marker
    )
    return glyph


def _map_line_props(newline, line2d):
    cap_style_map = {
        "butt": "butt",
        "round": "round",
        "projecting": "square",
    }
    # Note: these are not *just* the line properties, rather they are
    # the properties to set when a line2d represents a line plot 
    setattr(newline, "line_color", line2d.get_color())
    setattr(newline, "line_width", line2d.get_linewidth())
    setattr(newline, "line_alpha", line2d.get_alpha())
    # TODO: how to handle dash_joinstyle?
    setattr(newline, "line_join", line2d.get_solid_joinstyle())
    setattr(newline, "line_cap", cap_style_map[line2d.get_solid_capstyle()])
    # TODO: Handle line dash, translate between Matplotlib and Canvas-style dashes
    setattr(newline, "line_dash", _convert_dashes(line2d.get_linestyle()))
    # setattr(newline, "line_dash_offset", ...)

def _convert_dashes(dash):
    """ Converts a Matplotlib dash specification

    bokeh.properties.DashPattern supports the matplotlib named dash styles,
    but not the little shorthand characters.  This function takes care of
    mapping those.
    """
    mpl_dash_map = {
        "-": "solid",
        "--": "dashed",
        ":": "dotted",
        "-.": "dashdot",
    }
    # If the value doesn't exist in the map, then just return the value back.
    return mpl_dash_map.get(dash, dash)

def _make_line(datasource, xdr, ydr, line2d):
    newline = glyphs.Line()
    _map_line_props(newline, line2d)
    xydata = line2d.get_xydata()
    newline.x = datasource.add(xydata[:, 0])
    newline.y = datasource.add(xydata[:, 1])
    xdr.sources.append(datasource.columns(newline.x))
    ydr.sources.append(datasource.columns(newline.y))
    glyph = objects.Glyph(
        data_source = datasource,
        xdata_range = xdr,
        ydata_range = ydr,
        glyph = newline
    )
    return glyph


class MPLMultiLine(glyphs.MultiLine):

    @classmethod
    def convert(cls, linecollection):
        pass

class MPLText(glyphs.Text):

    @classmethod
    def convert(cls, text):
        return []

class MPLPatches(glyphs.Patches):

    @classmethod
    def convert(cls, patches):
        pass
