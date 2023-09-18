import argparse
import json
import os
import sys

import supervisely as sly
from dotenv import load_dotenv

import src.options as o
import src.settings as s
from dataset_tools import ProjectRepo
from src.convert import convert_and_upload_supervisely_project

PARENT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOCAL_ENV = os.path.join(PARENT_PATH, "local.env")from dataset_tools.templates import AnnotationType
from src.settings import ANNOTATION_TYPES

###############################################################################
# ! Set up values if you want to change default values of visualizations
###############################################################################

SAMPLE_RATE = 1  # make less if dataset is too big

# * Preview class to visualize in SUMMARY.md overview section
# * Literal["ClassesPreview", "HorizontalGrid", "SideAnnotationsGrid", "Poster", "HorizontalGridAnimated", "VerticalGridAnimated"]
# * If None, then preview_class will be set automatically to "ClassesPreview"
PREVIEW_CLASS = "Poster"

IS_DETECTION_TASK: bool = None  # ? Set True if you want to visualize only bbox annotations
if IS_DETECTION_TASK is None:
    IS_DETECTION_TASK = ANNOTATION_TYPES == [AnnotationType.ObjectDetection()]

###############################################################
####### * Set up visualization params for Poster class ########
POSTER_IS_DETECTION_TASK: bool = IS_DETECTION_TASK
POSTER_TITLE: str = None
###############################################################


###############################################################
#### * Set up visualization params for HorizontalGrid class ###
HORIZONTAL_GRID_ROWS: int = 1
HORIZONTAL_GRID_COLS: int = 4
HORIZONTAL_GRID_IS_DETECTION_TASK: bool = IS_DETECTION_TASK
###############################################################


###############################################################
#### * Set up visualization params for VerticalGrid class #####
VERTICAL_GRID_ROWS: int = None
VERTICAL_GRID_COLS: int = None
VERTICAL_GRID_IS_DETECTION_TASK: bool = IS_DETECTION_TASK
###############################################################


###############################################################
# * Set up visualization params for SideAnnotationsGrid class #
SIDE_ANNOTATIONS_GRID_ROWS: int = None
SIDE_ANNOTATIONS_GRID_COLS: int = None
SIDE_ANNOTATIONS_GRID_IS_DETECTION_TASK: bool = IS_DETECTION_TASK
###############################################################


###############################################################
###### * Set up visualization params for Previews class #######
PREVIEWS_IS_DETECTION_TASK: bool = IS_DETECTION_TASK
###############################################################

###############################################################
### * Set up visualization params for ClassesPreview class ####
CLASSES_PREVIEW_ROW_HEIGHT: int = None
CLASSES_PREVIEW_PADDINGS: dict = None
CLASSES_PREVIEW_ROWS: int = None
CLASSES_PREVIEW_GAP: int = None
# default {"top": "10%", "bottom": "10%", "left": "10%", "right": "10%"}
# set % or px as string values (e.i. "10%" or "10px")
###############################################################


###############################################################
### * Set up visualization params for ClassesHeatmaps class ###
# args for "to_image" method
DRAW_STYLE: str = None  # "inside_white" or "outside_black"
HEATMAP_ROWS: int = None
HEATMAP_COLS: int = None
HEATMAP_GRID_SPACING: int = None
HEATMAP_OUTER_GRID_SPACING: int = None
HEATMAP_OUTPUT_WIDTH: int = (
    None  # 1 class in dataset? -> 1600px for portrait images, 2200px for landscape
)
###############################################################


##################################
###### ? Do not edit bellow #####
##################################


def get_visualization_options():
    vis_settings = {
        "Poster": {
            "title": POSTER_TITLE,
            "is_detection_task": POSTER_IS_DETECTION_TASK,
        },
        "HorizontalGrid": {
            "rows": HORIZONTAL_GRID_ROWS,
            "cols": HORIZONTAL_GRID_COLS,
            "is_detection_task": HORIZONTAL_GRID_IS_DETECTION_TASK,
        },
        "VerticalGrid": {
            "rows": VERTICAL_GRID_ROWS,
            "cols": VERTICAL_GRID_COLS,
            "is_detection_task": VERTICAL_GRID_IS_DETECTION_TASK,
        },
        "SideAnnotationsGrid": {
            "rows": SIDE_ANNOTATIONS_GRID_ROWS,
            "cols": SIDE_ANNOTATIONS_GRID_COLS,
            "is_detection_task": SIDE_ANNOTATIONS_GRID_IS_DETECTION_TASK,
        },
    }

    checked_vis_settings = {}

    for class_name, class_settings in vis_settings.items():
        new_class_settings = {}
        for field, value in class_settings.items():
            if value is not None:
                new_class_settings[field] = value
        if len(new_class_settings) > 0:
            checked_vis_settings[class_name] = new_class_settings

    return checked_vis_settings


