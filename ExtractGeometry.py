import numpy
import csv
import copy


class GeometryExtractor(object):
    def __init__(self, coordinateFile):
        self.coordinateFile = coordinateFile

    def _findCentre(self, x, y):
        x = numpy.array(x)
        y = numpy.array(y)
        return x.sum()/len(x), y.sum()/len(y)

    def _extractCoordinates(self):
        with open(self.coordinateFile, 'rb') as posCsv:
            contents = list(csv.reader(posCsv, delimiter='\t'))
            del contents[0]
            garbage = []
            for i, row in enumerate(contents):
                if row[5] == '1' and row[6] == '1' and row[7] == '1' and row[8] == '1' and row[9] == '1':
                    garbage.append(i)
                del row[1]

            for i in sorted(garbage, reverse=True):
                del contents[i]

            contents = numpy.array(contents).astype(float)
            print "Num detectors: ", len(contents)
            self.detIDs = contents[:, 0]
            self.xpositions = contents[:, 4]
            self.ypositions = contents[:, 5]
            self.x = numpy.array([(x1, x2, x3, x4) for (x1, x2, x3, x4) in
                                  zip(contents[:, 6], contents[:, 8], contents[:, 10], contents[:, 12])])
            self.y = numpy.array([(y1, y2, y3, y4) for (y1, y2, y3, y4) in
                                  zip(contents[:, 7], contents[:, 9], contents[:, 11], contents[:, 13])])

            cx, cy = self._findCentre(self.xpositions, self.ypositions)
            self.xositions = numpy.array(self.xpositions)
            self.ypositions = numpy.array(self.ypositions)
            self.xpositions -= cx;
            self.ypositions -= cy;

            for i in xrange(len(self.xpositions)):
                self.x[i] = self.x[i] + self.xpositions[i]
                self.y[i] = self.y[i] + self.ypositions[i]

    def _extractMaps(self, vertPitchMapFull, detectorMapFull):
        vertPitchMap = {}
        detectorMap = {}
        for key in sorted(vertPitchMapFull):
            pitch, y1, y2 = key

            y1 = numpy.around(y1, 4)
            y2 = numpy.around(y2, 4)
            k1 = (pitch, y1)
            k2 = (pitch, y2)

            xvals = vertPitchMapFull[key]
            detIds = detectorMapFull[key]
            for xcoords, id in zip(xvals, detIds):
                if k1 in vertPitchMap:
                    vertPitchMap[k1].append(xcoords[0])
                    detectorMap[k1].append(id[0])
                else:
                    vertPitchMap[k1] = [xcoords[0]]
                    detectorMap[k1] = [id[0]]
                if k2 in vertPitchMap:
                    vertPitchMap[k2].append(xcoords[1])
                    detectorMap[k2].append(id[1])
                else:
                    vertPitchMap[k2] = [xcoords[1]]
                    detectorMap[k2] = [id[1]]
        return vertPitchMap, detectorMap

    def _sanitiseMaps(self, vertPitchMap, detectorMap):
        '''
        Removes duplicate x values for each row and matches detector IDs to vertices.
        :param vertPitchMap:
        :param detectorMap:
        :return: sanitised maps
        '''
        # sort and sanitise X values
        for key in sorted(vertPitchMap):
            allx = numpy.array(vertPitchMap[key])
            sortedIndices = numpy.argsort(allx)
            allx = allx[sortedIndices]
            allids = numpy.array(detectorMap[key])
            allids = allids[sortedIndices]
            uxvals, uindices = numpy.unique(numpy.around(allx, 0), return_index=True)
            allx = allx[uindices]
            uindices, = numpy.where(numpy.diff(allx) < 2)
            allx = allx.tolist()
            if len(uindices) > 0:
                for i in sorted(uindices, reverse=True):
                    del allx[i]

            vertPitchMap[key] = numpy.array(allx)
            temp, indices = numpy.unique(allids, return_index=True)
            indices.sort()
            allids = numpy.array(allids)
            detectorMap[key] = allids[indices]
        return vertPitchMap, detectorMap

    def _assembleComponents(self, vertPitchMap, detectorMap):
        '''
        Assemble all components together using the vertex aand detector maps
        :param vertPitchMap:
        :param detectorMap:
        :return:
        '''
        # add components together
        firstkey = sorted(vertPitchMap)[0]
        self.components = []
        lastlen = len(vertPitchMap[firstkey])
        lasty = -3000000.0#firstkey[1]
        lastpitch = firstkey[0]
        comp = []
        for key in sorted(vertPitchMap):
            length = len(vertPitchMap[key])
            if (numpy.around(lasty) != numpy.around(key[1]) and numpy.floor(lasty) != numpy.floor(
                    key[1])) or lastlen != length:
                if lastlen == length and lastpitch == key[0]:
                    comp.append((key[1], vertPitchMap[key], detectorMap[key]))
                else:
                    self.components = self.components + [comp]
                    comp = [(key[1], vertPitchMap[key], detectorMap[key])]

                lasty = key[1]
                lastpitch = key[0]
                lastlen = len(vertPitchMap[key])
        self.components = self.components + [comp]

    def _findComponents(self):
        vertPitchMapFull = {}
        detectorMapFull = {}
        # Create a map of pitch and y values corresponding to x corner values.
        for y, x, detID in zip(self.y, self.x, self.detIDs):
            y = numpy.array(y)
            pitch = numpy.around(y.max() - y.min())
            key1 = (pitch, y[0], y[1])
            key2 = (pitch, y[2], y[3])
            if key1 in vertPitchMapFull:
                vertPitchMapFull[key1].append(numpy.array([x[0], x[1]]))
                detectorMapFull[key1].append((numpy.array([detID, detID])))
            else:
                vertPitchMapFull[key1] = [numpy.array([x[0], x[1]])]
                detectorMapFull[key1] = [numpy.array([detID, detID])]
            if key2 in vertPitchMapFull:
                vertPitchMapFull[key2].append(numpy.array([x[2], x[3]]))
                detectorMapFull[key2].append((numpy.array([detID, detID])))
            else:
                vertPitchMapFull[key2] = [numpy.array([x[2], x[3]])]
                detectorMapFull[key2] = [numpy.array([detID, detID])]

        vertPitchMap, detectorMap = self._extractMaps(vertPitchMapFull, detectorMapFull)
        vertPitchMap, detectorMap = self._sanitiseMaps(vertPitchMap, detectorMap)
        self._assembleComponents(vertPitchMap, detectorMap)

    def getPosOffset(self):
        set1 = self.components[0][0]
        set2 = self.components[-1][-1]

        y1 = set1[0]
        y2 = set2[0]
        x1 = set1[1][0]
        x2 = set2[1][0]

        m = (y2 - y1) / (x2 - x1)

        c = y1 - (m*x1)
        centre = self._findCentre(self.xpositions, self.ypositions)
        dist = numpy.abs(c - centre[1])
        return centre[1] - dist

    def _sortComponents(self):
        vals = []
        for comp in self.components:
            vals.append(comp[0][0])
        indices = numpy.argsort(vals)
        components = copy.deepcopy(self.components)
        for i, si in enumerate(indices):
            self.components[i] = components[si]

    def _componentsPrintout(self):
        line = 0
        for i, comp in enumerate(self.components):
            print "component ", i
            for c in comp:
                print line, c[0], ":", c[1][0], "-", c[1][-1], " size:", len(c[1])
                line += 1

    def extract(self):
        self._extractCoordinates()
        self._findComponents()
        self._sortComponents()
        self._componentsPrintout()

    def getNumComponents(self):
        return len(self.components)

    def getComponent(self, compIndex):
        return self.components[compIndex]


if __name__ == "__main__":
    extractor = GeometryExtractor("coordinate.txt")
    extractor.extract()

    print str(extractor.getNumComponents()) + " components have been discovered."
