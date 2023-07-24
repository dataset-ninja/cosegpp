import supervisely as sly
import os
from dataset_tools.convert import unpack_if_archive
import src.settings as s
from urllib.parse import unquote, urlparse
from supervisely.io.fs import get_file_name, get_file_size
import shutil
import cv2
from tqdm import tqdm


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(desc=f"Downloading '{file_name_with_ext}' to buffer...", total=fsize) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    datasets = [
        "/mnt/c/users/german/documents/CosegPP/Buckwheat-C-1",
        "/mnt/c/Users/German/Documents/CosegPP/Buckwheat-D-1",
        "/mnt/c/Users/German/Documents/CosegPP/Sunflower-C-1",
        "/mnt/c/Users/German/Documents/CosegPP/Sunflower-D-1",
    ]

    def load_image_labels(image_path, labels_path):
        image_info = api.image.upload_path(
            dataset.id,
            (
                os.path.basename(image_path)
                + "_"
                + os.path.basename(sub_dataset)
                + "_"
                + os.path.basename(dataset_path)
            ),
            image_path,
        )
        mask = cv2.imread(labels_path, cv2.IMREAD_GRAYSCALE)
        thresh = 127
        labels = []
        mask_height, mask_width = mask.shape
        height = image_info.height
        width = image_info.width
        if [mask_height, mask_width] != [height, width]:
            mask = cv2.resize(mask, (width, height))
            # cv2.imwrite("maska_test.jpg", mask)
        im_bw = cv2.threshold(mask, thresh, 255, cv2.THRESH_BINARY)[1]

        bitmap_annotation = sly.Bitmap(
            im_bw,
        )
        obj_class = meta.get_obj_class(os.path.basename(dataset_path))
        label = sly.Label(bitmap_annotation, obj_class)
        labels.append(label)

        img_tag = sly.Tag(meta=img_tag_meta, value=os.path.basename(sub_dataset))

        ann = sly.Annotation(img_size=[height, width], labels=labels, img_tags=[img_tag])
        api.annotation.upload_ann(image_info.id, ann)

    # create project and initialize meta
    project = api.project.create(workspace_id, project_name)
    meta = sly.ProjectMeta()

    oneof_values = [
        "Fluo_SV_0",
        "Fluo_SV_72",
        "Fluo_SV_144",
        "Fluo_SV_216",
        "IR_SV_0",
        "IR_SV_72",
        "IR_SV_144",
        "IR_SV_216",
        "Vis_SV_0",
        "Vis_SV_72",
        "Vis_SV_144",
        "Vis_SV_216",
    ]
    img_tag_meta = sly.TagMeta(
        name="modality and resolution",
        value_type=sly.TagValueType.ONEOF_STRING,
        possible_values=oneof_values,
    )
    meta = sly.ProjectMeta.add_tag_meta(meta, img_tag_meta)
    api.project.update_meta(project.id, meta)

    for dataset_path in datasets:
        dataset = api.dataset.create(project.id, os.path.basename(dataset_path))
        # create object class
        cl = sly.ObjClass(os.path.basename(dataset_path), sly.Bitmap, color=[0, 255, 0])
        meta = meta.add_obj_class(cl)
        api.project.update_meta(project.id, meta)

        # iterate throught subdatasets
        datasets_subdir = [f.path for f in os.scandir(dataset_path) if f.is_dir()]
        for sub_dataset in datasets_subdir:
            mask_folder_path = os.path.join(
                os.path.dirname(dataset_path) + "_groundtruth",
                os.path.basename(dataset_path),
                os.path.basename(sub_dataset),
            )
            mask_path = sly.fs.list_files(mask_folder_path)
            # upload masks to images
            pbar = tqdm(desc=os.path.basename(sub_dataset), total=len(mask_path))
            for path in mask_path:
                if os.path.basename(path) == ".DS_Store":
                    pbar.update(1)
                    continue
                img_path = os.path.join(sub_dataset, os.path.basename(path))
                try:
                    load_image_labels(img_path, path)
                    pbar.update(1)
                except Exception as e:
                    print(e)
                    pbar.update(1)
                    continue
            pbar.close()
        print(f"Dataset '{dataset.name}' has been successfully created.")
    return project
