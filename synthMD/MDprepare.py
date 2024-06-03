##=============================================================
# The script: 
#    - reads the output files from import
#    - convert them to usable csv and data lists 
#    - generates input data charts
##=====================================================

import csv, json, sys, os, time
import numpy as np
from scipy.optimize import minimize

from synthMD import MDutils, MDcharts

# Function to read race data from a CSV file and restructure it
def getRaceData(cfg, raceDataFilePath):
    
    print("Reading race data: ", raceDataFilePath)
        
    #-------- race data for each state
    # Read race data from CSV file
    raceData     = [row for row in csv.reader(open(raceDataFilePath), delimiter=",", quotechar='"')]
    raceData[1:] = [ [s.strip("[]'") for s in x[0].split(', ')] for x in raceData[1:]]
    
    # Get race names from JSON configuration file   
    rdsPath = cfg["paths"]["rdsPath"] 
    rdsPath = os.path.join(*rdsPath)
    RDsData      = json.load(open(rdsPath))["RDs"]
    raceNamesLst = [x.split(",")[0] for x in list(RDsData[0]["race_percentage"]["races"].keys())]
    
    # Restructure labels and data 
    raceData[0]  = [ raceData[0][4], raceData[0][0], raceNamesLst[0], raceNamesLst[1],raceNamesLst[2], raceData[0][1] ]
    raceData[1:] = [ [int(x[4]), x[0], int(x[3]), int(x[2]), int(x[1])- int(x[2])-int(x[3]) ,int(x[1])] for x in raceData[1:]]

    # Save the restructured data to a new CSV file
    csv.writer(open(raceDataFilePath[:-4]+"_ext.csv", 'w', newline='')).writerows(raceData)
            
    return raceData 

#-------------------------------- Extract Age Sex Data from usaAgeSexDataFolderPath into 4 files
#  usaAgeSexDataFilePath: all useful extratced data 
#  usaAgeSexMaleDataFilePath, usaAgeSexFemaleDataFilePath, usaAgeSexTotalDataFilePath: data of male, female and both

# Function to extract and process age-sex data from multiple CSV files
def getAgeSexData(usaAgeSexDataFolderPath, usaAgeSexDataFilePath, usaAgeSexMaleDataFilePath, usaAgeSexFemaleDataFilePath, usaAgeSexTotalDataFilePath):
    
    ageSexData=[]
    if not os.path.exists(usaAgeSexDataFilePath):
       print("Reading age sex data files from: ", usaAgeSexDataFolderPath)
       fnms  = os.listdir(usaAgeSexDataFolderPath)
       fnms  = sorted([x for x in fnms if ".csv" in x ])
            
       # Read each file and process the data
       for fnm in fnms:            
            print("reading : ", fnm)
            
            #TODO: add columns config to config.json
            # Extract state ID and name from the filename
            id    = int(fnm[-9:-7])
            state = fnm[-6:-4]
            
            # Read the file into a list
            dataReader = csv.reader(open(os.path.join(usaAgeSexDataFolderPath,fnm)), delimiter=",", quotechar='"')
            fileData   = [row for row in dataReader]
            
            # Restructure and convert to numbers
            dataArray    = [[x[0], x[2], x[3], x[1]] for x in fileData[6:92]] 
            dataArray    = [[ i, x[1], x[2], x[3]]  for i, x in enumerate(dataArray)] 
            dataArray.insert(0,[id,state])
            # Flatten to 345 elements
            dataArray = [item for sublist in dataArray for item in sublist]

            # Add to list of all states                
            ageSexData.append(dataArray)
       
       # Restructure the data
       #ageSexData: 51 x id, state,    age, male, female, total,...,age, male female total
       labels = ["id", "state"]
       labels.extend(["age","male","female","total"]* 86)

       allData = []
       allData.append(labels)
       for x in ageSexData:
           allData.append(x)

       numStates = len(ageSexData)
    
       # For each ages, we have 4 fields age, m,f,t  
       numAges   = int((len(ageSexData[0])-2)/4)

       # Male population for each age for each state
       ageStateMaleLst    =[]
    
       # Female population for each age for each state       
       ageStateFemaleLst  =[]
    
       # Population for each age for each state       
       ageStateTotalLst  =[]
               
       # Create 3 large tables 51 rows x 2+86 columns
       # id state age_0-age_85 
       # for each state
       for i in range(numStates):
           # For each state, get Male, Female, and Total population of current age
           # Add id and state to each row
           rowM=[int(ageSexData[i][0]), ageSexData[i][1]]
           rowF=[int(ageSexData[i][0]), ageSexData[i][1]]
           rowT=[int(ageSexData[i][0]), ageSexData[i][1]]
           # For each age
           for j in range(numAges):     
               # Add population of each age 
               idx = (3*j + 3 + j)-1               
               rowM.append(int(ageSexData[i][idx+1]))
               rowF.append(int(ageSexData[i][idx+2]))
               rowT.append(int(ageSexData[i][idx+3]))
           ageStateMaleLst.append(rowM)   
           ageStateFemaleLst.append(rowF)   
           ageStateTotalLst.append(rowT)   
       labels = ["id","state"]
       labels.extend(["age_"+str(x) for x in range(numAges)])
       ageStateMaleLst.insert(0,labels)
       ageStateFemaleLst.insert(0,labels)
       ageStateTotalLst.insert(0,labels)

       # Create csv files from the lists
       data2Save = [allData, ageStateMaleLst, ageStateFemaleLst, ageStateTotalLst] 
       fnms      = [usaAgeSexDataFilePath, usaAgeSexMaleDataFilePath, usaAgeSexFemaleDataFilePath, usaAgeSexTotalDataFilePath]
       for fnm, fData in zip(fnms, data2Save):
            csv.writer(open(fnm,       'w', newline='')).writerows(fData)
              
    else:
       print("getAgeSexData(): files are already exist : ", usaAgeSexDataFilePath)  

       data2Read = [] 
       fnms      = [usaAgeSexMaleDataFilePath, usaAgeSexFemaleDataFilePath, usaAgeSexTotalDataFilePath]
       for fnm in fnms:
            # read csv files into lists
            fData   = [row for row in csv.reader(open(fnm), delimiter=",", quotechar='"')]
            # convert to integers
            fData[1:]   = [ [int(x)  if i>1 else x for i, x in enumerate(y) ] for y in fData[1:]]
            data2Read.append(fData)

       ageStateMaleLst, ageStateFemaleLst, ageStateTotalLst = data2Read 
    
    ageSexData = [ageStateMaleLst,ageStateFemaleLst,ageStateTotalLst]
    return ageSexData 

