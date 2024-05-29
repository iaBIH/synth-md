##=======================================================================================
#                 Evaluate the results
# Compare the statistics of the output synthetic dataset to the input statistics 
##=======================================================================================

import sys, os, time, re
import numpy as np
from fractions import Fraction as frac
from synthMD import MDutils, MDcharts  

#----------------- Printing with exception handling ----------------------
def tryPrint(txt, L, dx, vs=None, roundPlaces=None):
    logLine = ""
    roundPlaces = 2 if roundPlaces is None else roundPlaces
    try:
       x1 = round((len(L)/dx)*100,5)
       logLine =txt + " : " + str(f"{ str(x1):<10}  vs  {str(vs)} \n")
    except Exception as e:
       logLine= str(e)+"\n"  
    
    print(logLine)       
    return logLine

## ------------------------------------- getAgeGroupsEvaluation -------------------------------------  
def getRaceSexEvaluation(i, RDnamesLst, outputData, totalNumberOfPatients, sexWeights, raceWeights, raceNamesLst, clinicalParsLst, 
                            agePopulationsStatesAll, processingTime, logLines):
    
    roundPlaces = 2
    # Extracting age group populations for all states
    # For all states for all 7 age groups 
    # Size: 51 x 7
    agePopulations = agePopulationsStatesAll[2]
    totalUSA = sum([sum(s) for s in agePopulations])

    logLine = "=========================( "+ RDnamesLst[i] +" )========================\n"
    logLines.append(logLine)
    print(logLine)

    # Logging processing time
    logLine = " processing time in seconds: " +str(processingTime)+" \n"
    logLines.append(logLine)
    print(logLine)

    # Logging total USA population
    logLine = "USA population: "+ str(totalUSA) +"\n"
    logLines.append(logLine)
    print(logLine)
    pAll = len(outputData) -1
                                
    ## ----------------------------- total number of patients 
    # Logging total number of patients (result vs expected)
    logLine = "Total patients: result vs expected: "+ str(pAll) + " , "+ str(totalNumberOfPatients) +"\n"
    logLines.append(logLine )
    print(logLine)

    ## ----------------------------- Sex and Race Ratios
    # Logging ratios of sex and race
    logLine = "----------- Ratios: sex, AA, EA, OA, Death \n"
    logLines.append(logLine )
    print(logLine)
    #            0       1       2              3        4      5      6            7          8
    # pData = [pCount, pAge, usStateNames[s] ,pZipCode, pSex, pRace, pBirthDate, pDiagDate, pDeathDate]
    # Number of female and male patients in the dataset
    numF = ([x for x in outputData[1:] if x[4]=='f'])
    numM = ([x for x in outputData[1:] if x[4]=='m'])

    logLine = "number of male patients  : "+ str(len(numM)) +"\n"
    logLines.append(logLine )
    print(logLine)

    logLine = "number of female patients: "+ str(len(numF)) +"\n"
    logLines.append(logLine )
    print(logLine)

    # Logging female ratio
    logLine = tryPrint("Female ratio  : ", numF , pAll, sexWeights[i]                , roundPlaces )
    logLines.append(logLine )

    # Logging African American ratio
    logLine = tryPrint("AA ratio      : ", [x for x in outputData[1:] if x[5]==raceNamesLst[0]], pAll, raceWeights[i][0], roundPlaces )
    logLines.append(logLine )

    # Logging European American ratio
    logLine = tryPrint("AE ratio      : ", [x for x in outputData[1:] if x[5]==raceNamesLst[1]], pAll, raceWeights[i][1], roundPlaces )
    logLines.append(logLine )

    # Logging Other American ratio
    logLine = tryPrint("AO ratio      : ", [x for x in outputData[1:] if x[5]==raceNamesLst[2]], pAll, raceWeights[i][2], roundPlaces )
    logLines.append(logLine )

    ## ----------------------------- Clinical Parameters Ratios
    pCP1 = [x[9] for x in outputData[1:]]
    try:
        logLine = "ClinicalPar1 Mean STD: "+ str(round(np.mean(pCP1),2)) + "\t" + str(round(np.std(pCP1),2))+ "\n"
        logLines.append(logLine )
        print(logLine)
        logLine = "ClinicalPar1 Min Max : "+str(round(np.min(pCP1),2))+ "\t"+ str(round(np.max(pCP1),2))+"\t vs \t" +str(clinicalParsLst[i][0][2])+"\t"+str(clinicalParsLst[i][0][3])+ "\n"
        logLines.append(logLine )
        print(logLine)
    except Exception as e:
        print(e)

    # If a second clinical parameter is present, evaluate it as well
    if len(outputData[0])==11:
        pCP2= [x[10] for x in outputData[1:]]
        try:
            logLine = "ClinicalPar2 Mean STD: " + str(round(np.mean(pCP2),2)) + "\t" + str(round(np.std(pCP2),2)) + "\n"
            logLines.append(logLine )
            print(logLine)
            logLine = "ClinicalPar2 Min Max : " + str(round(np.min(pCP2),2)) + "\t" + str(round(np.max(pCP2),2)) +"\t vs \t" + str(clinicalParsLst[i][1][2])+"\t"+str(clinicalParsLst[i][1][3]) + "\n"
            logLines.append(logLine )
            print(logLine)
        except Exception as e:
            print(e)

    return logLines

