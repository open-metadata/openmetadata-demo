# OpenMetadata 2.0 RC1 Facade Limitations

> Applies exactly to `openmetadata-ingestion==2.0.0.0rc1` and the OpenMetadata
> `2.0.0-rc1-release` source at commit
> `8e199f486b63df9f44d4c827a9f43559d9e56e07`.

Three Context Center facades are exported by the Python SDK, and their generated
create models validate, but the RC1 Python client's route map does not contain
their entity types. A facade call reaches `OpenMetadata.get_suffix()` and raises
`MissingEntityTypeException` before it can issue an HTTP request.

| Facade | Create model | RC1 behavior |
| --- | --- | --- |
| `ContextFiles` | `CreateContextFile` | Entity type works; CRUD route resolution fails |
| `Folders` | `CreateFolder` | Entity type works; CRUD route resolution fails |
| `Pages` | `CreatePage` | Entity type works; CRUD route resolution fails |

The request models themselves are usable:

```python
from metadata.generated.schema.api.data.createContextFile import CreateContextFile
from metadata.generated.schema.api.data.createFolder import CreateFolder
from metadata.generated.schema.api.data.createPage import CreatePage
from metadata.generated.schema.entity.data.article import Article
from metadata.generated.schema.entity.data.contextFile import FileType
from metadata.generated.schema.entity.data.page import PageType

context_file = CreateContextFile(name="demo_file", fileType=FileType.Document)
folder = CreateFolder(name="demo_folder")
page = CreatePage(name="demo_page", pageType=PageType.Article, page=Article())
```

The intended public interface remains plain:

```python
from metadata.sdk import ContextFiles, Folders, Pages

intended_calls = (
    (ContextFiles, context_file),
    (Folders, folder),
    (Pages, page),
)
```

Do not execute those facade mutations with RC1. This repository intentionally
does not modify the SDK route map and does not ship a private client workaround.
No REST fallback is provided. These three examples are model-only until the
upstream SDK exposes working route resolution; they are not live-runnable.

## Live Method Limitations

Three route-backed helper methods also fail against the matching RC1 server or
SDK. The affected facades remain live-runnable through their other public
methods.

| Method | RC1 behavior | Example behavior |
| --- | --- | --- |
| `Containers.set_parent()` | The server-side re-parent PATCH raises an internal error while updating legacy feed links | `storage-assets` supplies the parent in `CreateContainerRequest`, then reads children and ancestors |
| `Metrics.add_related_metrics()` | The helper builds a plain list where the RC1 patch builder expects `EntityReferenceList`, so the patch is skipped | `governance-assets` deep-copies the metric and calls `Metrics.update()` |
| `DataContracts.validate_request()` | The validation endpoint returns a preview shape that the RC1 SDK tries to parse as `DataContractResult` | `governance-assets` validates `CreateDataContractRequest` locally, then creates and retrieves the contract |

The examples do not call these broken helpers, hide their failures, patch the
SDK, or add REST fallbacks. These limits were reproduced with the official
`2.0.0-rc1` Docker images and the exact Python dependency above.
