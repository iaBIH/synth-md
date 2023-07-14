import os, sys,  time, json
from synthMD import MDimport, MDprepare, MDcreate, MDevaluate, MDutils

# censusAPIKey="put your api key here"
censusAPIKey= None 

# if this script called directly,
if __name__ == "__main__":
   # testing 
   if len(sys.argv) > 1:
      print("input: ", sys.argv)
    
   #  #print(os.getcwd())
   startTimeTotal = time.time()

   cfgPath   = os.path.join("config","configUSA.json")
   resultsPath = "output"
   # Folder and file paths 
   usaFolderPath               = os.path.join("datasets", "usa")
   usaRaceDataPath             = os.path.join(usaFolderPath, "usa-2020-states-race.csv")
   usaAgeSexDataFolderPath     = os.path.join(usaFolderPath, "usaAge2020-2021")
   usaAgeSexDataFilePath       = os.path.join(usaFolderPath,"usa-2020-states-age-sex.csv")
   usaAgeSexMaleDataFilePath   = os.path.join(usaFolderPath,"usa-2020-states-age-sex-male.csv")
   usaAgeSexFemaleDataFilePath = os.path.join(usaFolderPath,"usa-2020-states-age-sex-female.csv")
   usaAgeSexTotalDataFilePath  = os.path.join(usaFolderPath,"usa-2020-states-age-sex-total.csv")
   usaAgeSexDataFilesPath = [usaAgeSexMaleDataFilePath,usaAgeSexFemaleDataFilePath,usaAgeSexTotalDataFilePath]
   catlabels=["male","female","total"]

   doImport     = 1
   doPrepare    = 1
   doCreate     = 1 
   doEvaluation = 1

   if doImport:
      # Import/download USA census data 
      
      # Use proxy if needed
      proxies ={}

      MDimport.getUSACensusData(censusAPIKey=censusAPIKey, datasetFolder=usaFolderPath)
   
   if doPrepare:
      # Preprocessing 
      cfg               = json.load(open(cfgPath))
      MDprepare.getPreparedData(cfg, usaRaceDataPath, usaAgeSexDataFolderPath, usaAgeSexDataFilePath, usaAgeSexMaleDataFilePath, usaAgeSexFemaleDataFilePath, usaAgeSexTotalDataFilePath, catlabels)

   if doCreate:
      # ---------------- Creating Synthetic Datasets --------------------
      cfg, RDsData, raceData, usaAgeSexData, usaAgeSexGroupData, paths = MDutils.readInputFiles(cfgPath)  
      MDcreate.createSyntheticDatasets(cfg, RDsData, raceData, usaAgeSexData, usaAgeSexGroupData, paths,  doEvaluation= 0)
 
   # Note evaluation can be done faster with createSyntheticDatasets function above 
   if doEvaluation:      
      MDevaluate.getAllEvaluation(cfgPath)

   endTmTotal = time.time() - startTimeTotal 
   print("Total time = ", endTmTotal, " seconds")

   print("-------------------  All tasks are done! -------------------------")
