import os
import archiver

groups = []

for item in os.listdir('.'):
    if item.endswith('.json'):
        data = archiver.load(item)
        if 'group' in data and data['group'] not in groups:
            groups.append(data['group'])
    elif item.endswith('.md'):
        with open(item, 'r') as f:
            print(f.readline().strip())

print()

print(*sorted(groups), sep='\n')