# Get initial list as linear distribution
def getLinearValue(x,x1,y1,x2,y2):
    # create linear distribution  y = m*x + b    
    m = (y2-y1)/(x2-x1)
    y = m*(x-x1) + y1
    return int(y)

# Reduce the error using optimisation
def minimizeError(estimated_population, estimation_sum):
    
    def func(x):
      return abs(np.sum(x) - estimation_sum)

    # Initialize the list
    x0 = estimated_population

    # Define the constraints
    constraints = [
        {'type': 'ineq', 'fun': lambda x: estimation_sum - np.sum(x)},
        {'type': 'ineq', 'fun': lambda x: x-5}, # values must be >=5
    ]
    # Minimize the absolute difference
    result = minimize(func, x0, constraints=constraints, method='SLSQP')
    return [int(z) for z in  result.x]

# Create a new estimated list for missing ages
# We distributed the last age value on the missing ages
def getEstimatedList(ages_population, maxInputAge=None, maxEstimatedAge=None, maxError=None):
    maxInputAge     = 84 if maxInputAge is None else maxInputAge
    maxEstimatedAge = 96 if maxEstimatedAge is None else maxEstimatedAge -1
    maxError        = 100 if maxError is None else maxError

    estimation_sum     = ages_population[-1]
    startElement       = ages_population[-2]

    endElement = 1 

    estimated_population = [ getLinearValue(x,maxInputAge,startElement,maxEstimatedAge,endElement) for x in range(maxInputAge,maxEstimatedAge+1)]

    estimated_population = minimizeError(estimated_population, estimation_sum)

    final_error = abs(estimation_sum-sum(estimated_population))
     
    # Check for negative values 
    hasNegative = any(x < 0 for x in estimated_population) 
    if hasNegative:
       print("Error: Negative values")
       for i,x in enumerate(estimated_population):
           print(i+85,x)
       sys.exit()  

    # Check if we havee large error
    largeError = final_error>maxError
    if largeError:
       print("Error: Large error")
       for i,x in enumerate(estimated_population):
           print(i+85,x)
       print("final_error : ",final_error)    
       sys.exit()  
       
    return estimated_population

