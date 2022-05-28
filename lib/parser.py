from abc import ABC, abstractmethod
from re import L
import stat

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
         
            
        
class SSMLEncloseTag (BaseTag):

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
                and
            node.__class__.__name__ not in self.__allowed_children__):

            raise ValueError(f"{node.__repr__()} is not a valid child for {self.__class__}")
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
        return f'<{tag_name}{attrs}>{children_nodes}</{tag_name}>'


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
            raise IndexError('Index out of bound')

        node = children[n]

        return self.remove_node_and_swap_pointers(node)



    def remove_child_by_id(self):
        pass

    def get_siblings(self):
        siblings  = []
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

    
    def __init__(self, text : str="", *args, **kwargs) -> None:
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
        return self.__text.isupper(*args ,**kwargs)
    
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
        attr_list = { 'time': self.time, 'strength': self.strength, 'xml:id': self.id }
        attrs = " ".join([f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)])
        return f'<break{" " + attrs} />'


class Speak(SSMLEncloseTag):

    __allowed_children__ = "__all__"

    def __init__(self, id=None, lang=None, *args, **kwargs) -> None:
        super().__init__(id, *args, **kwargs)
        self.lang = lang
    
    def  __str__(self) -> str:
        attr_list = { 'xml:lang': self.lang, 'xml:id': self.id }
        attrs = " ".join([f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)])
        return self.format_node(attrs)


class Audio(SSMLEncloseTag):

    __allowed_children__ = [Text]

    def __init__(self, id=None, src=None, clipBegin=None, clipEnd=None, speed=None, repeatCount=None, repeatDur=None, soundLevel=None, *args, **kwargs) -> None:
        super().__init__(id, *args, **kwargs)
        self.src = src
        self.clipBegin = clipBegin
        self.clipEnd = clipEnd
        self.speed = speed
        self.repeatCount = repeatCount
        self.repeatDur = repeatDur
        self.soundLevel = soundLevel
    
    def  __str__(self) -> str:
        attr_list = { 
            'src': self.src, 
            'xml:id': self.id, 
            'clipBegin': self.clipBegin, 
            'clipEnd': self.clipEnd, 
            'speed': self.speed, 
            'repeatCount': self.repeatCount,
            'repeatDur': self.repeatDur,
            'soundLevel': self.soundLevel
        }
        attrs = " ".join([f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)])
        return self.format_node(attrs)


class Media(SSMLEncloseTag):

    __allowed_children__ = [Speak, Audio]

    def __init__(self, id=None, begin=0, end=None, repeatCount=None, repeatDur=None, soundLevel=0, fadeInDur=0, fadeOutDur=0, *args, **kwargs) -> None:
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
            'begin': self.begin, 
            'xml:id': self.id, 
            'end' : self.end,
            'repeatCount': self.repeatCount,
            'repeatDur': self.repeatDur,
            'soundLevel': self.soundLevel,
            'fadeInDur': self.fadeInDur,
            'fadeOutDur': self.fadeOutDur
        }
        attrs = " ".join([f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)])
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
            'xml:id': self.id, 
        }
        attrs = " ".join([f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)])
        return self.format_node(attrs)

class Prosody(SSMLEncloseTag):

    __allowed_children__ = [Text]
    
    def __init__(self, id=None, rate=None, pitch=None, volume=None, duration=None, *args, **kwargs) -> None:
        super().__init__(id, *args, **kwargs)
        self.rate = rate
        self.pitch = pitch
        self.volume = volume
        self.duration = duration


    def __str__(self) -> str:
        attr_list = { 
            'xml:id': self.id, 
            'rate' : self.rate,
            'pitch': self.pitch,
            'volume': self.volume,
            'duration': self.duration,
        }

        attrs = " ".join([f'{attr}="{val}"' for attr, val in attr_list.items() if bool(val)])
        return self.format_node(attrs)




class SSMLTree:

    def __init__(self) -> None:
        self.__root = Speak(id='root', lang='en')

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
        with open(f'{filename}.xml', 'w') as f:
            f.write(str(self.__root))


    def to_markup_string(self):
        return str(self.__root)

    
    @staticmethod
    def parse(smml_text):
        pass



        
top = SSMLTree().root
root = top.add_child(Par()).add_child(Media(begin='0s', id='audio_body'))
# self.root = SSMLTag()
root = root.add_child(Speak())
root.add_child(Text("Hello, world!"))
root.add_child(Text("Man damnm")).upper(inplace=True)
root.add_child(Break(time="20s"))


print(str(top))
