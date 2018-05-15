import argparse
import GenerateIDF
import ConvertLOKIRuns
import os

parser = argparse.ArgumentParser(description='Convert LOKI Data')
parser.add_argument('-d', '--DataLocation',
                    help="Location of folder which contains LOKI runs. Must be *.toff files")
parser.add_argument('-c', '--CoordinateFile', help="Location of file which contains engineering coordinates for detector pads")
parser.add_argument('-n', "--NumberOfBanks", nargs='?', const=1, type=int, help="The desired number of LOKI panels")

args = parser.parse_args()

generator = GenerateIDF.LOKIGenerator(args.CoordinateFile, args.NumberOfBanks)
generator.generate()

mainPath = os.getcwd()
converter = ConvertLOKIRuns.ConvertLokiRuns(args.DataLocation, args.CoordinateFile,
                                            os.path.join(mainPath, "LOKI_BANDGEM_definition.xml"),
                                            os.path.join(mainPath, "LOKI_map.csv"))

converter.convert()
