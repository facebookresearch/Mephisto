---
sidebar_position: 2
---

# Hosting task assets

Generally there are two models for hosting assets related to a task, with distinct tradeoffs. These are to upload files to the routing server, or to store the files locally on Mephisto and share the data on connection. The former is generally the easier solution.


### Uploading files

**Pros:**
- Really simple to implement with `StaticBlueprint`-based tasks.
- Reduces bandwidth concerns from the main server running Mephisto, as the data is managed on the routing server.

**Cons:**
- Requires more storage space on the routing server. In some `Architect`s (like the `EC2Architect`), this may increase costs. In others (like the `HerokuArchitect`), it may not even be possible to exceed a maximum server size.
- Data is stored on an external server, and can be directly addressed. This exposes your source data to crawling while the server is up.
- Requires manual setup implementation on `Blueprint`s that don't extend the `StaticBlueprint`.

The method of uploading files directly involves taking a folder and uploading its contents to the statically accessible part of the routing server. With `StaticBlueprint`s, this is done by providing an argument for `mephisto.blueprint.extra_source_dir`. For instance:

```yaml
# my_conf.yaml
mephisto:
  blueprint:
    extra_source_dir: my_path/
...
```

This would make all of the files available at `my_path/` accessible from the frontend. As such, if the file `my_path/TestImg.png` was on the local machine running mephisto, you could access `<server>/TestImg.png` from your frontend. For instance:
```js
function LoadedImage({source}) {
  ...
  return <div>
    <img src={source}/>
  </div>
}
```
This component would be able to render with `<LoadedImage source={'TestImg.png'} />`. This means you can pass data for each task for the files you want it to reference in `task_data` and use these in the frontend.

### Local storage of files

**Pros:**
- All data is stored locally, and cannot be directly compromised. 
- Works with any `Architect`s and `Blueprint`s.

**Cons:**
- Increases the size of saved data, as base64 encodings of files will be included in the final files
- Reduces bandwidth for the task, as the Mephisto server is responsible for sending potentially large files

This process involves sending the binary of the object to the frontend, and directly rendering it. You'd likely do this process while assembling a `task_data` array. For instance if you're working with images:
```python
import base64

def get_task_data(img_dir: str):
    imgs = {}
    for filename in os.listdir(img_dir):
        with open(os.path.join(img_dir, filename), 'rb') as bin_image:
            imgs[filename] = "data:image/jpeg;base64," + base64.b64encode(bin_image.read())
    
    return [{'img_name': k, 'img_data': v} for k, v in imgs]
```

Then on the frontend you can access the `img_data` and use it in a component directly. For instance:

```js
function PassedImage({img_data}) {
  ...
  return <div>
    <img src={img_data}/>
  </div>
}
```

If data issues are a concern, one could modify the `AgentState` to delete the `img_data` (or other data-heavy keys) and retain filenames on the final save.