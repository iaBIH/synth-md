import sys, os, time
import matplotlib.pyplot as plt, numpy as np, geopandas as gpd, pandas as pd 
import matplotlib.patheffects as PathEffects
from synthRD import RDutils 

# Function to save chart data to a CSV file for external processing
def saveChartData(inputData,figPath):

    # Create default values if none are provided
    if inputData[2] is None:
       inputData[2] =list(range(len(inputData[0])))
    if inputData[3] is None:
       inputData[3] =list(range(len(inputData[0])))

    # Determine if the input data includes state labels
    if len(inputData[0]) == len(inputData[-1]):
       data = [[x,y,xT,xTLbl] for x,y,xT,xTLbl in zip(*inputData)]
    else:
       X,Y,Xticks,statesLabels = inputData
       data = [[x,y,xT] for x,y,xT in zip(X,Y,Xticks)] 

    # Create a CSV file path
    fnmPath = figPath[:-4] + ".csv"
    with open(fnmPath, 'w') as f:
        for row in data:
            line = "%s\n" % "; ".join([str(item) if isinstance(item, int) else f"'{item}'" for item in row])
            f.write(line)

    f.close()

# Function to plot data
def plotData(Y, figTitle=None, XticksLabelsLst=None, isPercentageOutput=None, doShow=None, chartFnmPath=None, szW=20, szH=10):

        # Set default values if none are provided
        doShow = 1 if doShow is None else doShow     
        isPercentageOutput=0 if isPercentageOutput is None else isPercentageOutput
    
        figTitle = "chart" if figTitle is None else figTitle

        # Convert data to percentages if required
        Y = [ x/sum(Y)*100 for x in Y] if isPercentageOutput else Y
        Ylabel= 'percentage %' if isPercentageOutput else 'counts'

        X = list(range(len(Y)))
        Xticks = list(range(len(X)))        
        XticksLabelsLst = X if XticksLabelsLst is None else XticksLabelsLst   
        XlabelRotation= 60 if len(X)>50 else 0     

        # Set up the figure
        plt.clf()
        plt.gcf().set_size_inches(szW,szH)
        plt.title(figTitle, fontsize=20)
        plt.xlabel('values', fontsize=18)
        plt.ylabel(Ylabel, fontsize=16)
        plt.rcParams["figure.autolayout"] = True
        plt.margins(x=0, y=0)
        plt.xticks(Xticks, fontsize=8, rotation=XlabelRotation, labels=XticksLabelsLst)
        plt.bar(X,Y)

        # Save the chart to a file if a path is provided
        if not chartFnmPath is None:            
           plt.savefig(chartFnmPath)           
           saveChartData([X,Y,Xticks,XticksLabelsLst],chartFnmPath)

        # Display the chart if requested
        if doShow:
           plt.show()        
        
        plt.close()

# Function to plot a map with data as a color map
def plotMap(input_data, cfg=None):

    # Default configuration if none is provided
    cfg = cfg if not cfg is None else { "shapefile_path": "datasets/usa/map/cb_2018_us_state_20m.shp",
                                        "xylim": [-130, -60, 20, 55],
                                        "fontsize": 6,
                                        "figsize":(15,10),
                                        "cmap":"magma",
                                        "outputFnmPath":"results/",
                                        "doSave":0,
                                        "doShow":1,
                                        "mapTitle": "Number of Patients per State",
                                        "mapName":"NAME",
                                        "dataName":"state"
                                    }


    # Load the shapefile using geopandas  
    shapefile_path = cfg["shapefile_path"]
    mapData = gpd.read_file(shapefile_path)

     # Convert the input data to a pandas DataFrame
    data = {
    "state": [name for name in input_data.keys()],
    "vals": list(input_data.values())
    }

    #Convert the data to a pandas DataFrame
    data_df = pd.DataFrame(data)

    # Merge the data DataFrame with the map DataFrame based on the common state column
    merged = mapData.set_index(cfg["mapName"]).join(data_df.set_index(cfg["dataName"]))

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=cfg["figsize"])

    # Plot the map
    merged.plot(column="vals", cmap=cfg["cmap"], linewidth=0.8, ax=ax, edgecolor="0.8", legend=True)
   
    # Adjust the x-limits and y-limits of the plot to better fit the map
    ax.set_xlim(cfg["xylim"][0], cfg["xylim"][1])
    ax.set_ylim(cfg["xylim"][2], cfg["xylim"][3])

    # Add annotations for each state
    for idx, row in merged.iterrows():
        
        # Get the coordinates for the annotation from the centroid of the geometry
        x, y = row['geometry'].centroid.x, row['geometry'].centroid.y

        # Get the state abbreviation and number of patients. Replace 'STUSPS' with the correct column for state abbreviations if needed
        state_abbr = row['STUSPS']
        vals = row['vals']

        # Create the annotation text
        annotation_text = f'{state_abbr}'

        # Add the annotation to the plot with a black text color and a white outline
        ax.annotate(annotation_text, xy=(x, y), ha='center', fontsize=cfg["fontsize"], color='black',
                     path_effects=[PathEffects.withStroke(linewidth=3, foreground='white')])


    # Set the title
    ax.set_title(cfg["mapTitle"])

    # Save the map to a file if requested
    if cfg["doSave"]:
       plt.savefig(cfg["outputFnmPath"])
       saveChartData([[name for name in input_data.keys()],list(input_data.values()),None,None],cfg["outputFnmPath"])

    # Display the map if requested
    if cfg["doShow"]:      
       # Show the plot
       plt.show()    
    
