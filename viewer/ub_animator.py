import numpy as np

def export_timeline_to_image_stack(projectmeta, map_attr, assets, att_name, fname, stylemeta):
    """Exports a model output data set to a stack of png images of rasters. These files are either displayed in the
    leaflet map or saved for further analysis later on.

    :param projectmeta: dict() of project metadata, relevant for looking up project path and relevant informaiton
    :param map_attr: UBComponent() global map attributes for the function to query map extents, etc.
    :param assets: list(), the relevant set of UrbanBEATS Components from which spatial data is obtained
    :param att_name: name of the attribute within the assets list to query
    :param fname: file naming convention that the function should use
    :param stylemeta: details on stylising the map, e.g. colours for different categories, should be a dictionary
        containing relevant information e.g. data type (continuous, categorical) and colour scheme
    :return: .png files are exported to the project/outputs/cache, a list of status and other info is returned
    """
    status = [False, ""]

    pass
    return status

def create_leaflet_animation_html(projectmeta, fname, ):
    """Creates the folium

    :param projectmeta:
    :param fname:
    :return:
    """
    pass