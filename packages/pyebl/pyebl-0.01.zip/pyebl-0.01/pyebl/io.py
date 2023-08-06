def save_ely(project, filename):
    """
    Use lxml/ElementTree to build xml
    """

    import time

    try:
        from lxml import etree
        lxml_import = True
        print("Found lxml, using for serialization.")
    except ImportError:
        lxml_import = False
        print(
            "Did not find lxml, defaulting to ElementTree for serialization.")
        import xml.etree.ElementTree as etree

    ELAYOUT = etree.Element("ELAYOUT", {"locked": str(
        project.locked).lower(), "name": project.name, "version": str(project.version)})

    ltime = time.localtime()
    uhr = "{day}.{month}.{year} {hour}:{minute}:{seconds}".format(
        day=ltime.tm_mday, month=ltime.tm_mon, year=ltime.tm_year, hour=ltime.tm_hour, minute=ltime.tm_min, seconds=ltime.tm_sec)

    etree.SubElement(
        ELAYOUT, "VERSION", {"created": uhr, "modified": uhr, "number": "1.0"})
    etree.SubElement(ELAYOUT, "GRID", {"horizontal": str(project.grid_horizontal), "show": str(
        project.grid_show).lower(), "snap_to": str(project.grid_snap_to).lower(), "vertical": str(project.grid_vertical)})

    LAYER_LIST = etree.SubElement(ELAYOUT, "LAYER_LIST")
    for structure in project:
        for layer in structure:
            etree.SubElement(LAYER_LIST, "LAYER", {"fill_color": layer.fill_color, "fill_opacity": str(
                layer.fill_opacity), "hidden": str(layer.hidden).lower(), "locked": str(layer.locked).lower(), "name": layer.name})

    STRUCTURE_LIST = etree.SubElement(ELAYOUT, "STRUCTURE_LIST")
    for structure in project:
        STRUCTURE = etree.SubElement(STRUCTURE_LIST, "STRUCTURE", {
                                     "locked": str(structure.locked).lower(), "name": structure.name})
        etree.SubElement(
            STRUCTURE, "VERSION", {"created": uhr, "modified": uhr, "number": "1.0"})
        etree.SubElement(STRUCTURE, "INSTANCE_LIST")

        for layer in structure:
            LAYER_REFERENCE = etree.SubElement(STRUCTURE, "LAYER_REFERENCE", {"frame_cx": str(
                layer.frame_cx), "frame_cy": str(layer.frame_cy), "frame_size": str(layer.frame_size), "ref": layer.name})
            for shape in layer:
                LAYER_REFERENCE.append(
                    etree.Element(shape.tag, shape.get_attrib()))

    ELAYOUT = etree.ElementTree(ELAYOUT)
    if lxml_import:
        ELAYOUT.write(
            filename, xml_declaration=True, pretty_print=True, encoding="UTF-8")
    else:
        ELAYOUT.write(filename, xml_declaration=True, encoding="UTF-8")


def save_svg(project, filename):
    try:
        import svgwrite
    except ImportError:
        raise ImportError(
            "No module found for svg output. Please install module svgwrite.")

    for structure in project:
        # Bit awkward code here. Idea is: loop through layers in structure,
        # and find dimensions of largest write field. Use these lengths for
        # the size of the svg document.
        # In addition, svg coordinate system doesn't have negative
        # coordinates. So we shift everything by the largest negative points
        # in x and y directions.
        for i, layer in enumerate(structure):
            if (i == 0):
                size_x, size_y = 0, 0
                (min_x, min_y) = layer.bbox[0], layer.bbox[2]
            (mn_x, mx_x, mn_y, mx_y) = layer.bbox
            min_x = min(min_x, mn_x)
            min_y = min(min_y, mn_y)
            size_x = max(size_x, abs(mx_x - mn_x))
            size_y = max(size_y, abs(mx_y - mn_y))
        shift_x, shift_y = -min_x, -min_y
        svg_x, svg_y = size_x, size_y
        #
        # Hereafter, straightforward serialization.
        #

        dwg = svgwrite.Drawing(filename=filename, size=(svg_x, svg_y))

        for layer in structure:
            svg_layer = dwg.add(dwg.g(id=layer.name))
            svg_layer.translate(tx=shift_x, ty=shift_y)
            for shape in layer:
                if shape.__class__.__name__ == "Rect":
                    svg_layer.add(dwg.rect(insert=(shape.x, shape.y), size=(
                        shape.width, shape.height), fill = layer.fill_color, fill_opacity = layer.fill_opacity))
                elif shape.__class__.__name__ == "Polygon":
                    svg_layer.add(dwg.polygon(
                        points=shape.points, fill=layer.fill_color, fill_opacity=layer.fill_opacity))
                elif shape.__class__.__name__ == "Lines":
                    svg_layer.add(dwg.polyline(
                        points=shape.points, stroke=layer.fill_color, stroke_opacity=layer.fill_opacity))

        dwg.save()

