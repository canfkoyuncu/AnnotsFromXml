import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import numpy as np
import openslide
import matplotlib.pyplot as plt
import os

def getAnnotFromXML(imFile, xmlfile, outPath):
    padding = 5
    showFlag = False

    if not os.path.exists(outPath):
        os.makedirs(outPath)

    osh = openslide.OpenSlide(imFile)
    tree = ET.parse(xmlfile)
    root = tree.getroot()
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

            minr -= padding
            minc -= padding
            maxr += padding
            maxc += padding
            width, height = int(maxc-minc), int(maxr-minr)
            img = osh.read_region((int(minc), int(minr)), 0, (width, height)).convert('RGB')

            new_points = []
            for p in points:
                new_points.append((p[0]-minc, p[1]-minr))

            mask = Image.new('1', (width, height), 0)
            ImageDraw.Draw(mask).polygon(new_points, outline=1, fill=1)

            basename = os.path.basename(imFile)
            mask.save(f"{outPath}//{basename}_x{minc}_y{minr}_mask.png")
            img.save(f"{outPath}//{basename}_x{minc}_y{minr}_image.png")

            if showFlag and len(new_points) > 4:
                plt.imshow(mask, cmap='gray')
                plt.show()

                points = np.asarray(points)
                plt.imshow(img)
                plt.scatter(x=points[:, 0]-minc, y=points[:, 1]-minr, c='g', s=20)
                plt.show()


if __name__ == '__main__':
    imFname = 'Z:\\Vanderbilt_Multinucleation_Jim\\1stRound\\1_001.svs'
    annotFname = 'Z:\\Vanderbilt_Multinucleation_Jim\\1stRound\\1_001.xml'
    outPath = '.\\annot\\'
    getAnnotFromXML(imFname, annotFname, outPath)
