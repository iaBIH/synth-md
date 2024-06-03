# #=============================================================
# The script: 
#    - imports USA states information using us lib
#    - imports USA census race data using API and save to csv file
#    - downloads USA census age and sex excel tables and convert them to csv
#    - pip install census --proxy http://8.8.8.8/
#
# Requirements:
#   - install us and census (note census lib is not used, it seems out of date)
#       pip3 install census us
#   - getting api key from here: https://api.census.gov/data/key_signup.html
#       after that they key will be submitted to the email and needs activation
# Important note: some census variables may need update, check the census website for details
# #=============================================================


import os, sys, csv, json, requests, urllib, time
import pandas as pd

from synthMD import MDutils

## -------------------------  Get Race populations using USA census API

# Function to get USA census race data using the Census API
def getUSACensusDataRace(censusAPIKey, censusQueryYear=None, censusXLSXYear=None, forceDownload=None,
                         usaIDs=None,race_data_path=None, doSave=None, proxies=None):
        
        proxies= {} if proxies is None else proxies
        usaIDs = [ "0" + str(id) if id <10 else str(id) for id in usaIDs]
        
        ## Get states race             
        ## Total, white, black: Ref:  https://api.census.gov/data/2020/dec/pl/variables.html
        censusVars      = "NAME,P1_001N,P1_003N,P1_004N"
        dataset_acronym = "/dec/pl"
        stateIDs        = "*" # we can also get one or more specific states e.g. 01,02,06
        query_url_race       = "https://api.census.gov/data/"+str(censusQueryYear)+dataset_acronym+"?get="+censusVars+"&for=state:"+stateIDs+"&key=" + censusAPIKey

        # Use requests package to call out to the API
        response = requests.get(query_url_race) if not proxies else requests.get(query_url_race, proxies=proxies) 
        print(response.text) 
        
        ## Convert the response to text and print the result
        labels=["State","Total","White", "Black", "ID"]

        ## Save the data as csv  
        race_data = [ [x for x in json.loads(response.text)[1:] if id==x[4] ] for id in usaIDs]

        race_data.insert(0, labels)

        ## Open a new CSV file
        csv.writer(open(race_data_path, 'w', newline='')).writerows(race_data)    

##  -------------- Get USA census age sex data using excel tables

# Function to get USA census age and sex data using Excel tables
def getUSACensusDataAgeSex(censusAPIKey=None, censusQueryYear=None, censusXLSXYear=None, forceDownload=None,
                            usaIDs=None, usaSNames=None, usaAgeFolderPath=None, doSave=None,  proxies=None):
        """
        Calculates the area of a circle with the given radius.

        Args:
          radius (float): The radius of the circle.

        Returns:
           float: The area of the circle.
        """      
        proxies= {} if proxies is None else proxies  
        forceDownload = 0 if forceDownload is None else forceDownload

        ### Note: this query 2020 and 2021  age sex (does not cover details)
        ##  query_url = "https://api.census.gov/data/2016/acs/acs1?get=group(B01001)&for=us:*&key=" + censusAPIKey
        # The required data are available as xlxs for download    
        query_url_age_sex = "https://www2.census.gov/programs-surveys/popest/tables/" + censusXLSXYear + "/state/asrh/sc-est2021-syasex-"
        # Download all files and convert to csvs
        # Create directory for age data if it doesn't exist
        if not os.path.exists(usaAgeFolderPath):
             os.mkdir(usaAgeFolderPath)
          
        # Download and convert Excel files to CSV
        for i,id in enumerate(usaIDs):
                    id       = "0" + str(id) if id <10 else str(id)
                    fnm      = id + ".xlsx" 
                    webLink  = query_url_age_sex + fnm 
                    xlsxPath = os.path.join(usaAgeFolderPath,"usa-age-sex-"+censusXLSXYear+"-"+id+"-"+usaSNames[i]+".xlsx")
                    csvPath  = xlsxPath[:-4]+"csv"
          
                    # Download only if file does not exist, to force download anyway use forceDownload=1
                    if forceDownload or not os.path.exists(csvPath):
                        try:
                            print("downloading : ", csvPath)
                            
                            if proxies:
                                # Define the proxy information
                                proxy_handler = urllib.request.ProxyHandler(proxies)
                                opener = urllib.request.build_opener(proxy_handler)
                                urllib.request.install_opener(opener)

                            urllib.request.urlretrieve(webLink, xlsxPath)
                            #print("convert xlsx to csv ....")
                            # Read the excel file into a pandas dataframe
                            df = pd.read_excel(xlsxPath,  engine='openpyxl')
                            # Write the dataframe to a csv file
                            df.to_csv(csvPath, index=False)
                            #print("removing old xlsx file ....")
                            #os.remove(xlsxPath)
                        except Exception as e: 
                            print(e)      
                    else:
                        print("age-sex data file exist: ", csvPath) 

## --------------------------------- Get USA Census Data                             
def getUSACensusData(censusAPIKey, datasetFolder, censusQueryYear=None, censusXLSXYear=None, getAgeSexData=None, getRaceData=None,forceDownload=None,  doSave=None, proxies=None):
    print("=========================== Getting USA Census DATA ================================")
  
  # Check if API key is provided  
  if censusAPIKey==None:
       print("please get your API key from here: https://api.census.gov/data/key_signup.html")
       sys.exit(0)
    impTimeStart = time.time()
    proxies =  {} if proxies is None else proxies
    censusQueryYear   = 2020 if censusQueryYear is None else censusQueryYear
    censusXLSXYear    = "2020-2021" if censusXLSXYear is None else censusXLSXYear
    doSave            = 0 if doSave is None else doSave
    forceDownload     = 0 if forceDownload is None else forceDownload
    getAgeSexData     = 1 if getAgeSexData is None else getAgeSexData
    getRaceData       = 1 if getRaceData is None else getRaceData

    # Define storage paths
    # TODO: get from config file, also add using optional arguments from terminal
    usaAgeFolderPath         = os.path.join(datasetFolder,"usaAge"+censusXLSXYear)
    race_data_path           = os.path.join(datasetFolder,"usa-"+str(censusQueryYear)+"-states-race.csv")

    # Get USA state IDs and names
    # IDs and short names are useful to work with API and other libs
    usaFIPS, usaSNames, usaLNames  = MDutils.getUSAstateNames() 
 
    if getRaceData and not os.path.exists(race_data_path):        
       getUSACensusDataRace(censusAPIKey,censusQueryYear, censusXLSXYear, forceDownload,usaFIPS,race_data_path,
                             doSave, proxies=proxies)
    else:
        print("race data file exists: ", race_data_path)

    # Get age/sex data if required
    if getAgeSexData: 
       getUSACensusDataAgeSex(censusAPIKey,censusQueryYear, censusXLSXYear, forceDownload, 
                              usaFIPS, usaSNames,usaAgeFolderPath, doSave, proxies=proxies)
   
    impTimeEnd = time.time() - impTimeStart
    print("Import time process took: ", impTimeEnd, " seconds")
    
# If this script called directly
if __name__ == "__main__":
    # testing 
    if len(sys.argv) > 1:
       print("input arguments: ", sys.argv)
