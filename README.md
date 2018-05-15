# LOKI Band Gem Scripts
Scripts for the generation and parsing of LOKI BandGem geometry and data:

## Creating the IDF
`GenerateIDF.py` uses `ExtractGeometry.py` to extract the pixel corner vertices and centroids using `coordinate.txt`. GenerateIDF takes the path to `coordinate.txt` and the number of desired detector banks as input (up to a maximum of 8 banks). The output is the LOKI IDF and a detector map file which is used to transform between the ids in the `coordinate.txt` file and those in the IDF `StructuredDetector` for data loading.

## Loading data into Mantid
`ConvertLOKIRuns.py` takes the path to the folder containing the LOKI/LARMOR runs as `*.toff` files, the path to `coordinate.txt`, the path to the IDF produced in the last section, and the detector_map for transforming data.

**NB `ConvertLOKIRuns.py` is meant to be run in MantidPython** 
