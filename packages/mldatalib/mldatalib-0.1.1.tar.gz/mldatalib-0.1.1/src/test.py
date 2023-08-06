__author__ = 'georgeoblapenko'

from os import path

import numpy as np
from skimage.io import imread
from skimage import img_as_ubyte
import skimage.filter
import skimage.feature
import matplotlib.pyplot as plt
from skimage.morphology import convex_hull_image
from skimage.measure import regionprops, moments_hu, moments_normalized
from skimage.morphology import disk, label, closing, square, erosion
from sklearn.ensemble import GradientBoostingClassifier
import csv
from scipy.spatial.distance import pdist
from skimage.feature import daisy
from scipy.ndimage.measurements import center_of_mass
from mahotas.features.zernike import zernike_moments
from skimage.exposure import histogram
from skimage.measure import perimeter
from skimage.morphology import skeletonize
from mahotas import thin
from mldatalib.dataset import LabeledDataSet, UnlabeledDataSet


def read_and_otsu_bw(fpath):
    img = imread(fpath, as_grey=True)
    thresh = skimage.filter.threshold_otsu(img)
    binary_img = img > thresh
    twotone_img = binary_img.astype(int)
    return twotone_img


def read_erode_and_otsu_bw(fpath, radius=4):
    img = imread(fpath, as_grey=True)
    img = erosion(img, disk(radius))
    thresh = skimage.filter.threshold_otsu(img)
    binary_img = img > thresh
    twotone_img = binary_img.astype(int)
    return twotone_img


def read_erode_close_and_otsu_bw(fpath, er_radius=4, cl_radius=5):
    img = imread(fpath, as_grey=True)
    img = erosion(img, disk(er_radius))
    img = closing(img, disk(cl_radius))
    thresh = skimage.filter.threshold_otsu(img)
    binary_img = img > thresh
    twotone_img = binary_img.astype(int)
    return twotone_img


def chull(fpath):
    img = imread(fpath, as_grey=True)
    img = erosion(img, disk(12))
    thresh = skimage.filter.threshold_otsu(img)
    binary_img = img > thresh

    chull_img = convex_hull_image(binary_img)
    binary_img = binary_img.astype(int)
    return 1. * np.count_nonzero(chull_img) / (np.count_nonzero(binary_img))


def central_pixel(fpath):
    img = imread(fpath)
    x = img.shape[0] / 2
    y = img.shape[1] / 2
    return np.array([img[x, y, 0], img[x, y, 1], img[x, y, 2]]) * (1.0 / 255.0)


def color_percentage(fpath):
    img = imread(fpath)
    red = img[:, :, 0].sum()
    green = img[:, :, 1].sum()
    blue = img[:, :, 2].sum()
    totalc = red + green + blue
    normalizer = 1.0 / totalc
    return np.array([red, green, blue]) * normalizer


def color_means(fpath):
    img = imread(fpath)
    flattened = img.sum(2)
    flattened = flattened > 0.0
    red = img[:, :, 0]
    red = red[flattened].sum()
    green = img[:, :, 1]
    green = green[flattened].sum()
    blue = img[:, :, 2]
    blue = blue[flattened].sum()
    normalizer = 1.0 / (img.shape[0] * img.shape[1])
    return np.array([red, green, blue]) * normalizer


def color_std(fpath):
    img = imread(fpath)
    flattened = img.sum(2)
    flattened = flattened > 0.0
    red = img[:, :, 0]
    red = red[flattened]
    red_std = np.std(red, dtype=np.float64)
    green = img[:, :, 1]
    green = green[flattened]
    green_std = np.std(green, dtype=np.float64)
    blue = img[:, :, 2]
    blue = blue[flattened]
    blue_std = np.std(blue, dtype=np.float64)
    return np.array([red_std, green_std, blue_std])


def galaxy_size(fpath):
    img = imread(fpath, as_grey=True)
    thresh = skimage.filter.threshold_otsu(img)
    binary_img = img > thresh
    twotone_img = binary_img.astype(int)
    return np.count_nonzero(twotone_img) / (1. * img.shape[0] * img.shape[1])