def getAgeGroupsEvaluation(i, outputData, agePopulationsStatesAll, pAll,totalUSA, rdAgeGroupsLst,roundPlaces,  logLines):
   
    mAgePopulations, fAgePopulations, agePopulations = agePopulationsStatesAll

    # Summing up the age group populations
    logLine = " Age group percentages:------------ \n"
    logLines.append(logLine )
    print(logLine)
    agePopulationsSum  = [ sum(s)for s in zip(*agePopulations)]
    for k in range(len(rdAgeGroupsLst)):

        # Number of patients in age group k
        L = [x for x in outputData[1:] if MDutils.getAgeGroupIndex(x[1])==k ]
        logLine = tryPrint(" Age groups  "+rdAgeGroupsLst[k]+"\t" , L , pAll, round((agePopulationsSum[k]/totalUSA)*100, roundPlaces) , roundPlaces )
        logLines.append(logLine )

    # Summing up the female age group populations
    logLine = " Age groups Female:------------ \n"
    logLines.append(logLine )
    print(logLine)    
    agePopulationsFSum = [ sum(s)for s in zip(*fAgePopulations)]
    for k in range(len(rdAgeGroupsLst)):

        # Number of female patients in age group k
        L = [x for x in outputData[1:] if MDutils.getAgeGroupIndex(x[1])==k and x[4]=='f']        
        logLine = tryPrint(" Age groups  "+rdAgeGroupsLst[k]+"\t" , L , pAll, round((agePopulationsFSum[k]/totalUSA)*100, roundPlaces) , roundPlaces )
        logLines.append(logLine )

    # Summing up the male age group populations
    logLine = " Age groups Male  :------------ \n"
    logLines.append(logLine )
    print(logLine)    
    agePopulationsMSum = [ sum(s)for s in zip(*mAgePopulations)]
    for k in range(len(rdAgeGroupsLst)):

        # Number of male patients in age group k
        L = [x for x in outputData[1:] if MDutils.getAgeGroupIndex(x[1])==k and x[4]=='m']        
        logLine = tryPrint(" Age groups  "+rdAgeGroupsLst[k]+"\t" , L , pAll, round((agePopulationsMSum[k]/totalUSA)*100, roundPlaces) , roundPlaces )
        logLines.append(logLine )
    
    return logLines, agePopulationsSum

