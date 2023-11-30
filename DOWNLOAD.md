Dataset **CosegPP** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://www.dropbox.com/scl/fi/l46ksr90kbfteaz1gn1aw/cosegpp-DatasetNinja.tar?rlkey=3ewin2u27ibose6a6kqyzeoh3&dl=1)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='CosegPP', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be downloaded here:

- [Images](https://zenodo.org/record/5117176/files/CosegPP.zip?download=1)
- [Annotations](https://zenodo.org/record/5117176/files/CosegPP_groundtruth.zip?download=1)
