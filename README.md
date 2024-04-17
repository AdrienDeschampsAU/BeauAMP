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

The produced database is directly available on [Zenodo](https://doi.org/10.5281/zenodo.10980643). The detail of this processing are described in the following article [[D’23]](#references)

This work was conducted in the framework of the DeCoMaP ANR project (Detection of corruption in public procurement markets -- ANR-19-CE38-0004).

# Organization
This repository is composed of the following elements:
XXX

The script requires the SIRENE data, which can be downloaded [here](https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/) for the characteristics of agents and [here](https://www.data.gouv.fr/fr/datasets/geolocalisation-des-etablissements-du-repertoire-sirene-pour-les-etudes-statistiques/) for their GPS positions.

# Installation
You first need to install `python` and the required packages:
XXX

# Use
In order to build the BeauAMP database:
1. Open the Python console.

# Dependencies
XXXX

# Data
The produced database is directly available publicly online on [Zenodo](https://doi.org/XXXXX), under three different forms:
* Single CSV containing all data
* Several CSVs, each containing one year's data
* Pickle file

* Note Adrien : je pensais faire un zenodo à part à destination des non chercheurs avec une version francophone et en csv. Tu en penses quoi ?


# References
XXXXX
