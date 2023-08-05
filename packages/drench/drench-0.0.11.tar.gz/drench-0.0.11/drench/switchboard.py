import os
import bitarray
import copy
import json
from collections import namedtuple


start_end_pair = namedtuple('start_end_pair', 'start end')


def all_subdirs(dir):
    subdirs = []
    dir_walker = os.walk(os.getcwd())
    while 1:
        try:
            subdirs.append(dir_walker.next()[0])
        except:
            return subdirs


def build_dirs(files):
    '''
    Build necessary directories based on a list of file paths
    '''
    for i in files:
        if type(i) is list:
            build_dirs(i)
            continue
        else:
            if len(i['path']) > 1:
                addpath = os.path.join(os.getcwd(), *i['path'][:-1])
                subdirs = all_subdirs(os.getcwd())
                if addpath and addpath not in subdirs:
                    os.makedirs(addpath)
                    print 'just made path', addpath


def get_want_file_pos(file_list):
    '''
    Ask the user which files in file_list he or she is interested in.
    Return indices for the files inside file_list
    '''
    want_file_pos = []
    print '\nFiles contained:\n'
    for i in file_list:
        print(os.path.join(*i['path']))
    while 1:
        all_answer = raw_input('\nDo you want all these files? (y/n): ')
        if all_answer in ('y', 'n'):
            break
    if all_answer == 'y':
        want_file_pos = range(len(file_list))
        return want_file_pos
    if all_answer == 'n':
        for j, tfile in enumerate(file_list):
            while 1:
                file_answer = raw_input('Do you want {}? '
                                        '(y/n): '.format(os.path.join
                                                        (*tfile['path'])))

                if file_answer in ('y', 'n'):
                    break
            if file_answer == 'y':
                want_file_pos.append(j)
        print "Here are all the files you want:"
        for k in want_file_pos:
            print os.path.join(*file_list[k]['path'])
        return want_file_pos


def get_file_starts(file_list):
    '''
    Return the starting position (in bytes) of a list of files by
    iteratively summing their lengths
    '''
    starts = []
    total = 0
    for i in file_list:
        starts.append(total)
        total += i['length']
    print starts
    return starts


def get_rightmost_index(byte_index=0, file_starts=[0]):

    '''
    Retrieve the highest-indexed file that starts at or before byte_index.
    '''
    i = 1
    while i <= len(file_starts):
        start = file_starts[-i]
        if start <= byte_index:
            return len(file_starts) - i
        else:
            i += 1
    else:
        raise Exception('byte_index lower than all file_starts')


def get_heads_tails(want_file_pos=[], file_starts=[], num_pieces=0,
                    piece_length=0):
    heads_tails = []
    for i in want_file_pos:
        head_tail = get_head_tail(want_index=i, file_starts=file_starts,
                                  num_pieces=num_pieces,
                                  piece_length=piece_length)
        heads_tails.append(head_tail)
    return heads_tails


def get_head_tail(want_index=0, file_starts=[], num_pieces=0,
                  piece_length=0):

    # Find the byte value where the file starts
    byte_start = file_starts[want_index]

    # The firt piece we care about is at the point where the combined length
    # is *just* less than or equal to byte_start
    first_piece = byte_start // piece_length

    # We want it in a separate variable so we can iterate
    piece_pos = first_piece

    # Find if we want the last file in the torrent
    if want_index == len(file_starts) - 1:
        last_piece = num_pieces - 1

    # Otherwise we want a different piece
    elif want_index < len(file_starts) - 1:
        next_file_start = file_starts[want_index + 1]
        while piece_pos * piece_length < next_file_start:
            piece_pos += 1

        # We want the piece *before* the first one after the next file starts
        last_piece = piece_pos - 1

    return start_end_pair(start=first_piece, end=last_piece)


def get_write_index(write_file_description, outfiles):
    # Retrieve the file object whose name matches
    # write_file_description
    i = 0
    while i < len(outfiles):
        if outfiles[i].name == os.path.join(*write_file_description['path']):
            return i
        else:
            i += 1
    else:
        raise Exception('Nothing matches')


def build_bitfield(heads_and_tails=[], num_pieces=0):
    this_bitfield = bitarray.bitarray('0' * num_pieces)
    for i in heads_and_tails:
        for j in range(i.start, i.end + 1):
            this_bitfield[j] = True
    return this_bitfield


