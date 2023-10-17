Dataset **CosegPP** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/j/I/fS/pEAYryGnMjOEW7DK9NK9hrSue9n2e7I3px02pUVIIRga6owWf1OZgepHi9dmttfaB2s3cGsNNHWukM4ROEjc14kDd0EP8pXqIuHbxjxa3wuoHw4WxxsmqvgEGjsN.tar)

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