def label_regions(fpath):
    img = read_erode_close_and_otsu_bw(fpath, 4, 8)
    label_img = label(img)
    return len(regionprops(label_img))


def daisy_feature(fpath):
    img = imread(fpath, as_grey=True)
    descs = daisy(img, step=120, radius=80, rings=2, histograms=4,
                  orientations=4)
    return np.reshape(descs, descs.shape[0] * descs.shape[1] * descs.shape[2])


def means_and_std(fpath):
    img = imread(fpath, as_grey=True)
    return np.array([np.mean(img), np.std(img)])


def peaks(fpath):
    img = imread(fpath, as_grey=True)
    peak_points = skimage.feature.peak_local_max(img)
    distmat = pdist(peak_points)
    # print distmat.shape
    if distmat is None:
        return 0
    elif distmat is []:
        return 0
    elif distmat.shape[0] != 0:
        return distmat.sum() / (2 * distmat.shape[0])
    else:
        return 0


def hu(fpath):
    img = imread(fpath, as_grey=True)
    mom_norm = moments_normalized(img, 4)
    hu_mom = moments_hu(mom_norm)
    proper_ind = [1, 2, 4, 5, 6]
    return hu_mom[proper_ind]


def otsu_val(fpath):
    img = imread(fpath, as_grey=True)
    return skimage.filter.threshold_otsu(img)


def color_otsu_val(fpath):
    img = imread(fpath)
    r_otsu = skimage.filter.threshold_otsu(img[:, :, 0])
    g_otsu = skimage.filter.threshold_otsu(img[:, :, 1])
    b_otsu = skimage.filter.threshold_otsu(img[:, :, 2])
    return np.array([r_otsu, g_otsu, b_otsu])


def dist_max_mass(fpath):
    img = imread(fpath, as_grey=True)
    img = erosion(img, disk(5))
    img_max = np.unravel_index(np.argmax(img), (img.shape[0], img.shape[1]))
    img_mass = center_of_mass(img)
    return ((img_max[0] - img_mass[0]) ** 2 + (img_max[1] - img_mass[1]) ** 2) ** 0.5


def dist_max_mass_base(imgc):
    img_max = np.unravel_index(np.argmax(imgc), (imgc.shape[0], imgc.shape[1]))
    img_mass = center_of_mass(imgc)
    return ((img_max[0] - img_mass[0]) ** 2 + (img_max[1] - img_mass[1]) ** 2) ** 0.5


def color_dist_max_mass(fpath):
    img = imread(fpath)
    result = np.zeros(3)
    for i in xrange(3):
        tmp = erosion(img[:, :, i], disk(5))
        result[i] = dist_max_mass_base(tmp)
    return result


def erodes(fpath):
    img = imread(fpath, as_grey=True)
    output_arr = np.zeros(6)

    img_d = erosion(img, disk(2))
    output_arr[0] = np.mean(img_d)
    output_arr[1] = np.std(img_d)

    img_d = erosion(img, disk(5))
    output_arr[2] = np.mean(img_d)
    output_arr[3] = np.std(img_d)

    img_d = erosion(img, disk(8))
    output_arr[4] = np.mean(img_d)
    output_arr[5] = np.std(img_d)
    return output_arr


def rgb_vals(fpath):
    img = imread(fpath)
    flattened = img.sum(2)
    flattened = flattened > 0.0
    red = img[:, :, 0]
    red = red[flattened]
    red_m = np.mean(red, dtype=np.float64)
    green = img[:, :, 1]
    green = green[flattened]
    green_m = np.mean(green, dtype=np.float64)
    blue = img[:, :, 2]
    blue = blue[flattened]
    blue_m = np.mean(blue, dtype=np.float64)
    if red_m == 0:
        red_m = np.mean(img[:, :, 0])
    if green_m == 0:
        green_m = np.mean(img[:, :, 1])
    if blue_m == 0:
        blue_m = np.mean(img[:, :, 2])

    return np.array([red_m / green_m, blue_m / red_m, green_m / blue_m])


