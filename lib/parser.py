from abc import ABC, abstractmethod
from re import L
import re
from lib.exceptions import InvalidSSMLSyntax

from utils.constants import (
    CLOSE_TAG_PATTERN,
    ENCLOSED_TAG_PATTERN,
    INLINE_TAG_PATTERN,
    TAG_PATTERN,
    TEXT_PATTERN,
)
from utils.helpers import get_attribute_dict


"""
SSML tags Implemented: text, break, speak, media, audio, seq, par, prosody

A basic object model for the Speech Synthesis Markup Language (SSML) used for text to speech. defined here

https://cloud.google.com/text-to-speech/docs/ssml

"""


class BaseTag(object):
    def __init__(self, id=None, *args, **kwargs) -> None:
        self.id = id
        self.attrib = kwargs
        self.prev_node = None
        self.next_node = None
        self.parent_node = None

    def is_root(self):
        return self.prev_node is None

    def is_tail(self):
        return self.next_node is None


class NodeTraversal:
    @staticmethod
    def find(start_node, tag):
        if not isinstance(start_node, SSMLEncloseTag):
            return None
        traverse_queue = start_node.get_children()

        while len(traverse_queue) != 0:
            node = traverse_queue.pop(0)
            if node.__class__.__name__.lower() == tag:
                return node
            if isinstance(node, SSMLEncloseTag):
                traverse_queue.extend(node.get_children())
        return None

    @staticmethod
    def find_by_id(start_node, id):
        if not isinstance(start_node, SSMLEncloseTag):
            return None
        traverse_queue = start_node.get_children()

        while len(traverse_queue) != 0:
            node = traverse_queue.pop(0)
            if node.id == id:
                return node
            if isinstance(node, SSMLEncloseTag):
                traverse_queue.extend(node.get_children())
        return None

    @staticmethod
    def find_all(start_node, tag):
        if not isinstance(start_node, SSMLEncloseTag):
            return None
        traverse_queue = start_node.get_children()
        matched_nodes = []

        while len(traverse_queue) != 0:
            node = traverse_queue.pop(0)
            if node.__class__.__name__.lower() == tag:
                matched_nodes.append(node)
            if isinstance(node, SSMLEncloseTag):
                traverse_queue.extend(node.get_children())
        return matched_nodes

    @staticmethod
    def traverse_list(start_node):
        traverse_queue = [start_node]
        node_set = set()
        while len(traverse_queue) != 0:
            node = traverse_queue.pop(0)
            if isinstance(node, SSMLEncloseTag):
                children = node.get_children()
                traverse_queue += children
                node_set.add(node)
            elif not isinstance(node, Text):
                node_set.add(node)
        return node_set


class SSMLEncloseTag(BaseTag):

    __allowed_children__ = []

    def __init__(self, id=None, *args, **kwargs) -> None:
        super().__init__(id=id, *args, **kwargs)
        self.child_ptr = None

    def get_children(self):
        res = []

        curr_node = self.child_ptr
        while curr_node is not None:
            res.append(curr_node)
            curr_node = curr_node.next_node
        return res

    def add_child(self, node):
        if self.__allowed_children__ != "__all__" and (
            type(node) not in self.__allowed_children__
            and node.__class__.__name__ not in self.__allowed_children__
        ):

            raise ValueError(
                f"{node.__repr__()} is not a valid child for {self.__class__}"
            )
        if self == node:
            raise ValueError("Can't add the object as it's child")

        if node.parent_node == self:
            raise ValueError("")

        curr_node = self.child_ptr
        if curr_node is not None:
            while curr_node.next_node is not None:
                curr_node = curr_node.next_node

            node.prev_node = curr_node
            curr_node.next_node = node
        else:
            self.child_ptr = node
        node.parent_node = self
        return node

    def format_node(self, attrs) -> str:
        children_nodes = "".join([str(node) for node in self.get_children()])
        tag_name = self.__class__.__name__.lower()
        if attrs:
            attrs = " " + attrs
        return f"<{tag_name}{attrs}>{children_nodes}</{tag_name}>"

    def remove_node_and_swap_pointers(self, node):
        next_node = node.next_node
        if node.prev_node is not None:
            node.prev_node.next_node = next_node
        if next_node is not None:
            next_node.prev_node = node.prev_node
        node.next_node = None
        node.prev_node = None

        return node

    def remove_child_node(self, node):
        if node not in self.get_children():
            return None
        node = self.remove_node_and_swap_pointers(node)
        return node

    def remove_nth_child(self, n):
        children = self.get_children()
        if n > len(children):
            raise IndexError("Index out of bound")

        node = children[n]

        return self.remove_node_and_swap_pointers(node)

    def remove_child_by_id(self):
        pass

    def get_siblings(self):
        siblings = []
        prev_sib_node = self.prev_node
        while prev_sib_node is not None:
            siblings.append(prev_sib_node)
            prev_sib_node = prev_sib_node.prev_node

        next_sib_node = self.next_node
        while next_sib_node is not None:
            siblings.append(next_sib_node)
            next_sib_node = next_sib_node.next_node
        return siblings

    def find(self, tag):
        return NodeTraversal.find(self, tag)

    def find_all(self, tag):
        return NodeTraversal.find_all(self, tag)

    def find_by_id(self, id):
        return NodeTraversal.find_by_id(self, id)


