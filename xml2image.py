import random
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import numpy as np
import openslide
import matplotlib.pyplot as plt
import os

from NucleiSegmentation.src.dl_nuclei_seg import forwardImage


def getAnnotFromXML(imFile, xmlFile, outPath, patchSize, numPatchesFromEachComponent=20, scale=0, offsetFromCentroid=50):
    batch_size = 4
    if not os.path.exists(outPath):
        os.makedirs(outPath)

    if not os.path.exists(f"{outPath}//img//"):
        os.makedirs(f"{outPath}//img//")

    if not os.path.exists(f"{outPath}//label//"):
        os.makedirs(f"{outPath}//label//")

    batch_index = 0
    batches = []
    fnames = []
    osh = openslide.OpenSlide(imFile)
    tree = ET.parse(xmlFile)
    root = tree.getroot()

    basename = os.path.basename(imFile)
    for annotation in root.iter('Annotation'):
        for region in annotation.iter('Region'):
            points = []
            minr, minc, maxr, maxc = -1, -1, -1, -1
            for coordinate in region.iter('Vertex'):
                # append news dictionary to news items list
                x = float(coordinate.attrib["X"])
                y = float(coordinate.attrib["Y"])
                points.append((x, y))
                if minc == -1 or x < minc:
                    minc = x
                if maxc == -1 or x > maxc:
                    maxc = x
                if minr == -1 or y < minr:
                    minr = y
                if maxr == -1 or y > maxr:
                    maxr = y

            points = np.mean(np.array(points), axis=0)
            centerr = round(points[1])
            centerc = round(points[0])
            for ind in range(0, numPatchesFromEachComponent):
                randr = random.randint(centerr - offsetFromCentroid, centerr + offsetFromCentroid)
                randc = random.randint(centerc - offsetFromCentroid, centerc + offsetFromCentroid)

                minc = randc - patchSize // 2
                minr = randr - patchSize // 2

                img = osh.read_region((int(minc), int(minr)), scale, (patchSize, patchSize)).convert('RGB')

                '''if batch_index < batch_size:
                    batches.append(img)
                    fnames.append(f"{basename}_x{minc}_y{minr}")
                    batch_index += 1
                else:
                    cells = forwardImage(batches)
                    for i in range(0, batch_size):
                        batches[i].save(f"{outPath}//img//{fnames[i]}.png")
                        cells[i].save(f"{outPath}//label//{fnames[i]}.png")
                    fnames = []
                    batch_index = []
                    batch_index = 0'''

                cells = forwardImage(img)
                img.save(f"{outPath}//img//{basename}_x{minc}_y{minr}.png")
                cells[0].save(f"{outPath}//label//{basename}_x{minc}_y{minr}.png")


if __name__ == '__main__':
    imFname = 'Z:\\Vanderbilt_Multinucleation_Jim\\1stRound\\1_001.svs'
    annotFname = 'Z:\\Vanderbilt_Multinucleation_Jim\\1stRound\\1_001.xml'
    outPath = '.\\annot\\'
    getAnnotFromXML(imFname, annotFname, outPath, patchSize=256, numPatchesFromEachComponent=20, scale=0, offsetFromCentroid=75)
