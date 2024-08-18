from typing import Any, Dict, List, Optional, Union

import pandas as pd

SourceTypeVar = Optional[Union[pd.DataFrame, str, bytes, Dict[str, Any]]]
StrLStrTypeVar = Optional[Union[str, List[str]]]