class Text(BaseTag):
    def __init__(self, text: str = "", *args, **kwargs) -> None:
        super().__init__(None, *args, **kwargs)
        if type(text) != str:
            raise TypeError("Invalid type, text only recieves object of type str")
        self.__text = text

    def startswith(self, *args, **kwargs):
        return self.__text.startswith(*args, **kwargs)

    def endswith(self, *args, **kwargs):
        return self.__text.endswith(*args, **kwargs)

    def replace(self, *args, **kwargs):
        return self.__text.replace(*args, **kwargs)

    def upper(self, inplace=False, *args, **kwargs):
        if inplace:
            self.__text = self.__text.upper()
        return self.__text.upper(*args, **kwargs)

    def lower(self, inplace=False, *args, **kwargs):
        if inplace:
            self.__text = self.__text.lower()
        return self.__text.upper(*args, **kwargs)

    def isupper(self, *args, **kwargs):
        return self.__text.isupper(*args, **kwargs)

    def islower(self, *args, **kwargs):
        return self.__text.islower(*args, **kwargs)

    def __str__(self) -> str:
        return self.__text


class Break(BaseTag):
    def __init__(self, id=None, time=None, strength=None, *args, **kwargs) -> None:
        super().__init__(id, *args, **kwargs)
        self.time = time
        self.strength = strength

    def __str__(self) -> str:
        attr_list = {"time": self.time, "strength": self.strength, "xml:id": self.id}
        attrs = " ".join(
            [f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)]
        )
        return f'<break{" " + attrs} />'


class Speak(SSMLEncloseTag):

    __allowed_children__ = "__all__"

    def __init__(self, id=None, lang=None, *args, **kwargs) -> None:
        super().__init__(id, *args, **kwargs)
        self.lang = lang

    def __str__(self) -> str:
        attr_list = {"xml:lang": self.lang, "xml:id": self.id}
        attrs = " ".join(
            [f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)]
        )
        return self.format_node(attrs)


class Audio(SSMLEncloseTag):

    __allowed_children__ = [Text]

    def __init__(
        self,
        id=None,
        src=None,
        clipBegin=None,
        clipEnd=None,
        speed=None,
        repeatCount=None,
        repeatDur=None,
        soundLevel=None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(id, *args, **kwargs)
        self.src = src
        self.clipBegin = clipBegin
        self.clipEnd = clipEnd
        self.speed = speed
        self.repeatCount = repeatCount
        self.repeatDur = repeatDur
        self.soundLevel = soundLevel

    def __str__(self) -> str:
        attr_list = {
            "src": self.src,
            "xml:id": self.id,
            "clipBegin": self.clipBegin,
            "clipEnd": self.clipEnd,
            "speed": self.speed,
            "repeatCount": self.repeatCount,
            "repeatDur": self.repeatDur,
            "soundLevel": self.soundLevel,
        }
        attrs = " ".join(
            [f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)]
        )
        return self.format_node(attrs)


