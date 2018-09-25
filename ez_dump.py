#! /usr/bin/env python2
# -*- coding:utf-8 -*-


class UniqueWordFilter(object):
    def __init__(self):
        self.hash_list = []

    def filter(self, word_list):
        rest_list = []
        for word in word_list:
            if isinstance(word, unicode):
                word = word.encode('utf-8')
            if word in self.hash_list:
                continue
            else:
                self.hash_list.append(word)
                rest_list.append(word)
        return rest_list


class EzDumper(object):
    def __init__(self, out_file, total=0, tag=''):
        self.out_file = out_file
        self.tag = tag
        self.total = total
        self.current = 0
        self.unique_filter = UniqueWordFilter()

    def set_total(self, total):
        self.total = total

    def dump(self, current, debug, word_list=''):
        if not current:
            current = self.current
        else:
            self.current = current
        percent = None
        if self.total > 0:
            percent = 100.0 * current / self.total

        log_msg = '[%s][%.2f%%][%s / %s] %s:%s \n' % (self.tag, percent, current, self.total, debug, word_list)
        print log_msg

        if not word_list:
            return
        if not isinstance(word_list, (list, tuple, set)):
            word_list = [word_list]
        word_list = self.unique_filter.filter(word_list)

        with open(self.out_file, 'a') as f:
            for word in word_list:
                f.write(word)
                f.write('\n')


if __name__ == '__main__':
    # ez = EzDumper('test.txt', 10, 'Test')
    # for i in xrange(10):
    #     ez.dump(i, '?' * i)
    #
    # ez.dump(None, 'debug:msg')
    # ez.dump(None, 'data', 'data.data')
    # ez.dump(None, 'data', 'a')
    # ez.dump(None, 'data', 'a')
    # ez.dump(None, 'data', 'a')

    unique_filter = UniqueWordFilter()
    x = ['блокування екрану як у айфоні 7', u'блокування екрану як у айфоні 7']
    print len(unique_filter.filter(x))