def hist(fpath):
    img = imread(fpath, as_grey=True)
    histg = histogram(img, 10)[0]
    return histg / (0.01 * img.shape[0] * img.shape[1])


def zernike_mom(fpath):
    img = imread(fpath, as_grey=True)
    img = erosion(img, disk(2))
    return zernike_moments(img, radius=10, degree=8)


def perim(fpath):
    img = read_and_otsu_bw(fpath)
    return 1. * np.array([perimeter(img, 4), perimeter(img, 8)])


def skeleton(fpath):
    img = read_and_otsu_bw(fpath)
    # return np.count_nonzero(skeletonize(img)) / (1. * img.shape[0] * img.shape[1])
    return np.count_nonzero(thin(img))


def move_to(name):
    datapath = path.join(path.dirname(path.realpath(__file__)), path.pardir)
    datapath = path.join(datapath, '../gzoo_data', 'images', name)
    print path.normpath(datapath)
    return path.normpath(datapath)


def labels():
    datapath = path.join(path.dirname(path.realpath(__file__)), path.pardir)
    datapath = path.join(datapath, '../gzoo_data', 'train_solution.csv')
    return path.normpath(datapath)


def res(no):
    datapath = path.join(path.dirname(path.realpath(__file__)), path.pardir)
    tmp_str = 'result' + str(no) + '.csv'
    datapath = path.join(datapath, '../gzoo_data', tmp_str)
    return path.normpath(datapath)


def perim_minus_skel(fpath, features):
    done_perim = features['perim']
    skel = features['skeleton']
    return (done_perim - skel) / done_perim


def zernike_mom_new(fpath, features):
    f = features['zernike_mom']
    return np.delete(f, [0, 17, 21])


def color_std_new(fpath, features):
    f = features['color_std']
    return np.delete(f, [1])


def erodes_new(fpath, features):
    f = features['erodes']
    return np.delete(f, [1, 3])


def rprops(fpath):
    img = imread(fpath, as_grey=True)
    img = img[40:img.shape[0]-40, 40:img.shape[1]-40]


    thresh = skimage.filter.threshold_otsu(img)
    rimg = img > thresh
    rimg = erosion(rimg, disk(2))

    label_image = label(rimg)
    max_ar = 0
    eig1 = 0
    eig2 = 0
    rad = 0
    per = 0

    for region in regionprops(label_image):
        if max_ar < region['area']:
            max_ar = region['area']

    for region in regionprops(label_image):
        if region['area'] == max_ar:
            eigs = region['inertia_tensor_eigvals']
            eig1 = eigs[0]
            eig2 = eigs[1]
            rad = region['equivalent_diameter'] / region['minor_axis_length']
            per = region['perimeter'] / region['equivalent_diameter']

    return np.array([eig1, eig2, rad, per])


def c_offset(fpath):
    img = imread(fpath, as_grey=True)
    img = img[40:img.shape[0]-40, 40:img.shape[1]-40]

    thresh = skimage.filter.threshold_otsu(img)
    rimg = img > thresh
    rimg = erosion(rimg, disk(2))

    label_image = label(rimg)
    dist_offs = 0

    max_ar = 0

    for region in regionprops(label_image):
        if max_ar < region['area']:
            max_ar = region['area']

    for region in regionprops(label_image):
        if region['area'] == max_ar:
            bb = region['bbox']
            cent = np.array([(bb[2] + bb[0]) / 2, (bb[3] + bb[1]) / 2])
            centr = region['centroid']
            dist_offs = np.sqrt((cent[1] - centr[1]) ** 2 + (cent[0] - centr[0]) ** 2) / region['minor_axis_length']
            # print region['moments_hu']

    return dist_offs


def new_hu(fpath):
    img = imread(fpath, as_grey=True)
    img = img[40:img.shape[0]-40, 40:img.shape[1]-40]

    thresh = skimage.filter.threshold_otsu(img)
    rimg = img > thresh
    rimg = erosion(rimg, disk(2))

    label_image = label(rimg)
    result = np.zeros(7)

    max_ar = 0

    for region in regionprops(label_image):
        if max_ar < region['area']:
            max_ar = region['area']

    for region in regionprops(label_image):
        if region['area'] == max_ar:
            result[:] = region['moments_hu']

    return result


