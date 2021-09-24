import numpy
import struct
from sklearn.neighbors import KNeighborsClassifier
# version: sklearn-0.24.2
 
def decode_idx3_ubyte(idx3_ubyte_file):
    bin_data = open(idx3_ubyte_file, 'rb').read()
    offset = 0
    fmt_header = '>iiii'
    magic_number, num_images, num_rows, num_cols = struct.unpack_from(fmt_header, bin_data, offset)
    image_size = num_rows * num_cols
    offset += struct.calcsize(fmt_header)
    fmt_image = '>' + str(image_size) + 'B'
    images = numpy.empty((num_images, num_rows, num_cols))
    for i in range(num_images):
        images[i] = numpy.array(struct.unpack_from(fmt_image, bin_data, offset)).reshape((num_rows, num_cols))
        offset += struct.calcsize(fmt_image)
    return images.tolist()
 
def decode_idx1_ubyte(idx1_ubyte_file):
    bin_data = open(idx1_ubyte_file, 'rb').read()
    offset = 0
    fmt_header = '>ii'
    magic_number, num_images = struct.unpack_from(fmt_header, bin_data, offset)
    offset += struct.calcsize(fmt_header)
    fmt_image = '>B'
    labels = numpy.empty(num_images)
    for i in range(num_images):
        labels[i] = struct.unpack_from(fmt_image, bin_data, offset)[0]
        offset += struct.calcsize(fmt_image)
    return labels.tolist()
 
def main():
    # load datasets
    print('loading datasets ...')
    train_images = decode_idx3_ubyte('data/train-images.idx3-ubyte')
    print('train_images loaded')
    train_labels = decode_idx1_ubyte('data/train-labels.idx1-ubyte')
    print('train_labels loaded')
    test_images = decode_idx3_ubyte('data/t10k-images.idx3-ubyte')
    print('test_images loaded')
    test_labels = decode_idx1_ubyte('data/t10k-labels.idx1-ubyte')
    print('test_labels loaded')
    # concatenate image rows 
    print('concatenate image rows ...')
    train_images_concatenated = []
    for img in train_images:
        train_images_concatenated.append(numpy.concatenate(img))
    test_images_concatenated = []
    for img in test_images:
        test_images_concatenated.append(numpy.concatenate(img))        
    print('image rows concatenated')
    # create knn
    print('creating knn ...')
    k_nearest_neighbors = KNeighborsClassifier(n_neighbors=3)
    # train knn
    print('training knn ...')   
    k_nearest_neighbors.fit(train_images_concatenated, train_labels)
    print('train completed')
    # test
    print('testing ...')   
    predicted_labels = []
    for test in range(len(test_labels)):
        predicted_label = k_nearest_neighbors.predict([test_images_concatenated[test]])
        predicted_labels.append(predicted_label)
    print('test completed')
    # report the results
    print('reporting the results ...')   
    number_of_true = 0
    number_of_false = 0
    digit_number_of_true = [0,0,0,0,0,0,0,0,0,0]
    digit_number_of_false = [0,0,0,0,0,0,0,0,0,0]
    for i in range(len(test_labels)):
        if predicted_labels[i] == test_labels[i]:
            number_of_true += 1
            digit_number_of_true[int(test_labels[i])] += 1
        else:
            number_of_false += 1
            digit_number_of_false[int(test_labels[i])] += 1
    total_precision = number_of_true / (number_of_true + number_of_false)
    print('total precision:')
    print(total_precision)
    digit_precision = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    for digit in range(10):
        digit_precision[digit] = digit_number_of_true[digit] / (digit_number_of_true[digit] + digit_number_of_false[digit])
        print('digit ' + str(digit) + ' precision:')
        print(digit_precision[digit])            
if __name__ == '__main__':
    main()