def get_stats_options():
    stats_settings = {
        "ClassesPreview": {
            "row_height": CLASSES_PREVIEW_ROW_HEIGHT,
            "pad": CLASSES_PREVIEW_PADDINGS,
            "rows": CLASSES_PREVIEW_ROWS,
            "gap": CLASSES_PREVIEW_GAP,
        },
        "ClassesHeatmaps": {
            "draw_style": DRAW_STYLE,
            "rows": HEATMAP_ROWS,
            "cols": HEATMAP_COLS,
            "grid_spacing": HEATMAP_GRID_SPACING,
            "outer_grid_spacing": HEATMAP_OUTER_GRID_SPACING,
            "output_width": HEATMAP_OUTPUT_WIDTH,
        },
        "Previews": {
            "is_detection_task": PREVIEWS_IS_DETECTION_TASK,
        },
        "Other": {"sample_rate": SAMPLE_RATE},
    }

    checked_stats_settings = {}

    for class_name, class_settings in stats_settings.items():
        new_class_settings = {}
        for field, value in class_settings.items():
            if value is not None:
                new_class_settings[field] = value
        if len(new_class_settings) > 0:
            checked_stats_settings[class_name] = new_class_settings

    return checked_stats_settings

load_dotenv(os.path.expanduser("~/ninja.env"))
load_dotenv(LOCAL_ENV)
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
TEAM_ID = sly.env.team_id()
WORKSPACE_ID = sly.env.workspace_id()


def get_project_info(api: sly.Api):
    s.check_names()

    project_info = api.project.get_info_by_name(WORKSPACE_ID, s.PROJECT_NAME)
    if not project_info:
        # If project doesn't found on instance, create it and use new project info.
        sly.logger.info(f"Project {s.PROJECT_NAME} not found on instance. Creating a new one...")
        project_info = convert_and_upload_supervisely_project(api, WORKSPACE_ID, s.PROJECT_NAME)
        sly.logger.info("Now you can explore created project and choose 'preview_image_id'.")
        sys.exit(0)
    else:
        sly.logger.info(f"Found project {s.PROJECT_NAME} on instance, will use it.")

    return project_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload dataset to instance.")
    parser.add_argument(
        "--forces", type=json.loads, default="{}", help="Which parameters to force."
    )

    args = parser.parse_args()
    forces = args.forces

    sly.logger.info(f"Script is starting with forces: {forces}")

    sly.fs.mkdir("./stats")
    sly.fs.mkdir("./visualizations")

    api = sly.Api.from_env()
    sly.logger.info(
        f"Connected to Supervisely. Server address: {SERVER_ADDRESS}, team_id: {TEAM_ID}, workspace_id: {WORKSPACE_ID}."
    )
    project_id = get_project_info(api).id
    settings = s.get_settings()

    stat_options = o.get_stats_options()
    vis_options = o.get_visualization_options()

    sly.logger.info(f"Starting to work with project id: {project_id}.")

    force_stats = forces.get("force_stats")
    force_visuals = forces.get("force_visuals")
    force_demo = forces.get("force_demo")
    force_download_sly_url = forces.get("force_download_sly_url")
    force_texts = forces.get("force_texts")

    settings["force_texts"] = force_texts
    settings["force_download_sly_url"] = force_download_sly_url
    project_repo = ProjectRepo(api, project_id, settings)
    project_repo.build_stats(force=force_stats, settings=stat_options)
    project_repo.build_visualizations(force=force_visuals, settings=vis_options)
    project_repo.build_demo(force=force_demo)
    project_repo.build_texts(force=force_texts, preview_class=o.PREVIEW_CLASS)

    sly.logger.info("Script finished.")