# Function to fix age-sex data by adding estimated values for missing ages
def getFixAgeSexData(ageSexData=None, maxAge=None, fnmPath=None, usaAgeSexDataFilesPath=None, catlabels=None):
    
    # First check if the files exist
    fixedFilePaths =  [x[:-4]+"_ext.csv" for x in usaAgeSexDataFilesPath]
    
    ## This is computed only when the files are created
    optimizationError=[]

    if not all([os.path.exists(x) for x in fixedFilePaths]):
        
        maxAge = 95 if maxAge is None else maxAge
        
        # Fix the ageSexData
        fixedAgeSexData = [[ statePop[:-1] + 
                            sorted(getEstimatedList(statePop[2:], maxInputAge=len(statePop)-3, maxEstimatedAge=maxAge + 1, maxError=100),reverse=True) 
                            for statePop in cat[1:]] for i, cat in enumerate(ageSexData)]

        # Save the result to csv files
        for c in range(3):
            csv.writer(open(fixedFilePaths[c],   'w', newline='')).writerows(fixedAgeSexData[c])
    
            ## Plot the result and save the charts
            Y0 = [ sum([ x[i+2] for x in ageSexData[c][1:] ])  for i in range(86)]
            Y1 = [ sum([ x[i+2] for x in fixedAgeSexData[c]])  for i in range(maxAge+1)]
            errCount      = Y0[-1]-sum(Y1[85:])
            errPercentage =format(errCount/sum(Y0)*100, ".10f")
            print("total "+catlabels[c]+" error: ",  errCount, errPercentage) 
            optimizationError.append([errCount,errPercentage])
            fnm1 = os.path.join("datasets","usa","chart_usa-2020-states-age-sex-"+catlabels[c]+".png")
            fnm2 = os.path.join("datasets","usa","chart_usa-2020-states-age-sex-"+catlabels[c]+"_ext.png")
            MDcharts.plotData(Y0, figTitle=catlabels[c]+" Age Before", XticksLabelsLst=None, isPercentageOutput=None, doShow=0, chartFnmPath=fnm1)
            MDcharts.plotData(Y1, figTitle=catlabels[c]+" Age After, error count: "+str(errCount)+" error: "+errPercentage+"%", XticksLabelsLst=None, isPercentageOutput=None,  doShow=0, chartFnmPath=fnm2)
        
    else:
        # Read the file and return the data:
        print("Fixed: usaAgeSexData files exist: ", fixedFilePaths[0])
         
        fixedAgeSexData= [[ [int(x[0]), x[1]] +[int(y) for y in x[2:] ] for x in 
                              [row for row in 
                                       csv.reader(open(fixedFilePaths[c]), delimiter=",", quotechar='"')]] 
                                              for c in range(3)]
    return fixedAgeSexData

