def classify(text, mode):
    text = text.strip()
    text = text.lower()
    warning = True
    if text[0] == '+':
        add_word = True
        text = text[1:]
        text = text.strip()
    else:
        add_word = False
    if text[0] == '-':
        del_word = True
        text = text[1:]
        text = text.strip()
    else:
        del_word = False
    words = text.split()
    if (words[0].startswith('алиса') or words[0].startswith('alice')) and len(words) > 1:
        words = words[1:]
    if words[0].startswith('add') or words[0].startswith('добавь'):
        add_word = True
        words = words[1:]
    if words[0].startswith('delete') or words[0].startswith('del') or words[0].startswith('удали'):
        del_word = True
        words = words[1:]
    if add_word:
        if mode != 0:
            warning = True
        else:
            warning = False
        if del_word:
            answer = ''
            label = 'incorrect'
            warning = True
        elif len(words) == 1:
            label = 'suggest_some_translation&suggest_to_add'
            answer = words[:]
        elif len(words) == 2:
            label = 'add'
            answer = words[:]
        else:
            label = 'translate&suggest_to_add'
            answer = ' '.join(words)
    elif del_word:
        if mode != 0:
            warning = True
        else:
            warning = False
        label = 'del'
        answer = ' '.join(words)
    else:
        label = 'use_mode'
        answer = text
        warning = False

    return {'warning': warning, 'class': label, 'answer': answer}

print(classify('+a', 0))
print(classify('a', 0))
print(classify('a', 3))
print(classify('+a', 3))
print(classify('Alice, add smth', 0))
print(classify('Alice, add smth что-то', 0))
print(classify('Алиса, давай музло', 'game'))
print(classify('Алиса, давай музло', 0))
print(classify('Алиса, добавь музло', 'game'))
print(classify('Алиса, добавь музло дважды трижды', 'game'))
print(classify('-a', 3))
print(classify('-a', 0))