def getDeathGroupsEvaluation(i, outputData, deathRates, statePatientsDeads, statePatientsAlives, rdAgeGroupsLst,agePopulationsSum, logLines):
    print(" Age groups Deaths: ")

    # Summing up the dead and alive patients per state and age group
    # NumberOfPatientsAges 51 x 7
    # Print(fix dead patients number vs ground truth and check for other diseases)
    statePatientsDeadsSum  = [sum(s) for s in zip(*statePatientsDeads) ]
    statePatientsAlivesSum = [sum(s) for s in zip(*statePatientsAlives)]

    sumPatients   = 0
    sumDead       = 0
    sumPrevalence = 0
    sumDeathRate  = 0

    logLine = "age 	 population pat	  dead 	 expected 	 rate  rateGT     prevalence prevalenceGT  \n"
    logLines.append(logLine)
    print(logLine)

    for k in range(len(rdAgeGroupsLst)):
        # Total population of age group k
        groupPopulation                = agePopulationsSum[k]
        numberOfPatientsPerGroup       = len([x for x in outputData[1:] if MDutils.getAgeGroupIndex(x[1])==k ])

        # Number of dead patients in age group k
        numberOfPatientsPerGroupDead = len([x for x in outputData[1:] if MDutils.getAgeGroupIndex(x[1]) == k and x[8] not in (None, 0)])

        # Expected number of dead patients based on ground truth data
        numAgeDeadPtGT   =  int(statePatientsDeadsSum[k])
        
        # Calculating death rate and prevalence 
        deathRate = f'{(numberOfPatientsPerGroupDead / numberOfPatientsPerGroup)*100:.5f}'
        deathRateGT = f'{deathRates[i][k]:.7f}'
        prevalence = f'{numberOfPatientsPerGroup / groupPopulation:.8f}'
        prevalenceGT = f'{numberOfPatientsPerGroup / groupPopulation:.8f}'

        sumPatients  = sumPatients    + numberOfPatientsPerGroup
        sumDead       = sumDead       + numberOfPatientsPerGroupDead
        sumPrevalence = sumPrevalence + numberOfPatientsPerGroup / groupPopulation
        sumDeathRate  = sumDeathRate  + numberOfPatientsPerGroupDead / numberOfPatientsPerGroup
        try:
            logLine =            str(rdAgeGroupsLst[k]) + ":\t  "+str(f" {str(groupPopulation):<6} {str(numberOfPatientsPerGroup):<6}  {str(numberOfPatientsPerGroupDead):<6} ")
            logLine = logLine +  str( f"{str(numAgeDeadPtGT):<6} {str(deathRate):<6}  {str(deathRateGT):<6} {str(prevalence):<6} {str(prevalenceGT):<6}   \n")
            logLines.append(logLine)
            print(logLine)
        except Exception as e:
            print(e)

    return logLines, sumPatients, sumDead, sumPrevalence, sumDeathRate    
## ------------------------------------- getAgeGroupsEvaluation -------------------------------------  
# Evaluates the distribution of age groups and deaths in the synthetic dataset.
def getGroupsEvaluation(i, outputData, deathRates, agePopulationsStatesAll, numberOfPatientsAges, rdAgeGroupsLst, logLines):

    pAll = len(outputData) -1
    totalUSA = sum([sum(s) for s in agePopulationsStatesAll[2]])
    roundPlaces = 2
    statePatientsDeads   =  [ [ round((x/100.0) * y) for x,y in zip(deathRates[i], numberOfPatientsAges[s])] for s in range((51)) ]

    statePatientsAlives  =  [ [ x-y for x,y in zip(numberOfPatientsAges[s], statePatientsDeads[s]) ] for s in range((51)) ]

    logLines, agePopulationsSum =  getAgeGroupsEvaluation(i, outputData, agePopulationsStatesAll, pAll,totalUSA, rdAgeGroupsLst,roundPlaces,  logLines)

    logLines, sumPatients, sumDead, sumPrevalence, sumDeathRate =getDeathGroupsEvaluation (i, outputData, deathRates, statePatientsDeads, statePatientsAlives, rdAgeGroupsLst,agePopulationsSum, logLines)

    return logLines, sumPatients, sumPrevalence, sumDead, sumDeathRate

