##=======================================================================================
#                 Create Synthetic data set
##=======================================================================================
import os, sys, csv, time, datetime, random
import numpy as np
# for zip codes
from pyzipcode import ZipCodeDatabase
zcdb = ZipCodeDatabase()
from synthMD import MDevaluate, MDutils

# -------------------- generateGroupPatientsgData---------------------
def getStateGroupPatients(patentsCount, ageDist, sexDist, rdAgeGroupsLst,deathRateAgeDists, stateZips,raceDist,ageDiagDist,parData,
                              addTimeToDates, usaNames, s ):
        
        usaIDs,  usaStateShortNames, usaStateLongNames  = usaNames
        groupPatientsData=[]
        for g, ag in enumerate(rdAgeGroupsLst):                       
            # get age group distribution and shuffle it 
            # instead of random sampling we will pick element each time 

            gDist = ageDist[g] if s is None else ageDist[s][g]
            random.shuffle(gDist)

            # get death distribution of this age group 
            ageDeadDist  = deathRateAgeDists[g]               
             
            # reset patients counter 
            p = 0
            for p in range(len(gDist)):
                
                # the patient should be distributed based on race, and gender statistics 
                               
                pState    = usaStateShortNames[random.randint(0,50)] if  s is None  else s
             
                pSex      = random.choice(sexDist[g])  #  if  s is None  else random.choice(sexDist[s])          

                # select sex randomlly based on the rare disease weight and the population of this age group
                patentsCount = patentsCount + 1

                #  get random age from current age group  
                pAge      = gDist.pop() 
                         
                pZipCode = random.choice(stateZips)
                        
                pRace = random.choice(raceDist) 

                # generate random birthdate based on age
                pBirthDate = datetime.date(2023,1,1) + datetime.timedelta(days=-pAge*365)

                #  generate random diagonsis date based on the birthdate and the disease
                ageDiagFactor = round(random.choice(ageDiagDist))
                pDiagDate     = pBirthDate + datetime.timedelta(days=ageDiagFactor)

                # get death date if patient is dead, the age and death rate decide the death status
                pDeathDate = None

               # check if the patient is alive or not            
                isAlive  = random.choice(ageDeadDist) 

                # check the gender 
                if not isAlive:  
                    pBirthDate, pDiagDate, pDeathDate = MDutils.getDeathDate(pAge, pBirthDate, pDiagDate, ageDiagFactor, addTimeToDates)            
                elif addTimeToDates:
                    pBirthDate =  MDutils.getRandomTime(pBirthDate)
                    pDiagDate  =  MDutils.getRandomTime(pDiagDate)  
                else:
                    pBirthDate = str(pBirthDate)
                    pBirthDate = pBirthDate[:10]  if len( pBirthDate)>10 else pBirthDate                           
                    pDiagDate  = str(pDiagDate)  
                
                # TODO:  fix a bug of time is added 
                # generate clinical parameters based on the disease
                pParData = [round(random.choice(x),3) for x in parData]                              

                # create a patient data row
                pData = [patentsCount, pAge, usaStateLongNames[pState] ,pZipCode, pSex, pRace, pBirthDate, pDiagDate, pDeathDate]
                pData.extend(pParData)

                # get next patient for this age group  
                p = p + 1

                groupPatientsData.append(pData)

        return patentsCount, groupPatientsData