save_fmt = {"ely": save_ely, "svg": save_svg}


def save(savething, filename="noname", format="ely"):
    # First we wrap whatever was passed in a project
    # using defaults (see class declaration)
    if savething.__class__.__name__ == "Project":
        project = savething
    elif savething.__class__.__name__ == "Structure":
        from .__init__ import proj
        project = proj()
        project.add(savething)
    elif savething.__class__.__name__ == "Layer":
        from .__init__ import proj, struct
        tmp_struct = struct()
        tmp_struct.add(savething)
        project = proj()
        project.add(tmp_struct)
    elif savething.__class__.__name__ in ("Rect", "Polygon", "Lines"):
        from .__init__ import proj, struct, layer
        tmp_layer = layer()
        tmp_layer.add(savething)
        tmp_struct = struct()
        tmp_struct.add(tmp_layer)
        project = proj()
        project.add(tmp_struct)
    else:
        raise TypeError("Did not pass a save-able object.")

    # Then we pretty up the filename
    # And check that we support the output format.
    fformat = format
    fformat = fformat.split(",")
    fformat = [f.lower().strip(". ") for f in fformat]
    for f in fformat:
        if f not in ["svg", "ely"]:
            raise ValueError("Format " + f + " not supported!")

    import os
    raw_filename = os.path.basename(filename)

    filepath = ["" for x in fformat]
    for i, f in enumerate(fformat):
        if len(raw_filename.split(".")) == 2:
            filepath[i] = filename.split(".")[0] + "." + f
        elif len(raw_filename.split(".")) == 1:
            filepath[i] = filename + "." + f

    # Next we set the scanning area for all layers.
    # We do this here, since we can be sure that
    # the sample design is complete. Otherwise, we'd
    # be obliged to insert code at each add...
    for structure in project:
        for layer in structure:
            layer.scanning_area()

    # Finally, we pass on project and filepath to the
    # save routine for the appropriate format
    for i, f in enumerate(fformat):
        save_fmt[f](project, filepath[i])

"""
def load(project, filename):
    Parses .ely file into interal classes

    try:
        from lxml import etree
	lxml_import = True
	print("Found lxml, using for parsing.")
    except ImportError:
        lxml_import = False
	print("Did not find lxml, defaulting to ElementTree for parsing.")
        import xml.etree.ElementTree as etree

    infile = etree.parse(filename)
    inroot = infile.getroot()

    project.name = inroot.attrib["name"]
    project.locked = bool(inroot.attrib["locked"])
    project.version = inroot.attrib["version"])

    grid = inroot.find("GRID")

    project.grid_horizontal = grid["grid_horizontal"]
    project.grid_vertical = grid["grid_vertical"]
    project.grid_show = bool(grid["grid_show"])
    project.grid_snap_to = bool(grid["grid_snap_to"])

    layer_list = inroot.find("LAYER_LIST")

    structure_list = inroot.find("STRUCTURE_LIST")

    for structure in structure_list.findall("STRUCTURE"):
        project.add_structure(eDraw.Structure(name = structure.attrib["name"], locked = bool(structure.attrib["locked"])))

    for structure in project:
        for xml_structure in structure_list:
            if structure.name == xml_structure.attrib["name"]:
                for xml_layer in xml_structure.findall("LAYER_REFERENCE"):
                    layer = structure.add_layer(eDraw.Layer(name=xml_layer.attrib["ref"], frame_cx=xml_layer.attrib["frame_cx"], frame_cy=xml_layer.attrib["frame_cy"], frame_size=xml_layer.attrib["frame_size"]))
                    for xml_shape in xml_layer:
                        if xml_shape.tag == "RECT":
                            layer.add_shape(eDraw.Rect(height=xml_shape.attrib["height"], width=xml_shape.attrib["width"], x=xml_shape.attrib["x"], y=xml_shape.attrib["y"]))
                        elif xml_shape.tag == "POLYGON":
                            layer.add_shape(eDraw.Polygon(points=list(xml_shape.attrib["points"])))

    for structure in project:
        for layer in structure:
            for xml_layer in layer_list:
                if layer.name == xml_layer.atrrib["name"]:
                    layer.fill_color = xml_layer.attrib["fill_color"]
                    layer.fill_opacity = xml_layer.attrib["fill_opacity"]
                    layer.hidden = bool(xml_layer.attrib["hidden"])
                    layer.locked = bool(xml_layer.attrib["locked"])
"""
