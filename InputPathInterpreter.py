import os
from typing import List

class InputPathInterpreter:

    def __init__(self, input_path : str):
        self.__input_path : str = input_path

        self.__input_files : List[os.PathLike] = []

    def run(self):
        cwd_joined_input_path = os.path.join(os.getcwd(), self.__input_path)
        input_path = os.path.normpath(self.__input_path)
        if os.path.isdir(input_path) and os.path.isabs(input_path):
            print("1")
            self.__input_files = self.__find_files_in_directory(input_path)
        elif os.path.isdir(cwd_joined_input_path):
            print("2")
            self.__input_files = self.__find_files_in_directory(cwd_joined_input_path)
        elif os.path.isfile(input_path) and os.path.isabs(input_path):
            print("3")
            self.__input_files = [input_path]
        elif os.path.isfile(cwd_joined_input_path):
            print("4")
            self.__input_files = [cwd_joined_input_path]
        else:
            raise RuntimeError(f"Unable to interpret input_path: {self.__input_path}. It can be an absolute or relative to cwd file or directory with files.")

    def get_input_files(self) -> List[os.PathLike]:
        return self.__input_files

    def __find_files_in_directory(self, directory : os.PathLike) -> List[os.PathLike]:
        return [os.path.join(directory, file) for file in os.listdir(directory)]