def getDeathEvaluation(i, outputData, deathRates, numberOfPatientsAges, rdAgeGroupsLst, sumPatients, sumPrevalence, sumDead, sumDeathRate, logLines):    
# Evaluates the death rates in the synthetic dataset compared to the expected values.
    
    # Number of dead patients in the results 
    numDeathResult = 0
    try:
        ## note, if it is processed, it will be zero instead of None
        numDeathResult = len([x for x in outputData[1:] if x[8] not in (None, 0)])
    except Exception as e:
        print("Error numDeathResult:  ", e)
        numDeathResult = 0
    
    # Calculating the expected number of dead patients 
    # Number of dead and alive patients per state
    # Dead patients  = deathRates * numer of patients in the state 
    statePatientsDeads   =  [ [ round((x/100.0) * y) for x,y in zip(deathRates[i], numberOfPatientsAges[s])] for s in range((51)) ]
    print("statePatientsDeads : ", statePatientsDeads)
    print()
    print("deathRates         : ", deathRates[i])
    try:
        totalNumberOfPatientsDead   = sum([sum(x) for x in statePatientsDeads])
        print("Death cases       : ",numDeathResult ,"\t vs ", totalNumberOfPatientsDead)       
        logLine = "Death cases       : " + str(numDeathResult) +"\t vs " + str(totalNumberOfPatientsDead) + "\n"
        logLines.append(logLine )
        print(logLine)
    except Exception as e:
        print("Error numDeath     : ", e)

    logLine = "Total : ................................. \n"
    logLines.append(logLine)
    print(logLine)

    logLine = "total Patients : " + str(sumPatients) + "\n"
    logLines.append(logLine)
    print(logLine)

    logLine = "prevalence     : " + str(sumPrevalence) + "\t" + str(frac(sumPrevalence).limit_denominator()) +  "\n"
    logLines.append(logLine)
    print(logLine)

    logLine = "total dead     : " + str(sumDead) + "\n"
    logLines.append(logLine)
    print(logLine)

    sumDeathRate  = sumDeathRate   / len(rdAgeGroupsLst)
    logLine = "death rate     : " + str(sumDeathRate) + "\t" + str(frac(sumDeathRate).limit_denominator()) +  "\n"
    logLines.append(logLine)
    print(logLine)
    print("sumPrevalence : ", frac(sumPrevalence).limit_denominator())
    print("sumDeathRate  : ", frac(sumDeathRate).limit_denominator())
    return logLines

#----------- Evaluation  ------------------
# Performs the full evaluation of the synthetic dataset
# Print statistics about results 
def getEvaluation(i, RDnamesLst, rd_datasset_size, outputData, totalNumberOfPatients, sexWeights, raceWeights, raceNamesLst, clinicalParsLst, deathRates,
                      agePopulationsStatesAll, numberOfPatientsAges, processingTime, rdAgeGroupsLst, sexlabels, raceLabels, resultFilePath, doSave=None, doPlot=None):
       
        doSave = 1 if doSave is None else doSave
        doPlot = 1 if doPlot is None else doPlot
    
        logLines = []

        # Get total staistics  
        logLines =  getRaceSexEvaluation(i, RDnamesLst, outputData, totalNumberOfPatients, sexWeights, raceWeights, raceNamesLst, clinicalParsLst,  
                            agePopulationsStatesAll, processingTime, logLines)
        
        logLines, sumPatients, sumPrevalence, sumDead, sumDeathRate = getGroupsEvaluation(i, outputData, deathRates, agePopulationsStatesAll, numberOfPatientsAges, rdAgeGroupsLst, logLines)

        # Get death statistics
        logLines = getDeathEvaluation(i, outputData, deathRates, numberOfPatientsAges, rdAgeGroupsLst, sumPatients, sumPrevalence, sumDead, sumDeathRate, logLines)

        # Saving the results
        if doSave:
            #------------------------------------------------
            print("Saving results log  ...................")
            #------------------------------------------------
            resultsRDpath = os.path.dirname(resultFilePath)
            logFilePath                   = os.path.join(resultsRDpath,"log_"+RDnamesLst[i]+"_"+str(rd_datasset_size)+".txt")
            print("logFilePath : ", logFilePath)
            with open(logFilePath, 'w') as fp:
                for x in logLines:
                    fp.write(x)  
            fp.close() 

        # Plotting the results
        if doPlot:
           MDcharts.plotRareDiseaseData(resultFilePath, sexlabels, raceLabels)

