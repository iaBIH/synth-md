import os, sys,  time, json
from synthMD import MDimport, MDprepare, MDcreate, MDevaluate, MDutils

# censusAPIKey = "put your API key here"
censusAPIKey= None 

# Check if the script is called directly
if __name__ == "__main__":
   
    # Print input arguments
   if len(sys.argv) > 1:
      print("input: ", sys.argv)
    
   # Record the start time of the script
   startTimeTotal = time.time()

    # Define paths to configuration and result files
   cfgPath   = os.path.join("config","configUSA.json")
   resultsPath = "output"
   
    # Define folder and file paths for datasets
   usaFolderPath               = os.path.join("datasets", "usa")
   usaRaceDataPath             = os.path.join(usaFolderPath, "usa-2020-states-race.csv")
   usaAgeSexDataFolderPath     = os.path.join(usaFolderPath, "usaAge2020-2021")
   usaAgeSexDataFilePath       = os.path.join(usaFolderPath,"usa-2020-states-age-sex.csv")
   usaAgeSexMaleDataFilePath   = os.path.join(usaFolderPath,"usa-2020-states-age-sex-male.csv")
   usaAgeSexFemaleDataFilePath = os.path.join(usaFolderPath,"usa-2020-states-age-sex-female.csv")
   usaAgeSexTotalDataFilePath  = os.path.join(usaFolderPath,"usa-2020-states-age-sex-total.csv")
   usaAgeSexDataFilesPath = [usaAgeSexMaleDataFilePath,usaAgeSexFemaleDataFilePath,usaAgeSexTotalDataFilePath]
   catlabels=["male","female","total"]

    # Flags for executing various steps
   doImport     = 1
   doPrepare    = 1
   doCreate     = 1 
   doEvaluation = 1

   if doImport:
      # Import or download USA census data
      # Use proxy if needed
      proxies ={}
      MDimport.getUSACensusData(censusAPIKey=censusAPIKey, datasetFolder=usaFolderPath)
   
   if doPrepare:
      # Preprocess the data
      cfg               = json.load(open(cfgPath))
      MDprepare.getPreparedData(cfg, usaRaceDataPath, usaAgeSexDataFolderPath, usaAgeSexDataFilePath, usaAgeSexMaleDataFilePath, usaAgeSexFemaleDataFilePath, usaAgeSexTotalDataFilePath, catlabels)

   if doCreate:
      # Create synthetic datasets
      cfg, RDsData, raceData, usaAgeSexData, usaAgeSexGroupData, paths = MDutils.readInputFiles(cfgPath)  
      MDcreate.createSyntheticDatasets(cfg, RDsData, raceData, usaAgeSexData, usaAgeSexGroupData, paths,  doEvaluation= 0)

   # Evaluate the synthetic datasets
   # Note evaluation can be done faster with createSyntheticDatasets function above 
   if doEvaluation:      
      MDevaluate.getAllEvaluation(cfgPath)

   # Calculate the total execution time
   endTmTotal = time.time() - startTimeTotal 
   print("Total time = ", endTmTotal, " seconds")

   print("-------------------  All tasks are done! -------------------------")
