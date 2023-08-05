import random


def generate(filename, count=1024, numbers_to_generate='random', template_number=0):
    """ outputs a list of hex numbers into a file (in range 0x00 to 0xFF)"""
    count = int(count)
    if count < 1:
        raise ValueError("count cannot be negative, count=%s" % str(count))

    with open(filename, 'w') as f:
        f.write(str(count) + '\n')

        if numbers_to_generate == 'random':
            for i in xrange(count):
                number = hex(random.randint(0, 255))
                f.write(number+'\n')
        elif numbers_to_generate == 'same':
            input_number = int(template_number)
            if input_number != input_number % 256:
                raise ValueError("invalid template_number: %s" % template_number)
            number = hex(input_number)
            for i in xrange(count):
                f.write(number+'\n')
        else:
            raise ValueError("unknown numbers_to_generate=%s" % numbers_to_generate)
