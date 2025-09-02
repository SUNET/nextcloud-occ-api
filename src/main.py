import subprocess
import tempfile
import os
import base64
from shlex import quote
from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel


class Command(BaseModel):
    command: str
    parameters: list[str] | None = None
    env: dict[str, str] | None = None
    files: dict[str, str] | None = None


app = FastAPI()
router = APIRouter()


@router.post("/occ/")
def run_command(command: Command, request: Request):
    our_token = os.environ['OCC_TOKEN']
    base64_token = request.headers['Authorization'].split(' ')[1]
    their_token = base64.b64decode(base64_token).decode()
    if not (their_token and our_token):
        return {"message": "Missing token"}
    if not (their_token == our_token):
        return {"message": "Invalid token"}

    cmdline = ["php", "/var/www/html/occ", quote(command.command)]
    if command.parameters:
        for param in command.parameters:
            cmdline.append(quote(param))
    temp_dir = tempfile.TemporaryDirectory()
    if command.files:
        for filename, file in command.files:
            with open(os.path.join(temp_dir.name, filename), "w") as fh:
                fh.write(file)

    result = subprocess.run(cmdline,
                            env=command.env,
                            capture_output=True,
                            shell=False)
    temp_dir.cleanup()
    return {
        "message": "Command executed",
        "result": result.returncode,
        "output": result.stdout.decode()
    }


app.include_router(router)
