import csv
import numpy
import os
from mantid.simpleapi import CreateWorkspace, LoadInstrument, SaveNexus

class ConvertLokiRuns(object):
    '''
    THIS FILE IS INTENDED TO BE RUN FROM THE MANTID SCRIPT WINDOW
    Converts *.toff files to Nexus files by loading data, creating the workspace
    and loading the appropriate instrument.
    '''

    def __init__(self, dataFolder, coordinateFile, IDF, detectorMapFile=""):
        '''
        Constructor
        :param dataFolder: Folder which contains LOKI runs as *.toff files
        :param coordinateFile: File which contains all coordinates with respect to detector IDs
        :param IDF: Instrument definition file which contains instrument geometry.
        :param detectorMapFile: Optional detector map to transform detector IDs in physical space to that of the StructuredDetector if it is used.
        '''
        self.folder = dataFolder
        self.coordinateFile = coordinateFile
        self.idf = IDF
        self.detectorMapFile = detectorMapFile
        self.ext = ".toff"

    def _loadValidIDs(self):
        '''
        Uses the coordinate file to obtain the list of valid detector IDs.
        :return: List of valid detector IDs.
        '''
        validIDs = []
        with open(self.coordinateFile, "rb") as f:
            contents = list(csv.reader(f, delimiter='\t'))
            del contents[0]
            for line in contents:
                if "Z" not in line[1]: # Z represents a dummy entry
                    validIDs.append(line[0])
        monitor = int(validIDs[-1])
        validIDs.append(str(monitor + 1))

        return numpy.array(validIDs).astype(int)

    def _loadDetectorMap(self):
        '''
        If provided, load the detector map from file as a csv with no headers.
        :return: Detector map
        '''
        if self.detectorMapFile is not "":
            with open(self.detectorMapFile, "rb") as map:
                contents = list(csv.reader(map, delimiter=","))
                contents = numpy.array(contents).astype(int)

                realid = contents[:, 0]
                id = contents[:, 1]
                detectormap = {}
                for rid, id in zip(realid, id):
                    detectormap[rid] = id
            return detectormap
        else:
            return None

    def _loadTofData(self, file, validIDs, detMap):
        '''
        TOF data is loaded from file and sanitised using the valid detector IDs and detectormap if valid
        :param file: File which contains tof data
        :param validIDs: Valid detector IDs as file contains dummy data
        :param detMap: Optional map between physical detector ids and IDF detector IDs
        :return: Tof Data
        '''
        with open(file, "rb") as f:
            contents = list(csv.reader(f, delimiter='\t'))
            tof = contents[0] # time points as file header
            del contents[0]
            del tof[0] # column 0 is the detector id
            del tof[-1] # the last column contains nothing.
            tof = numpy.array(tof).astype(float) / 1000.0
            x = numpy.zeros((len(validIDs), len(tof)))
            y = numpy.zeros((len(validIDs), len(tof)))

            for i, id in enumerate(validIDs):
                line = contents[id]
                del line[0]
                del line[-1]
                line = numpy.array(line).astype(float)
                if detMap == None:
                    y[i] = line
                    x[i] = tof
                else:
                    y[detMap[id]] = line
                    x[detMap[id]] = tof

        return x, y

    def _loadRunsAndReturnWorkspaceNames(self):
        '''
        Loads tof data from all files in a specified folder into workspaces. The instrument geometry is loaded using
        the IDF provided.
        :return: The list of workspace names for saving.
        '''
        files = [f for f in os.listdir(self.folder) if self.ext in f]

        self.wsNames = []
        for file in files:
            infile = os.path.join(self.folder, file)
            print "Loading ", infile
            validIDs = self._loadValidIDs()
            detMap = self._loadDetectorMap()
            tofData = self._loadTofData(infile, validIDs, detMap)
            tofx, tofy = tofData

            wsName = file.replace(self.ext, "")
            ws = CreateWorkspace(tofx, tofy, NSpec=len(validIDs), OutputWorkspace=wsName)
            LoadInstrument(ws, True, self.idf)
            self.wsNames.append(wsName)

    def _saveNexusFiles(self):
        for wsName in self.wsNames:
            outfile = os.path.join(self.folder, wsName + ".nxs")
            print "Saving ", outfile
            SaveNexus(wsName, outfile)

    def convert(self):
        '''
        Perform conversion
        '''
        print "Converting toff files to nexus"
        self._loadRunsAndReturnWorkspaceNames()
        self._saveNexusFiles()
        print "Conversion complete files saved to ", self.folder


if __name__ == "__main__":
    mainPath = os.path.dirname(os.path.realpath(__file__))
    converter = ConvertLokiRuns(os.path.join(mainPath, "LOKI_RUNS"),
                                os.path.join(mainPath, "coordinate.txt"),
                                os.path.join(mainPath, "LOKI_BANDGEM_definition.xml"),
                                os.path.join(mainPath, "LOKI_map.csv"))
    converter.convert()
