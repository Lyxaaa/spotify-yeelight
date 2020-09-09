import binascii
import numpy as np
import scipy.stats
import scipy.misc
import scipy.cluster
import scipy.sparse
import scipy.ndimage
import scipy

def dominant_colour(read_image):
    # print('Reading image colour')
    # im = Image.open(filename)
    im = read_image
    # im = im.resize((150, 150))      # optional, to reduce time
    ar = np.asarray(im)
    shape = ar.shape
    try:
        ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)
    except IndexError:
        return [0, 0, 0]
    # print('finding clusters')
    codes, dist = scipy.cluster.vq.kmeans(ar, 5)
    newcodes = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]])
    # print('cluster centres:\n', codes)
    cluster = 0
    count = 0
    while count < len(codes):
        under_check = 0
        over_check = 0
        mid_check = 0
        for value in range(3):
            # print('cluster [%d][%d]: %s --->>' % (count, value, codes[count][value]))
            if codes[count][value] < 80:
                # print("Added")
                under_check += 1
            elif codes[count][value] > 200:
                # print("Added")
                over_check += 1
            else:
                mid_check += 1
        if over_check <= 2 and under_check <= 2:
            newcodes[cluster] = codes[count]
            # print("codes contains: %s newcodes contains: %s" % (codes[count], newcodes[cluster]))
            cluster += 1
        count += 1
    # print('newcodes length: %s\n', len(newcodes))
    print('Cluster Centres:\n', newcodes)
    codes = newcodes
    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = scipy.ndimage.histogram(vecs, len(codes), len(codes), 2)    # count occurrences
    # print("Counts: %s\nBins: %s\n" %(counts, bins))
    index_max = np.argmax(counts)                    # find most frequent
    peak = codes[index_max]
    colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
    # print('most frequent is %s (#%s)' % (peak, colour))
    # draw_block(colour)
    return peak