def newer_hu(fpath, features):
    f = features['new_hu']
    a = [0, 1, 2, 3, 5]
    return f[a]


def bbox_size(fpath):
    img = imread(fpath, as_grey=True)
    img = img[40:img.shape[0]-40, 40:img.shape[1]-40]

    thresh = skimage.filter.threshold_otsu(img)
    img = img > thresh
    img = erosion(img, disk(2))

    c_area = 0
    a_del_b = 0

    label_image = label(img)
    max_ar = 0
    for region in regionprops(label_image):
        if max_ar < region['area']:
            max_ar = region['area']

    for region in regionprops(label_image):
        if region['area'] < max_ar:
            coords = region['coords']
            for i in xrange(coords.shape[0]):
                img[coords[i, 0], coords[i, 1]] = 0
        else:
            c_area = region['area'] / (1. * region['convex_area'])
            a_del_b = region['major_axis_length'] / region['minor_axis_length']

    nz = np.transpose(np.nonzero(img))
    #
    # plt.imshow(img)
    # plt.show()
    if nz.shape[0] == 0:
        return np.zeros(3)
    else:
        x_nz = nz[:, 0]
        y_nz = nz[:, 1]
        x_min = np.amin(x_nz)
        x_max = np.amax(x_nz)
        y_min = np.amin(y_nz)
        y_max = np.amax(y_nz)
        box_size = 1. * (y_max - y_min + 1) * (x_max - x_min + 1)
        g_size = np.count_nonzero(img)
        return np.array([g_size / box_size, c_area, a_del_b])