def getStatePatients(i,s,st, usaAgeSexGroupData, patentsCount, deathRates,numberOfPatientsForAgeGroups, sexWeight, rdSexWeight, rdAgeGroupsLst,
                     stateAgeDistLst, ageDiagDist, raceDist, parData, addTimeToDates, usaNames, raceNamesLst, raceWeights, sexlabels):
            """
            Get all aptients for a state st. This function calls generateGroupPatientsData which generates 
            patients for each age group for current state. 
            """

            ## Get all zip codes for this state
            stateZips    = [z.zip for z in zcdb.find_zip(state=st)]; stateZips = [z.zfill(5) for z in stateZips]

            # sex weight from age group population
            # femaleCount / femaleCount+maleCount
            sexWeightAges   = [round(( usaAgeSexGroupData[1][s][g]/( usaAgeSexGroupData[1][s][g]+ usaAgeSexGroupData[0][s][g]))*100) for g in range(len(rdAgeGroupsLst))]
            totalSexWeight  = [int(round( sexWeight * rdSexWeight + sexWeightAges[g]  * (1-rdSexWeight) )) for g in range(len(rdAgeGroupsLst))]
            # create sex distribution for this age group of this state 
            sexDist = [MDutils.getGroupDistriution(['f','m'], [totalSexWeight[g], 100-totalSexWeight[g]]) for g in range(len(rdAgeGroupsLst))]
            
            deathRateAgeDists  = MDutils.getStatesDeathRateDists(s, deathRates[i], numberOfPatientsForAgeGroups[s])  
            
            # --------------- Get all patirnts for each age group of the current state 
            patentsCount, pData = getStateGroupPatients(patentsCount, stateAgeDistLst, sexDist, rdAgeGroupsLst,deathRateAgeDists, 
                                                        stateZips, raceDist, ageDiagDist,parData,addTimeToDates, usaNames=usaNames,  s = s )
            
            return   patentsCount, pData

