from sbdk.error import SbdkError


def check_project_dir(project):
    if not project.project_dir:
        raise SbdkError("Can't execute command: can't find project directory")


def check_project_data(project):
    if not project.project_data:
        raise SbdkError("Can't execute command: doesn't have a project data directory")


def check_project_state(project):
    if not project.state:
        raise SbdkError("Can't execute command: doesn't have a project state")


def check_image(project):
    if not project.image_id:
        raise SbdkError("Can't execute command: image-id not provided")
