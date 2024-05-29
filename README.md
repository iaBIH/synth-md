# SynthMD: Synthetic Datasets for Software Development in Rare Disease Research

SynthMD is a Python tool for generating synthetic patient data to support software development and evaluations in rare disease research. The method leverages publicly available statistics and correlations to generate synthetic records.

![](https://github.com/BIH-MI/synthetic-rd-data/blob/main/resources/RDsStats.png)

This repository contains code to use the tool for generating three [synthetic datasets](https://github.com/BIH-MI/synthetic-rd-data/tree/main/MDdata/result) for three popular rare diseases i.e. [Sickle Cell Disease](https://en.wikipedia.org/wiki/Sickle_cell_disease) (SCD), [Cystic Fibrosis](https://en.wikipedia.org/wiki/Cystic_fibrosis) (CF), and [Duchenne Muscular Dystrophy](https://en.wikipedia.org/wiki/Duchenne_muscular_dystrophy) (DMD). The datasets contain demographic data and selected clinical parameters.

## Repository Structure

                ├── RDdata: Contains our results and copy of all original downloaded and used files 
                │   ├── census
                │   │   ├── map
                │   │   └── usaAge2020-2021
                │   └── result
                │       ├── cf_patients_all_32093.csv
                │       ├── dmd_patients_all_55219.csv
                │       └── scd_patients_all_100403.csv
                ├── config: configuration files
                │   ├── configUSA.json
                │   └── RDsDataUSA.json
                ├── datasets: All downloaded census and preprocessed files will be saved here
                │       ├── map: required for map charts
                ├── output: All generated datasets will be saved here when run the tool 
                ├── LICENSE.txt
                ├── README.md
                ├── example.py: An example to show how to use the tool after installation
                ├── requirements.txt
                ├── resources: Images used in this Readme file.
                ├── setup.py: Setup file 
                └── synthMD: Source code
                   ├── __init__.py
                   ├── LICENSE.txt
                   ├── MDcharts.py: Charting 
                   ├── MDcreate.py: Synthetic data generation
                   ├── MDevaluate.py: Evaluation 
                   ├── MDimport.py: Importing data from census 
                   ├── MDprepare.py: Preprocessing 
                   ├── MDutils.py: Utilities 
                   └── synthMD.py: Setup                

## Installation Guide

Follow these steps to set up SynthMD and start generating synthetic datasets.
  
### 1. Obtain Your Census API Key
To import US Census data, you'll need an API key:
- Visit the [Census API Signup Page](https://api.census.gov/data/key_signup.html) to get your API key. Check the Census website for any additional details.
- (Modify the `MDimport` file if necessary to accommodate specific requirements.)
- You will receive the API key by e-mail.

### 2. Download and Install SynthMD

              git clone https://github.com/BIH-MI/synthetic-rd-data.git
              cd synthetic-rd-data
              pip install . --user 
              
### 3. Insert Your Census API Key
Replace 'None' with your Census API key in the example script in this [line](https://github.com/BIH-MI/synthetic-rd-data/blob/main/example.py#L5).
Note that it must be inserted as a string!
      
### 4. Execute the code
Run the example script to start the data generation process.

             python example.py
    
### File Locations
- **Downloaded US Census files:** `datasets` folder.
- **Generated synthetic datasets:** `output` folder.

_You can find three generated example files here: [Example files](https://github.com/BIH-MI/synthetic-rd-data/blob/main/output)._

## Extending the code

To extend the scripts to generate data for a new rare disease modify the file [MDsDataUSA.json](https://github.com/BIH-MI/synthetic-rd-data/blob/main/config/MDsDataUSA.json) and create a new disease configuration similar to the ones already included:

                  {
                  "RDID": 4,
                  "orphanet_code": 44444,
                  "short_name": "d4",
                  "name": "Disease Name",
                  "number_of_patients":  {
                    "nump_value": 1000,
                    "note":"NA: computed based on population and prevalence",
                    "refs":[""]  
                  },   
                  "prevalence":       {
                    "pr_value": 0.0001,
                    "note":"",
                    "refs":[""]  
                  },   
                  "race_percentage":{
                    "races": {
                        "African-American,AA": 30.0,
                        "European-American,EA": 30.0,
                        "Others,OA": 10.0
                      },
                      "refs":[""]        
                  },
                  "diagnosis_dates":{
                      "dg_min_days":30,
                      "dg_max_days":90,
                      "note":"how many days after birth until diagnostic, 1-3 years",
                      "refs":[""]     
                  },
                  "sex_percentage":{
                    "male": 20.0,
                    "female": 80.0,
                    "note": "",
                    "refs":[""]     
                  },
                  "death_percentage": {
                    "rates":{
                        "0-4":   0.0,
                        "5-14":  0.0,
                        "15-19": 0.0,
                        "20-24": 0.0,
                        "25-39": 0.0,
                        "40-60": 0.7,
                        "61-99": 30.0
                      },
                      "note":"",
                      "refs":[""]        
                  },
                  "clinical_parameters": [
                    {
                      "cp_name": "CP",
                      "cp_unit": "unit/L",
                      "cp_min_value": 10,
                      "cp_max_value": 50,
                      "refs":[""]            
                    }
                  ]
                  }
                

  If you want to add statistics about a new geography, create a new config file similar to [config/configUSA.json](https://github.com/BIH-MI/synthetic-rd-data/blob/main/config/configUSA.json). Information that needs to be provided:
  
- **states-race_ext.csv:** race information
- **states-age-sex:** age and sex information for male, female and both

Modify [example.py](https://github.com/BIH-MI/synthetic-rd-data/blob/main/example.py) and disable the steps import and preparation, e.g.:

        doImport     = 0
        doPrepare    = 0
        doCreate     = 1 
        doEvaluation = 1    
  
  After that, you can use MDcreate.py to create synthetic data using the newly provided statistics.

## License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
