import os
import json

class FileEditor:
    """
    Class to edit files based on the data provided in a JSON file or dictionary.

    Args:
    - json_file: path to the JSON file containing the data to edit the file
    - data: dictionary containing the data to edit the file

    Methods:
    - process: process the main operation (create or edit)
    - create_file: create a new file with the provided code
    - edit_file: edit the file from the start line to the end line with the provided code
    - delete_file: delete the file
    - delete_lines: delete the lines from the start line to the end line
    - append_to_beginning: append content to the beginning of the file
    - append_to_end: append content to the end of the file
    - insert_at_line: insert content at a specific line
    - replace_text: replace all occurrences of a text with another text
    - rename_file: rename the file
    """
    def __init__(self, json_file: str = None, data: dict = None):
        if data:
            self.data = data
        elif json_file:
            with open(json_file, 'r') as f:
                self.data = json.load(f)
        else:
            raise ValueError("Either json_file or data must be provided")

    def process(self):
        switcher = {
            'create': self.create_file,
            'edit': self.edit_file,
            'delete': self.delete_file,
            'delete_lines': self.delete_lines,
            'append_to_beginning': self.append_to_beginning,
            'append_to_end': self.append_to_end,
            'insert_at_line': self.insert_at_line,
            'replace_text': self.replace_text,
            'rename': self.rename_file
        }
        operation = self.data.get('op')
        func = switcher.get(operation)
        if func:
            func()
            return str(switcher.get(operation)) + self.data['file']
        else:
            print(f"Operation '{operation}' not supported.")
            return f"Operation '{operation}' not supported."


    def create_file(self):
        print("entered create file")
        with open(self.data['file'], 'w') as f:
            print("entered create file")
            f.write(self.data['code'])
        print(f"File {self.data['file']} created.")

    def edit_file(self):
        with open(self.data['file'], 'r') as f:
            lines = f.readlines()

        start, end = self.data['start'] - 1, self.data['end']
        new_lines = lines[:start] + [self.data['code']] + lines[end:]

        with open(self.data['file'], 'w') as f:
            f.writelines(new_lines)
        print(f"File {self.data['file']} edited from line {self.data['start']} to {self.data['end']}.")

    def delete_file(self):
        if os.path.exists(self.data['file']):
            os.remove(self.data['file'])
            print(f"File {self.data['file']} deleted.")
        else:
            print(f"File {self.data['file']} does not exist.")

    def delete_lines(self):
        with open(self.data['file'], 'r') as f:
            lines = f.readlines()

        start, end = self.data['start'] - 1, self.data['end']
        new_lines = lines[:start] + lines[end:]

        with open(self.data['file'], 'w') as f:
            f.writelines(new_lines)
        print(f"Lines {self.data['start']} to {self.data['end']} deleted from {self.data['file']}.")

    def append_to_beginning(self, content: str):
        with open(self.data['file'], 'r+') as f:
            existing_content = f.read()
            f.seek(0, 0)
            f.write(content.rstrip('\r\n') + '\n' + existing_content)
        print(f"Content appended to the beginning of {self.data['file']}.")

    def append_to_end(self, content: str):
        with open(self.data['file'], 'a') as f:
            f.write('\n' + content.lstrip('\r\n'))
        print(f"Content appended to the end of {self.data['file']}.")

    def insert_at_line(self, line_number: int, content: str):
        with open(self.data['file'], 'r') as f:
            lines = f.readlines()

        lines.insert(line_number - 1, content.rstrip('\r\n') + '\n')

        with open(self.data['file'], 'w') as f:
            f.writelines(lines)
        print(f"Content inserted at line {line_number} in {self.data['file']}.")

    def replace_text(self, old_text: str, new_text: str):
        with open(self.data['file'], 'r') as f:
            content = f.read()

        content = content.replace(old_text, new_text)

        with open(self.data['file'], 'w') as f:
            f.write(content)
        print(f"All occurrences of '{old_text}' replaced with '{new_text}' in {self.data['file']}.")

    def rename_file(self, new_name: str):
        old_name = self.data['file']
        os.rename(old_name, new_name)
        self.data['file'] = new_name
        print(f"File renamed from {old_name} to {new_name}.")