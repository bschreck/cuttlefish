# emacs-mode: -*- python-*-
from ControlElement import ControlElement
from LogicalDisplaySegment import LogicalDisplaySegment
class PhysicalDisplayElement(ControlElement):
    __module__ = __name__
    __doc__ = ' Class representing a display on the controller '
    _ascii_translations = {'0': 48,
     '1': 49,
     '2': 50,
     '3': 51,
     '4': 52,
     '5': 53,
     '6': 54,
     '7': 55,
     '8': 56,
     '9': 57,
     'A': 65,
     'B': 66,
     'C': 67,
     'D': 68,
     'E': 69,
     'F': 70,
     'G': 71,
     'H': 72,
     'I': 73,
     'J': 74,
     'K': 75,
     'L': 76,
     'M': 77,
     'N': 78,
     'O': 79,
     'P': 80,
     'Q': 81,
     'R': 82,
     'S': 83,
     'T': 84,
     'U': 85,
     'V': 86,
     'W': 87,
     'X': 88,
     'Y': 89,
     'Z': 90,
     'a': 97,
     'b': 98,
     'c': 99,
     'd': 100,
     'e': 101,
     'f': 102,
     'g': 103,
     'h': 104,
     'i': 105,
     'j': 106,
     'k': 107,
     'l': 108,
     'm': 109,
     'n': 110,
     'o': 111,
     'p': 112,
     'q': 113,
     'r': 114,
     's': 115,
     't': 116,
     'u': 117,
     'v': 118,
     'w': 119,
     'x': 120,
     'y': 121,
     'z': 122,
     '@': 64,
     ' ': 32,
     '!': 33,
     '"': 34,
     '.': 46,
     ',': 44,
     ':': 58,
     ';': 59,
     '?': 63,
     '<': 60,
     '>': 62,
     '[': 91,
     ']': 93,
     '_': 95,
     '-': 45,
     '|': 124,
     '&': 38,
     '^': 94,
     '~': 126,
     '`': 96,
     "'": 39,
     '%': 37,
     '(': 40,
     ')': 41,
     '/': 47,
     '\\': 92}

    def __init__(self, width_in_chars, num_segments):
        assert (width_in_chars != None)
        assert (num_segments != None)
        assert isinstance(width_in_chars, int)
        assert isinstance(num_segments, int)
        ControlElement.__init__(self)
        self._width = width_in_chars
        self._logical_segments = []
        self._translation_table = PhysicalDisplayElement._ascii_translations
        width_without_delimiters = ((self._width - num_segments) + 1)
        width_per_segment = int((width_without_delimiters / num_segments))
        for index in range(num_segments):
            new_segment = LogicalDisplaySegment(width_per_segment, self.update)
            self._logical_segments.append(new_segment)

        self._message_header = None
        self._message_tail = None
        self._message_part_delimiter = None
        self._message_clear_all = None
        self._block_messages = False



    def disconnect(self):
        ControlElement.disconnect(self)
        for segment in self._logical_segments:
            segment.disconnect()

        self._logical_segments = None
        self._translation_table = None
        self._message_header = None
        self._message_tail = None
        self._message_part_delimiter = None
        self._message_clear_all = None



    def set_translation_table(self, translation_table):
        assert (translation_table != None)
        assert isinstance(translation_table, dict)
        assert isinstance(translation_table['?'], int)
        self._translation_table = translation_table



    def set_message_parts(self, header, tail, delimiter = None):
        assert ((delimiter is None) or isinstance(delimiter, tuple))
        assert isinstance(header, tuple)
        assert isinstance(tail, tuple)
        self._message_header = header
        self._message_tail = tail
        self._message_part_delimiter = delimiter



    def set_clear_all_message(self, message):
        assert isinstance(message, tuple)
        self._message_clear_all = message



    def set_block_messages(self, block):
        assert isinstance(block, type(False))
        if (block != self._block_messages):
            self._block_messages = block



    def segment(self, index):
        assert (index != None)
        assert isinstance(index, int)
        assert (index in range(len(self._logical_segments)))
        return self._logical_segments[index]



    def update(self):
        assert (self._message_header != None)
        if ((len(self._logical_segments) > 0) and (not self._block_messages)):
            message = self._message_header
            for segment in self._logical_segments:
                message += segment.position_identifier()
                message += tuple([ self._translate_char(c) for c in segment.display_string() ])
                if ((self._message_part_delimiter != None) and (segment != self._logical_segments[-1])):
                    message += self._message_part_delimiter

            message += self._message_tail
            self.send_midi(message)



    def display_message(self, message):
        assert (self._message_header != None)
        assert (message != None)
        assert isinstance(message, str)
        if (not self._block_messages):
            message = LogicalDisplaySegment.adjust_string(message, self._width)
            self.send_midi(((self._message_header + tuple([ self._translate_char(c) for c in message ])) + self._message_tail))



    def reset(self):
        assert ((self._message_clear_all != None) or (self._message_header != None))
        if (not self._block_messages):
            if (self._message_clear_all != None):
                self.send_midi(self._message_clear_all)
            else:
                self.send_midi(((self._message_header + tuple([ self._translate_char(' ') for index in range(self._width) ])) + self._message_tail))



    def _translate_char(self, char_to_translate):
        assert (char_to_translate != None)
        assert (isinstance(char_to_translate, str) or isinstance(char_to_translate, unicode))
        assert (len(char_to_translate) == 1)
        result = 63
        if (char_to_translate in self._translation_table.keys()):
            result = self._translation_table[char_to_translate]
        else:
            result = self._translation_table['?']
        return result




# local variables:
# tab-width: 4
