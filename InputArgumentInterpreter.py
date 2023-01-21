import os
import logging
from typing import List, Optional

class InputArgumentInterpreter:

    def __init__(self, input_dir_path : str, tags_json_path : str):
        self.__input_dir_path : str = input_dir_path
        self.__tags_json_path : str = tags_json_path

        self.__input_files : List[os.PathLike] = []
        self.__tags_json_file : os.PathLike = None

    def get_input_files(self) -> List[os.PathLike]:
        return self.__input_files
    
    def get_tags_json_file(self) -> Optional[os.PathLike]:
        return self.__tags_json_file

    def run(self):
        self.__interpret_input_dir_path()
        self.__interpret_tags_json_path()

    def __interpret_input_dir_path(self):
        cwd_joined_input_dir_path = os.path.join(os.getcwd(), self.__input_dir_path)
        input_dir_path = os.path.normpath(self.__input_dir_path)
        if os.path.isdir(input_dir_path) and os.path.isabs(input_dir_path):
            self.__input_files = self.__find_files_in_directory(input_dir_path)
        elif os.path.isdir(cwd_joined_input_dir_path):
            self.__input_files = self.__find_files_in_directory(cwd_joined_input_dir_path)
        elif os.path.isfile(input_dir_path) and os.path.isabs(input_dir_path):
            self.__input_files = [input_dir_path]
        elif os.path.isfile(cwd_joined_input_dir_path):
            self.__input_files = [cwd_joined_input_dir_path]
        else:
            logging.error(f"Unable to interpret input_dir_path: {self.__input_dir_path}. It can be an absolute or relative to cwd file or directory with files.")

    def __find_files_in_directory(self, directory : os.PathLike) -> List[os.PathLike]:
        return [os.path.join(directory, file) for file in os.listdir(directory)]

    def __interpret_tags_json_path(self):
        cwd_joined_tags_json_path = os.path.join(os.getcwd(), self.__tags_json_path)
        tags_json_path = os.path.normpath(self.__tags_json_path)
        if os.path.isfile(tags_json_path) and os.path.isabs(tags_json_path):
            self.__tags_json_file = tags_json_path
        elif os.path.isfile(cwd_joined_tags_json_path):
            self.__tags_json_file = cwd_joined_tags_json_path
        else:
            logging.error(f"Unable to interpret tags_json_path: {self.__tags_json_path}. It can be an absolute or relative to cwd file path.")