def getAllEvaluation(cfgPath):
# Performs the full evaluation for all rare diseases based on the configuration files
    
    cfg, RDsData, raceData, usaAgeSexData, usaAgeSexGroupData, paths = MDutils.readInputFiles(cfgPath)

    usaAgeSexDataFilesPath, resultsFolderPath= paths

    RDnamesLst        = [x["name"]          for x in RDsData]
    RDFileNamesLst    = [x["short_name"]    for x in RDsData]
    rd_datasset_size  = cfg["rd_datasset_size"]["rd_dataset_size_value"]

    raceWeights, total_USA_Population_From_Race, prevalenceRaceLst, racePopulations, racePopulationsSt  = MDutils.getRaceData(raceData, RDsData) 
   
    clinicalParsLst = [[ [ val for val in cp.values()]  for cp in rd['clinical_parameters'] ] for rd in RDsData]
    sexWeights      = [x[1] for x in [list(rd['sex_percentage'].values()) for rd in RDsData]]
    rdAgeGroupsLst  = list(cfg["rdAgeGroupsLst"])
    usaNames        = MDutils.getUSAstateNames()
    sexlabels       = list(cfg["sexLabels"])
    raceLabels      = list(cfg["raceLabels"])
    raceNamesLst    = [x.split(",")[0] for x in list(RDsData[0]["race_percentage"]["races"].keys())]
    deathStatistics = [list(rd['death_percentage']["rates"].values()) for rd in RDsData]
    deathRates      = deathStatistics

    for i, rd in enumerate(RDnamesLst):
        startRdTm = time.time()

        resultsRDpath= os.path.join(resultsFolderPath,rd)
        print(resultsRDpath)
        if not os.path.exists(resultsRDpath):
          os.mkdir(resultsRDpath)  
   
        fnm = [ x for x in os.listdir(resultsRDpath) if "_all_" in x][0]
        resultFilePath = os.path.join(resultsRDpath,fnm,RDFileNamesLst[i]+"_"+ fnm+".csv")

        # Read the result file and get its statistics
        maxUSAAge, dataLabels, rdFinalData =  MDutils.readingCSVdata(resultFilePath, 0)

        totalNumberOfPatients   = round(sum([ (x *  y) for x,y in zip(prevalenceRaceLst[i], racePopulations)]))  
        numberOfPatientsStatesRace    = [ int(sum([(x *  y) for x,y in zip(prevalenceRaceLst[i], racePopulation)]))  for racePopulation in racePopulationsSt ]
        numberOfPatientsStatesResized = [  x for x in numberOfPatientsStatesRace]
      

        numberOfPatientsStatesFinal   = numberOfPatientsStatesResized   if rd_datasset_size > 0 else numberOfPatientsStatesRace  
        numberOfPatientsForAgeGroups  = [ [ round(x/sum(usaAgeSexGroupData[2][k]) * numberOfPatientsStatesFinal[k]) for x in usaAgeSexGroupData[2][k]] for k in range(len(usaNames[1]))]

        enddRdTm = time.time()-startRdTm

        getEvaluation(i, RDFileNamesLst, rd_datasset_size, rdFinalData, totalNumberOfPatients, sexWeights, raceWeights, raceNamesLst, 
                                       clinicalParsLst, deathRates, usaAgeSexGroupData, numberOfPatientsForAgeGroups,enddRdTm, 
                                       rdAgeGroupsLst,sexlabels,raceLabels, resultFilePath, doSave=1, doPlot=1)
        

