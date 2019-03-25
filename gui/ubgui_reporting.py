__author__ = "Peter M. Bach"
__copyright__ = "Copyright 2012. Peter M. Bach"


def generate_project_overview_html(global_options, project_info, mapstats, num_scenarios, data_sets):
    """Parses a basic html text summary of the project overview using the information from the project

    :param global_options: The dictionary containing global options
    :param project_info: The dictionary containing the project metadata
    :param mapstats: data on the boundary map loaded into the project, calculated when shapefile processed.
    :param num_scenarios: The total number of scenarios in the active simulation
    :param data_sets: The total number of data sets in the active simulation's data library.
    """
    htmlstring = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
                    <html><head><meta name="qrichtext" content="1" /><style type="text/css">p, li { white-space: pre-wrap; }
                    </style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;"><p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:10pt; font-weight:600;">"""+project_info["name"]+"""</span>
                    </p>
                    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-style:italic;">"""+project_info["modeller"]+"""<br />"""+project_info["affiliation"]+"""</span>
                    </p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-style:italic;">&lt;"""+project_info["date"]+"""&gt;</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt; font-style:italic;"><br /></p>
<hr />
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600;">METADATA</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Project Location:</strong> """+project_info["region"]+""", """+project_info["city"]+"""</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Coordinates:</strong> x """+str(mapstats["centroid"][0])+""", y """+str(mapstats["centroid"][1])+"""</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Case Study Size:</strong> """+str(round(mapstats["area"], 2))+""" km</span><span style=" font-size:8pt; vertical-align:super;">2</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Other Participants:</strong> """+project_info["otherpersons"]+"""</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Coordinate System:</strong> """+mapstats["coordsysname"]+""" ("""+str(mapstats["inputEPSG"])+""")</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Project Path:</strong> """+project_info["projectpath"]+"""</span></p>
<hr />
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600;">DESCRIPTION</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">"""+project_info["synopsis"]+"""</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600;">PROJECT STATUS</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"># Data Files in Library: """+str(data_sets)+"""</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"># Scenarios in Project: """+str(num_scenarios)+"""</span></p></body></html>
"""
    return htmlstring