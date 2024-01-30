
from dataclasses import dataclass
import os
from typing import List

@dataclass
class FinancialAnalysisInput:
    input_files : List[os.PathLike]
    tags_json_file : os.PathLike
    config_json_file : os.PathLike