# Function to get frequency of data from a list        
def getFreqFromList(data, isPercentageOutput=None):

    isPercentageOutput = isPercentageOutput if not isPercentageOutput is None else 0
    # get frequency of data 
    result = []
    # get unique values 
    labels = sorted(list(set(data)))
    freq = []
    for lbl in labels:     
        count = len( [y for y in data if y == lbl ] ) 
        freq.append(count )

    if isPercentageOutput:
       # get percentage instead of count
       freq = [ (x/sum(freq)*100) for x in freq]  

    result = [labels, freq]    
    return result

# Function to plot patient charts
def plotPatientsCharts(p, dataLabels, dataArray, chartFolderPath, rdSName,statesLabels,  rd_datasset_size, isPercentageOutput):

            statesIDs, statesSName, statesLName =  RDutils.getUSAstateNames()
            L =  [x[p] for x in dataArray if not x[p] is None ]
            L =  L if not p in[6,7,8] else [x for x in L if x !=0  ]

            pltTitle =  dataLabels[p] if p<9 else "CP"+str(p-8)
            chartFnm = "chart_"+rdSName+"_"+str(p)+"_"+pltTitle +"_"+str(rd_datasset_size)+'.png'
            chartFnmPath = os.path.join(chartFolderPath, chartFnm)
            print(chartFnmPath)
            szW = 6 if p in [4,5] else ( 10 if p in [2] else 15)
            szH = 6
            Ylabel= 'percentage %' if isPercentageOutput else 'counts'

            # Set up the figure
            plt.clf()
            plt.gcf().set_size_inches(szW,szH)
            plt.title(rdSName+" : "+pltTitle, fontsize=20)
            plt.xlabel('values', fontsize=18)
            plt.ylabel(Ylabel, fontsize=16)
            plt.rcParams["figure.autolayout"] = True
            plt.margins(x=0, y=0)
            
            ## Handling different data lists
            if p <9:    
                X, Y =  getFreqFromList(L, isPercentageOutput=isPercentageOutput); 
                Xticks = list(range(len(X)))
                if p==1: # X is age  list 
                        plt.xticks(Xticks, fontsize=8, rotation=60, labels=Xticks)
                elif p==2: # X is states list     
                    if len(X)!=len(statesLabels):
                        tmp=[]
                        for x in enumerate(X):
                            sn = x[0] #stateLNames.index(x)
                            tmp.append(statesLabels[sn])

                        statesLabels = tmp

                    plt.xticks(Xticks, fontsize=8, rotation=60, labels=statesLabels)
                    print("------------------- Create Maps    -------------------------")        
                    # Initialize an empty dictionary to store the counts of persons per state
                    state_counts = {state: val for state, val in zip(statesLName,Y)}
                    chartFnm = "chart_"+rdSName+"_"+str(p)+"_"+pltTitle +"_"+str(rd_datasset_size)+'_map.png'
                    chartFnmPath = os.path.join(chartFolderPath, chartFnm)
                    cfg = { "shapefile_path": "datasets/usa/map/cb_2018_us_state_20m.shp",
                            "xylim": [-130, -60, 20, 55],
                            "fontsize": 6,
                            "figsize":(15,10),
                            "cmap":"magma",
                            "outputFnmPath": chartFnmPath,
                            "doSave":1,
                            "doShow":0,
                            "mapTitle": pltTitle,
                            "mapName":"NAME",
                            "dataName":"state"
                        }
                    plotMap(state_counts, cfg)
                    
                elif p in [6,7,8]: # X is dates list
                        plt.xticks(X, fontsize=7, rotation=60, labels=X)
                
                plt.bar(X,Y)
                saveChartData([X,Y,Xticks,statesLabels],chartFnmPath)
                plt.savefig(chartFnmPath)
     
            else: 
                # Clinical parameters
                stepSize = 0.01
                X = np.arange((np.min(L)), (np.max(L)), stepSize) if (np.max(L) - np.min(L))  < 100 else np.arange((np.min(L)), (np.max(L)), 1)   
                n, bins, _ = plt.hist(L, bins=len(X))
                bin_centers = (bins[:-1] + bins[1:]) / 2
                saveChartData([bin_centers,n,None,None],chartFnmPath)
                plt.savefig(chartFnmPath)