def parse_file(file_name):
# Parses the evaluation results file and extracts key metrics
    data = {}
    with open(file_name, 'r') as f:
        lines = f.readlines()
        cp = 1
        data['ClinicalPars'] = []
        for line in lines:
            # -------------- General Info ---------------------------    
            if 'USA population' in line:
                data['USA population'] = re.findall(r'\d+', line)[0]
            elif 'number of male patients' in line:
                data['number of male patients'] = re.findall(r'\d+', line)[0]
            elif 'number of female patients' in line:
                data['number of female patients'] = re.findall(r'\d+', line)[0]
            elif 'prevalence' in line and not 'prevalenceGT' in line:
                data['prevalence'] = re.findall(r'[\d.]+', line)[0]
                data['prevalence fractions'] = re.findall(r'\d+/\d+', line)[0]
            elif 'total dead' in line :                
                data['total dead'] = re.findall(r'\d+', line)[0]
            elif 'death rate' in line:
                data['death rate'] =line.split(':')[1:]
            # -------------- Result vs Expected ---------------------------    
            elif 'Total patients' in line:
                data['Total patients'] = re.findall(r'\d+', line)
            elif 'Death cases' in line:
                data['Death cases'] = re.findall(r'\d+', line)
            elif 'Female ratio' in line:
                data['Female ratio'] = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            elif 'AA ratio' in line:
                data['AA ratio'] =  re.findall(r"[-+]?\d*\.\d+|\d+", line)
            elif 'AE ratio' in line:
                data['AE ratio'] =  re.findall(r"[-+]?\d*\.\d+|\d+", line)
            elif 'AO ratio' in line:
                data['AO ratio'] =  re.findall(r"[-+]?\d*\.\d+|\d+", line)
            elif 'ClinicalPar' in line and not 'Mean' in line:
                vals = line.split(":")[1].split()
                cpMin= str(float(vals[0]))+' , '+str(float(vals[3]))
                cpMax= str(float(vals[1]))+' , '+str(float(vals[4]))
                data['ClinicalPars'].append([cpMin,cpMax])
                cp =cp + 1
        # ---------------- Age Groups: Total, Male, Female--------------------------  
        # Extract age group data
        for l in range(len(lines)):
            if 'Age groups' in lines[l]:
                break 
        for i in ["Total ", "Female ","Male "]:
            for j in ["<5","5-14","15-19","20-24","25-39","40-60",">60"]:
                vals = lines[l].split(":")[1].split("vs") 
                txt = str(float(vals[0]))+' , '+str(float(vals[1]))  
                data[i + j] = txt
                l = l +1 
            l=l+1 
        # -------------- Age Groups: Death Info----------------------------  
        # Extract age group death data
        for l in range(len(lines)):
           if 'age' in lines[l] and 'population' in lines[l]:            
            break 
        l = l + 1
        for j in ["<5","5-14","15-19","20-24","25-39","40-60",">60"]:
            txt = [str(float(x)) for x in lines[l].split(":")[1].split() ]
            data["death " + j] = txt
            l = l + 1
    return data

