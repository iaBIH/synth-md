# SynthMD: Synthetic Datasets for Software Development in Rare Disease Research

SynthMD is a Python tool for generating realistic synthetic patient data for a wide range of diseases 
without input datasets. The method leverages available statistics to create attribute distributions. 

![](https://github.com/iaBIH/synth-md/blob/main/resources/RDsStats.png)

The tool is used to generate [synthetic datasets](https://github.com/iaBIH/synth-md/edit/main/rare_disease_datasets) with 187,709 patients for three popular rare diseases i.e. [Sickle Cell Disease](https://en.wikipedia.org/wiki/Sickle_cell_disease#:~:text=Sickle%20cell%20disease%20(SCD)%20is,like%20shape%20under%20certain%20circumstances.) (SCD, ORPHA code: 232), [Cystic Fibrosis](https://en.wikipedia.org/wiki/Cystic_fibrosis) (CF, ORPHA code: 586), and [Duchenne Muscular Dystrophy](https://en.wikipedia.org/wiki/Duchenne_muscular_dystrophy) (DMD, ORPHA code: 98896). 
Each dataset has 10+ attributes including patient personal information and clinical parameters. 

![](https://github.com/iaBIH/synth-md/blob/main/resources/SampleData.png)

The synthetic data follow the input census and disease statistics with high accuracy. 

<p float="left">
<img src="https://github.com/iaBIH/synth-md/blob/main/resources/result_Gender.png" width="400">
<img src="https://github.com/iaBIH/synth-md/blob/main/resources/result_Race.png" width="400">
<img src="https://github.com/iaBIH/synth-md/blob/main/resources/result_Age.png" width="400">
</p>

### Citation: 

This tool and the datasets are described in this paper: [Synthetic Datasets for Software Development in Rare Disease Research]() (to be published). 

### Features:

 * No need for input datasets (only basic statistics are needed).
 * Very fast, can generate thousands of synthetic patient data in a few seconds.
 * Can generate synthetic data for a single disease or multiple diseases at the same time.
 * Adding a new disease is simply done by modifying a JSON file (see the sections below).
 * The synthetic data follow the input census and disease statistics with high accuracy. 

## Repository Structure:

                ├── RDdata: Contains our results and copy of all original downloaded and used files 
                │   ├── census
                │   │   ├── map
                │   │   └── usaAge2020-2021
                │   └── result
                │       ├── cf_patients_all_32093.csv
                │       ├── dmd_patients_all_55219.csv
                │       └── scd_patients_all_100403.csv
                ├── config: configueration files
                │   ├── configUSA.json
                │   └── RDsDataUSA.json
                ├── datasets: All downloaded census and preprocessed files will be saved here
                │       ├── map: required for map charts
                ├── output: All generated datasets will be saved here when run the tool 
                ├── LICENSE.txt
                ├── README.md
                ├── example.py: An example to shoe how to use the tool after installation
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

## Installation: 
  
  1. To import the U.S.A census data, one needs to get api key from here: https://api.census.gov/data/key_signup.html after that they key will be submitted to the email and needs activation. Some census variables may need update, check the census website for details and modify the file MDimport if needed (or open a new issue and we will update them).

  2. Download and install SynthMD: 

              git clone https://github.com/iaBIH/synth-md.git
              cd synth-md
              pip install . --user 


## Example:

   The provided [example](https://github.com/iaBIH/synth-md/blob/main/example.py) shows how to use the tool: 

   1. Get a census api from https://api.census.gov/data/key_signup.html
   2. Replace None by your census api in this [line](https://github.com/iaBIH/synth-md/blob/73abf642d45b895a608644c3728bc1730dd8d770/example.py#L5) in the example:
      
              censusAPIKey= None 

   3. Run these lines in your terminal

             cd synth-md
             python example.py
    
      The downloaded files from census will be saved in datasets folder. The generated synthetic datasets will be saved in output folder.

## Generating synthetic data for a new disease:

  To add a new disease using its statistics related to the U.S.A, 
  modify the file [RDsDataUSA.json](https://github.com/iaBIH/synth-md/blob/main/config/RDsDataUSA.json) and create a new disease similar to the ones available 
  e.g. copy/paste one of the diseases and change the values: 
  
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
                        "40-60": 0.7
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
                

  To add a new disease for a different country/area, you should create a new config file similar to 
  [config/configUSA.json](https://github.com/iaBIH/synth-md/blob/main/config/configUSA.json) and use it. In the new config file, you should provide census data with the 
  same format as the one provided for the U.S.A:
     
     - states-race_ext.csv: race information 
     - states-age-sex: age and sex information for male, female and both

  Modify [example.py](https://github.com/iaBIH/synth-md/blob/main/example.py) and disable import, preparation (the evaluation part is optional) e.g. 

        doImport     = 0
        doPrepare    = 0
        doCreate     = 1 
        doEvaluation = 1    
  
  After that, you can use RDcreate.py to create the synthetic data as shown in the section above.  
  You can also automate the process by importing the census data directly but you will have to modify the files
  RDimport and RDprepare.


  
## License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
