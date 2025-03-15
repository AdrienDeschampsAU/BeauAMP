BeauAMP v1.0.0
-------------------------------------------------------------------------
*Base Étendue, Améliorée et Unifiée des Annonces des Marchés Publics*

* Copyright 2024 Adrien DESCHAMPS & Lucas POTIN

BeauAMP is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation. For source availability and license information see `licence.txt`

* **GitHub repo:** https://github.com/AdrienDeschampsAU/BeauAMP
* **Data:** https://doi.org/10.5281/zenodo.10980643
* **Contact:** Adrien Deschamps <adrien.deschamps@univ-avignon.fr>
 
-------------------------------------------------------------------------

# Description
These scripts create the BeauAMP database v.1.0.0 from raw BOAMP files. This database covers all public procurement contracts published in the BOAMP from 2015 to 2023. It also proposes an enrichment of these data, thanks to the siretization of agents (i.e. the retrieval of their unique IDs) as well as the categorization of award criteria, and other processing.

The produced database is directly available on [Zenodo](https://doi.org/10.5281/zenodo.11001277). The detail of this processing are described in the following [article](https://www.sciencedirect.com/science/article/pii/S2352340925000095).

This work was conducted in the framework of the DeCoMaP ANR project (Detection of corruption in public procurement markets -- ANR-19-CE38-0004).

# Organization
This repository is composed of the following elements:
* The file "data_processing" downloads and processes the data from the BOAMP website.
* The file "listing_agents" generates the input of the machine learning algorithm used to estimate SIRETs (i.e. identifiers) from the processed table.
* The file "siret_import" integrates the estimated SIRETs to the processed table.
* The file "consolidation" uses the SIRETs to import data from the SIRENE repository into the dataset.
* The file "geolocation" estimates the geolocation of foreing companies mentioned in the dataset.
* The folder "required_files" contains CSV files used for the consolidation of the dataset. The script also requires the SIRENE data, which can be downloaded [here](https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/) for the characteristics of agents and [here](https://www.data.gouv.fr/fr/datasets/geolocalisation-des-etablissements-du-repertoire-sirene-pour-les-etudes-statistiques/) for their GPS positions. These files are too heavy to be uploaded on the GitHub.

# Installation
You first need to install `python` and the required packages:
* `pandas`
* `geopy`
* `numpy`


# Dependencies
Tested with Python version 3.11.7, with the following packages:
* `pandas`: version 2.2.1
* `geopy`: version 2.4.1
* `numpy`: version 1.26.4

# Data
The produced database is directly available publicly online on [Zenodo](https://doi.org/XXXXX), under three different forms:
* Single CSV containing all data
* Several CSVs, each containing one year's data
* Pickle file (recommended)


# References

[Adrien Deschamps, Lucas Potin,
Processing and consolidation of open data on public procurement in France (2015–2023),
Data in Brief,
Volume 58,
2025,
111277,
ISSN 2352-3409,
https://doi.org/10.1016/j.dib.2025.111277](https://www.sciencedirect.com/science/article/pii/S2352340925000095)
