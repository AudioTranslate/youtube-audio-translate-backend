# import subprocess


# text = "There is no evidence that people became more \
# intelligent with time. Foragers knew the secrets of nature long before the \
# Agricultural Revolution, since their survival depended on an intimate knowledge \
# of the animals they hunted and the plants they gathered. Rather than heralding a \
# new era of easy living, the Agricultural Revolution left farmers with lives \
# generally more difficult and less satisfying than those of foragers."

# subprocess.run(['tts', '--text', text, '--out', 'test_out.wav'])
# print('done')


import itertools, functools
import time
# a = functools.reduce(lambda x, y: x + y, )

a = itertools.accumulate(itertools.cycle(map(lambda x: ord(x), "Close")))

for i in a :
    print(i)
    time.sleep(0.8)

