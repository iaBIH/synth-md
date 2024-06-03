import os, sys, csv, random, datetime, json
from us import states
from scipy import special
import numpy as np
from faker import Faker
fake = Faker()

#--------------- Read Input Files-----------
def readInputFiles(cfgPath):
      """
      Read configuration, rare disease and USA statistics from files:
      cfgPath: path to the configuration file
      rdsPath: path to the RDs data file
      """
      # Read configuration and rare disease data from files:
      cfg               = json.load(open(cfgPath))

      # Construct paths from configuration
      rdsPath = os.path.join(*list(cfg["paths"]["rdsPath"]))
      usaRaceDataPath = os.path.join(*list(cfg["paths"]["usaRaceDataPath"]))
      usaAgeSexDataFilesPath= os.path.join(*list(cfg["paths"]["usaAgeSexDataFilePath"]))
      resultsFolderPath= os.path.join(*list(cfg["paths"]["resultsFolderPath"]))
      age_sex_catigories = list(cfg["age_sex_catigories"])

      # Append age/sex categories to the path
      usaAgeSexDataFilesPath = [usaAgeSexDataFilesPath+x for x in age_sex_catigories]

      # Read rare disease data
      RDsData           = json.load(open(rdsPath))
      RDsData           = RDsData["RDs"]
       
      # Read race data from CSV
      # USA states populations per race: 51 x 6
      # ID	State	African-American	European-American	Others	Total
      raceData = [row for row in csv.reader(open(usaRaceDataPath), delimiter=",", quotechar='"')]
      raceData = [  [int(x[0]), x[1], int(x[2]),int(x[3]),int(x[4]),int(x[5]) ] for x in raceData[1:]]
   
      # Read age/sex data from CSV  
      usaAgeSexData = [ [ [int(x[0]), x[1]] +[int(y) for y in x[2:] ] for x in [row for row in csv.reader(open(fnm+"_ext.csv"), delimiter=",", quotechar='"')]] for fnm in usaAgeSexDataFilesPath]
      usaAgeSexGroupData = [ [ [int(x[0]), x[1]] +[int(y) for y in x[2:] ] for x in [row for row in csv.reader(open(fnm+"_grp.csv"), delimiter=",", quotechar='"')]] for fnm in usaAgeSexDataFilesPath]
      
      # USA states populations per sex and age
      # 51 x 96
      # ID	State	Age_0,...,Age_maxAge
      usaAgeSexMaleData   = [x[2:] for x in usaAgeSexData[0]]
      usaAgeSexFemaleData = [x[2:] for x in usaAgeSexData[1]]
      usaAgeSexBothData   = [x[2:] for x in usaAgeSexData[2]]
      usaAgeSexData = [usaAgeSexMaleData, usaAgeSexFemaleData, usaAgeSexBothData]

      # 51 x 7
      # ID	State	AgeGroup_0,...,AgeGroup_6
      usaStatesAgeSexGroupMale     =  [x[2:] for x in usaAgeSexGroupData[0]]
      usaStatesAgeSexGroupFemale   =  [x[2:] for x in usaAgeSexGroupData[1]]
      usaStatesAgeSexGroupBoth     =  [x[2:] for x in usaAgeSexGroupData[2]]
      usaAgeSexGroupData = [usaStatesAgeSexGroupMale, usaStatesAgeSexGroupFemale, usaStatesAgeSexGroupBoth]

      return cfg, RDsData, raceData, usaAgeSexData, usaAgeSexGroupData, [usaAgeSexDataFilesPath, resultsFolderPath]