def write_comparison(RDNames,filesData, output_file):
# Writes a comparison of the evaluation results into an output file and generates LaTeX tables
    
    latexTables = []
    
    with open(output_file, 'w') as f:
        # Iterate through each rare disease results  
        tblCaption = "Summary of Patient Data"
        tblLabel = "table:tbl01"
        tblFormat = "|c|c|c|c|c|c|"
        tblHeadTxt = "Number of Patients, Male , Female , Total , Prevalence (Fractions) , Total Dead"
        tblHead = [tblHeadTxt]
        tblRows = [] 

        txt = " --------------"+tblCaption +"---------------------------"    
        f.write(txt+"\n")
        print(txt)
        for i in range(len(filesData)): 
            txt = f"{RDNames[i]} USA population: {filesData[i]['USA population']}"
            print(txt)
            f.write(txt+"\n")
        f.write(tblHeadTxt+"\n")
        print(tblHeadTxt)
        for i in range(len(filesData)): 
            txt = f"{RDNames[i]} number of patients  : {filesData[i]['number of male patients']}, {filesData[i]['number of female patients']}, \
                    {int(filesData[i]['number of male patients']) + int(filesData[i]['number of female patients'])}, {filesData[i]['prevalence']}\
                     ({filesData[i]['prevalence fractions']}), {filesData[i]['total dead']}"
            tblRows.append([txt])
            # txt = txt[:-1]
            print(txt)
            f.write(txt+"\n")  
        
        txtTable = [ tblHead ]
        for row in tblRows:
            txtTable.append(row)

        latexTables.append(getLatexTable(txtTable, tblCaption, tblLabel , tblFormat))

        # Write age group data for total, male, and female
        tblCaption = "Result vs Expected for SCD, CF, and DMD"
        txt = " --------------"+tblCaption +"---------------------------"    
        print(txt)

        tblLabel = "table:tbl02"
        tblFormat = "p{2.9cm}|d{1} d{1}|d{1} d{1}|d{1} d{2}|"
        tblHeadTxt1 = r", \multicolumn{2}{c}{SCD} , \multicolumn{2}{|c}{CF} , \multicolumn{2}{|c|}{DMD}"
        tblHeadTxt2 = r", Result , Expected , Result , Expected , Result , Expected"
                 
        tblHead1 = [tblHeadTxt1]
        tblHead2 = [tblHeadTxt2]
        tblRows = [] 

        f.write(txt+"\n")
        print(tblHeadTxt1)
        f.write(tblHeadTxt1+"\n")
        print(tblHeadTxt2)
        f.write(tblHeadTxt2+"\n")
        tmpHeadLst = ['Total patients', 'Death cases', 'Female \%', 'African American \%','European American \%','Other American \%']
        for k,par in enumerate(['Total patients', 'Death cases', 'Female ratio', 'AA ratio','AE ratio','AO ratio']):
            txt = tmpHeadLst[k]+" : " ; t= ""
            for i in range(len(filesData)): 
                t  = t + ' , '.join(filesData[i][par]) + " , "
            txt = txt + t[:-2]
            print(txt)
            f.write(txt+"\n") 
            tblRows.append([txt])

        txtTable = [ tblHead1, tblHead2]
        for row in tblRows:
            txtTable.append(row)

        latexTables.append(getLatexTable(txtTable, tblCaption, tblLabel , tblFormat))

        # Write age group death information
        txt =" ---------------- Age Groups: Total, Male, Female--------------------------"
        print(txt)
        f.write(txt+"\n")
        txt = "Sex, Age group," + ", ".join([f"{name} result, {name} expected" for name in RDNames])
        print(txt)
        f.write(txt+"\n")
        for j in ["Total ", "Female ","Male "]:
            for k in ["<5","5-14","15-19","20-24","25-39","40-60",">60"]:
                txt = j+k+" : "
                t = ""
                for i in range(len(filesData)): 
                    t = t + filesData[i][j+k] +" , "                    
                txt = txt + t[:-2]     
                print(txt)
                f.write(txt+"\n")

        tblCaption = "Clinical Parameters: Result vs Expected"
        txt = " --------------"+tblCaption +"---------------------------"    
        print(txt)

        tblLabel = "table:tbl03"
        tblFormat = "lccr"
        tblHeadTxt = "Disease, Parameter , Result, Expected"
        tblHead = [tblHeadTxt]
        tblRows = [] 

        parNames = [["CBC (g/dL)", r"RC(\%)"], ["CH (mmol/L)"],  ["CK (unit/L)"]]

        f.write(txt+"\n")
        for i in range(len(filesData)):
           for j,cp in enumerate(filesData[i]['ClinicalPars']):
               txt =(RDNames[i]).upper()  +' , ' + parNames[i][j] + ' Min :' + cp[0] 
               print(txt)
               f.write(txt+"\n")
               tblRows.append([txt])
               txt = (RDNames[i]).upper() +' , ' + parNames[i][j] + ' Max :' + cp[1] 
               print(txt)
               f.write(txt+"\n")
               tblRows.append([txt])

        txtTable = [tblHead]
        for row in tblRows:
            txtTable.append(row)

        latexTables.append(getLatexTable(txtTable, tblCaption, tblLabel , tblFormat))

        txt =" ---------------- Age Groups: Death Info --------------------------"
        print(txt)
        f.write(txt+"\n")
        tblHead = ["Age Group ,Population , Patients , Death Result ,Death Expected , Death Rate Result , Death Rate , Prevalence Result , Prevalence"]

        for i in range(len(filesData)): 
            tblCaption = RDNames[i].upper() + " Death Information"
            txt = " --------------"+tblCaption +"---------------------------"    
            print(txt)
            f.write(txt+"\n")
            tblLabel = "table:tbl0"+str(i+4)
            tblFormat = "|p{0.8cm}|p{1.3cm}|p{1cm}|p{1cm}|p{1cm}|p{1cm}|p{1cm}|p{1.1cm}|p{1.1cm}|"
            tblRows = [] 
            txt = "Age Group , Population , Patients , Res. Death , Exp Death, Res. Death Rate , Exp. Death Rate , Res. Prevalence , Exp. Prevalence"
            tblHead = [txt]
            print(txt)
            f.write(txt+"\n")
            for k in ["<5","5-14","15-19","20-24","25-39","40-60",">60"]:
                t = str(filesData[i]["death " + k]).replace("'","").replace("[","").replace("]","") 
                t = t.split(",") 
                t = [ int(float(t[0])),int(float(t[1])),int(float(t[2])),int(float(t[3])),float(t[4]),float(t[5]),float(t[6]),float(t[7])]                  
                t = [str(x) for x in t ]
                # join the formatted numbers back into a single string
                t = ', '.join([f"{int(num):,}" if '.' not in num else f"{float(num):,.2f}" 
                               if int(float(num)) != 0 else f"{float(num):,.6f}".rstrip('0').rstrip('.')
                                 if len(num.split('.')[1]) > 2 else f"{float(num):,}" for num in t])

                txt = " " + k  +" , " + t
                print(txt)
                f.write(txt+"\n")   
                k = r"\textless{}5 "     if "<" in k else k
                k = r"\textgreater{}60 " if ">" in k else k
                txt = " " + k  +" , " + t
                tblRows.append([txt])
            txtTable = [tblHead]
            for row in tblRows:
                txtTable.append(row)

            latexTables.append(getLatexTable(txtTable, tblCaption, tblLabel , tblFormat))

    f.close()

    return latexTables