class Media(SSMLEncloseTag):

    __allowed_children__ = [Speak, Audio]

    def __init__(
        self,
        id=None,
        begin=0,
        end=None,
        repeatCount=None,
        repeatDur=None,
        soundLevel=0,
        fadeInDur=0,
        fadeOutDur=0,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(id, *args, **kwargs)
        self.begin = begin
        self.end = end
        self.repeatCount = repeatCount
        self.repeatDur = repeatDur
        self.soundLevel = soundLevel
        self.fadeInDur = fadeInDur
        self.fadeOutDur = fadeOutDur

    def __str__(self) -> str:
        attr_list = {
            "begin": self.begin,
            "xml:id": self.id,
            "end": self.end,
            "repeatCount": self.repeatCount,
            "repeatDur": self.repeatDur,
            "soundLevel": self.soundLevel,
            "fadeInDur": self.fadeInDur,
            "fadeOutDur": self.fadeOutDur,
        }
        attrs = " ".join(
            [f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)]
        )
        return self.format_node(attrs)


class Seq(SSMLEncloseTag):

    __allowed_children__ = ["Seq", "Par", Media]

    def __init__(self, id=None, *args, **kwargs) -> None:
        super().__init__(id, *args, **kwargs)


class Par(SSMLEncloseTag):

    __allowed_children__ = [Seq, "Par", Media]

    def __init__(self, id=None, *args, **kwargs) -> None:
        super().__init__(id, *args, **kwargs)

    def __str__(self) -> str:
        attr_list = {
            "xml:id": self.id,
        }
        attrs = " ".join(
            [f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)]
        )
        return self.format_node(attrs)


class Prosody(SSMLEncloseTag):

    __allowed_children__ = [Text]

    def __init__(
        self,
        id=None,
        rate=None,
        pitch=None,
        volume=None,
        duration=None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(id, *args, **kwargs)
        self.rate = rate
        self.pitch = pitch
        self.volume = volume
        self.duration = duration

    def __str__(self) -> str:
        attr_list = {
            "xml:id": self.id,
            "rate": self.rate,
            "pitch": self.pitch,
            "volume": self.volume,
            "duration": self.duration,
        }

        attrs = " ".join(
            [f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)]
        )
        return self.format_node(attrs)


tag_pattern_regex = re.compile(ENCLOSED_TAG_PATTERN)
inline_tag_pattern_regex = re.compile(INLINE_TAG_PATTERN)
text_pattern_regex = re.compile(TEXT_PATTERN)
opened_tag_regex = re.compile(TAG_PATTERN)


