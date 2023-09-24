import webvtt

from lib.parser import Break, Prosody, SSMLTree, S, Text

from utils.helpers import format_vtt_timestamp_to_ms


def convert_vtt_to_ssml(vttfile: str):

    vtt_reader = webvtt.read(vttfile)
    ssml_tree = SSMLTree()
    root = ssml_tree.root
    prev_text = ""
    prev_node = None

    for i in range(len(vtt_reader)):
        caption_line = vtt_reader[i]
        curr_text = caption_line.text.strip('\n ')
        sublines = caption_line.lines
        starttime_ms = format_vtt_timestamp_to_ms(caption_line.start)
        endtime_ms = format_vtt_timestamp_to_ms(caption_line.end)
        duration = endtime_ms - starttime_ms
        create_or_update_break = False

        if curr_text == '' or curr_text.isspace():
            create_or_update_break = True
            break_duration = duration
            node = None
        elif (curr_text[0] == '[' and curr_text[-1] == ']'):
            node = Break(time=f"{duration}ms")
        elif prev_text == curr_text:
            create_or_update_break = True
            break_duration = duration
            node = None 
        elif prev_text == sublines[0].strip('\n '):
            if '<' in sublines[1]:
                starttime = sublines[1][sublines[1].find('<') + 1: sublines[1].find('>')]
                starttime_ms = format_vtt_timestamp_to_ms(starttime)
            curr_text = curr_text[len(prev_text): ].strip('\n ')
            duration = endtime_ms - starttime_ms
            if curr_text[0] == '[' and curr_text[-1] == ']':
                node = Break(time=f'{duration}ms')
            else:
                node = S()
                node.add_child(Prosody(duration=f'{duration}ms')).add_child(Text(curr_text))
            # create_or_update_break = True
            # break_duration = starttime_ms - format_vtt_timestamp_to_ms(caption_line.start)
        else:
            node = S()
            node.add_child(Prosody(duration=f'{duration}ms', rate='fast')).add_child(Text(curr_text))
        
        if create_or_update_break:
            if prev_node is not None and isinstance(prev_node, Break):
                new_duration = int(prev_node.time.replace('ms', '')) + break_duration
                prev_node.time = f'{new_duration}ms'
            else:
                break_node = Break(time=f'{break_duration}ms')
                root.add_child(break_node)
                prev_node = break_node
        prev_text = curr_text
        if node is not None:
            root.add_child(node)
            prev_node = node
    return ssml_tree