# Function to get race data
def getRaceData(raceData, RDsData): 

   # Sum populations by race
   # raceData: ID	State	African-American	European-American	Others	Total
   # African-American (AA), European-American (EA), and others (OA) populations of each state
   total_AA_Population = sum([x[2] for x in raceData])
   total_EA_Population = sum([x[3] for x in raceData])
   total_OA_Population = sum([x[4] for x in raceData])

   racePopulations =[total_AA_Population, total_EA_Population, total_OA_Population]

   # total race for each state 
   # raceData: ID	State	African-American	European-American	Others	Total

   # Populations per state by race
   AA_PopulationsSt  = [x[2] for x in raceData]         
   EA_PopulationsSt  = [x[3] for x in raceData]  
   OA_PopulationsSt  = [x[4] for x in raceData] 
   racePopulationsSt = [[x,y,z] for x,y,z in zip(AA_PopulationsSt, EA_PopulationsSt, OA_PopulationsSt)]

   total_USA_Population_From_Race  = sum([sum(x) for x in racePopulationsSt]) 

   # Get race weights and number of patients
   # How many patients per race AA,EA,OA
   # Notes: SCD affect AA moastly
   #        CF  affects EA moastly
   raceWeights = [list(rd['race_percentage']['races'].values()) for rd in RDsData]
                     
   actual_number_of_patients =  [int(rd['number_of_patients']['nump_value']) for rd in RDsData]

   # RD: prevalence
   # SCD value is conflicting with total number of patients 
   # Total number of patients should be around:
   # 100000, 32100, 55241
   prevalenceLst = [float(rd['prevalence']['pr_value']) for rd in RDsData]
   # fix missing values, sometimes prevalence or number of patients are missing
   prevalenceLst = [ actual_number_of_patients[i]/total_USA_Population_From_Race if x==0 else x for i,x in enumerate(prevalenceLst)]
   prevalenceRaceLst = [ [(prevalence * total_USA_Population_From_Race * rw / 100) / rp for rw,rp  in zip(raceWeight, racePopulations)] 
                                                                              for  raceWeight, prevalence in zip(raceWeights, prevalenceLst)]
  
   return raceWeights, total_USA_Population_From_Race, prevalenceRaceLst, racePopulations, racePopulationsSt
    
#--------------------------Functions for generating data--------------------------
# Get death rate based on age, race, sex statitics 
def getStatesDeathRateDists(s, rdDeathRates, numberOfPatientsForAgeGroups):
     
      # Find dead patients based on age 
      statePatientsDead    = [  round((x/100.0) * y) for x,y in zip(rdDeathRates, numberOfPatientsForAgeGroups) ]
      statePatientsAlive   = [      x - y    for x,y in zip(numberOfPatientsForAgeGroups, statePatientsDead)]

      # generate alive/dead distribution for all age groups of the current state
      deathRateAgeDists  = [ [False]*x + [True]*y for x,y in  zip(statePatientsDead, statePatientsAlive)]

      return  deathRateAgeDists

# Function to generate random time
def getRandomTime(inputDate):

    # Add random hours, minutes, and seconds
    randomHours   = random.randint(0,24)    
    randomMinutes = random.randint(0,60)
    randomSeconds = random.randint(0,60)

    # Format time values
    randomHours   = str(randomHours)   if randomHours>9   else "0" + str(randomHours)
    randomMinutes = str(randomMinutes) if randomMinutes>9   else "0" + str(randomMinutes)
    randomSeconds = str(randomSeconds) if randomSeconds>9 else "0" + str(randomSeconds)

    randomTime = " " + randomHours + ":" + randomMinutes + ":"+ randomSeconds
    outDateTime = str(inputDate) + randomTime
    return outDateTime

