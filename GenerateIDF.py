import ExtractGeometry
import math


class LOKIGenerator(object):
    def __init__(self, coordFile, numBanks=1):
        self.extractor = ExtractGeometry.GeometryExtractor(coordFile)
        self.numBanks = numBanks
        self.outFile = open("LOKI_BANDGEM_definition.xml", "w")
        self.mapFile = open("LOKI_map.csv", "w")
        self.pi = math.pi
        self.piDiv = self.pi / 180.0

    def __del__(self):
        self.outFile.close()
        self.mapFile.close()

    def _writeInstrumentHeader(self):
        self.outFile.write("<?xml version='1.0' encoding='ASCII'?>\n")
        self.outFile.write("<!-- For help on the notation used to specify an Instrument Definition File \n")
        self.outFile.write("     see http://www.mantidproject.org/IDF -->\n")
        self.outFile.write("<instrument xmlns=\"http://www.mantidproject.org/IDF/1.0\" \n")
        self.outFile.write("            xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n")
        self.outFile.write(
            "            xsi:schemaLocation=\"http://www.mantidproject.org/IDF/1.0 http://schema.mantidproject.org/IDF/1.0/IDFSchema.xsd\"\n")
        self.outFile.write(" name=\"LOKI\" valid-from   =\"1900-01-31 23:59:59\"\n")
        self.outFile.write("                         valid-to     =\"2100-01-31 23:59:59\"\n")
        self.outFile.write("		          last-modified=\"2010-11-16 12:02:05\">\n")
        self.outFile.write("<!---->\n")

    def _writeInstrumentFooter(self):
        self.outFile.write("</instrument>")

    def _writeDefaults(self):
        self.outFile.write("<defaults>\n")
        self.outFile.write("\t<length unit=\"metre\"/>\n")
        self.outFile.write("\t<angle unit=\"degree\"/>\n")
        self.outFile.write("\t<reference-frame>\n")
        self.outFile.write("\t\t<along-beam axis=\"z\"/>\n")
        self.outFile.write("\t\t<pointing-up axis=\"y\"/>\n")
        self.outFile.write("\t\t<handedness val=\"right\"/>\n")
        self.outFile.write("\t</reference-frame>\n")
        self.outFile.write("\t\t<default-view axis-view=\"z-\"/>")
        self.outFile.write("</defaults>\n\n")

    def _writeLARMORSourceAndSample(self):
        self.outFile.write("<component type=\"source\">\n")
        self.outFile.write("\t<location />\n")
        self.outFile.write("</component>\n")
        self.outFile.write("<type name=\"source\" is=\"Source\" />\n\n")

        self.outFile.write("<component type=\"some-sample-holder\">\n")
        self.outFile.write("\t<location z=\"25.300\" />\n")
        self.outFile.write("</component>\n")
        self.outFile.write("<type name=\"some-sample-holder\" is=\"SamplePos\" />\n\n")

    def _writeMonitors(self, monitorID):
        self.outFile.write("<component type=\"Moderator-Monitor4\" idlist=\"monitors\">\n")
        self.outFile.write("\t<location z=\"25.760\" name=\"monitor4\" />\n")
        self.outFile.write("</component>\n\n")

        self.outFile.write("<type name=\"Moderator-Monitor4\" is=\"monitor\">\n")
        self.outFile.write("\t<percent-transparency val=\"99.9\" />\n")
        self.outFile.write("\t<cuboid id=\"shape\">\n")
        self.outFile.write("\t\t<left-front-bottom-point x=\"0.0125\" y=\"-0.0125\" z=\"0.0\" />\n")
        self.outFile.write("\t\t<left-front-top-point x=\"0.0125\" y=\"-0.0125\" z=\"0.005\" />\n")
        self.outFile.write("\t\t<left-back-bottom-point x=\"-0.0125\" y=\"-0.0125\" z=\"0.0\" />\n")
        self.outFile.write("\t\t<right-front-bottom-point x=\"0.0125\" y=\"0.0125\" z=\"0.0\" />\n")
        self.outFile.write("\t</cuboid>\n")
        self.outFile.write("\t<algebra val=\"shape\" />\n")
        self.outFile.write("</type>\n\n")

        self.outFile.write("<idlist idname=\"monitors\">\n")
        self.outFile.write("\t<id val=\"" + str(monitorID) + "\" />\n")
        self.outFile.write("</idlist>\n\n")
        self.mapFile.write("2496," + str(monitorID))

    def _writeStructuredPanel(self, compIndex):
        component = self.extractor.getComponent(compIndex)
        xpixels = len(component[0][1]) - 1
        ypixels = len(component) - 1

        print
        "Processing component ", compIndex
        self.outFile.write("<type name=\"Structured_" + str(
            compIndex) + "\" is=\"StructuredDetector\" xpixels=\"" + str(xpixels) + "\" ypixels=\"" + str(
            ypixels) + "\" type=\"pixel\">\n")

        idlist = []
        for i, set in enumerate(component):
            y = set[0]
            xmin = set[1][0]
            xmax = set[1][-1]
            pitch = (xmax - xmin) / (len(set[1]) - 1)
            xval = xmin
            for x in set[1]:
                self.outFile.write("\t<vertex x=\"" + str(xval / 1000.0) + "\" y=\"" + str(y / 1000.0) + "\"/>\n")
                xval += pitch
            for id in set[2]:
                if id not in idlist and i != len(component):
                    idlist.append(id)
        self.outFile.write("</type>\n\n")
        return idlist

    def _writeCompAssemblies(self):
        r = self.extractor.getPosOffset() / 1000.0
        angle = 90.0
        start = 0
        idstart = []
        for i in xrange(self.numBanks):
            self.outFile.write("<component type=\"bank_" + str(i) + "\">\n")
            x = -r * math.sin(self.piDiv * angle)
            y = r * math.cos(self.piDiv * angle)
            self.outFile.write("\t<location x=\"" + str(x) + "\" y=\"" + str(y) + "\" z=\"25.300\" rot=\"" + str(
                angle) + "\" axis-x=\"0.0\" axis-y=\"0.0\" axis-z=\"1.0\" />\n")
            self.outFile.write("</component>\n")
            angle += 45

            self.outFile.write("\n\n")

            self.outFile.write("<type name=\"bank_" + str(i) + "\">\n")
            self.outFile.write("<properties />\n")

            numPanels = self.extractor.getNumComponents()

            starts = []
            for i in xrange(numPanels):
                starts.append(start)
                component = self.extractor.getComponent(i)
                xpixels = len(component[0][1]) - 1
                ypixels = len(component) - 1
                self.outFile.write(
                    "<component type=\"Structured_" + str(i) + "\" idstart=\"" + str(
                        start) + "\" idfillbyfirst=\"x\" idstepbyrow=\"" + str(xpixels) + "\" idstep=\"1\">\n")
                self.outFile.write("\t<location x=\"0.0\" y=\"0.0\" z=\"3.406\" />\n")
                self.outFile.write("</component>\n")
                start += (xpixels * ypixels)
            idstart.append(starts)
            self.outFile.write("</type>\n\n")

        idlists = []
        for i in xrange(numPanels):
            idlists.append(self._writeStructuredPanel(i))

        self.outFile.write("<type is=\"detector\" name=\"pixel\" />\n\n")

        for i in xrange(self.numBanks):
            for j, idlist in enumerate(idlists):
                start = idstart[i][j]
                for k, id in enumerate(idlist):
                    self.mapFile.write(str(int(id)) + "," + str(start + i) + "\n")

    def generate(self):
        self._writeInstrumentHeader()
        self._writeDefaults()
        self._writeLARMORSourceAndSample()

        self.extractor.extract()
        monitorID = 0
        for i in xrange(self.extractor.getNumComponents()):
            component = self.extractor.getComponent(i)
            xpixels = len(component[0][1]) - 1
            ypixels = len(component) - 1
            monitorID += (xpixels * ypixels)
        monitorID *= self.numBanks

        self._writeMonitors(monitorID)
        self._writeCompAssemblies()
        self._writeInstrumentFooter()


if __name__ == "__main__":
    generator = LOKIGenerator("coordinate.txt", 1)
    generator.generate()

    print
    "Loki generated!"
