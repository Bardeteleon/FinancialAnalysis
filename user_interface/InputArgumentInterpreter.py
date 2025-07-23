import os
from user_interface.logger import logger
import re
from typing import List, Optional
from FinancialAnalysisInput import FinancialAnalysisInput

class InputArgumentInterpreter:

    def __init__(self, input_dir_path : str, tags_json_path : str, config_json_path : str):
        self.__input_dir_path : str = input_dir_path
        self.__tags_json_path : str = tags_json_path
        self.__config_json_path : str = config_json_path

        self.__input_files : List[os.PathLike] = []
        self.__base_path : os.PathLike = None
        self.__tags_json_file : os.PathLike = None
        self.__config_json_file : os.PathLike = None
        self.__error : bool = False

    def get_financial_analysis_input(self) -> Optional[FinancialAnalysisInput]:
        return FinancialAnalysisInput(self.__input_files, self.__tags_json_file, self.__config_json_file) if not self.has_error() else None

    def get_input_files(self) -> List[os.PathLike]:
        return self.__input_files
    
    def get_tags_json_file(self) -> Optional[os.PathLike]:
        return self.__tags_json_file

    def get_config_json_file(self) -> Optional[os.PathLike]:
        return self.__config_json_file

    def run(self):
        self.__interpret_input_dir_path()
        logger.info(self.__base_path)
        self.__interpret_tags_json_path()
        self.__interpret_config_json_path()
    
    def has_error(self) -> bool:
        return self.__error

    def __interpret_input_dir_path(self):
        if self.has_error():
            return
        cwd_joined_input_dir_path = os.path.join(os.getcwd(), self.__input_dir_path)
        input_dir_path = os.path.normpath(self.__input_dir_path)
        if os.path.isdir(input_dir_path) and os.path.isabs(input_dir_path):
            self.__input_files = self.__find_files_in_directory_recursively(input_dir_path)
            self.__base_path = os.path.join(input_dir_path, os.pardir)
        elif os.path.isdir(cwd_joined_input_dir_path):
            self.__input_files = self.__find_files_in_directory_recursively(cwd_joined_input_dir_path)
            self.__base_path = os.path.join(cwd_joined_input_dir_path, os.pardir)
        elif os.path.isfile(input_dir_path) and os.path.isabs(input_dir_path):
            self.__input_files = [input_dir_path]
            self.__base_path = os.path.join(input_dir_path, os.pardir)
        elif os.path.isfile(cwd_joined_input_dir_path):
            self.__input_files = [cwd_joined_input_dir_path]
            self.__base_path = os.getcwd()
        else:
            self.__error = True
            logger.error(f"Unable to interpret input_dir_path: {self.__input_dir_path}. It can be an absolute or relative to cwd file or directory with files.")

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
        if self.has_error():
            return
        cwd_joined_tags_json_path = os.path.join(os.getcwd(), self.__tags_json_path)
        base_path_joined_tags_json_path = os.path.join(self.__base_path, self.__tags_json_path)
        tags_json_path = os.path.normpath(self.__tags_json_path)
        if os.path.isfile(tags_json_path) and os.path.isabs(tags_json_path):
            self.__tags_json_file = tags_json_path
        elif os.path.isfile(cwd_joined_tags_json_path):
            self.__tags_json_file = cwd_joined_tags_json_path
        elif os.path.isfile(base_path_joined_tags_json_path):
            self.__tags_json_file = base_path_joined_tags_json_path
        else:
            self.__error = True
            logger.error(f"Unable to interpret tags_json_path: {self.__tags_json_path}. It can be an absolute or relative to cwd file path.")

    def __interpret_config_json_path(self):
        if self.has_error():
            return
        cwd_joined_config_json_path = os.path.join(os.getcwd(), self.__config_json_path)
        base_path_joined_config_json_path = os.path.join(self.__base_path, self.__config_json_path)
        config_json_path = os.path.normpath(self.__config_json_path)
        if os.path.isfile(config_json_path) and os.path.isabs(config_json_path):
            self.__config_json_file = config_json_path
        elif os.path.isfile(cwd_joined_config_json_path):
            self.__config_json_file = cwd_joined_config_json_path
        elif os.path.isfile(base_path_joined_config_json_path):
            self.__config_json_file = base_path_joined_config_json_path
        else:
            self.__error = True
            logger.error(f"Unable to interpret config_json_path: {self.__config_json_path}. It can be an absolute or relative to cwd file path.")
