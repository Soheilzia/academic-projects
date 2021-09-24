import numpy
import struct
from hmmlearn.hmm import GaussianHMM
# version: hmmlearn-0.2.5
 
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
    train_images_one_state = []
    for img in train_images:
        train_images_one_state.append(numpy.concatenate(img))
    test_images_one_state = []
    for img in test_images:
        test_images_one_state.append(numpy.concatenate(img))        
    print('image rows concatenated')
    # create hmm for each digit
    print('creating hmms ...')
    hidden_markov_models = []
    for digit in range(10):
        hidden_markov_models.append(GaussianHMM())
    print('for each digit an hmm created')
    # seperate dataset corresponding to each digit in order to train
    print('seperating datasets ...')
    digit_train_images = [[],[],[],[],[],[],[],[],[],[]]
    for i in range(0, len(train_labels)):
        digit_train_images[int(train_labels[i])].append(train_images_one_state[i])
    digit_test_images = [[],[],[],[],[],[],[],[],[],[]]
    for i in range(0, len(test_labels)):
        digit_test_images[int(test_labels[i])].append(test_images_one_state[i])
    print('for each digit image dataset created')
    # train each hmm
    print('training hmms ...')   
    for digit in range(10):
        hidden_markov_models[digit].fit(digit_train_images[digit])
        print('hmm ' + str(digit) + ' trained')
    print('train completed')
    # test
    print('testing ...')   
    predicted_labels = []
    for test in range(len(test_labels)):
        max_score = -numpy.inf
        predicted_label = -1
        for digit in range(10):
            temp_score = hidden_markov_models[digit].score([test_images_one_state[test]])
            if temp_score > max_score:
                max_score = temp_score            
                predicted_label = digit
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