class Switchboard(object):
    def __init__(self, dirname='', file_list=[], piece_length=0, num_pieces=0,
                 multifile=False, download_all=False, vis_socket=None):
        self.dirname = dirname
        self.file_list = copy.deepcopy(file_list)
        self.piece_length = piece_length
        self.num_pieces = num_pieces
        self.file_starts = (get_file_starts(self.file_list) if multifile
                            else [0])

        self.download_all = download_all
        self.vis_socket = vis_socket
        self.encoder = json.JSONEncoder()

        if self.download_all:
            self.want_file_pos = range(len(self.file_list))
        elif multifile:
            self.want_file_pos = (get_want_file_pos(self.file_list))
        else:
            self.want_file_pos = [0]

        self.outfiles = []
        self.queued_messages = []
        if self.dirname:
            if not os.path.exists(self.dirname):
                os.mkdir(self.dirname)
            os.chdir(os.path.join(os.getcwd(), self.dirname))
        want_files = [self.file_list[index] for index in self.want_file_pos]
        if multifile:
            build_dirs(want_files)
        for i in self.want_file_pos:
            if multifile:
                thisfile = open(os.path.join(*self.file_list[i]
                                             ['path']), 'w')
            else:
                thisfile = open(self.file_list[i]['path'], 'w')
            self.outfiles.append(thisfile)
        self.heads_and_tails = get_heads_tails(want_file_pos=
                                               self.want_file_pos,
                                               file_starts=self.file_starts,
                                               num_pieces=self.num_pieces,
                                               piece_length=self.piece_length)
        self.bitfield = build_bitfield(self.heads_and_tails,
                                       num_pieces=self.num_pieces)
        self.vis_init()

    def get_next_want_file(self, byte_index, block):
        '''
        Returns the leftmost file in the user's list of wanted files
        (want_file_pos). If the first file it finds isn't in the list,
        it will keep searching until the length of 'block' is exceeded.
        '''
        while block:
            rightmost = get_rightmost_index(byte_index=byte_index,
                                            file_starts=self.file_starts)
            if rightmost in self.want_file_pos:
                return rightmost, byte_index, block
            else:
                    file_start = (self.file_starts
                                  [rightmost])
                    file_length = self.file_list[rightmost]['length']
                    bytes_rem = file_start + file_length - byte_index
                    if len(block) > bytes_rem:
                        block = block[bytes_rem:]
                        byte_index = byte_index + bytes_rem
                    else:
                        block = ''
        else:
            return None

    def set_piece_index(self, piece_index):
        self.piece_index = piece_index

    # TODO -- refactor write to simply map from a piece index to a set
    # of files and byte indices so I can implement seeding.
    # Write should contain a call to another method that returns
    # files and byte ranges
    def write(self, byte_index, block):

        # TODO -- is there a way to catch this exception earlier?
        try:
            a = self.get_next_want_file(byte_index, block)
            file_list_index, write_byte_index, block = a
        except:
            return

        # TODO -- re-think this test
        if (file_list_index is not None and write_byte_index is not None and
                block is not ''):

            index_in_want_files = self.want_file_pos.index(file_list_index)

            # The actual file object to write to
            write_file = self.outfiles[index_in_want_files]

            file_start = self.file_starts[file_list_index]

            # And find where we start writing within the file
            file_internal_index = write_byte_index - file_start

            if write_file.closed:
                return

            write_file.seek(file_internal_index)
            file_length = self.file_list[file_list_index]['length']
            bytes_writable = file_length - file_internal_index

            # If we can't write the entire block
            if bytes_writable < len(block):
                write_file.write(block[:bytes_writable])
                block = block[bytes_writable:]
                write_byte_index = write_byte_index + bytes_writable

                # Find the would-be next highest index
                # (we could be on last file)
                j = self.file_starts.index(file_start) + 1

                # If we're not at the end of the list,
                # keep trying to write
                if j <= self.want_file_pos[-1]:
                    self.write(write_byte_index, block)
                else:
                    return

            # If we can write the entire block
            else:
                write_file.write(block)
                block = ''

    def vis_init(self):
        '''
        Sends the state of the BTC at the time the visualizer connects,
        initializing it.
        '''
        init_dict = {}
        init_dict['kind'] = 'init'
        assert len(self.want_file_pos) == len(self.heads_and_tails)
        init_dict['want_file_pos'] = self.want_file_pos
        init_dict['files'] = self.file_list
        init_dict['heads_and_tails'] = self.heads_and_tails
        init_dict['num_pieces'] = self.num_pieces
        self.broadcast(init_dict)

    def broadcast(self, data_dict):
        '''
        Send to the visualizer (if there is one) or enqueue for later
        '''
        if self.vis_socket:
            self.queued_messages.append(data_dict)
            self.send_all_updates()

    def send_all_updates(self):
        while self.queued_messages:
            # TODO -- ask if this makes sense
            next_message = (self.encoder.encode(self.queued_messages.pop(0)) +
                            '\r\n\r\n')
            self.vis_socket.send(next_message)

    def mark_off(self, index):
        self.bitfield[index] = False

    @property
    def complete(self):
        if any(self.bitfield):
            return False
        else:
            return True

    def close(self):
        for i in self.outfiles:
            i.close()
