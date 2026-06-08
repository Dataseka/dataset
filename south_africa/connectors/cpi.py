import io
import os
import pathlib
import shutil
import zipfile

import httpx

from south_africa.tools import utils
from south_africa.tools.http_client import HttpClient

DATA_FOLDER = pathlib.Path(__file__).parent.parent / "data"
CPI_AVG_ALL_URBAN_FILE = f"{DATA_FOLDER}/cpi-avg-prices-all-urban"


async def download(url: str):
    async with HttpClient() as http_client:
        try:
            resp = await http_client.get(url=url)

            with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                for original_name in z.namelist():
                    if original_name.endswith("/"):
                        continue

                    url = os.path.basename(original_name)

                    slug_name = utils.slugify(filename=url)

                    destination_filepath = os.path.join(DATA_FOLDER, slug_name)

                    with (
                        z.open(original_name) as source,
                        open(destination_filepath, "wb") as target,
                    ):
                        shutil.copyfileobj(source, target)

            print(f"File download complete: {slug_name}")
        except httpx.HTTPStatusError as exc:
            print(f"Http error: {exc}")
        except Exception as exc:
            print(f"Processing error: {exc}")
