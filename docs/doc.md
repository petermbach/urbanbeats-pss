# UrbanBEATS Planning-Support System - Documentation

Documentation for the UrbanBEATS Planning-support System outlining details on the program, its use and code base.

Last Update: *April 22nd, 2022*

Author: *Peter M. Bach*

## Table of Contents

---

### Software & Package Requirements

* UrbanBEATS is built in Python 3, uses several different Python spatial and temporal libraries
    * The user interface is built with the PyQt Library
    * Spatial data handling using GDAL, Geopandas, Fiona, Shapely, Rasterio and Numpy Libraries
    * Plotting libraries: matplotlib, folium
* UrbanBEATS also uses web-based libraries that are rendered within the software
    * Mapping using the Leaflet library
    * Animated charts with HighCharts.js
* UrbanBEATS installer built with PyInstaller

### UrbanBEATS Project Structure

### Simulation Modules

1. Spatial Representation
    * [Simulation Grid](./mod_simgrid.md)
2. Hydrology
    * Catchment Delineation
3. Urban Regional Analysis
    * CBD Analysis

### Publications

#### Key Publications

* Bach, P.M., Kuller, M., McCarthy, D.T. and Deletic, A., 2020. A spatial planning-support system for generating decentralised urban stormwater management schemes. *Science of The Total Environment*, 726, p.138282.

* Bach, P.M., Deletic, A., Urich, C. and McCarthy, D.T., 2018. Modelling characteristics of the urban form to support water systems planning. *Environmental Modelling & Software*, 104, pp.249-269.

* Bach, P.M., Staalesen, S., McCarthy, D.T. and Deletic, A., 2015. Revisiting land use classification and spatial aggregation for modelling integrated urban water systems. *Landscape and Urban Planning*, 143, pp.43-55.

* Bach, P.M., Deletic, A., Urich, C., Sitzenfrei, R., Kleidorfer, M., Rauch, W. and McCarthy, D.T., 2013. Modelling interactions between lot-scale decentralised water infrastructure and urban form–a case study on infiltration systems. *Water Resources Management*, 27(14), pp.4845-4863.

* Bach, P.M., McCarthy, D.T., Urich, C., Sitzenfrei, R., Kleidorfer, M., Rauch, W. and Deletic, A., 2013. A planning algorithm for quantifying decentralised water management opportunities in urban environments. *Water science and technology*, 68(8), pp.1857-1865.

#### Supplementary Publications

* Zhang, K., Bach, P.M., Mathios, J., Dotto, C.B. and Deletic, A., 2020. Quantifying the benefits of stormwater harvesting for pollution mitigation. *Water Research*, 171, p.115395.
