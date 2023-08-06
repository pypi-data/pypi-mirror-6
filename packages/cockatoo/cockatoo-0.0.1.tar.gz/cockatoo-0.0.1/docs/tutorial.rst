Tutorial
========

cockatoo is an implementation of a distance metric for the comparison of
macromolecular crystallization cocktails (or conditions). A cockatil is a
mixture of distinct chemical components. A screen is a collection of one or more
cocktails. Using cockatoo we can compare the similarity between two cocktails or
screens. 


Distance between cocktails
---------------------------

Cocktails are represented in `JSON <http://json.org/>`_ format. For example,
C0160.json: 

.. code-block:: javascript

    {
        "name": "8_C0160", 
        "ph": 7.5,
        "components": [
            {
                "conc": 4.48, 
                "molecular_weight": 58.4428, 
                "name": "sodium chloride", 
                "smiles": "[Na+].[Cl-]", 
                "unit": "M"
            },
            {
                "conc": 0.1, 
                "density": 1.325, 
                "molecular_weight": 238.3045, 
                "name": "hepes", 
                "smiles": "[O-]S(=O)(=O)CCN1CC[NH+](CC1)CCO", 
                "unit": "M"
            }
        ]
    }

Here we define a cocktail named 8_C0160 with two chemical components at pH 7.5. To
compare the distance between two cocktails we can use the cockatoo command line
utility:

.. code-block:: bash

    $ cockatoo cdist -1 C0160.json -2 C0163.json
    Using CD_coeff algorithm
    Computing distance between 8_C0160 and 8_C0163...
    Distance: 0.252356552114


Distance between screens
---------------------------

Screens are also represented in `JSON <http://json.org/>`_ format. For example,
hwi-gen8.json: 

.. code-block:: javascript

    {
        "name": "hwi-gen8",
        "cocktails": [
            {
                "name": "8_C0160", 
                "ph": 7.5,
                "components": [
                    {
                        "conc": 4.48, 
                        "molecular_weight": 58.4428, 
                        "name": "sodium chloride", 
                        "smiles": "[Na+].[Cl-]", 
                        "unit": "M"
                    },
                    {
                        "conc": 0.1, 
                        "density": 1.325, 
                        "molecular_weight": 238.3045, 
                        "name": "hepes", 
                        "smiles": "[O-]S(=O)(=O)CCN1CC[NH+](CC1)CCO", 
                        "unit": "M"
                    }
                ]
            },
            ... 
            ...
        ]
    }

To compute the distance between two screens we can use the cockatoo command line utility:

.. code-block:: bash

    $ cockatoo sdist -1 hwi-gen8.json -2 hwi-gen8A.json
    Using CD_coeff algorithm
    Computing distance between hwi-gen8 and hwi-gen8A...
    Distance: 0.00200980839646

Converting screens to JSON format
----------------------------------

Crystallization screens can be stored in CSV format and converted to JSON using
the cockatoo command line utility. The CSV format is as follows::

    name,overall_ph,[conc,unit,name,ph]*

    where [conc,unit,name,ph] is repeated 1 or more times for each compound

    C1,3.4,0.100,M,MOPS,,1.000,M,ammonium chloride,
    C2,3.9,0.100,M,MOPS,,1.000,M,ammonium chloride,
    C3,4.4,0.100,M,MOPS,,1.000,M,ammonium chloride,
    C4,4.9,0.100,M,MOPS,,1.000,M,ammonium chloride,

We also need to provide cockatoo information about each compound such as
molecular weight, SMILES, etc. An example of this file can be found in the
source distributuion data/hwi-compounds.csv.  This file should contain
information on each compound used in your cocktails in TAB delimitted format.
For example::

    name,conc_max,conc_min,formula,smiles,molecular_weight,density

To convert a screen to JSON format we run:

.. code-block:: bash

    $ cockatoo convert -s screen.csv -o screen.json -n screen_name -c compound-data.csv
