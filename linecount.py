import os


total_line_count = 0

for subdirectories, directories, files in os.walk('.'):
    if 'venv' in subdirectories:
        continue

    for file_name in files:
        if file_name == 'linecount.py':
            continue

        file_loc = subdirectories + os.path.sep + file_name

        if file_loc.endswith(".py"):
            with open(file_loc) as file:
                line_count = len(file.readlines())

            total_line_count += line_count
            print(f'{file_loc} - {line_count}')

print(f'Total line count: {total_line_count}')
