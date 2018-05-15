import argparse
import GenerateIDF
import ConvertLOKIRuns
import os

parser = argparse.ArgumentParser(description='Convert LOKI Data from *.toff files to *.nexus.')
parser.add_argument('-d', '--DataLocation',
                    help="Location of folder which contains LOKI runs. Must be *.toff files.")
parser.add_argument('-c', '--CoordinateFile', help="Location of coordinate.txt file which contains engineering coordinates for detector pads.")
parser.add_argument('-n', "--NumberOfBanks", nargs='?', const=1, type=int, help="The desired number of LOKI panels. Defaults to 1.")
parser.add_argument('-o', '--OutputFolder', nargs='?', const="", help="Optional location for converted nexus files. Defaults to the DataLocation")

args = parser.parse_args()

generator = GenerateIDF.LOKIGenerator(args.CoordinateFile, args.NumberOfBanks)
generator.generate()

mainPath = os.getcwd()
converter = ConvertLOKIRuns.ConvertLokiRuns(args.DataLocation, args.CoordinateFile,
                                            os.path.join(mainPath, "LOKI_BANDGEM_definition.xml"),
                                            os.path.join(mainPath, "LOKI_map.csv"), args.OutputFolder)

converter.convert()
