# Use the following import statement for the mods_master_guis
# --- SPATIAL REPRESENTATION MODULES ---
from .mod_simgrid import CreateSimGrid      # structure: from .py file, import the UBModule class
from .mod_mapregions import MapRegionsToSimGrid
from .mod_landuse_import import MapLandUseToSimGrid
from .mod_population import MapPopulationToSimGrid
from .mod_topography import MapTopographyToSimGrid
from .mod_natural_features import MapNaturalFeaturesToSimGrid

# --- HYDROLOGY MODULES ---
from .mod_rainfallanalyst import RainfallDataAnalyst
from .mod_catchmentdelin import DelineateFlowSubCatchments
# from .mod_climatescale import ClimateScaling

# --- URBAN AND REGIONAL ---
from .mod_cbdanalysis import UrbanCentralityAnalysis
from .mod_accessibility import AccessibilityAnalysis
from .mod_neighbourattract import NeighbourhoodAttractionMapping

# --- DEFINE URBAN FORM MODULES ---
from .mod_urbanformgen import UrbanFormAbstraction
# from .mod_urbanformimport import ImportUrbanFormData
# from .mod_landcoveralgo import GenerateLandCoverFromUrbanForm
# from .mod_landcoverimport import ImportLandCoverData

# --- DEFINE SPATIAL PLANNING MODULES ---
from .mod_planningoverlays import DefinePlanningOverlays
from .mod_zoningmap import CreateZoningMap
from .mod_ugsanalysis import UrbanGreenSpaceAnalysis

# --- URBAN WATER MODULES ---
from .mod_waterdemand import WaterDemandMapping
# from .mod_floodhazard import FloodHazardAssessment
# from .mod_pollutiongen import PollutionGeneration

# --- BIODIVERSITY MODULES ---
#from .mod_sdm import SpeciesDistributionModel
#from .mod_resistancemap import ResistanceMapping
#from .mod_circuitscape import Circuitscape
#from .mod_biodiversitynetwork import AnalyzeBiodiversityNetwork

# --- NbS PLANNING AND DESIGN MODULES ---
from .mod_nbssuitabilitymap import NbSSuitabilityMapping
from .mod_nbsdesigntoolbox import NbSDesignToolboxSetup
from .mod_nbslayoutgen import NbSLayoutGeneration

# --- SOCIAL ANALYSIS ---
from .mod_define_stakeholders import DefineStakeholders
from .mod_stakeholder_network import StakeholderNetworkAnalysis

MODULES_CATS = ["Spatial Representation",
                "Urban Regional Analysis",
                "Urban Form",
                "Spatial Planning",
                "Urban Hydrology",
                "Urban Water Management",
                "Urban Climatology",
                "Urban Ecology",
                "Technology Planning",
                "NbS Planning and Design",
                "Social Analysis"]

# For main code:
# import model.mods_master as UBToolkit
# import inspect
#
# for name, obj in inspect.getmembers(UBToolkit):
    # if inspect.isclass(obj):
    #       then the obj is one of the UBModule classes.

# To identify the parent class (inheritance of the UBMOdules classes, i.e. "UBModule")
# obj.__base__  --> Return <class 'model.ubmodule.UBModule'>
# obj.__base__.__name__ --> Returns 'UBModule'