def realstuff(attempt, predict=True):
    testset_path = move_to('test')
    trainset_path = move_to('train')
    labelspath = labels()
    #
    testdata = UnlabeledDataSet(testset_path, path.dirname(path.realpath(__file__)), file_suffix='.jpg')
    traindata = LabeledDataSet(trainset_path, path.dirname(path.realpath(__file__)), labelspath, file_suffix='.jpg')

    print testdata.return_feature_list()

    feature_list = ['color_means', 'chull', 'peaks', 'color_percentage', 'label_regions',
                    'central_pixel', 'galaxy_size', 'means_and_std', 'otsu_val', 'color_otsu_val', 'dist_max_mass',
                    'color_dist_max_mass', 'rgb_vals', 'hist', 'zernike_mom_new',
                    'color_std_new', 'erodes_new', 'perim_minus_skel', 'bbox_size', 'rprops', 'c_offset', 'newer_hu']

    # feature_list = 'all'
    # lbs = traindata.return_labels_numpy(True)

    # traindata.extract_feature(new_hu, verbose=1000)
    traindata.extract_feature_dependent_feature(newer_hu, verbose=1000, force_extraction=True)
    # traindata.extract_feature_dependent_feature(zernike_mom_new, verbose=1000, force_extraction=True)
    # traindata.extract_feature_dependent_feature(color_std_new, verbose=1000, force_extraction=True)
    # traindata.extract_feature_dependent_feature(erodes_new, verbose=1000, force_extraction=True)
    print 'TESTDATA'
    # testdata.extract_feature(new_hu, verbose=1000)
    testdata.extract_feature_dependent_feature(newer_hu, verbose=1000, force_extraction=True)
    # testdata.extract_feature_dependent_feature(zernike_mom_new, verbose=1000, force_extraction=True)
    # testdata.extract_feature_dependent_feature(color_std_new, verbose=1000, force_extraction=True)
    # testdata.extract_feature_dependent_feature(erodes_new, verbose=1000, force_extraction=True)
    flist = testdata.return_feature_list_numpy()

    print 'feature list', flist
    s_step = 0
    for fl in enumerate(flist):
        fl_tuple = fl[1]
        if fl_tuple[0] in feature_list:
            print 'length of feature', fl_tuple[0], '=', fl_tuple[1]
            s_step += fl_tuple[1]
    train_features = traindata.return_features_numpy(feature_list)
    train_labels = traindata.return_labels_numpy(True)

    test_features = testdata.return_features_numpy(feature_list)
    test_ex = test_features.shape[0]
    results = np.zeros([test_ex, 37])
    print 'feature vector dimension: ' + str(train_features.shape[1])
    class_lengths = [('c1', 3), ('c2', 2), ('c3', 2), ('c4', 2), ('c5', 4), ('c6', 2), ('c7', 3), ('c8', 7), ('c9', 3),
                     ('c10', 3), ('c11', 6)]
    #
    spoint = 0

    importances = np.zeros([train_features.shape[1], 11])
    if predict is True:
        for i in enumerate(class_lengths):
            ind_el = i[1]
            print 'classifying class ' + str(ind_el[0])
            curr_length = ind_el[1]
            tmp_res = train_labels[:, spoint:spoint + curr_length]
            labels_res = np.argmax(tmp_res, 1)

            clf = GradientBoostingClassifier(n_estimators=120, max_depth=5)
            clf.fit(train_features, labels_res)
            importances[:, i[0]] = clf.feature_importances_
            probs = clf.predict_proba(test_features)

            class_name = ind_el[0]

            if class_name == 'c2':
                multiplier = results[:, 1]
            elif class_name == 'c3':
                multiplier = results[:, 4]
            elif class_name == 'c4':
                multiplier = results[:, 4]
            elif class_name == 'c5':
                multiplier = results[:, 4]
            elif class_name == 'c7':
                multiplier = results[:, 0]
            elif class_name == 'c8':
                multiplier = results[:, 13]
            elif class_name == 'c9':
                multiplier = results[:, 3]
            elif class_name == 'c10':
                multiplier = results[:, 7]
            elif class_name == 'c11':
                multiplier = results[:, 7]
            else:
                multiplier = 1.0

            if len(probs.shape) > 1:
                for j in xrange(probs.shape[1]):
                    probs[:, j] *= multiplier
            else:
                probs[:] *= multiplier

            results[:, spoint:spoint + curr_length] = probs
            spoint += curr_length

        header = ['GalaxyID', 'Class1.1', 'Class1.2', 'Class1.3', 'Class2.1', 'Class2.2', 'Class3.1', 'Class3.2', 'Class4.1',
                  'Class4.2', 'Class5.1', 'Class5.2', 'Class5.3', 'Class5.4', 'Class6.1', 'Class6.2', 'Class7.1', 'Class7.2',
                  'Class7.3', 'Class8.1', 'Class8.2', 'Class8.3', 'Class8.4', 'Class8.5', 'Class8.6', 'Class8.7', 'Class9.1',
                  'Class9.2', 'Class9.3', 'Class10.1', 'Class10.2', 'Class10.3', 'Class11.1', 'Class11.2', 'Class11.3',
                  'Class11.4', 'Class11.5', 'Class11.6']

        true_ids = testdata.return_real_id()
        path_to_results = res(attempt)
        with open(path_to_results, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for j in xrange(results.shape[0]):
                tmp_r = [true_ids[j]]
                for k in xrange(37):
                    tmp_r.append(results[j, k])
                spamwriter.writerow(tmp_r)
    avg_importances = np.average(importances, 1)
    print 'avg_importances shape', avg_importances.shape
    s_step = 0
    for fl in enumerate(flist):
        fl_tuple = fl[1]
        if fl_tuple[0] in feature_list:
            print 'importance of feature', fl_tuple[0], '=', avg_importances[s_step:s_step + fl_tuple[1]]
            s_step += fl_tuple[1]

    print 'averaged importances:', np.average(importances, 1)

pth = move_to('train')
pth = path.join(pth, '112527.jpg')
# print entropy(pth)
# print means_and_std(pth)
# print daisy_feature(pth).shape
# print hu(pth)
print new_hu(pth)
#
# pth2 = path.join(move_to('train'), '100150.jpg')
# print zernike_mom(pth2).shape
# print otsu_val(pth)
# print color_otsu_val(pth)
# print dist_max_mass(pth)
# print color_dist_max_mass(pth)
realstuff(27, True)