# Regroup into 7 groups
# Output should be 51 states x 7 age groups
def getGroupedAgeSexData(ageSexData=None, rdsAgeGroups=None, maxAge=None, usaAgeSexDataFilesPath=None, catlabels=None):     

    # First check if the files exist
    groupedFilePaths =  [x[:-4]+"_grp.csv" for x in usaAgeSexDataFilesPath]

    groupedAgeSexData =  []
    if not all([os.path.exists(x) for x in groupedFilePaths]):
       for c in range(3):  # for each catigory
            cStates= []
            for st in ageSexData[c]:  # For each state 
                cStAge = st[2:]
                cState = [st[0],st[1]]
                for i,lbl in enumerate(rdsAgeGroups): # for each age group
                    ageStart, ageEnd = MDutils.getAgeRangeFromAgeGroup(i, maxAge)
                    # print("a,b    : ", ageStart,ageEnd)
                    # find population of this age group
                    sumAgeGroup = 0
                    s = 0
                    for a, age in enumerate(cStAge): 
                        s += age
                        if (ageStart<= a) and (a<ageEnd):
                            # put in this age group
                            sumAgeGroup += age
                    cState = cState + [sumAgeGroup]
                cStates.append(cState)        
            groupedAgeSexData.append(cStates)
                
       ## Save the result to csv files
       statesIDs, statesSName, statesLName =  MDutils.getUSAstateNames()
       for c in range(3):
           csv.writer(open(groupedFilePaths[c], 'w', newline='')).writerows(groupedAgeSexData[c])
          
           # Population of each state
           Y = [ sum(groupedAgeSexData[c][s][2:]) for s in range(len(groupedAgeSexData[c])) ]
           fnm = os.path.join("datasets","usa","chart_usa-2020-states-age-sex-"+catlabels[c]+"_state.png")
           figTitle = catlabels[c]+" population per state"
           MDcharts.plotData(Y, figTitle=figTitle, XticksLabelsLst=statesSName, isPercentageOutput=None, doShow=0, chartFnmPath=fnm)
           print("------------------- Create Maps    -------------------------")        
           # Initialize an empty dictionary to store the counts of persons per state
           state_counts = {state: val for state, val in zip(statesLName,Y)}
           #print(state_counts)
           fnm = os.path.join("datasets","usa","chart_usa-2020-states-age-sex-"+catlabels[c]+"_state_map.png")
           cfg = { "shapefile_path": "datasets/usa/map/cb_2018_us_state_20m.shp",
                    "xylim": [-130, -60, 20, 55],
                    "fontsize": 6,
                    "figsize":(15,10),
                    "cmap":"magma",
                    "outputFnmPath": fnm,
                    "doSave":1,
                    "doShow":0,
                    "mapTitle": figTitle,
                    "mapName":"NAME",
                    "dataName":"state"
                }
           MDcharts.plotMap(state_counts, cfg)

           Y = [sum(groupedAgeSexData[c][s][g+2] for s in range(len(groupedAgeSexData[c]))) for g in range(len(groupedAgeSexData[c][0])-2)]
           print("Total age Groups Populations "+catlabels[c],Y)
           fnm = os.path.join("datasets","usa","chart_usa-2020-states-age-sex-"+catlabels[c]+"_grp.png")
           MDcharts.plotData(Y, figTitle=catlabels[c]+" Age grouped", XticksLabelsLst=rdsAgeGroups, isPercentageOutput=None, doShow=0, chartFnmPath=fnm)
    else:
        print("Grouped: usaAgeSexData files exist: ", groupedFilePaths[0])
        groupedAgeSexData = [ [ [int(x[0]), x[1]] +[int(y) for y in x[2:] ] for x in [row 
                                     for row in csv.reader(open(groupedFilePaths[c]), delimiter=",", quotechar='"')]]
                                                  for c in range(3)]
    return groupedAgeSexData

# Main function to prepare data by calling all necessary sub-functions
def getPreparedData(cfg, usaRaceDataPath, usaAgeSexDataFolderPath, usaAgeSexDataFilePath, usaAgeSexMaleDataFilePath, usaAgeSexFemaleDataFilePath, usaAgeSexTotalDataFilePath, catlabels):
    
    prepTimeStart = time.time()
    maxAge          = cfg["maxAge"]["max-age-value"]

    ## rdAgeGroupsLst  = [  "<5"   ,"5-14"  ,"15-19"  ,"20-24"  ,"25-39"  ,"40-60"  ,">60"]
    rdAgeGroupsLst    = cfg["rdAgeGroupsLst"]
    
    ## get race data and use labels from config file
    raceData        = getRaceData(cfg, usaRaceDataPath)

    ## collect data from all files into one file 
    ageSexData      = getAgeSexData(usaAgeSexDataFolderPath, usaAgeSexDataFilePath, usaAgeSexMaleDataFilePath, usaAgeSexFemaleDataFilePath, usaAgeSexTotalDataFilePath)

    usaAgeSexDataFilesPath = [usaAgeSexMaleDataFilePath,usaAgeSexFemaleDataFilePath,usaAgeSexTotalDataFilePath]

    ## add missing ages 85:maxAge 
    fixedAgeSexData = getFixAgeSexData(ageSexData, maxAge=maxAge, usaAgeSexDataFilesPath=usaAgeSexDataFilesPath, catlabels=catlabels)

    groupedAgeSexData = getGroupedAgeSexData(fixedAgeSexData,rdAgeGroupsLst, maxAge=maxAge, usaAgeSexDataFilesPath=usaAgeSexDataFilesPath, catlabels=catlabels)
    
    prepTimeEnd = time.time() - prepTimeStart
    print("Prepared data took ", prepTimeEnd, " seconds") 

# If this script called directly
if __name__ == "__main__":
    # testing 
    if len(sys.argv) > 1:
       print("input: ", sys.argv)
