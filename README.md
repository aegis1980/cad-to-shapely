# CAD to shapely

convert a CAD file to [shapely](https://pypi.org/project/Shapely/) geometry for downstream processing.
Currently supports, to varying degrees:

- DXF using [ezdxf](https://pypi.org/project/ezdxf/)
- (IGES to follow)
- (SVG to follow)

## Utils

Also some utils in utils.py

## Example

To run example in `example.py` you need to install matplotlib `pip install matplotlib`.

## Development

1. right click on project root folder > select **open in terminal**
2. `python -m venv .venv` to setup python virtual environment for this project. TIP: copy from here and right click in terminal to paste-and-execute.
3. Dialog should come up asking you want this env as interpreter for project: answer yes.
4. If no to (3) on blue ribbon at bottom of VSCODE, on left click on interpreter, chose the **venv** one you just created.
5. Might get some bits and both e.g. 'install pylint' etc. click install for them.
6. `pip install -e .[dev]` to install the package (editable) with dev dependencies

## Releasing

*Note: releasing is only actionable by the repository owner.*

Versioning is handled by [setuptools-scm](https://setuptools-scm.readthedocs.io/): the package
version is derived from the git tag, so there is no version number in the source to bump.
Publishing to PyPI happens automatically via GitHub Actions (`.github/workflows/python-publish.yml`)
using PyPI Trusted Publishing when a GitHub release is published.

To cut a release:

```sh
$env:Path += ";C:\Program Files\GitHub CLI"
```


```sh
gh release create v0.3.3 --generate-notes
```

That's it. Tag format is `vX.Y.Z` (or `X.Y.Z` - both parse). The workflow builds the package
with the version taken from the tag and uploads it to PyPI.
