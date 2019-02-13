def classify(text, mode):
    from little_fuctions import language_match
    if mode == '':
        mode = 0
    text = text.strip()
    text = text.lower()
    text.replace(' - ', ' ')
    if text[0] == '+':
        add_word = True
        text = text[1:]
        text = text.strip()
        if not text:
            return {'class': 'use_mode', 'answer': '+'}
    else:
        add_word = False
    if text[0] == '-':
        del_word = True
        text = text[1:]
        text = text.strip()
        if not text:
            return {'class': 'use_mode', 'answer': '-'}
    else:
        del_word = False

    if text.startswith('alice, add word') or text.startswith('алиса, добавь слов') or \
            text.startswith('alice add word') or text.startswith('алиса добавь слов') or \
            text.startswith('алиса добавить слов') or text.startswith('алиса, добавить слов'):
        if text.count(' ') >= 3:
            text = ' '.join(text.split()[3:])
            add_word = True
        else:
            return {'class': 'use_mode', 'answer': text}

    elif text.startswith('alice, add') or text.startswith('алиса, добавь') or \
            text.startswith('add word') or text.startswith('добавь слов') or \
            text.startswith('alice add') or text.startswith('алиса добавь') or \
            text.startswith('алиса, добавить') or text.startswith('добавить слов') or \
            text.startswith('алиса, добавить'):
        if text.count(' ') >= 2:
            text = ' '.join(text.split()[2:])
            add_word = True
        else:
            return {'class': 'use_mode', 'answer': text}

    elif text.startswith('alice') or text.startswith('алиса') or \
            text.startswith('add') or text.startswith('добавь') or \
            text.startswith('word') or text.startswith('слов'):
        if ' ' in text:
            if not (text.startswith('alice') or text.startswith('алиса')):
                add_word = True
            text = text[text.index(' ') + 1:]
        else:
            if (text.startswith('alice') or text.startswith('алиса')):
                return {'class': 'its me', 'answer': text}
            else:
                return {'class': 'use_mode', 'answer': text}

    if add_word:
        for i in range(len(text)):
            if text[i] == ' ':
                words = [text[:i], text[i + 1:]]
                if language_match(words[0], words[1]):
                    return {'class': 'add', 'answer': words}
        else:
            return {'class': 'translate&suggest_to_add', 'answer': text}

    if text.startswith('alice, del word') or text.startswith('алиса, удали слов') or \
            text.startswith('alice del word') or text.startswith('алиса удали слов') or \
            text.startswith('алиса удалить слов') or text.startswith('alice delete word') or \
            text.startswith('alice, delete word') or text.startswith('алиса, удалить слов'):
        if text.count(' ') >= 3:
            text = ' '.join(text.split()[3:])
            return  {'class': 'del', 'answer': text}
        else:
            return {'class': 'use_mode', 'answer': text}

    elif text.startswith('alice, del') or text.startswith('алиса, удали') or \
            text.startswith('del word') or text.startswith('удали слов') or \
            text.startswith('alice del') or text.startswith('алиса удали') or \
            text.startswith('alice, delete') or text.startswith('алиса, удалить') or \
            text.startswith('delete word') or text.startswith('удалить слов') or \
            text.startswith('alice delete') or text.startswith('алиса удалить'):
        if text.count(' ') >= 2:
            text = ' '.join(text.split()[2:])
            return {'class': 'del', 'answer': text}
        else:
            return {'class': 'use_mode', 'answer': text}

    elif text.startswith('delete') or text.startswith('del') or \
            text.startswith('удали') or text.startswith('удалить'):
        if text.count(' ') >= 1:
            text = ' '.join(text.split()[1:])
            return  {'class': 'del', 'answer': text}
        else:
            return {'class': 'use_mode', 'answer': text}

    return {'class': 'use_mode', 'answer': text}