#------------------- Create death date  --------------------
# Create a random death date based on the patient age and probablity of death
# The patient will be died at the input age. The patient born after 1.1.1900
# def getDeathDate(inputAge, ageDeathRate, birthDate, diagDate, ageDiagFactor):
def getDeathDate(inputAge, birthDate, diagDate, ageDiagFactor, addTimeToDates):
        deathDateS = None
       
        # Update the birthdate and the diagnostic date relativly to the death date
        # The age now means the age when the patient died

        # Calculate birth and diagnostic dates
        startDate = datetime.date(1920,1,1)
        endDate   = datetime.date(2023-inputAge,1,1) 

        birthDate = fake.date_time_between(start_date=startDate, end_date=endDate)

        diagDate  = str(birthDate.date() + datetime.timedelta(days=ageDiagFactor))

        deathDate = str(birthDate.date() + datetime.timedelta(days=inputAge * 365))

        # Format birth date
        birthDate = str(birthDate)[:10]

        # Add time to dates if required
        if addTimeToDates:            
            birthDate = getRandomTime(birthDate)
            diagDate  = getRandomTime(diagDate)
            deathDate = getRandomTime(deathDate)
        return birthDate, diagDate, deathDate

#------------------- Create a distribution to sample from  --------------------
def getGroupDistriution(labelLst, countLst):       
    # Check if we have large numbers, reduce them
    countLst = [round(x) for x in countLst]
    if countLst[0]>1000:
       countLst = [int(x/1000) for x in countLst]  

    # Create distribution
    dist = [[x]*y for x,y in zip(labelLst, countLst)]
    
    # Flatten list
    dist   = [item for sublist in dist for item in sublist]
    
    # Shuffle
    random.shuffle(dist)
    return dist

# #-------------------- create age distribution ----------------------  
def  getAgeDistribution(stData, numPST, rdAgeGroupsLst, total_number_of_patients):
     stateAgeDist = []
     dataLabels=list(range(len(stData)))

     # Calculate total population of the state   
     stTotal = sum(stData)

     # Calculate age ratios and rates  
     stateAgeRatio = [ round( stData[x] / stTotal ,5)              for x in range(len(stData)) ]    

     # Number of patients per age for this state  
     stateAgeRates  = [ round(     stateAgeRatio[x]  *  numPST   )  for x in range(len(dataLabels)) ]    

     # Repeat for each age  
     for k in range(len(dataLabels)): 
         ageDist = []
         for r in range (stateAgeRates[k]):
             ageDist.append(k)
         stateAgeDist.append(ageDist)    
     
     # Collect age distribution into age groups     
     finalStateAgeDist = []    
     for g, ag in enumerate(rdAgeGroupsLst):         
         minAge,maxAge = getAgeRangeFromAgeGroup(g, dataLabels[-1])  
         stateAgeGroupDist = [stateAgeDist[k] for k in range(len(stateAgeDist)) if minAge<=k and k<maxAge]
         #flatten
         stateAgeGroupDist = [item for sublet in stateAgeGroupDist for item in sublet]
         finalStateAgeDist.append(stateAgeGroupDist)
      
     return finalStateAgeDist

#------------------- Sample from a normal distribution   --------------------
# based on minimum, maximum values. mean = (min + max)/2, std = mean/2
# Ref: https://stackoverflow.com/questions/62364477/python-random-number-generator-within-a-normal-distribution-with-min-and-max-val
#      https://www.thoughtco.com/range-rule-for-standard-deviation-3126231
def sampleFromNormalDistribution(minVal, maxVal, sampleSize=10000):   
    # TODO BUG: if the range is large samples ma not look like normally distributed
    mean = (minVal + maxVal) / 2.0
    std  = (maxVal - minVal) / 4.0  
    random_uniform_data = np.random.uniform(special.erf( (minVal - mean) / std), 
                                            special.erf( (maxVal - mean) / std), 
                                            sampleSize)
    random_gaussianized_data = (special.erfinv(random_uniform_data) * std) + mean
    return random_gaussianized_data

 #---------------  get state names  ---------------- 
