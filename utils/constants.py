ACCEPTABLE_TAGS = ['speak', 'media', 'audio', 'par', 'seq', 'prosody']
ACCEPTABLE_INLINE_TAGS = ['break']

ENCLOSED_TAG_PATTERN = r'\<([{0}]+)\s*([^>]*)\>([\w| \s| \d | \W]*)\<\/([{0}]+)\>.*'.format(' | '.join(ACCEPTABLE_TAGS))

TEXT_PATTERN = r'\s*([\w | \s | . | ,]*)(?:<[\w|\s|-]+.*>)'

INLINE_TAG_PATTERN = r'(\<[{0}]\s*[^/>]*/>)'.format('|'.join(ACCEPTABLE_INLINE_TAGS))

