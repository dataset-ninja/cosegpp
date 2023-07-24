Please visit dataset [homepage](https://doi.org/10.5281/zenodo.5117176) to download the data. 

Afterward, you have the option to download it in the universal supervisely format by utilizing the *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='CosegPP', dst_path='~/dtools/datasets/CosegPP.tar')
```