def getUSAstateNames(isDCIncluded=None):  
    """
      Return list of USA states IDs, long and short names

      Args:
         isDCIncluded (int): 1: to include or 0: to exclude Washington DC from the list

      Returns:
         List of lists: states IDS (int), states short names (str), state long names (str) 
         debends on isDCIncluded, the returned size may be  3x51 or 3x52 
    """       
    isDCIncluded = 1 if isDCIncluded is None else isDCIncluded

    usaFIPS    = [int(states.STATES[x].fips)   for x in range(len(states.STATES))]
    usaLNames  = [states.STATES[x].name        for x in range(len(states.STATES))]
    usaSNames  = [states.STATES[x].abbr        for x in range(len(states.STATES))]

    if isDCIncluded:
         # add Washington DC
         usaFIPS.append(11)
         usaFIPS = sorted(usaFIPS)
         usaLNames.insert(usaFIPS.index(11),"District of Columbia") 
         usaSNames.insert(usaFIPS.index(11),"DC") 

         usaNames = [usaFIPS, usaSNames, usaLNames]

         ## check if the list is sorted
         ## print(all(usaFIPS[i] <= usaFIPS[i+1] for i in range(len(usaFIPS) - 1)))       
    return usaNames

#------------------- Get index of age group --------------------
# Determine age group based on age
def getAgeGroupIndex(age):
        if age < 5:
           ageG = 0
        elif   5 <= age and age <= 14:
           ageG = 1
        elif  15 <= age and age <= 19:
           ageG = 2
        elif  20 <= age and age <= 24:
           ageG = 3
        elif  25 <= age and age <= 39:
           ageG = 4
        elif  40 <= age and age <= 60:
           ageG = 5
        elif  60 < age:
           ageG = 6
        return ageG  

#---------------  find range of each age group  ---------------- 
# Determine age range based on age group index
def getAgeRangeFromAgeGroup(ageGroupIndex, maxAge):
    ageStart = None; ageEnd= None
    if   ageGroupIndex == 0:
       ageStart = 0; ageEnd= 5
    elif ageGroupIndex == 1:
       ageStart = 5; ageEnd= 15
    elif ageGroupIndex == 2:
       ageStart = 15; ageEnd= 20
    elif ageGroupIndex == 3:
       ageStart = 20; ageEnd= 25
    elif ageGroupIndex == 4:
       ageStart = 25; ageEnd= 40
    elif ageGroupIndex == 5:
       ageStart = 40; ageEnd= 61
    elif ageGroupIndex == 6:
    #    print("maxAge : ",maxAge)
       ageStart = 61; ageEnd= maxAge + 1
    return   ageStart, ageEnd 

#--------------------------------   readingCSVdata  ----------------
# Read CSV data for charting
def readingCSVdata(csvFnm, maxUSAAge=None):
    with open(csvFnm) as dataFile:
        dataReader  = csv.reader(dataFile, delimiter=";", quotechar='"')
        data        = [row for row in dataReader]
        dataLabels  = data[0]
        dataArray   = data[1:]
        newDataArray = []
        if (maxUSAAge is None) or (maxUSAAge == 0): 
            maxUSAAge = np.max([int(x[1]) for x in dataArray])

        dataArray = [[row[0]] + [ (x)    for x in row[1:] ]  for row in dataArray]

        for row in dataArray:
            for i,col in enumerate(row): 
                if i in [0,1]:
                    row[i] = int(col) 
                elif  i in [9,10]:
                    row[i] = float(col) 
                elif  i in [6,7,8]: # Dates to years                      
                    row[i] = int(col[:4]) if not col=="" else 0
            newDataArray.append(row)        
        newDataArray = dataArray if newDataArray ==[] else newDataArray
       
    return maxUSAAge, dataLabels, newDataArray

# Function to get files matching a string in a directory
def RDGetFiles(directory, string):
    # Traverse the directory structure
    filesLst = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # Check if the desired string is in the filename
            if string in filename:
                filesLst.append(os.path.join(root, filename)) 
                
    return filesLst 

# if this script called directly
if __name__ == "__main__":
    # testing 
    if len(sys.argv) > 1:
       print("input: ", sys.argv)
   
