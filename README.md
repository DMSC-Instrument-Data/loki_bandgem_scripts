# LOKI Band Gem Scripts
Scripts for the generation and parsing of LOKI BandGem geometry and data:

## Creating the IDF
`GenerateIDF.py` uses `ExtractGeometry.py` to extract the pixel corner vertices and centroids using `coordinate.txt`. GenerateIDF takes the path to `coordinate.txt` and the number of desired detector banks as input (up to a maximum of 8 banks). The output is the LOKI IDF and a detector map file which is used to transform between the ids in the `coordinate.txt` file and those in the IDF `StructuredDetector` for data loading.

## Loading data into Mantid
`ConvertLOKIRuns.py` takes the path to the folder containing the LOKI/LARMOR runs as `*.toff` files, the path to `coordinate.txt`, the path to the IDF produced in the last section, and the detector_map for transforming data.

**NB `ConvertLOKIRuns.py` is meant to be run in MantidPython** 

## Running the entire conversion

Use `ConvertData.py` to run the whole conversion, including generating the IDF and detectormap, from mantidpython. ConvertData takes the following command line arguments.

```
Convert LOKI Data

optional arguments:
  -h, --help            show this help message and exit
  -d DATALOCATION, --DataLocation DATALOCATION
                        Location of folder which contains LOKI runs. Must be
                        *.toff files
  -c COORDINATEFILE, --CoordinateFile COORDINATEFILE
                        Location of file which contains engineering
                        coordinates for detector pads
  -n [NUMBEROFBANKS], --NumberOfBanks [NUMBEROFBANKS]
                        The desired number of LOKI panels
```

Steps:
 1. cd *PATH_TO_THIS_REPO_ON_YOUR_SYSTEM`
 2. PATH_TO_MANTID_INSTALL/bin/mantidpython.bat --classic ConvertData.py -d PATH_TO_FOLDER_WITH_RUNS -c coordinate.txt -n 1

3. The current data produces by the in-kind group only contains one bank.