def createSyntheticDatasets(cfg, RDsData, raceData, usaAgeSexData, usaAgeSexGroupData, paths, doEvaluation=None):
   """
   Create synthetic datasets for each rare disease in the input RDsData.
   """

   doEvaluation = 1 if doEvaluation is None else doEvaluation

   usaAgeSexDataFilesPath, resultsFolderPath= paths
             
   #----- Extract required fields and prepare the data  

   # Names, short names, and orpha codes 
   RDnamesLst        = [x["name"]          for x in RDsData]
   RDFileNamesLst    = [x["short_name"]    for x in RDsData]

   #Race groups 
   raceNamesLst      = [x.split(",")[0] for x in list(RDsData[0]["race_percentage"]["races"].keys())]

   rd_datasset_size  = cfg["rd_datasset_size"]["rd_dataset_size_value"]
   rd_datasset_size_lbl = "all_patients" if rd_datasset_size==0 else str(rd_datasset_size)
   addTimeToDates    = cfg["addTime2Date"]

   # rdAgeGroupsLst  = [  "<5"   ,"5-14"  ,"15-19"  ,"20-24"  ,"25-39"  ,"40-60"  ,">60"]
   rdAgeGroupsLst    = list(cfg["rdAgeGroupsLst"])

   sexlabels       = list(cfg["sexLabels"])
   raceLabels      = list(cfg["raceLabels"])
   usaNames          = MDutils.getUSAstateNames()
   usaStateShortNames  = usaNames[1]
   
   # 1: generates dates + time, 0: generate date only 
   addTime2Date = int(cfg["addTime2Date"])

   print("=======================================================================")
   print("        RD DATA CREATION START!!! Expected size: ", rd_datasset_size_lbl)
   print("=======================================================================")

   total_number_of_patients = rd_datasset_size

   # List: Population of each state 
   # 1 x 51 
   statePopulations       = [sum(x) for x in usaAgeSexGroupData[2]]

   # This is the total population
   # will be used to compute contribution of each state
   total_USA_Population_From_Age  = sum(statePopulations) 

   raceWeights, total_USA_Population_From_Race, prevalenceRaceLst, racePopulations, racePopulationsSt  = MDutils.getRaceData(raceData, RDsData) 

   ## Note, there is a small error e.g. 
   ## age: 331448970,  race: 331449281, diff = 311   
   total_USA_Population = int((total_USA_Population_From_Race+total_USA_Population_From_Age)/2)
   print("total_USA_Population = ", total_USA_Population)
   
   # Age populations per age groups 
   # size: 1 x 7
   # chart should be similar to e.g. usa-2020-states-age-sex-female_grp
   usaStatesAgeSexBothGroupSumStates   = [ sum( row[c] for row in usaAgeSexGroupData[2])    for c in range(len(usaAgeSexGroupData[2][0]))   ]
       
   # RD: Minimum and maximum days after birth for diagnostic
   # For simplicity: Using days unit. Month = 30 days and Year = 365 days
   diagDateLst = [list(rd['diagnosis_dates'].values())[:-1] for rd in RDsData]
   
   # RD: Clinical parameters
   clinicalParsLst = [[ [ val for val in cp.values()]  for cp in rd['clinical_parameters'] ] for rd in RDsData]

   # RD: Death rates per age group (7 age groups)
   deathStatistics = [list(rd['death_percentage']["rates"].values()) for rd in RDsData]
   # TODO: find solution or statistics
   #        we can use the total number of dead patients to compute the correction factor or
   #        find statistics about number of patients per age  

   # percentage of female affected for each rare disease
   sexWeights = [x[1] for x in [list(rd['sex_percentage'].values()) for rd in RDsData]]
   
   #  sex weight control   
   rdSexWeight = 0.990001 # if 1.0, ageSexWeight will not included

   raceDists =[MDutils.getGroupDistriution(raceNamesLst, raceWeights[i]) for i in range(len(RDnamesLst))]

   print("Creating the rare disease dataset   ..............")

   #---------------------------------------
   number_of_generated_patients_Lst = []
   ## Loop through diseases list:
   for i, rd in enumerate(RDnamesLst):
         
      startRdTm = time.time() 
      j = i + 1 # to start from first row
      print("---------------------------------------------------")
      print('           ',j, rd)
      print("--------------------------------------------------")
      
      # Compute total number of patients for this disease based on race  
      total_expected_patients   = round(sum([ (x *  y) for x,y in zip(prevalenceRaceLst[i], racePopulations)]))  

      # Compute number of patients for each age group
      ageGroupPatients   = [ int((x/sum(usaStatesAgeSexBothGroupSumStates))*total_expected_patients)  for x in usaStatesAgeSexBothGroupSumStates]  
      # Compute total death cases
      total_expected_death         = round(sum([ (x *  y/100.0) for x,y in zip(ageGroupPatients, deathStatistics[i])]))  
      print("Total expected number of patients = ", total_expected_patients)      
      print("Total expected death cases        = ", total_expected_death)  
      if rd_datasset_size > total_expected_patients:
         print("Error: Dataset size must be smaller than total number of patients")
         print("To generate all possible patients change rd_dataset_size_value to 0 in config.json")
         print("User input size: ",rd_datasset_size, " total number of patients: ",total_expected_patients) 
         sys.exit()

      # Create results folder 
      resultsRDpath= os.path.join(resultsFolderPath,rd)
      if not os.path.exists(resultsRDpath):
         os.mkdir(resultsRDpath)  

      # Initialization
      # Reset dat list, labels, and patients counter 
      patientsData = []
      # reset dataset labels 
      patientsDataLabels = list(cfg["outputDataLabels"])
      patentsCount = 0
     
      # Clinical parameters: create normal distribution
      parNames  = [x[0]+":"+x[1] for x in clinicalParsLst[i]]
      parValues = [[ x[2],x[3] ] for x in clinicalParsLst[i]]
      parData   = [MDutils.sampleFromNormalDistribution(minVal=x[0], maxVal=x[1], sampleSize=100000) for x in parValues]                              
      # add labels of the clinical parameters 
      patientsDataLabels.extend(parNames)    
      # add the labels to the dataset 
      patientsData.append(patientsDataLabels)
      
      # Date of diagnostic: create normal distribution      
      ageDiagDist = MDutils.sampleFromNormalDistribution(minVal=diagDateLst[i][0], maxVal=diagDateLst[i][1], sampleSize=100000)           

      # number of patients for each state based on race inforrmation           
      # 51 elements, each is the total number of patients
      numberOfPatientsStatesRace    = [ int(sum([(x *  y) for x,y in zip(prevalenceRaceLst[i], racePopulation)]))  for racePopulation in racePopulationsSt ]

      numberOfPatientsStatesResized = [  x for x in numberOfPatientsStatesRace]
      
      # final number of patients for each state 
      numberOfPatientsStatesFinal   = numberOfPatientsStatesResized   if rd_datasset_size > 0 else numberOfPatientsStatesRace  
      
      # Generate number of patients for each age group based on the above information
      # Note: we don't have statistics about number of patients per age group 
      # number of patient for each age group for each state:  51 x 7  
      #                           ageRatio * total_expected_patients                            
      numberOfPatientsForAgeGroups  = [ [ round(x/sum(usaAgeSexGroupData[2][k]) * numberOfPatientsStatesFinal[k]) for x in usaAgeSexGroupData[2][k]] for k in range(len(usaStateShortNames))]
     
      stTotals = [sum(usaAgeSexGroupData[2][s])  for s in range(len(usaStateShortNames))] 
      numPSTs  = [round((stTotals[s]/total_USA_Population) * total_expected_patients) for s in range(len(usaStateShortNames))] 
      

      # ------ create age distribution for each state          
      # 7 x 96  age groups and their age distributions
      # for each age, we create a distribution based on the population of each state
      #                             age group 0                                                                    age group n
      # the output should be [ [[age_0]*age_0_percentage],...,[[age_n]*age_percentage_n]],...,[[age_0]*age_0_percentage],...,[[age_n]*age_percentage_n]] ] 
      # this way we can select randomly from each age group
      stateAgeDistLst = [MDutils.getAgeDistribution(usaAgeSexData[2][s], numPSTs[s], rdAgeGroupsLst, total_number_of_patients) for s in range(len(usaStateShortNames))] 
      

      # ------------------------------------   Main Loop:  -------------------------------------------
      # The output should follow the state and the age groups distributions  
      #   - we generate patients for each state 
      #   -    we generate patients for each age group of current state   
      for s, st in enumerate(usaStateShortNames):

           patentsCount, pData =  getStatePatients(i,s, st,usaAgeSexGroupData,  patentsCount, deathStatistics, numberOfPatientsForAgeGroups, sexWeights[i], rdSexWeight, rdAgeGroupsLst,
                     stateAgeDistLst, ageDiagDist, raceDists[i], parData, addTimeToDates, usaNames, raceNamesLst, raceWeights[i], sexlabels)
           
           patientsData.extend( pData)
      
      deadCount=len([x for x in patientsData if not x[8] in (0,None)])
      print("Number of generated patients: ", len(patientsData[1:]))
      print("Number of dead patients     : ", deadCount)
      number_of_generated_patients_Lst.append(len(patientsData[1:]))

      print("-------------------     Get The final output   -------------------------")
      # it is more efficient to generate all paatients then sample from them 
      # the large the sample , the more the similarity to the original distribution 
      # TODO: there is an issue here: the patients are not distributed equally e.g. among states, age groups, etc
      #        a new function should be writtern to handle this 
      rdFinalLabels = patientsData[0]
      rdFinalData   = patientsData[1:]
      np.random.shuffle(rdFinalData)
      
      if rd_datasset_size > 0 : 
         print("Sampling ", rd_datasset_size)
         # take first part of the shuffled data
         rdFinalData = rdFinalData[0:rd_datasset_size-1]    

      rdFinalData.insert(0,rdFinalLabels)      
      
      print("-------------------     Saving Generated data     -------------------------")
      rd_datasset_size_str = "patients_"+str(rd_datasset_size) if rd_datasset_size > 0 else "patients_all_"+str(len(rdFinalData)-1)
      resultsRDDatasetPath= os.path.join(resultsRDpath, rd_datasset_size_str)
      rdFinalDataFilePath = os.path.join(resultsRDDatasetPath, RDFileNamesLst[i]+"_"+rd_datasset_size_str+".csv")

      if not os.path.exists(resultsRDDatasetPath):
         os.mkdir(resultsRDDatasetPath)  
      csv.writer(open(rdFinalDataFilePath, "w", newline=''), delimiter=";").writerows(rdFinalData)    
      
      endTmDataGeneration = time.time() - startRdTm 
      print(" Data generation time = ", endTmDataGeneration, " seconds")
      if doEvaluation:
         print("-------------------     Evaluation    -------------------------")
         MDevaluate.getEvaluation(i, RDFileNamesLst, rd_datasset_size, rdFinalData, total_expected_patients, sexWeights, raceWeights, raceNamesLst,
                                   clinicalParsLst, deathStatistics, usaAgeSexGroupData, numberOfPatientsForAgeGroups,startRdTm ,rdAgeGroupsLst,sexlabels,
                                   raceLabels, rdFinalDataFilePath, doSave=1, doPlot=1)
   
   return number_of_generated_patients_Lst

# if this script called directly,
if __name__ == "__main__":
   # testing 
   if len(sys.argv) > 1:
      print("input: ", sys.argv)