class SSMLTree:

    token_types = {
        "break": Break,
        "speak": Speak,
        "media": Media,
        "prosody": Prosody,
        "seq": Seq,
        "par": Par,
    }

    def __init__(self) -> None:
        self.__root = Speak(id="root", lang="en")

    @property
    def root(self):
        return self.__root

    def find(self, tag):
        return NodeTraversal.find(self.__root, tag)

    def find_node_by_id(self, id):
        return NodeTraversal.find_by_id(self.__root, id)

    def find_all(self, tag):
        return NodeTraversal.find_all(self.__root, tag)

    def traverse_tree(self):
        return NodeTraversal.traverse_list(self.__root)

    def write_to_file(self, filename):
        with open(f"{filename}.xml", "w") as f:
            f.write(str(self.__root))

    def to_markup_string(self):
        return str(self.__root)

    @staticmethod
    def get_text_index(text: str, substr: str, lastindex: int) -> float:
        try:
            index = text[lastindex:].find(substr)
            return index
        except TypeError:
            return float("inf")

    """
    tgyufug dsd <s><s>iotu <aaaa /> <p>io </p> </s> </s> <P> HJKFUTYFGJH</p>WWWW
    """

    @staticmethod
    def get_child_tags(text: str):
        open_tag_idx = text.find("<")
        opened_tags = []
        opened_tags_attrib = []
        child_tags = []
        while open_tag_idx != -1:
            close_open_tag_idx = text.find(">", open_tag_idx)
            tag = text[open_tag_idx : close_open_tag_idx + 1]
            if inline_tag_pattern_regex.match(tag):
                open_tag_idx = text.find("<", close_open_tag_idx)
                continue
            tag_name, attrib = opened_tag_regex.match(tag).groups()
            opened_tags.append(tag_name)
            opened_tags_attrib.append(attrib)
            next_tag_idx = text.find("<", close_open_tag_idx)
            if next_tag_idx == -1:
                raise InvalidSSMLSyntax("Error unclosed tag")
            close_next_tag_idx = -1
            while len(opened_tags) != 0:
                close_next_tag_idx = text.find(">", next_tag_idx)
                if close_next_tag_idx == -1:
                    raise InvalidSSMLSyntax("Tag not closed!")
                next_tag = text[next_tag_idx : close_next_tag_idx + 1]
                close_tag = re.match(CLOSE_TAG_PATTERN, next_tag)
                opened_tag_match = opened_tag_regex.match(next_tag)
                if close_tag is not None:
                    tag_name = close_tag[1]
                    if tag_name != opened_tags[-1]:
                        raise InvalidSSMLSyntax(
                            f"The last opened tag <{opened_tags[-1]} {opened_tags_attrib[-1]}> was not closed!"
                        )
                    opened_tags.pop()
                    opened_tags_attrib.pop()
                elif opened_tag_match is not None:
                    name, attrib = opened_tag_match.groups()
                    opened_tags.append(name)
                    opened_tags_attrib.append(attrib)

                next_tag_idx = text.find("<", close_next_tag_idx)

            child_tags.append((open_tag_idx, close_next_tag_idx + 1))
            open_tag_idx = text.find("<", close_next_tag_idx)
        res = {"tags": [text[i:j] for i, j in child_tags], "pos": child_tags}
        return res


    @staticmethod
    def parse(ssml_text: str):
        try:
            tag_match = tag_pattern_regex.match(ssml_text).groups()
            if tag_match is None:
                raise InvalidSSMLSyntax('document must be closed in a tag.')
            if tag_match[0].strip() != tag_match[-1].strip():
                raise InvalidSSMLSyntax(f"The tag {tag_match[0]} wasn't closed.")
            attributes = tag_match[1]
            body = tag_match[2]
            try:
                tag_class = SSMLTree.token_types[tag_match[0].strip()]
            except KeyError:
                raise InvalidSSMLSyntax(f"{tagname} is a Invalid tag.")

            root_node = tag_class(**get_attribute_dict(attributes))


            child_tags = SSMLTree.get_child_tags(body)

            text_tokens = [ t for t in text_pattern_regex.findall(body) if t != '']
            tag_tokens = child_tags["tags"]

            cleaned_text = body
            for start_pos, end_pos in child_tags["pos"]:
                cleaned_text = cleaned_text[: start_pos + 1] + cleaned_text[end_pos:]
            inline_tokens = [
                tag[0] for tag in inline_tag_pattern_regex.findall(cleaned_text)
            ]
            token_last_index = {}

            ordered_children = []
            tokens = [text_tokens, tag_tokens, inline_tokens]

            while len(tokens[0]) or len(tokens[1]) or len(tokens[2]):
                min_token_idx = None
                min_token_pos = float("inf")
                for i in range(len(tokens)):
                    if len(tokens[i]) != 0:
                        curr_token = tokens[i][0]
                        lastindex = token_last_index.get(curr_token, 0)
                        tag_pos = SSMLTree.get_text_index(
                            body, curr_token, lastindex
                        )
                        token_last_index[curr_token] = tag_pos
                        if tag_pos < min_token_pos:
                            min_token_pos = tag_pos
                            min_token_idx = i
                token = tokens[min_token_idx].pop(0)
                ordered_children.append(token.strip("\n"))

            childhead = None
            last_node = None
            for i, token in enumerate(ordered_children):
                is_text = re.match('[^<>]+', token)
                is_inline = inline_tag_pattern_regex.match(token)
                is_tag = tag_pattern_regex.match(token)
                if token == '': continue
                if is_text is not None:
                    node = Text(token)
                elif is_inline is not None:
                    _, tagname, tagattrib = is_inline.groups()
                    try:
                        tag_class = SSMLTree.token_types[tagname]
                        attribute_dict = get_attribute_dict(tagattrib)
                        node = tag_class(**attribute_dict)
                    except KeyError:
                        raise InvalidSSMLSyntax(f"{tagname} is a Invalid tag.")
                elif is_tag:
                    node = SSMLTree.parse(token)
                else:
                    raise InvalidSSMLSyntax(f'Invalid pattern {token}.')
                if i == 0:
                    childhead = node
                if last_node is not None:
                    last_node.next_node = node
                    node.prev_node = last_node
                last_node = node
            root_node.child_ptr = childhead
            return root_node
        except Exception as ex:
            raise ex