# Function to plot death charts
def plotDeathCharts(p, dataArray, sexLabels, racelabels, isPercentageOutput, maxUSAAge, rdSName, statesLabels, rd_datasset_size, chartFolderPath, szW,szH):
      
        raceNamesLst = racelabels[1]  
        sexLst       = sexLabels[0]

        # Death per: age, state, sex, race      
        Y1 = [len([x for x in dataArray if (x[8] not in (None, 0)) and (x[1]==a)])  for a in range(maxUSAAge+1)]
        Y2 = [len([x for x in dataArray if (x[8] not in (None, 0)) and (x[2]==a)])  for a in RDutils.getUSAstateNames()[2]]       
        Y3 = [len([x for x in dataArray if (x[8] not in (None, 0)) and (x[4]==a)])  for a in sexLst]
        Y4 = [len([x for x in dataArray if (x[8] not in (None, 0)) and (x[5]==a)])  for a in raceNamesLst]
        deathPlots = [Y1,Y2,Y3, Y4]
        # TODO: move to json config file
        deathPlotsLabels= ["DeathAge","DeathState","DeathSex","DeathRace"]
        XticksLabelsLst = [list(range(len(Y1))), RDutils.getUSAstateNames()[1], sexLst, raceNamesLst]

        for Y,pltTitle, XticksLabels in zip(deathPlots, deathPlotsLabels, XticksLabelsLst): 
            Y = [ x/sum(Y)*100 for x in Y] if isPercentageOutput else Y
            X = list(range(len(Y)))
            plt.clf()
            plt.gcf().set_size_inches(szW,szH)
            plt.title(rdSName+" : "+pltTitle, fontsize=20)
            plt.xlabel('values', fontsize=18)
            Ylabel= 'percentage %' if isPercentageOutput else 'counts'
            plt.ylabel(Ylabel, fontsize=16)
            plt.rcParams["figure.autolayout"] = True
            plt.margins(x=0, y=0)
            Xticks = list(range(len(X)))        
            rotation= 60 if len(X)>50 else 0   
            
            if (len(X)!=  len(XticksLabels)):
               XticksLabels=  RDutils.getUSAstateNames()[1]  

            plt.xticks(Xticks, fontsize=8, rotation=rotation, labels=XticksLabels)
            plt.bar(X,Y)
            chartFnm = "chart_"+rdSName+"_"+str(p)+"_"+pltTitle +"_"+str(rd_datasset_size)+'.png'
            chartFnmPath = os.path.join(chartFolderPath, chartFnm)
            print(chartFnmPath)
            saveChartData([X,Y,Xticks,XticksLabels],chartFnmPath)
            plt.savefig(chartFnmPath)
            p = p + 1

# Function to plot rare disease data
def plotRareDiseaseData(fnm, sexLabels, racelabels, isPercentageOutput=None):
        print("=======================================================================")
        print("        RD CREATE CHARTS ")
        print("=======================================================================")
        startTm = time.time()
        isPercentageOutput = isPercentageOutput if not isPercentageOutput is None else 0 

        # Get disease name and output path from the file name
        chartFolderPath, csvFnm = os.path.split(fnm) # os.path.dirname(fnm)
        rdSName =  csvFnm.split("_")[0]

        statesLabels = RDutils.getUSAstateNames()[1]

        #----------------------------------------------
        print("Reading input CSV files ..............")
        #----------------------------------------------
        maxUSAAge, dataLabels, dataArray =  RDutils.readingCSVdata(fnm, 0)

        rd_datasset_size = len(dataArray)

        print("============    Charts   ================")
        #   0,     1,     2,       3,         4,      5,       6,           7,          8,         9,     10  ]
        # "idx", "age",	"state", "zipCode",	"sex",	"race",	"birthDate", "diagDate", "deathDate", "CP1",  "CP2"]
    
        # Excluded labels
        excludedLabels =  ["idx","zipCode"]
        chartsIdx= [ j  for j in range(len(dataLabels)) if not dataLabels[j] in excludedLabels] 

        # Figure size 
        szW = 10; szH = 6
        for p in chartsIdx:                    
            plotPatientsCharts(p, dataLabels, dataArray, chartFolderPath, rdSName,statesLabels,  rd_datasset_size, isPercentageOutput)

        
        plotDeathCharts(p+1, dataArray, sexLabels, racelabels, isPercentageOutput, maxUSAAge, rdSName, statesLabels, rd_datasset_size, chartFolderPath, szW,szH)

        print("-------------------        Statistics    -------------------------")
        rdTime =  time.time() - startTm
        print("Preprocessing time = ",  rdTime , " seconds")  
        endTm = time.time() - startTm 
        print("Preprocessing time for plotting = ", endTm, " seconds")
        print("-------------------  Plotting done! -------------------------")

# Main script execution
if __name__ == "__main__":
    if len(sys.argv) > 1:
       fnm = sys.argv[1]
       print("input: ", fnm)
    