# Generates a LaTeX table from the given data.
def getLatexTable(txtTable, tblCaption, tblLabel , tblFormat):
    hLine = r"\hline"
    
    latexTable = []
    latexTable.append(r"\begin{table}[h!]")
    latexTable.append(r"\centering")
    latexTable.append(r"\hline")
    latexTable.append(r"\begin{tabular}{"+ tblFormat +"}")
    for row in txtTable:
        line = row[0].replace(', ', ' & ').replace(':','&') + " \\\\"
        latexTable.append(line)
        latexTable.append(r"\hline")
    latexTable.append(r"\end{tabular}")
    latexTable.append(hLine)
    latexTable.append(r"\caption{"+ tblCaption+ "}")
    latexTable.append(r"\label{" + tblLabel + "}")
    latexTable.append(r"\end{table}")
    return latexTable

# Writes the LaTeX tables to the output file
def writeLatexTables(latexTables, outputPath):
    print("writing latex tables ........")
    # Check if file exists
    if not os.path.exists(outputPath):
        print("create new file:", outputPath)
        # If it doesn't exist, create it by opening it in write mode
        with open(outputPath, 'w') as f:
            pass

    # Open the file in append mode ('a') and write some text to it
    with open(outputPath, 'a') as f:
         print("file exist, add at the end of the file: ", outputPath)
         for tbl in latexTables:
             for line in tbl:
                 f.write(line + "\n")
    f.close()

# Collects results from all evaluation files and writes a summary.
def getAllSummeryEvaluation(RDNames, resultPaths, outputPath):
    print("collecting results from all result files in : ", resultPaths)
    filesData =  [parse_file(file_name) for file_name in resultPaths]
    latexTables = write_comparison(RDNames,filesData, outputPath)
    writeLatexTables(latexTables, outputPath)


# Main script execution
if __name__ == "__main__":
    # testing 
    if len(sys.argv) > 1:
       print("input: ", sys.argv)
