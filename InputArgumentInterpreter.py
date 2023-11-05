import os
import logging
import re
from typing import List, Optional

class InputArgumentInterpreter:

    def __init__(self, input_dir_path : str, tags_json_path : str):
        self.__input_dir_path : str = input_dir_path
        self.__tags_json_path : str = tags_json_path

        self.__input_files : List[os.PathLike] = []
        self.__tags_json_file : os.PathLike = None

    def get_input_files(self) -> List[os.PathLike]:
        return self.__input_files

    def get_filtered_input_files(self, filter : str):
        return [file for file in self.__input_files if re.search(filter, file)]
    
    def get_tags_json_file(self) -> Optional[os.PathLike]:
        return self.__tags_json_file

    def run(self):
        self.__interpret_input_dir_path()
        self.__interpret_tags_json_path()

    def __interpret_input_dir_path(self):
        cwd_joined_input_dir_path = os.path.join(os.getcwd(), self.__input_dir_path)
        input_dir_path = os.path.normpath(self.__input_dir_path)
        if os.path.isdir(input_dir_path) and os.path.isabs(input_dir_path):
            self.__input_files = self.__find_files_in_directory_recursively(input_dir_path)
        elif os.path.isdir(cwd_joined_input_dir_path):
            self.__input_files = self.__find_files_in_directory_recursively(cwd_joined_input_dir_path)
        elif os.path.isfile(input_dir_path) and os.path.isabs(input_dir_path):
            self.__input_files = [input_dir_path]
        elif os.path.isfile(cwd_joined_input_dir_path):
            self.__input_files = [cwd_joined_input_dir_path]
        else:
            logging.error(f"Unable to interpret input_dir_path: {self.__input_dir_path}. It can be an absolute or relative to cwd file or directory with files.")

    def __find_files_in_directory_recursively(self, directory : os.PathLike) -> List[os.PathLike]:
        result = []
        for path in os.listdir(directory):
            absolute_path = os.path.join(directory, path)
            if os.path.isfile(absolute_path):
                result.append(absolute_path)
            else:
                result_from_subdir = self.__find_files_in_directory_recursively(absolute_path)
                if len(result_from_subdir) > 0:
                    result += result_from_subdir
        return result

    def __interpret_tags_json_path(self):
        cwd_joined_tags_json_path = os.path.join(os.getcwd(), self.__tags_json_path)
        tags_json_path = os.path.normpath(self.__tags_json_path)
        if os.path.isfile(tags_json_path) and os.path.isabs(tags_json_path):
            self.__tags_json_file = tags_json_path
        elif os.path.isfile(cwd_joined_tags_json_path):
            self.__tags_json_file = cwd_joined_tags_json_path
        else:
            logging.error(f"Unable to interpret tags_json_path: {self.__tags_json_path}. It can be an absolute or relative to cwd file path.")
